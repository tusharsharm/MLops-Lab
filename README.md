# MLops-Lab

This workspace contains several demo projects for MLOps experiments. The main project you will likely use here is the IPC RAG Predictor located in `ipc-rag-predictor/`.

Quick start for the IPC RAG Predictor:

- See [ipc-rag-predictor/README.md](ipc-rag-predictor/README.md) for full instructions.
- Typical local steps:
	- Place `ipc_book.pdf` in `ipc-rag-predictor/data/ipc_book.pdf`.
	- Create a virtual environment and install requirements: `python -m venv .venv && source .venv/bin/activate && pip install -r ipc-rag-predictor/requirements.txt`.
	- Run the API: `PYTHONPATH=ipc-rag-predictor uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

I updated the IPC RAG Predictor code to include fallbacks when heavy dependencies are not installed (embedding & vector store). The app has endpoints `/build-index` and `/predict` — use `curl` or the frontend to interact.

If you want, I can scaffold a small frontend next (React single-page app or a minimal server-rendered page). Which do you prefer?