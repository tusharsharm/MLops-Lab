from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import time

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.models.schemas import PredictRequest, PredictResponse
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStore
from app.services.predictor import Predictor

setup_logging()
logger = structlog.get_logger()
settings = get_settings()

predictor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global predictor
    logger.info("Starting IPC RAG Prediction Service")
    
    # Try to load existing index
    vector_store = VectorStore()
    if not vector_store.load_index():
        logger.warning("No existing index found. Use POST /build-index endpoint first.")
    
    predictor = Predictor()
    logger.info("Application startup completed")
    yield
    logger.info("Shutting down IPC RAG service")

app = FastAPI(
    title="IPC RAG Predictor",
    description="RAG-based Indian Penal Code Section Prediction System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ipc-rag-predictor"}

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    if not predictor:
        raise HTTPException(status_code=503, detail="Service not ready. Please try again later.")
    
    try:
        predictions = predictor.predict(
            crime_description=request.crime_description,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        return PredictResponse(
            predictions=predictions,
            query=request.crime_description,
            total_retrieved=len(predictions),
            processing_time_ms=0  # Will be updated in production logging
        )
    except Exception as e:
        logger.error("Prediction failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/build-index")
async def build_index():
    try:
        pdf_path = f"{settings.data_dir}/{settings.pdf_filename}"
        processor = PDFProcessor(pdf_path)
        sections = processor.extract_sections()
        
        vector_store = VectorStore()
        vector_store.build_index(sections)
        
        global predictor
        predictor = Predictor()
        
        return {"message": f"Index built successfully with {len(sections)} IPC sections"}
    except Exception as e:
        logger.error("Index build failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)