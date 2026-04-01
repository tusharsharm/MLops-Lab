import numpy as np
import pickle
import structlog
from pathlib import Path
from typing import List, Tuple
try:
    import mlflow
except Exception:
    # Lightweight mlflow stub when mlflow isn't installed
    from contextlib import contextmanager
    class _DummyMLflow:
        @contextmanager
        def start_run(self, *args, **kwargs):
            yield
        def log_param(self, *args, **kwargs):
            return None
        def log_metric(self, *args, **kwargs):
            return None
        def log_artifact(self, *args, **kwargs):
            return None
    mlflow = _DummyMLflow()
from app.core.config import get_settings
from app.services.embedder import Embedder

logger = structlog.get_logger()
settings = get_settings()

# Optional imports for faiss. If not available, fall back to numpy-based search.
try:
    import faiss  # type: ignore
    _HAS_FAISS = True
except Exception:
    faiss = None  # type: ignore
    _HAS_FAISS = False

class VectorStore:
    def __init__(self):
        self.index_path = Path(settings.index_path)
        self.embedder = Embedder()
        self.index = None
        self.sections = None
        self._use_faiss = _HAS_FAISS
        # Ensure the index directory exists (settings.index_path is a directory)
        self.index_path.mkdir(parents=True, exist_ok=True)

    def build_index(self, sections: List[dict]):
        logger.info("Building vector index", num_sections=len(sections))

        with mlflow.start_run(run_name="build_vector_index"):
            mlflow.log_param("num_sections", len(sections))
            mlflow.log_param("embedding_model", settings.embedding_model)
            mlflow.log_param("chunk_size", settings.chunk_size)

            texts = [f"{s['section']}. {s.get('title','')} {s.get('content','')}" for s in sections]
            embeddings = self.embedder.embed_texts(texts)

            embedding_array = np.array(embeddings).astype('float32')

            if self._use_faiss:
                # Normalize embeddings to unit vectors for inner-product (cosine) similarity
                norms = np.linalg.norm(embedding_array, axis=1, keepdims=True)
                norms[norms == 0] = 1e-12
                embedding_array = embedding_array / norms

                dimension = embedding_array.shape[1]
                self.index = faiss.IndexFlatIP(dimension)
                self.index.add(embedding_array)
                # Save index
                faiss.write_index(self.index, str(self.index_path / "ipc_index.faiss"))
                mlflow.log_artifact(str(self.index_path / "ipc_index.faiss"))
            else:
                # Keep embeddings in-memory / on-disk as numpy array
                self.index = embedding_array
                np.save(self.index_path / "ipc_embeddings.npy", embedding_array)

            self.sections = sections

            # Save metadata
            with open(self.index_path / "ipc_metadata.pkl", "wb") as f:
                pickle.dump(sections, f)

            mlflow.log_metric("index_size", len(sections))

            logger.info("Vector index built and saved successfully", faiss_available=self._use_faiss)

    def load_index(self):
        index_file = self.index_path / "ipc_index.faiss"
        embeddings_file = self.index_path / "ipc_embeddings.npy"
        metadata_file = self.index_path / "ipc_metadata.pkl"

        if metadata_file.exists():
            with open(metadata_file, "rb") as f:
                self.sections = pickle.load(f)

        if self._use_faiss and index_file.exists() and metadata_file.exists():
            logger.info("Loading existing FAISS index")
            self.index = faiss.read_index(str(index_file))
            return True

        if embeddings_file.exists() and metadata_file.exists():
            logger.info("Loading existing numpy embeddings index")
            self.index = np.load(embeddings_file)
            return True

        return False

    def search(self, query: str, top_k: int = 10) -> List[Tuple[dict, float]]:
        if self.index is None or self.sections is None:
            if not self.load_index():
                raise RuntimeError("Vector index not built. Call /build-index first.")

        query_embedding = self.embedder.embed_texts([query])[0]
        query_array = np.array([query_embedding]).astype('float32')

        results = []
        if self._use_faiss and hasattr(self.index, 'search'):
            # Normalize query to match index normalization
            qnorm = np.linalg.norm(query_array, axis=1, keepdims=True)
            qnorm[qnorm == 0] = 1e-12
            query_array = query_array / qnorm

            distances, indices = self.index.search(query_array, top_k)
            for idx, dist in zip(indices[0], distances[0]):
                if idx < len(self.sections):
                    section = self.sections[idx]
                    similarity = float(dist)
                    results.append((section, similarity))
            return results

        # Numpy-based search: cosine similarity via normalized dot product
        emb_matrix = self.index  # (N, D)
        # Normalize
        emb_norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
        emb_norms[emb_norms == 0] = 1e-12
        emb_normalized = emb_matrix / emb_norms

        q = query_array[0]
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            q_norm = 1e-12
        q_normalized = q / q_norm

        sims = np.dot(emb_normalized, q_normalized)
        # Get top_k indices
        topk_idx = np.argsort(-sims)[:top_k]
        for idx in topk_idx:
            if idx < len(self.sections):
                results.append((self.sections[idx], float(sims[idx])))

        return results