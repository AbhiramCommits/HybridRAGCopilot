import time
from typing import List, Dict, Any
from hybridrag.models import RetrievalResult, FusedResult, StageTimings
from hybridrag.retrieval.dense import DenseRetriever
from hybridrag.retrieval.bm25 import BM25Retriever
from hybridrag.retrieval.structured import StructuredRetriever
from hybridrag.retrieval.fusion import reciprocal_rank_fusion
from hybridrag.retrieval.rerank import CrossEncoderReranker

class HybridRetriever:
    def __init__(self, embedding_mode: str = "base"):
        self.dense = DenseRetriever(embedding_mode)
        self.bm25 = BM25Retriever()
        self.structured = StructuredRetriever()
        self.reranker = CrossEncoderReranker()

    def retrieve(
        self, 
        query: str, 
        k_each: int = 30, 
        k_out: int = 20, 
        mode: str = "hybrid_rerank"
    ) -> tuple[List[FusedResult], StageTimings]:
        timings = {}
        t0 = time.time()

        dense_results = []
        bm25_results = []
        structured_results = []

        if mode in ["dense", "hybrid", "hybrid_rerank"]:
            t_start = time.time()
            dense_results = self.dense.search(query, k=k_each)
            timings["dense"] = time.time() - t_start

        if mode in ["bm25", "hybrid", "hybrid_rerank"]:
            t_start = time.time()
            bm25_results = self.bm25.search(query, k=k_each)
            timings["bm25"] = time.time() - t_start

        if mode in ["structured", "hybrid", "hybrid_rerank"]:
            t_start = time.time()
            structured_results = self.structured.search(query, k=k_each)
            timings["structured"] = time.time() - t_start

        if mode == "dense":
            fused = [FusedResult(chunk_id=r.chunk_id, score=r.score, rank=i, chunk=r.chunk) for i, r in enumerate(dense_results[:k_out], start=1)]
        elif mode == "bm25":
            fused = [FusedResult(chunk_id=r.chunk_id, score=r.score, rank=i, chunk=r.chunk) for i, r in enumerate(bm25_results[:k_out], start=1)]
        elif mode == "structured":
            fused = [FusedResult(chunk_id=r.chunk_id, score=r.score, rank=i, chunk=r.chunk) for i, r in enumerate(structured_results[:k_out], start=1)]
        else:
            t_start = time.time()
            result_lists = []
            weights = []
            if dense_results:
                result_lists.append(dense_results)
                weights.append(1.0)
            if bm25_results:
                result_lists.append(bm25_results)
                weights.append(1.0)
            if structured_results:
                result_lists.append(structured_results)
                weights.append(1.2) # slight boost for metadata match

            fused = reciprocal_rank_fusion(result_lists, k=60, weights=weights)[:k_out]
            timings["fusion"] = time.time() - t_start

        if mode == "hybrid_rerank" and fused:
            t_start = time.time()
            fused = self.reranker.rerank(query, fused, top_n=min(5, len(fused)))
            timings["rerank"] = time.time() - t_start

        timings["total"] = time.time() - t0
        return fused, StageTimings(timings=timings)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--mode", default="hybrid_rerank")
    args = parser.parse_args()

    retriever = HybridRetriever()
    results, timings = retriever.retrieve(args.query, mode=args.mode)
    print(f"Results for query: '{args.query}' (mode={args.mode})")
    print(f"Timings: {timings.timings}")
    for r in results:
        print(f"Rank {r.rank}: {r.chunk_id} (Score: {r.score:.4f}) - {r.chunk.title if r.chunk else ''}")
