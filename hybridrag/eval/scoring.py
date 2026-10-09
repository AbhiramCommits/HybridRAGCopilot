import numpy as np


def recall_at_k(retrieved_ids: list[str], gold_ids: list[str], k: int) -> float:
    if not gold_ids:
        return 1.0 if not retrieved_ids[:k] else 0.0
    retrieved_set = set(retrieved_ids[:k])
    hits = sum(1 for g in gold_ids if g in retrieved_set)
    return hits / len(gold_ids)

def reciprocal_rank(retrieved_ids: list[str], gold_ids: list[str]) -> float:
    if not gold_ids:
        return 1.0
    for rank, r_id in enumerate(retrieved_ids, start=1):
        if r_id in gold_ids:
            return 1.0 / rank
    return 0.0

def ndcg_at_k(retrieved_ids: list[str], gold_ids: list[str], k: int) -> float:
    if not gold_ids:
        return 1.0
    dcg = 0.0
    for i, r_id in enumerate(retrieved_ids[:k]):
        if r_id in gold_ids:
            dcg += 1.0 / np.log2(i + 2)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(k, len(gold_ids))))
    if idcg == 0:
        return 0.0
    return dcg / idcg

def citation_precision(citations: list, retrieved_chunks: list) -> float:
    if not citations:
        return 1.0
    valid_hits = 0
    chunk_map = {c.chunk_id: c for c in retrieved_chunks}
    for cit in citations:
        chunk = chunk_map.get(cit.chunk_id)
        if chunk and cit.quoted_text in chunk.content:
            valid_hits += 1
    return valid_hits / len(citations)

def faithfulness(answer_text: str, citations: list, retrieved_chunks: list) -> float:
    # Every sentence in answer must be supported by a cited span
    sentences = [s.strip() for s in answer_text.split(".") if s.strip()]
    if not sentences or not citations:
        return 1.0 if not citations else 0.0

    supported = 0
    chunk_map = {c.chunk_id: c for c in retrieved_chunks}
    for sent in sentences:
        is_supported = False
        for cit in citations:
            chunk = chunk_map.get(cit.chunk_id)
            if chunk and (cit.quoted_text in chunk.content or cit.quoted_text in sent):
                is_supported = True
                break
        if is_supported:
            supported += 1
    return supported / len(sentences)

def abstention_accuracy(is_abstained: bool, actually_answerable: bool) -> float:
    # Correct if abstained when unanswerable, or did not abstain when answerable
    if not actually_answerable and is_abstained:
        return 1.0
    if actually_answerable and not is_abstained:
        return 1.0
    return 0.0
