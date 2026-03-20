# DocStruct (DocumentParser)

A comprehensive document structure extraction system with AI-powered parsing capabilities.

## Overview

DocStruct extracts hierarchical document structure (headings, sections, tables, images) from a wide range of file formats — PDF, DOCX, EPUB, HTML, PPTX — and exposes the results as structured JSON and Markdown. A fast heuristic pipeline handles well-formed documents; an optional VLM (vision-language model) path via OpenRouter handles complex PDFs and image-based files (PNG, JPEG, TIFF) that lack machine-readable structure.

## Features

- End-to-end document structure extraction from PDF, DOCX, EPUB, HTML, and PPTX
- FastAPI backend with a deterministic/heuristic pipeline and optional AI (VLM) path
- React + Vite split-pane UI with live progress, PDF viewer, JSON and Markdown output views
- Async job system — upload a file, poll for progress, retrieve results
- Automatic image and table extraction with artifact serving
- CLI for local batch extraction (no server required)
- Auto job cleanup (1-hour TTL) to keep the server lean

## Architecture

For deeper implementation details, see [ARCHITECTURE.md](./ARCHITECTURE.md).

- **Backend**: FastAPI + DocStruct processing pipeline (`backend/`)
- **Frontend**: React + Vite (`frontend/`)
- **Languages**: Python (55.9%), TypeScript (43.4%)

```
DocumentParser/
├── backend/
│   ├── main.py                  # FastAPI app & job management
│   ├── requirements.txt
│   ├── .env / .env.example
│   └── docstruct/
│       ├── pipeline.py          # Orchestrates parsers → extraction → serializers
│       ├── parsers/             # pdf, docx, epub, html, pptx, vlm parsers
│       ├── extraction/          # Heading classification, tree building, routing
│       ├── content/             # Image & table extraction, text population
│       ├── serializers/         # JSON and Markdown output
│       └── core/                # Config and schema
└── frontend/
    └── src/
        ├── App.tsx
        ├── components/          # TopBar, UploadZone, DocumentViewer, OutputViewer, StatusBar
        ├── hooks/               # useExtraction
        ├── store/               # Zustand store
        ├── api/                 # Axios client
        └── types/
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm

### Backend Setup

From `DocumentParser/backend/`:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -U pip
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# Edit `backend/.env` and set your `OPENROUTER_API_KEY` (required for VLM path).
# Security note: do NOT commit `backend/.env` to GitHub. Keep only `backend/.env.example`.
.venv\Scripts\uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend runs at `http://127.0.0.1:8000`. Interactive API docs are available at `http://127.0.0.1:8000/docs`.

#### VLM-powered extraction

Set `OPENROUTER_API_KEY` in `backend/.env` to enable AI-powered extraction for complex PDFs (those without bookmarks/outlines) and image files. Without the key the system still works for PDFs with outlines via the fast path, and falls back to heuristic parsing for PDFs without outlines.

Optional `.env` variables:

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | — | Required for VLM path |
| `DOCSTRUCT_VLM_MODEL` | provider default | OpenRouter model slug |
| `DOCSTRUCT_VLM_DPI` | `150` | DPI used when rendering PDF pages for VLM |

### Frontend Setup

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

## Usage

1. Open `http://localhost:5173` in your browser.
2. Drag-and-drop or click to upload a document (PDF, DOCX, EPUB, HTML, PPTX, PNG, JPEG, TIFF).
3. The backend processes the file asynchronously — a progress bar shows per-page extraction status.
4. Once complete, browse the extracted structure in the **JSON**, **Markdown**, or **Cards** view on the right pane.
5. Download the JSON or Markdown output using the download bar.

### CLI usage (no server required)

```bash
# From DocumentParser/backend/
.venv\Scripts\python -m docstruct.cli path/to/document.pdf --format markdown
```

## API Documentation

Interactive Swagger UI is available at `http://127.0.0.1:8000/docs` while the backend is running.

### Key endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/extract` | Upload a file; returns `job_id` (202 Accepted) |
| `GET` | `/status/{job_id}` | Poll extraction progress |
| `GET` | `/result/{job_id}` | Retrieve JSON + Markdown result |
| `GET` | `/file/{job_id}` | Download original uploaded file |
| `GET` | `/asset/{job_id}/{path}` | Serve extracted assets (images, etc.) |
| `DELETE` | `/job/{job_id}` | Delete job and clean up temp files |

## Troubleshooting

### `npm` can't reach the registry

If you see `ECONNREFUSED` fetching packages, your machine can't reach `registry.npmjs.org` (often proxy/VPN/firewall related). Configure your proxy or use your organisation's npm registry mirror, then re-run `npm install`.

### Backend won't start

- Make sure you activated the venv (`.venv\Scripts\activate`) or prefix commands with `.venv\Scripts\`.
- Confirm `requirements.txt` installed without errors (`pip install -r requirements.txt`).
- Check that port `8000` is not already in use.

## Contributing

1. Fork the repository and create a feature branch.
2. Follow existing code style — Python (PEP 8), TypeScript (strict mode).
3. Add or update tests under `backend/tests/` for any backend changes.
4. Open a pull request with a clear description of the change and why it is needed.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contact

Open an issue in the repository for bug reports, feature requests, or questions.
