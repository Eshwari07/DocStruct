# DocStruct Frontend — Comprehensive Implementation Plan
**For review + implementation by Opus**
Version 1.0 | March 2026

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Tech Stack & Rationale](#2-tech-stack--rationale)
3. [UI Layout & Component Map](#3-ui-layout--component-map)
4. [Component Breakdown](#4-component-breakdown)
5. [Backend API Design (FastAPI)](#5-backend-api-design-fastapi)
6. [State Management](#6-state-management)
7. [File Upload Flow](#7-file-upload-flow)
8. [Left Panel — Document Viewer](#8-left-panel--document-viewer)
9. [Right Panel — Output Viewer](#9-right-panel--output-viewer)
10. [JSON View Specification](#10-json-view-specification)
11. [Markdown View Specification](#11-markdown-view-specification)
12. [Node Linking — Click-to-Highlight](#12-node-linking--click-to-highlight)
13. [Processing States & UX](#13-processing-states--ux)
14. [Download & Copy Functionality](#14-download--copy-functionality)
15. [Long Document Handling in UI](#15-long-document-handling-in-ui)
16. [Multi-Column Document Handling in UI](#16-multi-column-document-handling-in-ui)
17. [Error Handling in UI](#17-error-handling-in-ui)
18. [Responsive & Resizable Panels](#18-responsive--resizable-panels)
19. [Project Structure](#19-project-structure)
20. [Dependency List](#20-dependency-list)
21. [Build Phases](#21-build-phases)
22. [Prompt for Opus Implementation](#22-prompt-for-opus-implementation)

---

## 1. System Overview

### What the Frontend Does

The DocStruct frontend is a **split-pane web application** that lets a user:

1. Upload any supported document (PDF, DOCX, HTML, Markdown, EPUB, PPTX)
2. See the **original document rendered** on the left panel
3. See the **extracted hierarchical structure** on the right panel, toggling between JSON and Markdown views
4. Click any section node on the right to **jump to that page** in the left panel
5. Download the extracted output as JSON or Markdown files

The frontend communicates with a **FastAPI backend** that runs the DocStruct Python pipeline locally. No cloud calls. No data leaves the machine.

### Core Design Philosophy

- **Local-first**: everything runs on localhost. No auth, no user accounts, no cloud storage.
- **Split-pane**: the document viewer and the output viewer are always visible side by side, linked by page/section.
- **Zero-latency toggle**: switching between JSON and Markdown views must be instant (client-side only — the server returns both representations in one response).
- **Confidence-aware**: nodes with low confidence scores (slow-path extractions) are visually flagged so the user knows where to manually verify.

---

## 2. Tech Stack & Rationale

### Frontend
| Technology | Version | Why |
|---|---|---|
| React | 18+ | Component model fits the panel/tree structure cleanly |
| Vite | 5+ | Fast dev server, minimal config |
| TypeScript | 5+ | Type safety for the DocNode schema |
| Tailwind CSS | 3+ | Utility classes, no CSS files to manage |
| react-pdf | 7+ | In-browser PDF rendering without a server round-trip |
| react-json-view | 1+ | Collapsible, syntax-highlighted JSON tree |
| react-markdown | 9+ | Renders Markdown with syntax highlighting |
| react-syntax-highlighter | latest | Code syntax highlighting for JSON raw view |
| react-resizable-panels | latest | Drag-to-resize split pane |
| axios | latest | HTTP client for API calls |
| zustand | 4+ | Lightweight state management (no Redux overhead) |

### Backend
| Technology | Version | Why |
|---|---|---|
| FastAPI | 0.110+ | Async, automatic OpenAPI docs, minimal boilerplate |
| uvicorn | latest | ASGI server |
| python-multipart | latest | File upload support in FastAPI |
| DocStruct | (local) | The extraction pipeline |

### Why not Streamlit?
Streamlit would work for a quick demo, but it cannot provide: a side-by-side split pane with a real PDF renderer, instant client-side toggle between JSON/Markdown, click-to-highlight synchronisation between panels, or drag-to-resize panels. React gives you all of these.

### Why not Next.js?
This is a local tool, not a deployed web app. Vite + React has zero server-side rendering complexity, instant HMR, and simpler deployment (just `npm run build` → serve static files).

---

## 3. UI Layout & Component Map

```
┌─────────────────────────────────────────────────────────────────┐
│  TopBar                                                         │
│  [DocStruct logo]  [Upload button]  [Format badge]  [Status]   │
├──────────────────────────────┬──────────────────────────────────┤
│                              │                                  │
│   LEFT PANEL                 │   RIGHT PANEL                   │
│   DocumentViewer             │   OutputViewer                  │
│                              │                                  │
│   ┌──────────────────────┐   │   [JSON] [Markdown] ← toggle   │
│   │                      │   │                                  │
│   │   PDF / DOCX / HTML  │   │   ┌──────────────────────────┐  │
│   │   rendered in-browser│   │   │  1 · Introduction        │  │
│   │                      │   │   │  ├── 1.1 Background      │  │
│   │   [highlighted page  │   │   │  ├── 1.2 Scope           │  │
│   │    region when node  │   │   │  │   └── 1.2.1 ...       │  │
│   │    is selected]      │   │   │  2 · Methodology         │  │
│   │                      │   │   └──────────────────────────┘  │
│   └──────────────────────┘   │                                  │
│                              │   [Download JSON] [Download MD]  │
│   ← 3 / 42 →  [zoom]        │   [Copy to clipboard]           │
│                              │                                  │
├──────────────────────────────┴──────────────────────────────────┤
│  StatusBar: "Extracted 42 sections from report.pdf  (fast path,│
│  1.2s)"                                                         │
└─────────────────────────────────────────────────────────────────┘
```

### Panel Sizing
- Default split: 50% / 50%
- User can drag the divider to resize
- Minimum panel width: 300px
- On screens < 900px wide: stack vertically (document viewer on top, output below)

---

## 4. Component Breakdown

```
src/
├── App.tsx                        # Root — layout, global state provider
│
├── components/
│   ├── TopBar/
│   │   ├── TopBar.tsx             # Logo, upload trigger, format badge, status indicator
│   │   └── UploadButton.tsx       # File input, drag-and-drop zone
│   │
│   ├── DocumentViewer/
│   │   ├── DocumentViewer.tsx     # Orchestrator — routes to correct sub-viewer
│   │   ├── PdfViewer.tsx          # react-pdf renderer + page navigation
│   │   ├── DocxViewer.tsx         # DOCX: converts to HTML via mammoth.js, renders
│   │   ├── HtmlViewer.tsx         # HTML/Markdown: iframe sandbox render
│   │   ├── PptxViewer.tsx         # PPTX: slide image thumbnails
│   │   ├── GenericViewer.tsx      # Fallback: raw text display
│   │   ├── PageControls.tsx       # ← prev / current / total / next →
│   │   └── SectionHighlight.tsx   # Overlay that dims non-selected page region
│   │
│   ├── OutputViewer/
│   │   ├── OutputViewer.tsx       # Orchestrator — toggle + content area
│   │   ├── FormatToggle.tsx       # JSON / Markdown pill toggle
│   │   ├── JsonView.tsx           # react-json-view collapsible tree
│   │   ├── MarkdownView.tsx       # react-markdown rendered output
│   │   ├── NodeCard.tsx           # One section in the tree (title, id, confidence badge)
│   │   ├── ConfidenceBadge.tsx    # Color-coded badge: green ≥0.9, amber 0.6–0.9, red <0.6
│   │   └── DownloadBar.tsx        # Download JSON / Download MD / Copy buttons
│   │
│   ├── UploadZone/
│   │   ├── UploadZone.tsx         # Full-screen drag-and-drop overlay (shown on first load)
│   │   └── FormatList.tsx         # Shows accepted formats with icons
│   │
│   └── StatusBar/
│       └── StatusBar.tsx          # Extraction stats: sections, format, path, time
│
├── hooks/
│   ├── useExtraction.ts           # Manages the upload → poll → result lifecycle
│   ├── useDocumentViewer.ts       # Page navigation, zoom, highlight state
│   └── useOutputViewer.ts         # Toggle state, scroll position, selected node
│
├── store/
│   └── useDocStructStore.ts       # Zustand store — global app state
│
├── types/
│   └── docstruct.ts               # TypeScript types mirroring the Python schema
│
├── api/
│   └── client.ts                  # Axios client + API functions
│
└── utils/
    ├── fileHelpers.ts             # File type detection, size formatting
    └── treeHelpers.ts             # Flatten tree, find node by id, etc.
```

---

## 5. Backend API Design (FastAPI)

### Endpoints

#### POST /extract
Upload a document and begin extraction.

```
Request:
  Content-Type: multipart/form-data
  Body:
    file: <binary file upload>
    ocr: boolean (default false)
    max_pages: integer | null (default null = no limit)

Response (202 Accepted):
  {
    "job_id": "uuid-string",
    "status": "processing",
    "filename": "report.pdf",
    "file_size_bytes": 2048000
  }
```

#### GET /status/{job_id}
Poll for job completion. Frontend polls every 500ms.

```
Response:
  {
    "job_id": "uuid-string",
    "status": "processing" | "complete" | "error",
    "progress_page": 12,        // current page being processed (for progress bar)
    "total_pages": 42,
    "elapsed_seconds": 3.2
  }
```

#### GET /result/{job_id}
Get the completed extraction result. Only returns when status = "complete".

```
Response:
  {
    "document": { ...DocumentTree JSON... },
    "markdown": "---\nsource_file: ...\n---\n# 1 · Introduction\n...",
    "stats": {
      "total_nodes": 47,
      "extraction_path": "fast",
      "elapsed_seconds": 1.2,
      "total_pages": 42
    }
  }
```

Note: both JSON tree and full Markdown string are returned in a single response. The toggle between views is entirely client-side — no second server call needed.

#### GET /file/{job_id}
Serve the original uploaded file back to the browser (for the document viewer).

```
Response:
  Content-Type: application/pdf (or appropriate MIME)
  Body: raw file bytes
```

This is needed because react-pdf needs a URL to load from, not a blob in state.

#### DELETE /job/{job_id}
Clean up server-side temp files when user closes the session or uploads a new document.

### Backend Implementation Notes

```python
# main.py skeleton

from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid, tempfile, asyncio
from pathlib import Path

app = FastAPI(title="DocStruct API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (sufficient for local single-user tool)
jobs: dict[str, dict] = {}

@app.post("/extract")
async def extract(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    # Save uploaded file to temp dir
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix)
    tmp.write(await file.read())
    tmp.close()

    jobs[job_id] = {
        "status": "processing",
        "filename": file.filename,
        "file_path": tmp.name,
        "result": None,
        "error": None,
        "progress_page": 0,
        "total_pages": 0,
    }

    background_tasks.add_task(run_extraction, job_id, tmp.name)
    return {"job_id": job_id, "status": "processing", "filename": file.filename}


async def run_extraction(job_id: str, file_path: str):
    try:
        from docstruct import DocStructPipeline
        pipeline = DocStructPipeline()
        tree = pipeline.process(file_path)

        from docstruct.serializers import to_json, to_markdown
        jobs[job_id]["result"] = {
            "document": tree.to_dict()["document"],
            "markdown": to_markdown(tree),
            "stats": {
                "total_nodes": len(tree.flat_list()),
                "extraction_path": tree.extraction_path,
                "total_pages": tree.total_pages,
            }
        }
        jobs[job_id]["status"] = "complete"
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
```

---

## 6. State Management

### Zustand Store Structure

```typescript
// store/useDocStructStore.ts

interface DocStructState {
  // Upload state
  uploadedFile: File | null
  jobId: string | null
  jobStatus: 'idle' | 'uploading' | 'processing' | 'complete' | 'error'
  errorMessage: string | null

  // Extraction result
  documentTree: DocumentTree | null
  markdownOutput: string | null
  extractionStats: ExtractionStats | null

  // Viewer state
  currentPage: number           // physical page shown in left panel
  totalPages: number
  selectedNodeId: string | null // id of node clicked in right panel
  outputFormat: 'json' | 'markdown'

  // Actions
  setUploadedFile: (file: File) => void
  setJobId: (id: string) => void
  setJobStatus: (status: JobStatus) => void
  setResult: (tree: DocumentTree, markdown: string, stats: ExtractionStats) => void
  setCurrentPage: (page: number) => void
  setSelectedNode: (nodeId: string | null) => void
  setOutputFormat: (format: 'json' | 'markdown') => void
  reset: () => void
}
```

### Key State Interactions

- When `selectedNodeId` changes → `DocumentViewer` reads the node's `pages.physical_start` and navigates the PDF viewer to that page.
- When `currentPage` changes (user navigates PDF) → highlight the node in the right panel whose page range contains `currentPage`.
- When `outputFormat` changes → no API call. Just renders the already-stored `markdownOutput` or `documentTree`.

---

## 7. File Upload Flow

### Upload Lifecycle

```
User drops file / clicks Upload
        │
        ▼
Validate file type + size
(reject if > 500MB or unsupported extension)
        │
        ▼
POST /extract  →  receive job_id
        │
        ▼
Store job_id, set status = "processing"
Show progress bar + animated spinner
        │
        ▼
Poll GET /status/{job_id} every 500ms
  → Update progress bar: progress_page / total_pages
        │
        ▼
status = "complete"
        │
        ▼
GET /result/{job_id}
Store documentTree + markdownOutput in Zustand
        │
        ▼
Render split-pane view
Left: load document from GET /file/{job_id}
Right: render JSON tree
```

### File Validation (client-side)

```typescript
const ACCEPTED_FORMATS = ['.pdf', '.docx', '.doc', '.html', '.htm',
                           '.md', '.markdown', '.epub', '.pptx', '.ppt',
                           '.png', '.jpg', '.jpeg', '.tiff']
const MAX_FILE_SIZE_MB = 500

function validateFile(file: File): string | null {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (!ACCEPTED_FORMATS.includes(ext)) {
    return `Unsupported format: ${ext}. Accepted: ${ACCEPTED_FORMATS.join(', ')}`
  }
  if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
    return `File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB. Max: ${MAX_FILE_SIZE_MB}MB`
  }
  return null  // valid
}
```

### Drag-and-Drop Zone

The `UploadZone` component renders as a full-screen overlay on initial load (before any file is uploaded). It:
- Accepts drag events on the `window` level (not just a specific zone)
- Shows a highlight border on dragover
- Dismisses once a file is dropped
- After upload + result, shows a smaller "Upload new document" button in the TopBar instead

---

## 8. Left Panel — Document Viewer

### Format-Specific Rendering

#### PDF (react-pdf)

```typescript
// PdfViewer.tsx
import { Document, Page } from 'react-pdf'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'

// Key props:
// - file: `http://localhost:8000/file/${jobId}` (URL, not blob)
// - pageNumber: currentPage from Zustand store
// - width: panel width in px (computed from panel ref)
// - renderAnnotationLayer: true (preserves clickable links in PDF)
// - renderTextLayer: true (preserves selectable text)
```

**Page navigation**: Previous / Next buttons update `currentPage` in the store. Also show a page number input field that accepts manual entry.

**Zoom**: Scale prop on `<Page>`. Add +/- buttons and a reset to fit-width. Store zoom level in local component state (not global store — it's purely display preference).

**Highlight**: When `selectedNodeId` is set in the store, look up the node's `pages.physical_start`. If the PDF is not already on that page, animate-scroll to it. Add a subtle amber highlight bar at the top of the page to indicate this is the target page. (Full pixel-level highlight of a specific region within a PDF page is complex — page-level highlighting is sufficient for Phase 1.)

#### DOCX (mammoth.js → HTML)

DOCX cannot be rendered directly in the browser. Convert to HTML client-side:

```typescript
// DocxViewer.tsx
import mammoth from 'mammoth'

// On file load:
const arrayBuffer = await file.arrayBuffer()
const result = await mammoth.convertToHtml({ arrayBuffer })
// Render result.value as inner HTML in a sandboxed div
// Apply basic prose CSS (font-size: 14px, line-height: 1.6, max-width: 680px)
```

mammoth.js runs entirely in the browser. No server call needed for rendering.

#### HTML / Markdown

Render in a sandboxed `<iframe>` with `srcdoc`:
```typescript
// For HTML: srcdoc = raw HTML file content (fetched from /file/{jobId})
// For Markdown: convert to HTML using marked.js, then srcdoc
// sandbox="allow-same-origin" (no scripts, no external resources)
```

#### PPTX

python-pptx cannot run in the browser. Options:
1. **Phase 1**: On the backend, when a PPTX is processed, also render each slide as a PNG image and store them. Return slide image URLs. Frontend renders them as an image gallery.
2. **Phase 2**: Use a proper slide renderer.

For Phase 1, add to the backend: after DocStruct processes a PPTX, use `python-pptx` + `Pillow` to export each slide as a PNG thumbnail.

#### Fallback (EPUB, etc.)

Show a plain-text view of the raw extracted text. Not ideal but functional for Phase 1.

---

## 9. Right Panel — Output Viewer

### Structure

```
┌─────────────────────────────────────────┐
│  [JSON]  [Markdown]          ← toggle  │
├─────────────────────────────────────────┤
│                                         │
│  [scrollable content area]              │
│                                         │
│  (JSON view or Markdown view here)      │
│                                         │
├─────────────────────────────────────────┤
│  [↓ JSON]  [↓ Markdown]  [⎘ Copy]      │
└─────────────────────────────────────────┘
```

### Format Toggle

```typescript
// FormatToggle.tsx
// A pill toggle (not a tab) — cleaner for binary choice

<div className="flex rounded-full border border-gray-200 p-0.5 w-fit">
  <button
    className={`px-4 py-1.5 rounded-full text-sm transition-colors ${
      format === 'json'
        ? 'bg-purple-600 text-white'
        : 'text-gray-500 hover:text-gray-700'
    }`}
    onClick={() => setOutputFormat('json')}
  >
    JSON
  </button>
  <button
    className={`px-4 py-1.5 rounded-full text-sm transition-colors ${
      format === 'markdown'
        ? 'bg-purple-600 text-white'
        : 'text-gray-500 hover:text-gray-700'
    }`}
    onClick={() => setOutputFormat('markdown')}
  >
    Markdown
  </button>
</div>
```

---

## 10. JSON View Specification

### Two Sub-Modes

The JSON panel has two modes toggled by a small secondary button:

1. **Tree view** (default): A visual collapsible tree where each DocNode is rendered as a `NodeCard`. This is human-readable, not raw JSON.
2. **Raw JSON** (secondary): Syntax-highlighted raw JSON using `react-syntax-highlighter`. For developers who want to copy/inspect the exact output.

### NodeCard Design

Each section in the tree view renders as a card:

```
┌──────────────────────────────────────────────────┐
│  ▶  1.2 · Scope                      [0.87] ●   │
│     id: 0003  ·  pages: 4–5  ·  2 children      │
└──────────────────────────────────────────────────┘

▶ = expand/collapse chevron (shows children)
[0.87] = ConfidenceBadge (amber — between 0.6 and 0.9)
● = node type indicator: filled = parent, hollow = child
```

### ConfidenceBadge

```typescript
// ConfidenceBadge.tsx
function ConfidenceBadge({ confidence }: { confidence: number }) {
  const color =
    confidence >= 0.9 ? 'bg-green-100 text-green-800' :
    confidence >= 0.6 ? 'bg-amber-100 text-amber-800' :
                        'bg-red-100 text-red-800'

  return (
    <span className={`text-xs px-1.5 py-0.5 rounded font-mono ${color}`}>
      {confidence.toFixed(2)}
    </span>
  )
}
```

Rules:
- `confidence >= 0.9` → green badge (fast path or high-confidence slow path)
- `0.6 <= confidence < 0.9` → amber badge (slow path, moderate confidence)
- `confidence < 0.6` → red badge (low confidence — user should verify)

### Tree Interaction

- All top-level nodes (depth=1) are expanded by default
- Deeper nodes (depth≥2) are collapsed by default
- Clicking the chevron toggles expand/collapse
- Clicking anywhere on the card (not just chevron) selects the node → sets `selectedNodeId` in store → left panel jumps to `pages.physical_start`
- Selected node is highlighted with a subtle left border accent

### Expand / Collapse All

Add two buttons above the tree: "Expand all" and "Collapse all". These change a local `expandedNodes: Set<string>` state.

---

## 11. Markdown View Specification

### Rendering

Use `react-markdown` with `remark-gfm` plugin (for tables support):

```typescript
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

<ReactMarkdown
  remarkPlugins={[remarkGfm]}
  components={{
    h1: ({children}) => <h1 className="text-2xl font-medium mt-6 mb-2 text-gray-900">{children}</h1>,
    h2: ({children}) => <h2 className="text-xl font-medium mt-5 mb-2 text-gray-800">{children}</h2>,
    h3: ({children}) => <h3 className="text-lg font-medium mt-4 mb-1.5 text-gray-700">{children}</h3>,
    // ... h4, h5, h6
    table: ({children}) => <table className="border-collapse w-full text-sm my-4">{children}</table>,
    code: ({children}) => <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono">{children}</code>,
    // Suppress rendering of HTML comment lines (the <!-- id:... --> metadata)
    // These are visible in "raw" mode but hidden in rendered view
  }}
>
  {markdownOutput}
</ReactMarkdown>
```

### Section Clickability in Markdown View

Each heading in the rendered Markdown should be clickable to select the corresponding node. Implementation:

Parse the `<!-- id:XXXX ... -->` comment that immediately follows each heading. Use a custom `h1`/`h2` etc. component that reads the next sibling's content to extract the node ID, then fires `setSelectedNode(id)` on click.

This is the trickiest part of the Markdown view. Simpler fallback for Phase 1: parse the section_id from the heading text (`1.2 · Scope` → `section_id = "1.2"`) and look up the node by `section_id`.

---

## 12. Node Linking — Click-to-Highlight

### Right-to-Left (node click → PDF jump)

```typescript
// In NodeCard onClick handler:
function handleNodeClick(node: DocNode) {
  setSelectedNode(node.id)
  setCurrentPage(node.pages.physical_start)
}

// In PdfViewer, watch currentPage:
useEffect(() => {
  if (pdfRef.current) {
    pdfRef.current.scrollToPage(currentPage)  // react-pdf API
  }
}, [currentPage])
```

### Left-to-Right (PDF page → node highlight)

When the user manually navigates the PDF (prev/next buttons), find the deepest node whose page range contains the new current page and highlight it in the right panel:

```typescript
function findDeepestNodeForPage(nodes: DocNode[], page: number): DocNode | null {
  let best: DocNode | null = null
  function walk(node: DocNode) {
    if (node.pages.physical_start <= page && page <= node.pages.physical_end) {
      if (!best || node.depth > best.depth) best = node
      node.children.forEach(walk)
    }
  }
  nodes.forEach(walk)
  return best
}

// Scroll the right panel to show the highlighted node
useEffect(() => {
  const node = findDeepestNodeForPage(documentTree.nodes, currentPage)
  if (node) {
    setSelectedNode(node.id)
    // Scroll right panel to the node card element
    document.getElementById(`node-${node.id}`)?.scrollIntoView({
      behavior: 'smooth', block: 'nearest'
    })
  }
}, [currentPage])
```

---

## 13. Processing States & UX

### State Machine

```
idle
  │ (user drops/selects file)
  ▼
uploading
  │ (POST /extract returns job_id)
  ▼
processing
  │ (polling GET /status every 500ms)
  │ (show progress bar: progress_page / total_pages)
  ▼
complete ──────────────────────── error
  │                                  │
  ▼                                  ▼
show split-pane view          show error card with
                              message + retry button
```

### Progress Bar Design

During `processing` state, show a full-width progress bar across the split pane area:

```
Processing annual_report.pdf...
[████████████░░░░░░░░░░░░░░░░░░]  12 / 42 pages  (3.2s)

  Extraction path: fast (PDF bookmarks detected)
```

- Progress percentage: `progress_page / total_pages * 100`
- Show elapsed time, updating every second
- Show extraction path as soon as backend detects it (fast/slow/mixed)
- For fast-path documents, processing is so quick the bar may jump straight to 100% — that's fine

### Long Document Warning

When `total_pages > 200`, show a yellow info banner below the upload area:
```
Long document detected (42 0 pages).
Extraction may take 30–120 seconds for untagged PDFs.
Fast-path documents (tagged PDFs, DOCX) complete in under 10 seconds.
```

---

## 14. Download & Copy Functionality

### Download JSON

```typescript
function downloadJson(tree: DocumentTree, filename: string) {
  const json = JSON.stringify({ document: tree }, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename.replace(/\.[^.]+$/, '_structure.json')
  a.click()
  URL.revokeObjectURL(url)
}
```

### Download Markdown

```typescript
function downloadMarkdown(markdown: string, filename: string) {
  const blob = new Blob([markdown], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename.replace(/\.[^.]+$/, '_structure.md')
  a.click()
  URL.revokeObjectURL(url)
}
```

### Copy to Clipboard

Copy whichever format is currently active in the toggle:

```typescript
async function copyToClipboard(content: string) {
  await navigator.clipboard.writeText(content)
  // Show "Copied!" toast for 2 seconds
  setToastMessage('Copied to clipboard')
  setTimeout(() => setToastMessage(null), 2000)
}
```

### Toast Notification

A simple, non-blocking toast anchored to the bottom-right of the screen:

```typescript
// Simple toast — no library needed
{toastMessage && (
  <div className="fixed bottom-4 right-4 bg-gray-900 text-white text-sm
                  px-4 py-2 rounded-lg shadow-lg animate-fade-in">
    {toastMessage}
  </div>
)}
```

---

## 15. Long Document Handling in UI

### Problem
A 700-page PDF may have 400+ section nodes. Rendering all of them in the DOM at once will make the right panel laggy.

### Solution: Virtual Scrolling

Use `react-window` (or `@tanstack/virtual`) to virtualise the flat node list in the JSON tree view. Only render nodes that are currently visible in the viewport.

```typescript
import { FixedSizeList } from 'react-window'

// Flatten the tree to a visible list (respecting collapsed state)
const visibleNodes = flattenVisibleNodes(documentTree.nodes, expandedNodes)

<FixedSizeList
  height={panelHeight}
  itemCount={visibleNodes.length}
  itemSize={64}   // height of one NodeCard in px
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>
      <NodeCard node={visibleNodes[index]} />
    </div>
  )}
</FixedSizeList>
```

### Flatten Visible Nodes

```typescript
function flattenVisibleNodes(
  nodes: DocNode[],
  expanded: Set<string>,
  depth: number = 0
): Array<{ node: DocNode, depth: number }> {
  const result = []
  for (const node of nodes) {
    result.push({ node, depth })
    if (expanded.has(node.id) && node.children.length > 0) {
      result.push(...flattenVisibleNodes(node.children, expanded, depth + 1))
    }
  }
  return result
}
```

### Progress During Extraction of Long Documents

For long documents, the backend should emit progress updates. The simplest approach: the `GET /status/{job_id}` endpoint returns `progress_page` which the frontend increments the bar with. For very long documents (400+ pages on slow path), this gives meaningful feedback.

---

## 16. Multi-Column Document Handling in UI

### What the UI Does (vs What the Backend Does)

The backend handles the multi-column detection and re-ordering of text spans. The UI has no special logic for multi-column — it just renders the output it receives.

However, the UI should surface one important signal: when the backend detects multi-column layout, it sets a field on the extraction result. Display this in the StatusBar:

```
Extracted 38 sections from report.pdf  ·  fast path  ·  2-column layout detected  ·  1.4s
```

If `extraction_path = "slow"` and the document had multi-column layout, the confidence scores on affected nodes will be lower. The ConfidenceBadge already handles this visually.

### No Special PDF Viewer Handling

`react-pdf` renders the PDF exactly as it was created. Multi-column PDFs will look correct in the left panel. The right panel shows the re-ordered, correctly-structured output. The user can visually compare the two.

---

## 17. Error Handling in UI

### Error Types and Display

| Error | Display |
|-------|---------|
| Unsupported file type | Inline error below upload zone |
| File too large | Inline error below upload zone |
| Backend offline | Full-panel error with retry + "Make sure the backend is running" |
| Extraction failed (corrupt file) | Right panel error card with error message from backend |
| OCR not available | Warning banner with install instructions |
| Partial extraction (low confidence) | Amber banner: "Some sections detected with low confidence. Review amber-marked nodes." |

### Error Card Design

When `jobStatus === 'error'`:

```
┌──────────────────────────────────────┐
│  Extraction failed                   │
│                                      │
│  annual_report.pdf                   │
│  "Could not parse PDF: corrupt file" │
│                                      │
│  [Try again]  [Upload different file]│
└──────────────────────────────────────┘
```

---

## 18. Responsive & Resizable Panels

### Drag-to-Resize

Use `react-resizable-panels`:

```typescript
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'

<PanelGroup direction="horizontal" autoSaveId="docstruct-layout">
  <Panel defaultSize={50} minSize={25}>
    <DocumentViewer />
  </Panel>
  <PanelResizeHandle className="w-1 bg-gray-200 hover:bg-purple-400 transition-colors cursor-col-resize" />
  <Panel defaultSize={50} minSize={25}>
    <OutputViewer />
  </Panel>
</PanelGroup>
```

`autoSaveId` persists the panel sizes to localStorage so they survive page refresh.

### Responsive Breakpoints

```css
/* Default: side-by-side (>= 900px) */
.panel-group { flex-direction: row; }

/* Mobile: stacked (< 900px) */
@media (max-width: 900px) {
  .panel-group { flex-direction: column; }
  /* Document viewer becomes top half, output bottom half */
  /* Each panel gets min-height: 300px */
}
```

---

## 19. Project Structure

```
docstruct-ui/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── index.html
│
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   │
│   ├── components/
│   │   ├── TopBar/
│   │   │   ├── TopBar.tsx
│   │   │   └── UploadButton.tsx
│   │   ├── DocumentViewer/
│   │   │   ├── DocumentViewer.tsx
│   │   │   ├── PdfViewer.tsx
│   │   │   ├── DocxViewer.tsx
│   │   │   ├── HtmlViewer.tsx
│   │   │   ├── PptxViewer.tsx
│   │   │   ├── GenericViewer.tsx
│   │   │   ├── PageControls.tsx
│   │   │   └── SectionHighlight.tsx
│   │   ├── OutputViewer/
│   │   │   ├── OutputViewer.tsx
│   │   │   ├── FormatToggle.tsx
│   │   │   ├── JsonView.tsx
│   │   │   ├── MarkdownView.tsx
│   │   │   ├── NodeCard.tsx
│   │   │   ├── ConfidenceBadge.tsx
│   │   │   └── DownloadBar.tsx
│   │   ├── UploadZone/
│   │   │   ├── UploadZone.tsx
│   │   │   └── FormatList.tsx
│   │   └── StatusBar/
│   │       └── StatusBar.tsx
│   │
│   ├── hooks/
│   │   ├── useExtraction.ts
│   │   ├── useDocumentViewer.ts
│   │   └── useOutputViewer.ts
│   │
│   ├── store/
│   │   └── useDocStructStore.ts
│   │
│   ├── types/
│   │   └── docstruct.ts
│   │
│   ├── api/
│   │   └── client.ts
│   │
│   └── utils/
│       ├── fileHelpers.ts
│       └── treeHelpers.ts
│
└── docstruct-backend/           # Python FastAPI backend
    ├── main.py
    ├── requirements.txt
    └── README.md
```

---

## 20. Dependency List

### Frontend (package.json)

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "react-pdf": "^7.0.0",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "react-syntax-highlighter": "^15.0.0",
    "react-resizable-panels": "^2.0.0",
    "react-window": "^1.8.0",
    "zustand": "^4.0.0",
    "axios": "^1.6.0",
    "mammoth": "^1.7.0",
    "marked": "^11.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.0.0",
    "autoprefixer": "^10.0.0",
    "postcss": "^8.0.0"
  }
}
```

### Backend (requirements.txt)

```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.9
# DocStruct dependencies (same as main implementation plan)
pdfplumber>=0.10.0
pymupdf>=1.23.0
python-docx>=1.0.0
beautifulsoup4>=4.12.0
markdown>=3.5.0
ebooklib>=0.18.0
python-pptx>=0.6.0
scikit-learn>=1.3.0
Pillow>=10.0.0   # for PPTX slide thumbnail export
```

---

## 21. Build Phases

### Phase 1 — Core UI Shell (1–2 weeks)
**Goal**: Upload a file, see the original document on the left, see raw JSON on the right.

- [ ] Vite + React + TypeScript + Tailwind scaffold
- [ ] FastAPI backend with `/extract`, `/status`, `/result`, `/file` endpoints
- [ ] `UploadZone` with drag-and-drop and file validation
- [ ] `TopBar` with upload trigger and format badge
- [ ] `DocumentViewer` — PDF only (react-pdf)
- [ ] `OutputViewer` — raw JSON view only (react-syntax-highlighter)
- [ ] `useExtraction` hook — full upload → poll → result lifecycle
- [ ] Zustand store — all state connected
- [ ] Progress bar during extraction
- [ ] Download JSON button

Success criterion: upload a PDF, see it rendered left, see valid JSON right, download works.

### Phase 2 — Polish + Full Format Support (1–2 weeks)
**Goal**: All format viewers, Markdown view, node linking.

- [ ] `DocxViewer` via mammoth.js
- [ ] `HtmlViewer` via sandboxed iframe
- [ ] `PptxViewer` via slide thumbnails (PNG from backend)
- [ ] `FormatToggle` — JSON / Markdown pill
- [ ] `MarkdownView` via react-markdown
- [ ] `NodeCard` tree view (collapsible, confidence badges)
- [ ] Node click → PDF page jump
- [ ] PDF page navigation → node highlight
- [ ] Download Markdown button
- [ ] Copy to clipboard + toast
- [ ] `StatusBar` with extraction stats
- [ ] Error states (all error types)

### Phase 3 — Performance + UX (1 week)
**Goal**: Works smoothly on 400-page documents.

- [ ] Virtual scrolling for large node trees (react-window)
- [ ] Drag-to-resize panels (react-resizable-panels)
- [ ] Expand/collapse all buttons
- [ ] Long document warning banner
- [ ] Responsive layout for small screens
- [ ] Persist panel size to localStorage

---

## 22. Prompt for Opus Implementation

> You are implementing the frontend for **DocStruct**, a local document structure extraction tool. The backend is a FastAPI server. The frontend is a React + TypeScript + Tailwind application built with Vite.
>
> **What the UI does**: The user uploads a document (PDF, DOCX, HTML, MD, EPUB, PPTX). The left panel renders the original document. The right panel shows the extracted hierarchical section tree, toggling between a JSON tree view and a Markdown view. Clicking a section node in the right panel jumps to that page in the left panel. The user can download the output as JSON or Markdown.
>
> **Non-negotiable rules**:
> 1. The toggle between JSON and Markdown is client-side only. No second API call. The backend returns both in one `/result` response.
> 2. The PDF viewer uses `react-pdf`, loading from `GET /file/{job_id}` — not from a blob in state.
> 3. The Zustand store is the single source of truth. Components do not have their own copies of the document tree.
> 4. Virtual scrolling (react-window) must be used for the node list when `total_nodes > 100`.
> 5. The FastAPI backend has exactly these endpoints: `POST /extract`, `GET /status/{job_id}`, `GET /result/{job_id}`, `GET /file/{job_id}`, `DELETE /job/{job_id}`. Do not add others.
> 6. The TypeScript types in `src/types/docstruct.ts` must mirror the Python schema exactly — every field name and type must match the backend JSON output.
>
> **Implementation sequence** (do in this order):
>
> **Step 1**: `src/types/docstruct.ts` — TypeScript interfaces for `DocNode`, `DocumentTree`, `PageRange`, `ImageRef`, `ExtractionStats`, `JobStatus`.
>
> **Step 2**: `src/api/client.ts` — Axios client with `uploadDocument()`, `pollStatus()`, `getResult()`, `getFileUrl()`, `deleteJob()`.
>
> **Step 3**: `src/store/useDocStructStore.ts` — Zustand store with all state and actions.
>
> **Step 4**: `src/hooks/useExtraction.ts` — the upload → poll → result lifecycle hook.
>
> **Step 5**: `docstruct-backend/main.py` — full FastAPI backend with all 5 endpoints.
>
> **Step 6**: `src/App.tsx` + `src/components/TopBar/TopBar.tsx` + `src/components/UploadZone/UploadZone.tsx` — layout shell and upload flow.
>
> **Step 7**: `src/components/DocumentViewer/PdfViewer.tsx` — react-pdf viewer with page navigation.
>
> **Step 8**: `src/components/OutputViewer/OutputViewer.tsx` + `FormatToggle.tsx` + `JsonView.tsx` + `NodeCard.tsx` + `ConfidenceBadge.tsx`.
>
> **Step 9**: `src/components/OutputViewer/MarkdownView.tsx` + `DownloadBar.tsx`.
>
> **Step 10**: Node linking — implement `findDeepestNodeForPage()` in `treeHelpers.ts`, wire up click-to-jump and page-to-highlight in both panels.
>
> **Step 11**: `src/components/StatusBar/StatusBar.tsx` + error states + progress bar.
>
> After all 11 steps pass a manual smoke test (upload PDF, see output, toggle, download), proceed to Phase 2 (remaining format viewers, virtual scrolling, resizable panels).
>
> Write complete, production-quality code for each step. No placeholder components. No TODO comments except where explicitly flagged in the plan.

---

*End of DocStruct Frontend Implementation Plan v1.0*
