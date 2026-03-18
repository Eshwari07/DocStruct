# DocStruct (DocumentParser)

End-to-end document structure extraction with:

- **Backend**: FastAPI + a deterministic/heuristic document structure pipeline (`backend/`)
- **Frontend**: React + Vite split-pane UI (`frontend/`)

## Quickstart

### Backend

From `DocumentParser/backend/`:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -U pip
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend runs at `http://127.0.0.1:8000`.

### Frontend

From `DocumentParser/frontend/`:

```bash
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and calls the backend at `http://localhost:8000` by default.

To override the backend URL:

```bash
set VITE_BACKEND_URL=http://127.0.0.1:8000
npm run dev
```

## Troubleshooting

### `npm` can’t reach the registry

If you see `ECONNREFUSED` fetching packages, your machine can’t reach `registry.npmjs.org` (often proxy/VPN/firewall related).
Configure your proxy or use your organization’s npm registry mirror, then re-run `npm install`.

