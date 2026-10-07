import time
from typing import List
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from hybridrag.config import settings
from hybridrag.models import FusedResult, RetrievalResult

class CrossEncoderReranker:
    def __init__(self):
        self.model_name = settings.RERANKER_MODEL
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.eval()

    def rerank(self, query: str, candidates: List[FusedResult], top_n: int = 5) -> List[FusedResult]:
        if not candidates:
            return []

        pairs = [[query, c.chunk.content if c.chunk else ""] for c in candidates]
        
        with torch.no_grad():
            inputs = self.tokenizer(pairs, padding=True, truncation=True, return_tensors="pt", max_length=512)
            scores = self.model(**inputs).logits.squeeze(-1)
            if scores.ndim == 0:
                scores = scores.unsqueeze(0)
            scores = scores.cpu().numpy()

        scored_candidates = []
        for cand, score in zip(candidates, scores):
            cand_copy = cand.model_copy()
            cand_copy.score = float(score)
            scored_candidates.append(cand_copy)

        scored_candidates.sort(key=lambda x: x.score, reverse=True)
        for i, c in enumerate(scored_candidates[:top_n], start=1):
            c.rank = i

        return scored_candidates[:top_n]
