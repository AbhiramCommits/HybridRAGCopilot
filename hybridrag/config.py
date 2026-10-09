import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/hybridrag"
    EMBEDDING_BACKEND: str = "base"
    BASE_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LORA_MODEL_PATH: str = "artifacts/lora_embed"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ANTHROPIC_API_KEY: str = ""
    ABSTAIN_THRESHOLD: float = 0.15
    TOP_K_DEFAULT: int = 5
    FAISS_INDEX_PATH: str = "artifacts/faiss.index"
    CHUNKS_STORE_PATH: str = "artifacts/chunks.parquet"
    BM25_STORE_PATH: str = "artifacts/bm25.pkl"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
os.makedirs("artifacts", exist_ok=True)
os.makedirs("results", exist_ok=True)
os.makedirs("data/corpus", exist_ok=True)
os.makedirs("data/eval", exist_ok=True)
