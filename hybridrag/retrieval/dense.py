import os

import faiss
import pandas as pd

from hybridrag.config import settings
from hybridrag.ingest.pipeline import load_encoder
from hybridrag.models import Chunk, RetrievalResult


class DenseRetriever:
    def __init__(self, mode: str = "base"):
        self.mode = mode
        self.encoder = load_encoder(mode)
        self.index = None
        self.chunks = []
        self._load_store()

    def _load_store(self):
        if os.path.exists(settings.FAISS_INDEX_PATH):
            self.index = faiss.read_index(settings.FAISS_INDEX_PATH)
        if os.path.exists(settings.CHUNKS_STORE_PATH):
            df = pd.read_parquet(settings.CHUNKS_STORE_PATH)
            self.chunks = [Chunk(**row) for _, row in df.iterrows()]

    def search(self, query: str, k: int = 30) -> list[RetrievalResult]:
        if not self.index or not self.chunks:
            self._load_store()
        if not self.index or not self.chunks:
            return []

        if hasattr(self.encoder, "encode"):
            q_emb = self.encoder.encode([query], convert_to_numpy=True)
        else:
            q_emb = self.encoder.encode([query])

        faiss.normalize_L2(q_emb)
        scores, indices = self.index.search(q_emb, min(k, len(self.chunks)))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]
            results.append(RetrievalResult(
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                score=float(score),
                retriever_name="dense",
                chunk=chunk
            ))
        return results
