import os
import pickle
import pandas as pd
from hybridrag.config import settings
from hybridrag.models import RetrievalResult, Chunk

class BM25Retriever:
    def __init__(self):
        self.bm25 = None
        self.chunk_ids = []
        self.chunks_map = {}
        self._load_store()

    def _load_store(self):
        if os.path.exists(settings.BM25_STORE_PATH):
            with open(settings.BM25_STORE_PATH, "rb") as f:
                data = pickle.load(f)
                self.bm25 = data["bm25"]
                self.chunk_ids = data["chunk_ids"]
        if os.path.exists(settings.CHUNKS_STORE_PATH):
            df = pd.read_parquet(settings.CHUNKS_STORE_PATH)
            for _, row in df.iterrows():
                chunk = Chunk(**row)
                self.chunks_map[chunk.chunk_id] = chunk

    def search(self, query: str, k: int = 30) -> list[RetrievalResult]:
        if not self.bm25 or not self.chunks_map:
            self._load_store()
        if not self.bm25:
            return []

        # Light normalization: lowercase, keep alphanumeric and currency tokens
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        
        # Sort indices by score descending
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results = []
        for idx in sorted_indices[:k]:
            score = float(scores[idx])
            if score <= 0:
                continue
            chunk_id = self.chunk_ids[idx]
            chunk = self.chunks_map.get(chunk_id)
            if chunk:
                results.append(RetrievalResult(
                    chunk_id=chunk_id,
                    doc_id=chunk.doc_id,
                    score=score,
                    retriever_name="bm25",
                    chunk=chunk
                ))
        return results
