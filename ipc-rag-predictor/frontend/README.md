# IPC RAG Frontend

Minimal React frontend (Vite) for querying the IPC RAG Predictor API.

Run locally:

```bash
cd ipc-rag-predictor/frontend
npm install
npm run dev
```

The frontend expects the backend API to be available at the same origin. If running backend on port 8000, run the frontend in a way that proxies `/predict` to the API, or run the frontend on the same host/port via a reverse proxy.
