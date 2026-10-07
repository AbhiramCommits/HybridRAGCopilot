from typing import List, Optional
from hybridrag.models import FusedResult, RetrievalResult

def reciprocal_rank_fusion(
    result_lists: List[List[RetrievalResult]], 
    k: int = 60, 
    weights: Optional[List[float]] = None
) -> List[FusedResult]:
    if not result_lists:
        return []

    if weights is None:
        weights = [1.0] * len(result_lists)

    fusion_scores = {}
    chunk_map = {}

    for w, r_list in zip(weights, result_lists):
        for rank, res in enumerate(r_list, start=1):
            chunk_id = res.chunk_id
            if chunk_id not in fusion_scores:
                fusion_scores[chunk_id] = 0.0
                chunk_map[chunk_id] = res.chunk

            # RRF formula: w / (k + rank)
            fusion_scores[chunk_id] += w / (k + rank)

    sorted_chunks = sorted(fusion_scores.items(), key=lambda x: x[1], reverse=True)

    fused_results = []
    for rank, (chunk_id, score) in enumerate(sorted_chunks, start=1):
        fused_results.append(FusedResult(
            chunk_id=chunk_id,
            score=float(score),
            rank=rank,
            chunk=chunk_map.get(chunk_id)
        ))

    return fused_results
