import os
import glob
import pickle
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from hybridrag.config import settings
from hybridrag.models import Chunk
from hybridrag.ingest.chunker import chunk_text
from hybridrag.ingest.structured import seed_structured_data, load_structured_chunks

def load_encoder(mode: str = "base"):
    if mode == "lora" and os.path.exists(settings.LORA_MODEL_PATH):
        try:
            from peft import PeftModel
            from transformers import AutoModel, AutoTokenizer
            base_model = AutoModel.from_pretrained(settings.BASE_EMBEDDING_MODEL)
            model = PeftModel.from_pretrained(base_model, settings.LORA_MODEL_PATH)
            # Wrap in a simple encoder class
            class LoRAModelWrapper:
                def __init__(self, m, base_name):
                    self.m = m
                    self.tokenizer = AutoTokenizer.from_pretrained(base_name)
                    import torch
                def encode(self, sentences, **kwargs):
                    import torch
                    encoded = self.tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")
                    with torch.no_grad():
                        out = self.m(**encoded)
                        # Mean pooling
                        token_embeddings = out[0]
                        input_mask_expanded = encoded['attention_mask'].unsqueeze(-1).expand(token_embeddings.size()).float()
                        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                        embeddings = sum_embeddings / sum_mask
                        # L2 normalize
                        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
                    return embeddings.cpu().numpy()
            return LoRAModelWrapper(model, settings.BASE_EMBEDDING_MODEL)
        except Exception as e:
            print(f"Failed to load LoRA model ({e}), falling back to base model.")
    return SentenceTransformer(settings.BASE_EMBEDDING_MODEL)

def ingest_all(mode: str = "base"):
    print(f"Starting ingestion pipeline with embedding mode: {mode}")
    seed_structured_data()

    # 1. Load unstructured documents
    doc_paths = glob.glob(os.path.join("data/corpus", "*.md"))
    all_chunks = []
    doc_count = 0

    for path in doc_paths:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        doc_id = os.path.basename(path).replace(".md", "")
        chunks = chunk_text(text, doc_id, {})
        all_chunks.extend(chunks)
        doc_count += 1

    # 2. Load structured chunks
    structured_chunks = load_structured_chunks()
    all_chunks.extend(structured_chunks)
    structured_row_count = len(structured_chunks)

    print(f"Loaded {doc_count} unstructured documents and {structured_row_count} structured rows.")
    print(f"Total chunks to index: {len(all_chunks)}")

    # 3. Generate embeddings
    encoder = load_encoder(mode)
    contents = [c.content for c in all_chunks]
    
    # Handle different encoder return types
    if hasattr(encoder, "encode"):
        embeddings = encoder.encode(contents, show_progress_bar=True, convert_to_numpy=True)
    else:
        embeddings = encoder.encode(contents, show_progress_bar=True)

    # Ensure L2 normalized for IndexFlatIP (cosine similarity)
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Save FAISS index
    faiss.write_index(index, settings.FAISS_INDEX_PATH)

    # Save chunks store as Parquet
    df_chunks = pd.DataFrame([c.model_dump() for c in all_chunks])
    # Convert list heading_path to string or json for parquet compatibility
    df_chunks['heading_path'] = df_chunks['heading_path'].apply(lambda x: str(x))
    df_chunks.to_parquet(settings.CHUNKS_STORE_PATH, index=False)

    # Save BM25 corpus pickle (tokenized)
    tokenized_corpus = [c.content.lower().split() for c in all_chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    with open(settings.BM25_STORE_PATH, "wb") as f:
        pickle.dump({"bm25": bm25, "chunk_ids": [c.chunk_id for c in all_chunks]}, f)

    print(f"Ingestion complete! Indexed {doc_count} docs, {structured_row_count} rows, {len(all_chunks)} total chunks.")
    return doc_count, structured_row_count, len(all_chunks)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="base", choices=["base", "lora"])
    args = parser.parse_args()
    ingest_all(args.mode)
