import json
import os
import random


def build_pairs():
    os.makedirs("data/eval", exist_ok=True)

    # Generate 2,500 train pairs and 500 held-out pairs from corpus chunks
    import glob

    from hybridrag.ingest.chunker import chunk_text
    from hybridrag.ingest.pipeline import load_structured_chunks

    chunks = []
    for path in glob.glob(os.path.join("data/corpus", "*.md")):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        doc_id = os.path.basename(path).replace(".md", "")
        chunks.extend(chunk_text(text, doc_id, {}))
    chunks.extend(load_structured_chunks())

    random.seed(42)
    random.shuffle(chunks)

    split_idx = int(len(chunks) * 0.8)
    train_chunks = chunks[:split_idx]
    heldout_chunks = chunks[split_idx:]

    def make_pairs_from_chunks(chunk_list):
        pairs = []
        for c in chunk_list:
            # synthesize query from title and category
            q1 = f"What is the policy regarding {c.title.lower()}?"
            q2 = f"Tell me about {c.category.replace('_', ' ')} guidelines for {c.department}."
            pairs.append({"query": q1, "positive_passage": c.content, "chunk_id": c.chunk_id, "doc_id": c.doc_id})
            pairs.append({"query": q2, "positive_passage": c.content, "chunk_id": c.chunk_id, "doc_id": c.doc_id})
        return pairs

    train_pairs = make_pairs_from_chunks(train_chunks[:1500])
    heldout_pairs = make_pairs_from_chunks(heldout_chunks[:300])

    with open("data/eval/pairs_train.jsonl", "w", encoding="utf-8") as f:
        for p in train_pairs:
            f.write(json.dumps(p) + "\n")

    with open("data/eval/pairs_heldout.jsonl", "w", encoding="utf-8") as f:
        for p in heldout_pairs:
            f.write(json.dumps(p) + "\n")

    print(f"Generated {len(train_pairs)} training pairs and {len(heldout_pairs)} held-out pairs.")
    print(f"Train/Held-out document split: {len(train_chunks)} train chunks, {len(heldout_chunks)} held-out chunks.")

if __name__ == "__main__":
    build_pairs()
