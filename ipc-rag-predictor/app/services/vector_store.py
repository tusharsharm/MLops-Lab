import faiss
import numpy as np
import pickle
import structlog
from pathlib import Path
from typing import List, Tuple
import mlflow
from app.core.config import get_settings
from app.services.embedder import Embedder
from typing import List, Tuple
logger = structlog.get_logger()
settings = get_settings()

class VectorStore:
    def __init__(self):
        self.index_path = Path(settings.index_path)
        self.embedder = Embedder()
        self.index = None
        self.sections = None
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    def build_index(self, sections: List[dict]):
        logger.info("Building FAISS index", num_sections=len(sections))
        
        with mlflow.start_run(run_name="build_vector_index"):
            mlflow.log_param("num_sections", len(sections))
            mlflow.log_param("embedding_model", settings.embedding_model)
            mlflow.log_param("chunk_size", settings.chunk_size)

            texts = [f"{s['section']}. {s['title']} {s['content']}" for s in sections]
            embeddings = self.embedder.embed_texts(texts)

            dimension = len(embeddings[0])
            self.index = faiss.IndexFlatIP(dimension)
            embedding_array = np.array(embeddings).astype('float32')
            self.index.add(embedding_array)

            self.sections = sections

            # Save index and metadata
            faiss.write_index(self.index, str(self.index_path / "ipc_index.faiss"))
            with open(self.index_path / "ipc_metadata.pkl", "wb") as f:
                pickle.dump(sections, f)

            mlflow.log_artifact(str(self.index_path / "ipc_index.faiss"))
            mlflow.log_metric("index_size", len(sections))

            logger.info("FAISS index built and saved successfully")

    def load_index(self):
        index_file = self.index_path / "ipc_index.faiss"
        metadata_file = self.index_path / "ipc_metadata.pkl"

        if index_file.exists() and metadata_file.exists():
            logger.info("Loading existing FAISS index")
            self.index = faiss.read_index(str(index_file))
            with open(metadata_file, "rb") as f:
                self.sections = pickle.load(f)
            return True
        return False

    def search(self, query: str, top_k: int = 10) -> List[Tuple[dict, float]]:
        if not self.index or not self.sections:
            if not self.load_index():
                raise RuntimeError("Vector index not built. Call /build-index first.")

        query_embedding = self.embedder.embed_texts([query])[0]
        query_array = np.array([query_embedding]).astype('float32')

        distances, indices = self.index.search(query_array, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.sections):
                section = self.sections[idx]
                similarity = float(dist)  # Since using Inner Product (higher = better)
                results.append((section, similarity))

        return results