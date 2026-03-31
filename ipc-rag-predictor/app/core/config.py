from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 10
    similarity_threshold: float = 0.35
    mlflow_tracking_uri: str = "http://mlflow:5000"
    data_dir: str = "ipc-rag-predictor/data"
    pdf_filename: str = "ipc_book.pdf"
    index_path: str = "ipc-rag-predictor/data/faiss_index"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()