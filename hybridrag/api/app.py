import os

from fastapi import FastAPI, HTTPException
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from hybridrag.api.observability import log_request_middleware
from hybridrag.api.routes import FeedbackRequest, QueryRequest
from hybridrag.generate.generator import get_generator
from hybridrag.ingest.pipeline import ingest_all
from hybridrag.models import Answer
from hybridrag.retrieval.hybrid import HybridRetriever

app = FastAPI(title="HybridRAG Enterprise Copilot", version="0.1.0")

app.middleware("http")(log_request_middleware)

# Prometheus metrics
REQUEST_COUNT = Counter("hybridrag_requests_total", "Total query requests", ["mode", "status"])
LATENCY_HISTOGRAM = Histogram("hybridrag_stage_latency_seconds", "Stage execution latency", ["stage"])

retriever = HybridRetriever()
generator = get_generator()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/query", response_model=Answer)
def query_endpoint(req: QueryRequest):
    try:
        results, timings = retriever.retrieve(req.query, k_out=req.top_k, mode=req.mode)

        for stage, duration in timings.timings.items():
            LATENCY_HISTOGRAM.labels(stage=stage).observe(duration)

        answer = generator.generate(req.query, results, prompt_version=req.prompt_version)
        answer.stage_timings = timings.timings

        status_label = "abstained" if answer.abstained else "success"
        REQUEST_COUNT.labels(mode=req.mode, status=status_label).inc()
        return answer
    except Exception as e:
        REQUEST_COUNT.labels(mode=req.mode, status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
def ingest_endpoint(mode: str = "base"):
    try:
        docs, rows, chunks = ingest_all(mode)
        return {"status": "success", "documents": docs, "structured_rows": rows, "total_chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/feedback")
def feedback_endpoint(req: FeedbackRequest):
    # Store feedback into artifacts or database
    import json
    os.makedirs("results", exist_ok=True)
    feedback_path = "results/feedback.jsonl"
    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(req.model_dump()) + "\n")
    return {"status": "saved"}
