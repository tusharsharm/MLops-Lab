
from typing import List
import structlog
from pathlib import Path
from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class Embedder:
    def __init__(self):
        self.model_name = settings.embedding_model
        self.model = None
        self.vectorizer = None
        self._use_sentence_transformers = False
        self._use_sklearn = False

        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self._use_sentence_transformers = True
        except Exception:
            logger.info("sentence-transformers not available, using lightweight fallback")
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
                self._use_sklearn = True
            except Exception:
                logger.info("sklearn not available, using deterministic hash-based fallback")

    def load_model(self):
        if self._use_sentence_transformers and self.model is None:
            from sentence_transformers import SentenceTransformer  # type: ignore
            logger.info("Loading embedding model", model=self.model_name)
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        return self.model

    def _hash_fallback(self, texts: List[str], dim: int = 128) -> List[List[float]]:
        out = []
        for t in texts:
            vec = [((hash(t + str(i)) % 1000) / 1000.0) for i in range(dim)]
            out.append(vec)
        return out

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        logger.info("Embedding texts", count=len(texts))

        if self._use_sentence_transformers:
            model = self.load_model()
            embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
            try:
                return embeddings.tolist()
            except Exception:
                return [list(map(float, e)) for e in embeddings]

        if self._use_sklearn:
            # Use TF-IDF as a lightweight embedding approximation
            if self.vectorizer is None:
                from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
                self.vectorizer = TfidfVectorizer(max_features=512)
                emb = self.vectorizer.fit_transform(texts).toarray()
            else:
                emb = self.vectorizer.transform(texts).toarray()
            return emb.astype(float).tolist()

        # Final fallback: deterministic hash-based vectors
        return self._hash_fallback(texts)