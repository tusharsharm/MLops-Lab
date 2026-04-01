# MLops-Lab

Monorepo with an IPC RAG Predictor demo (FastAPI backend + Vite React frontend) and MLflow tracking.

Repository layout
- `ipc-rag-predictor/` — main project
	- `app/` — FastAPI application code
	- `frontend/` — Vite + React frontend
	- `data/` — input files (place `ipc_book.pdf` here)
	- `mlruns/` — MLflow server data (persisted by Docker Compose)
	- `Dockerfile`, `docker-compose.yml`, `requirements.txt` — project infra
- `mlruns/` — example MLflow runs (artifact store)

Quick overview
- Backend: FastAPI app served by Uvicorn on port `8000` (development: `--reload` supported).
- Frontend: Vite dev server on port `5173` (or production build served by a static server).
- MLflow UI: port `5000` (when using the provided Docker Compose service).

Run everything (recommended, Docker)
1. From repo root:

```bash
cd ipc-rag-predictor
docker compose up --build
```

This starts three services:
- Backend: http://localhost:8000
- Frontend (Vite dev): http://localhost:5173
- MLflow UI: http://localhost:5000

Run locally in VS Code (no Docker)
1) Backend (Python virtualenv)

```bash
# from repo root
python -m venv .venv
source .venv/bin/activate
pip install -r ipc-rag-predictor/requirements.txt

# start backend (dev)
PYTHONPATH=ipc-rag-predictor uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2) Frontend (Vite)

```bash
cd ipc-rag-predictor/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Notes for VS Code / Codespaces
- Use the integrated terminal to run the commands above.
- In Codespaces or DevContainers, forward ports `8000`, `5173`, and `5000` in the Ports view to open them in your browser.
- To enable backend live-reload in Docker Compose we mount the backend sources and run Uvicorn with `--reload` (development convenience).

Useful endpoints
- `POST /build-index` — build the FAISS/TF-IDF index from `data/ipc_book.pdf` (required for meaningful predictions).
- `POST /predict` — send JSON with `crime_description` to get predicted IPC sections.

Troubleshooting
- If native ML packages like `faiss` or `sentence-transformers` fail to install, the code provides fallbacks so you can still run basic functionality.
- Ensure `data/` contains the `ipc_book.pdf` file before building the index.

If you want, I can:
- add a `docker-compose.dev.yml` override to keep production compose unchanged, or
- add a VS Code `tasks.json` and `launch.json` to automate the dev workflow.

Sub-README files have been consolidated into this single top-level README.