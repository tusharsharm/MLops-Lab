# IPC RAG Predictor - Indian Penal Code Section Prediction System

Production-ready RAG-based system to predict relevant IPC sections from crime descriptions using semantic retrieval over the official IPC PDF.

## Features
- Semantic search (RAG) over full Indian Penal Code book
- Multi-label IPC section prediction
- FastAPI backend with async support
- FAISS vector store with persistence
- MLflow experiment tracking
- Fully Dockerized (multi-stage build)
- Optimized PDF chunking by IPC sections

## Setup Instructions

1. Download the dataset from Kaggle:
   https://www.kaggle.com/datasets/harshit804/ipc-data
   → Download `ipc_book.pdf` and place it in the `data/` folder as `ipc_book.pdf`

2. Build and run:
```bash
docker compose up --build