from typing import Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid_rerank"
    prompt_version: str = "v3_abstain_guard"
    top_k: int = 5

class FeedbackRequest(BaseModel):
    query: str
    answer: str
    rating: str = Field(..., description="thumbs_up or thumbs_down")
    comments: Optional[str] = None
