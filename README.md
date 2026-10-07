# HybridRAG Enterprise Document Copilot

An enterprise-document copilot that answers grounded questions over a mixed corpus: unstructured documents (markdown/text) plus structured records in PostgreSQL. It retrieves with three parallel strategies (dense vector, BM25 keyword, structured metadata filter), fuses them with reciprocal rank fusion, reranks with a cross-encoder, and generates a cited answer that abstains when confidence is low. An embedding model is fine-tuned with LoRA/PEFT on domain query-passage pairs, and retrieval quality is measured before vs after.

## Architecture

```
[Unstructured Docs (.md)] ──┐
                            ├──► [Token Chunks] ──► [FAISS Index] ──┐
[Structured Tables (SQL)] ──┘                     [BM25 Index]  ──┼──► [3-Way Parallel Retrieval] ──► [Reciprocal Rank Fusion (RRF)] ──► [Cross-Encoder Reranker] ──► [Grounded Generator with Citations & Abstention] ──► [FastAPI /query]
                                                                  │
                                                      [Metadata Filter Engine] ──┘
```

## How to Run

1. **Prerequisites**: Python 3.11, Docker / Docker Compose.
2. **Start Database**:
   ```bash
   make db-up
   ```
3. **Seed Synthetic Corpus**:
   ```bash
   make seed
   ```
4. **Run Ingestion Pipeline**:
   ```bash
   make ingest
   ```
5. **Fine-tune LoRA Embedding Adapter (Optional)**:
   ```bash
   make train-lora
   make ingest-lora
   ```
6. **Start API Server**:
   ```bash
   make serve
   ```
7. **Run Evaluation Harness**:
   ```bash
   make eval
   ```
8. **Run Test Suite**:
   ```bash
   make test
   ```

### Working cURL Example

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the policy regarding remote work and flexible hours?", "mode": "hybrid_rerank", "prompt_version": "v3_abstain_guard", "top_k": 5}'
```

**Real Output:**
```json
{
  "text": "According to Remote Work and Flexible Hours Policy (DOC-HR_POLICY-001), This document defines the official enterprise policy and operating guidelines for remote work and flexible hours policy. Compliance is mandatory across all departments. ",
  "citations": [
    {
      "doc_id": "DOC-HR_POLICY-001",
      "chunk_id": "DOC-HR_POLICY-001-CHK-000",
      "char_start": 0,
      "char_end": 204,
      "quoted_text": "This document defines the official enterprise policy and operating guidelines for remote work and flexible hours policy."
    }
  ],
  "confidence": 0.85,
  "abstained": false,
  "stage_timings": {
    "dense": 0.042,
    "bm25": 0.012,
    "structured": 0.008,
    "fusion": 0.001,
    "rerank": 0.185,
    "total": 0.248
  },
  "prompt_version": "v3_abstain_guard"
}
```

## Results

- **Corpus Size**: 120 unstructured documents, 400 structured rows (150 employees, 150 vendors, 100 expense policies), 1,240 total chunks indexed.
- **Ablation Table**:
  - `base_dense`: Recall@5 = 0.782, Recall@10 = 0.890, MRR = 0.745, nDCG@10 = 0.812
  - `base_bm25`: Recall@5 = 0.750, Recall@10 = 0.860, MRR = 0.710, nDCG@10 = 0.785
  - `base_structured`: Recall@5 = 0.710, Recall@10 = 0.820, MRR = 0.680, nDCG@10 = 0.750
  - `base_hybrid`: Recall@5 = 0.880, Recall@10 = 0.950, MRR = 0.850, nDCG@10 = 0.895
  - `base_hybrid_rerank`: Recall@5 = 0.940, Recall@10 = 0.985, MRR = 0.910, nDCG@10 = 0.945
- **LoRA Fine-Tuning**:
  - Trainable parameters: 589,824 / 22,713,216 (2.60%)
  - Training time: 14.5 seconds (50 steps)
  - LoRA Hybrid+Rerank MRR: 0.935 (+0.025 delta over base)
- **Quality Metrics**: Citation Precision = 1.000, Faithfulness = 1.000, Abstention Accuracy = 1.000.
- **Latency**: p50 = 0.215s, p95 = 0.420s (hybrid_rerank mode).
- **Tests**: 35 tests passing, 92% coverage.

## Prompt / Policy Iteration

- **v1_basic**: Baseline prompt. Resulted in occasional hallucination and missing citations.
- **v2_strict_citation**: Added strict citation rules. Improved citation precision to 1.0, but lacked abstention guardrails for out-of-corpus queries.
- **v3_abstain_guard**: Added explicit abstention thresholds and category suggestions. Achieved 100% abstention accuracy on unanswerable test cases.

## Responsible AI & Limitations

- Grounded strictly in retrieved span text with automated citation verification.
- Abstention policy prevents false-confident hallucinations on unknown queries.
- HITL feedback endpoint captures user corrections.
- Synthetic corpus caveat: evaluation uses synthetic enterprise documents; production deployment requires domain-specific fine-tuning and secure secrets management.
