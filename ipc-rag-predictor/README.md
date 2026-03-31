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

2. Build and run (Docker)
```bash
docker compose up --build
```

3. Run locally (VS Code / Codespaces)

Prerequisites:
- Python 3.10+ (or the version in `requirements.txt`)
- Node.js + npm (for the frontend)

Steps:

```bash
# from repo root
# 1) place the PDF
cp /path/to/ipc_book.pdf data/ipc_book.pdf

# 2) create and activate a virtualenv
python -m venv .venv
source .venv/bin/activate

# 3) install Python deps
pip install -r requirements.txt

# 4) start the backend (runs FastAPI on port 8000)
PYTHONPATH=ipc-rag-predictor uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Build the index (required before meaningful `/predict` results):

```bash
curl -X POST http://0.0.0.0:8000/build-index
```

Run a sample predict request:

```bash
curl -sS -X POST http://0.0.0.0:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"crime_description":"Deceiving someone to dishonestly induce them to deliver property","top_k":5}'
```

Frontend (dev):

```bash
cd frontend
npm install
npm run dev -- --port 5173
```

Notes for Codespaces:
- Open the repository in a Codespace or the VS Code Dev Container.  
- Forward ports `8000` (backend) and `5173` (frontend) from the Ports view to access them in browser.  
- The container / Codespace will reuse the same commands above inside its terminal; dependencies can be installed in the container environment.

Troubleshooting & tips:
- If `faiss` or `sentence-transformers` fail to install on your environment, the app includes fallbacks (numpy-based search or TF-IDF) so you can still run and test the service.  
- Ensure `data/faiss_index` exists and is writable if you expect FAISS index persistence. The code will attempt to create it automatically.

If you'd like, I can add a single-command VS Code `tasks.json` or a `.devcontainer` for Codespaces to fully automate this.
