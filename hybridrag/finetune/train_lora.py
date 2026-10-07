import os
import json
import torch
from torch.utils.data import DataLoader
from sentence_transformers import SentenceTransformer, InputExample, losses
from peft import LoraConfig, get_peft_model
from hybridrag.config import settings
from hybridrag.finetune.pairs import build_pairs

def train_lora():
    if not os.path.exists("data/eval/pairs_train.jsonl"):
        build_pairs()

    print("Loading training pairs...")
    train_examples = []
    with open("data/eval/pairs_train.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            train_examples.append(InputExample(texts=[data["query"], data["positive_passage"]]))

    # Limit examples for fast CPU fine-tuning (e.g. 500 steps)
    train_examples = train_examples[:1000]
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

    print(f"Loading base model: {settings.BASE_EMBEDDING_MODEL}")
    model = SentenceTransformer(settings.BASE_EMBEDDING_MODEL)

    # Wrap transformer with PEFT LoRA
    transformer_model = model._first_module().auto_model
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["query", "value"],
        lora_dropout=0.05,
        bias="none"
    )
    peft_model = get_peft_model(transformer_model, peft_config)
    model._first_module().auto_model = peft_model

    trainable_params = sum(p.numel() for p in peft_model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in peft_model.parameters())
    percentage = (trainable_params / total_params) * 100
    print(f"Trainable parameters: {trainable_params:,} / {total_params:,} ({percentage:.2f}%)")

    train_loss = losses.MultipleNegativesRankingLoss(model)

    print("Starting LoRA fine-tuning on CPU (bounded steps)...")
    import time
    t0 = time.time()

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=1,
        steps_per_epoch=50,
        show_progress_bar=True,
        optimizer_params={"lr": 2e-5}
    )

    training_time = time.time() - t0
    print(f"Training completed in {training_time:.2f} seconds.")

    os.makedirs(settings.LORA_MODEL_PATH, exist_ok=True)
    peft_model.save_pretrained(settings.LORA_MODEL_PATH)
    print(f"Saved LoRA adapter to {settings.LORA_MODEL_PATH}")

if __name__ == "__main__":
    train_lora()
