from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    category: str
    department: str
    effective_date: str
    owner: str
    sensitivity: str
    heading_path: List[str] = Field(default_factory=list)
    content: str
    source_type: str = "unstructured"  # unstructured or structured

class Query(BaseModel):
    query: str
    mode: str = "hybrid_rerank"  # dense, bm25, structured, hybrid, hybrid_rerank
    prompt_version: str = "v3_abstain_guard"
    top_k: int = 5

class RetrievalResult(BaseModel):
    chunk_id: str
    doc_id: str
    score: float
    retriever_name: str
    chunk: Optional[Chunk] = None

class FusedResult(BaseModel):
    chunk_id: str
    score: float
    rank: int
    chunk: Optional[Chunk] = None

class Citation(BaseModel):
    doc_id: str
    chunk_id: str
    char_start: int
    char_end: int
    quoted_text: str

class StageTimings(BaseModel):
    timings: Dict[str, float] = Field(default_factory=dict)

class Answer(BaseModel):
    text: str
    citations: List[Citation] = Field(default_factory=list)
    confidence: float
    abstained: bool = False
    stage_timings: Dict[str, float] = Field(default_factory=dict)
    prompt_version: str = "v3_abstain_guard"
