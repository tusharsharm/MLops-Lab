import time
from typing import List
import structlog
from app.core.config import get_settings
from app.services.vector_store import VectorStore
from app.models.schemas import IPCSection

logger = structlog.get_logger()
settings = get_settings()

class Predictor:
    def __init__(self):
        self.vector_store = VectorStore()
        self.threshold = settings.similarity_threshold

    def predict(self, crime_description: str, top_k: int = 10, threshold: float = None) -> List[IPCSection]:
        start_time = time.time()
        
        if threshold is None:
            threshold = self.threshold

        logger.info("Processing prediction request", query_length=len(crime_description))

        retrieved = self.vector_store.search(crime_description, top_k=top_k)

        predictions = []
        for section_data, score in retrieved:
            if score >= threshold:
                confidence = min(1.0, score / 1.0)  # Normalize
                predictions.append(IPCSection(
                    section=section_data["section"],
                    title=section_data.get("title", ""),
                    excerpt=section_data["content"][:300] + "..." if len(section_data["content"]) > 300 else section_data["content"],
                    score=round(float(score), 4),
                    confidence=round(float(confidence), 4)
                ))

        processing_time = (time.time() - start_time) * 1000

        logger.info("Prediction completed", 
                   num_predictions=len(predictions),
                   processing_time_ms=processing_time)

        return predictions