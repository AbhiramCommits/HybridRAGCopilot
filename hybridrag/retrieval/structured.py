import os
import re
import pandas as pd
from hybridrag.config import settings
from hybridrag.models import RetrievalResult, Chunk

class StructuredRetriever:
    def __init__(self):
        self.chunks = []
        self._load_store()

    def _load_store(self):
        if os.path.exists(settings.CHUNKS_STORE_PATH):
            df = pd.read_parquet(settings.CHUNKS_STORE_PATH)
            self.chunks = [Chunk(**row) for _, row in df.iterrows()]

    def search(self, query: str, k: int = 30) -> list[RetrievalResult]:
        if not self.chunks:
            self._load_store()

        q_lower = query.lower()

        # Extract filters with regex and keyword mapping
        category_match = None
        for cat in ["hr_policy", "security_policy", "finance_sop", "engineering_runbook", "product_faq", "vendor_contract"]:
            if cat.replace("_", " ") in q_lower or cat in q_lower:
                category_match = cat

        department_match = None
        for dept in ["hr", "security", "finance", "engineering", "product", "legal", "peopleops", "procurement"]:
            if dept in q_lower:
                department_match = dept.upper()

        sensitivity_match = None
        for sens in ["internal", "confidential", "restricted", "public"]:
            if sens in q_lower:
                sensitivity_match = sens

        # Filter and score chunks
        results = []
        for chunk in self.chunks:
            score = 0.0
            # Boost structured chunks if query implies structured records or specific entity
            if chunk.source_type == "structured":
                score += 1.0

            if category_match and chunk.category == category_match:
                score += 3.0
            if department_match and department_match in chunk.department.upper():
                score += 2.0
            if sensitivity_match and chunk.sensitivity == sensitivity_match:
                score += 1.5

            # Keyword overlap in content or title
            q_words = set(q_lower.split())
            content_words = set(chunk.content.lower().split())
            overlap = len(q_words.intersection(content_words))
            score += float(overlap) * 0.2

            if score > 0:
                results.append(RetrievalResult(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    score=score,
                    retriever_name="structured",
                    chunk=chunk
                ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:k]
