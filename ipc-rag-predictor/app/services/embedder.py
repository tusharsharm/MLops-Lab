
from typing import List
from sentence_transformers import SentenceTransformer
import structlog
from pathlib import Path
from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class Embedder:
    def __init__(self):
        self.model_name = settings.embedding_model
        self.model = None

    def load_model(self):
        if self.model is None:
            logger.info("Loading embedding model", model=self.model_name)
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        return self.model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        model = self.load_model()
        logger.info("Embedding texts", count=len(texts))
        embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
        return embeddings.tolist()