# System Architecture (DocStruct)

This document explains the end-to-end architecture of **DocStruct (DocumentParser)**: how it ingests documents, how it extracts a hierarchical structure (sections/headings, tables, and images), how it optionally uses a VLM via OpenRouter for hard cases, and how it serves results through an async API and a local CLI.

## Problem This System Resolves

Many documents arrive as *unstructured files* (PDFs, DOCX, HTML, PPTX, EPUB, and images). They often contain:

- Nested sections/headings (not just plain text).
- Tables that are visually laid out but not semantically represented.
- Diagrams/figures and other non-text content.

DocStruct’s goal is to convert these inputs into a consistent **structured output**:

- A `DocumentTree` of `DocNode` elements (hierarchical headings/sections).
- Embedded `TableBlock` objects and `ImageRef` assets (with page ranges and coordinates).
- Output as JSON and Markdown that the UI can render and users can download.

## High-Level Architecture

At runtime, DocStruct is composed of these major areas:

1. **FastAPI server (async job API)**: accepts uploads, runs extraction in a background task, and serves status/results/assets.
2. **Pipeline orchestration**: detects input format and routes to the correct parser path (heuristic vs VLM).
3. **Parsers**: format-specific extraction engines that produce a `DocumentTree`.
4. **Content extraction** (PDF-specific): table extraction (pdfplumber) and image/diagram extraction (PyMuPDF), attaching assets to the `DocumentTree`.
5. **Serializers**: converts `DocumentTree` into JSON and Markdown.

### Key Code Locations

- API: [`backend/main.py`](backend/main.py)
- Pipeline/router: [`backend/docstruct/pipeline.py`](backend/docstruct/pipeline.py)
- Data model/schema: [`backend/docstruct/core/schema.py`](backend/docstruct/core/schema.py)
- PDF parser: [`backend/docstruct/parsers/pdf_parser.py`](backend/docstruct/parsers/pdf_parser.py)
- VLM parser (OpenRouter): [`backend/docstruct/parsers/vlm_parser.py`](backend/docstruct/parsers/vlm_parser.py)
- Table extraction: [`backend/docstruct/content/pdf_table_extractor.py`](backend/docstruct/content/pdf_table_extractor.py)
- Image extraction: [`backend/docstruct/content/image_extractor.py`](backend/docstruct/content/image_extractor.py)
- Serializers:
  - JSON: [`backend/docstruct/serializers/json_serializer.py`](backend/docstruct/serializers/json_serializer.py)
  - Markdown: [`backend/docstruct/serializers/markdown_serializer.py`](backend/docstruct/serializers/markdown_serializer.py)
- CLI: [`backend/docstruct/cli.py`](backend/docstruct/cli.py)

### Architecture Diagram

```mermaid
flowchart LR
  U[User Upload] --> API[FastAPI POST /extract]
  API --> J[Create job_id + in-memory job record]
  J --> BG[BackgroundTasks: _run_extraction]
  BG --> PIPE[DocStructPipeline.process]
  PIPE --> ROUTE{Format + routing}
  ROUTE -->|PDF outline| PDF[PdfParser + extraction path]
  ROUTE -->|No outline + VLM| VLM[VlmParser (render + OpenRouter)]
  ROUTE -->|DOCX/HTML/MD/EPUB/PPTX| P[Format parser]
  PDF --> TEX[extract_tables_from_pdf]
  PDF --> IEX[extract_images_from_pdf]
  VLM --> MD2TREE[Markdown -> DocumentTree]
  PIPE --> SER[Serializers: JSON + Markdown]
  SER --> STORE[Store in jobs[job_id].result]
  API -->|Poll| STAT[GET /status]
  API -->|Fetch| RES[GET /result]
  API -->|Serve| ASSET[GET /asset for images/tables]
```

## Data Model / Schema Contracts

The primary contract is a `DocumentTree` containing hierarchical nodes:

- `DocumentTree` (root contract): overall metadata plus extracted structure:
  - `source_file`: original uploaded filename (string)
  - `source_format`: a `SourceFormat` value (`pdf/docx/html/markdown/epub/pptx/image`)
  - `total_pages`: total physical page count (int)
  - `extracted_at`: ISO-8601 UTC timestamp (`datetime.now(timezone.utc).isoformat()`)
  - `extraction_path`: an `ExtractionPath` value (`fast/slow/mixed/vlm`)
  - `nodes`: list of top-level `DocNode`s
- `DocNode`: a section/heading node:
  - `title` and extracted `text`
  - `pages` (`PageRange | None`) describing physical page boundaries (and optional logical ranges)
  - `confidence` score (float)
  - `images` (`List[ImageRef]`) and `tables` (`List[TableBlock]`)
  - `children` forming the hierarchy (`List[DocNode]`)
  - Finalization-assigned fields (via `DocumentTree.finalise()`):
    - `id`: flat sequential id (`0001`, `0002`, ...) assigned for cross-references
    - `section_id`: nesting-based section numbering (`1`, `1.1`, `1.2`, ...)
    - `depth` and `node_type` (`root/parent/child`), recomputed after finalization
- `PageRange`:
  - `physical_start` / `physical_end`: inclusive physical page bounds (ints)
  - optional `logical_start` / `logical_end`: reserved for future logical page mapping
- `ImageRef` (assets entry attached to a node):
  - `path`: API-served asset path (e.g. `assets/images/<filename>`)
  - `page`: physical page number (int)
  - `label`, `caption`, `image_id`, `image_type` (e.g. `raster` or `vector`)
  - internal spatial fields (`y0/y1`, `bbox`, `width_px/height_px`) used for placement logic; not serialized for JSON output
- `TableBlock` (structured table representation):
  - `table_id`, `caption`, `page`
  - `headers` and `rows`
  - `markdown`: pre-computed GFM table string (string)
  - `image_path`: API-served table image path (e.g. `assets/tables/<table_id>.png`)
  - internal extraction fields (`extraction_method`, `is_valid_table`) used during extraction/validation

### IDs, Section IDs, and Serialization

During finalization (`DocumentTree.finalise()`):

- Section IDs are assigned (`DocNode.section_id`) based on nesting.
- Flat sequential IDs are assigned (`DocNode.id`) used by the Markdown serializer when `include_metadata=True` (format: `0001`, `0002`, ...).
- Node types (`root`, `parent`, `child`) are recomputed based on tree structure.

### Marker Handling for Inline Images

Some pipeline stages insert internal image markers into `DocNode.text` to preserve *where an image belongs* spatially. Those markers are removed from JSON serialization via logic in `schema.py`, while Markdown serialization can replace the markers with actual `![label](assets/images/...)` links.

Marker format (inserted by the PDF image extractor):
- `{{IMG:<filename>|<label>|<caption>}}`
These markers are stripped from JSON (`DocNode.to_dict()`), then replaced during Markdown generation.

## End-to-End Flows

### API Flow (FastAPI Async Jobs)

Main server file: [`backend/main.py`](backend/main.py)

1. **Upload** (`POST /extract`, status `202`):
   - A new `job_id` is generated.
   - The uploaded file is written to a job directory under the OS temp directory:
     - `tempfile.gettempdir() / "docstruct" / {job_id}`
   - A job record is created in an in-memory `jobs` dict.
   - A background task starts `_run_extraction(job_id)`.
2. **Background execution** (`_run_extraction`):
   - Creates a `DocStructPipeline()` instance.
   - Calls `pipeline.process(file_path, artifact_dir=tmp_dir, progress_callback=...)`.
   - On success:
     - Computes Markdown (`to_markdown(tree)`)
     - Stores a `result` object containing:
       - `document` (from `tree.to_dict()`)
       - `markdown`
       - `stats` (node count, page count, elapsed time, extraction path)
   - On failure:
     - Sets `status="error"` and stores an error string.
3. **Poll status** (`GET /status/{job_id}`):
   - Returns `status`, current `progress_page`, `total_pages`, `elapsed_seconds`, and `extraction_path`.
4. **Fetch result** (`GET /result/{job_id}`):
   - Returns JSON payload once `status="complete"`.
5. **Asset serving**:
   - `GET /asset/{job_id}/{asset_path:path}` serves images/tables created during extraction.
   - The handler resolves the requested path and ensures it stays within the job’s base temp directory to prevent path traversal.
6. **Job deletion and TTL cleanup**:
   - `DELETE /job/{job_id}` removes job artifacts.
   - A purge task runs periodically and removes jobs older than 1 hour from the in-memory store and temp directories.

### CLI Flow (Local Batch Extraction)

The CLI entrypoint: [`backend/docstruct/cli.py`](backend/docstruct/cli.py)

1. Parse args (input path, output directory, output format).
2. Run `DocStructPipeline.process(input_path, artifact_dir=output_dir)`.
3. Write:
   - `{stem}.docstruct.json` and/or `{stem}.docstruct.md` into the output directory.

## Pipeline Routing Logic

Pipeline/router entrypoint: [`backend/docstruct/pipeline.py`](backend/docstruct/pipeline.py)

### 1. Format Detection

`DocStructPipeline` maps extensions to `SourceFormat`:

- `pdf` -> `SourceFormat.PDF`
- `docx/doc` -> `SourceFormat.DOCX`
- `html/htm` -> `SourceFormat.HTML`
- `md/markdown` -> `SourceFormat.MARKDOWN`
- `epub` -> `SourceFormat.EPUB`
- `pptx/ppt` -> `SourceFormat.PPTX`
- `png/jpg/jpeg/tiff/tif` -> `SourceFormat.IMAGE`

Unsupported extensions raise an error.

### 2. VLM Availability and When VLM Is Used

VLM availability is determined by whether `OPENROUTER_API_KEY` is configured in the environment.

Routing behavior:

- **Images** (`SourceFormat.IMAGE`):
  - Requires OpenRouter API key.
  - If not configured, the pipeline raises an error.
- **PDFs** (`SourceFormat.PDF`):
  - The pipeline checks whether the PDF contains a usable outline/bookmark structure via `fitz` (PyMuPDF) TOC extraction.
  - If no usable outline is found:
    - If VLM is available: route to `VlmParser`.
    - If VLM is not available: route to the heuristic PDF slow path.

### 3. Parser Selection After Routing

If the pipeline does not choose VLM:

- PDFs route to [`PdfParser`](backend/docstruct/parsers/pdf_parser.py).
- DOCX/HTML/Markdown/EPUB/PPTX route to their corresponding format parsers.

## VLM (OpenRouter) Integration in Detail

VLM parser entrypoint: [`backend/docstruct/parsers/vlm_parser.py`](backend/docstruct/parsers/vlm_parser.py)

### 1. Rendering Pages as Images

- For PDFs, each page is rendered using PyMuPDF with a DPI-controlled zoom:
  - `render_page_to_png(doc, page_num, dpi)`
  - The zoom is computed as `dpi / 72.0`.
- VLM configuration (from environment variables):
  - `DOCSTRUCT_VLM_DPI` (default `150`) controls `VLM_PAGE_DPI`
  - `DOCSTRUCT_VLM_MODEL` (default `openai/gpt-4o-mini`) controls the OpenRouter `model`
  - `VLM_MAX_RETRIES=3`, with `VLM_RETRY_DELAY=2.0` seconds between attempts
  - `VLM_REQUEST_TIMEOUT=60` seconds per request
- For image inputs:
  - PNG bytes are used directly for `.png`.
  - Other image formats are converted into PNG bytes using PyMuPDF.

### 2. OpenRouter API Call Shape

OpenRouter endpoint:

- `https://openrouter.ai/api/v1/chat/completions`

Request authentication:

- `Authorization: Bearer {OPENROUTER_API_KEY}`
- `HTTP-Referer: https://docstruct.local`
- `X-Title: DocStruct`

Request payload:

- `messages[0]`: the system prompt (`VLM_SYSTEM_PROMPT`) that instructs the model how to emit Markdown and what to ignore (headers/footers, TOC-only pages, cover pages, etc.).
- `messages[1]`: a multimodal `content` array with:
  - `image_url` containing the rendered PNG as a `data:image/png;base64,...` URI
  - `text` containing instructions to extract the current page number and (optionally) tail context from the previous page

Retry behavior:

- The API call retries up to `VLM_MAX_RETRIES` (default 3) with increasing delays.

### 3. Markdown Cleaning

After OpenRouter returns Markdown:

- Code fences are stripped if the model wrapped the output.
- Running header/footer artefacts are removed using line-level heuristics:
  - remove standalone URLs (`www.` / `http://` / `https://`) when lines are short
  - remove month+year stamps (e.g. `December 2025`) and page-number patterns (`3`, `Page 3 of 47`, roman numerals)
- Excess blank lines are collapsed to at most one blank line.
- “Heading promotion” is prevented for likely header/footer lines by demoting specific short uppercase/URL/month-year patterns that start with `#`.

### 4. Continuation Handling

The VLM prompt instructs page-by-page extraction. The parser additionally supports page continuation:

- If the model output includes `[CONTINUATION]`, the parser merges the continuation into the most recent open node.
- If continuation is not explicitly marked, a heuristic check attempts to detect mid-list/mid-sentence continuity and injects `[CONTINUATION]`.
- During merge, the parser also attempts to extract any tables embedded in the continuation text and appends them to the current node.

### 5. Markdown-to-DocumentTree Conversion

The function `_parse_pages_to_tree(...)` converts VLM page Markdown into `DocumentTree`:

- Headings are detected by AtX markers (`#`..`######`) using a regex.
- A stack-based structure builder attaches new headings as children of the current stack top.
- Tables are detected as GFM tables (rows and separator lines).
  - Accepted tables become `TableBlock` nodes.
  - Otherwise, the content is appended back as prose lines (invalid tables are not emitted as `TableBlock`s).
- Heading nodes create `DocNode`s with `pages.physical_start/physical_end` initialized to the heading’s page, and these ranges are expanded as pages progress.
- If the model output produces no headings/nodes, a fallback node is created using `Path(source_file).stem` as the title and concatenating all non-blank page markdown.

The resulting tree is finalized (`tree.finalise()`), producing section IDs and IDs consistent with other pipelines.

## PDF Artifacts: Tables + Images

PDF pipeline artifact extraction happens when `artifact_dir` is provided (API passes the job temp directory).

### 1. Table Extraction (`pdfplumber`)

Table extraction entrypoint:

- [`backend/docstruct/content/pdf_table_extractor.py`](backend/docstruct/content/pdf_table_extractor.py)

Key responsibilities:

- Runs multiple pdfplumber strategies per page (lines, text, and mixed).
- Deduplicates overlapping table candidates.
- Filters false positives using quality heuristics (rows/cols limits, empty-cell ratios, truncation signals).
- Extracts tables into `TableBlock` objects.
- Renders pixel-accurate table images (`assets/tables/{table_id}.png`) into the job artifact directory and attaches `TableBlock.image_path`.
- Returns per-page table bounding boxes so the image extractor can skip capturing diagram regions that overlap known tables.

### 2. Image/Diagram Extraction (PyMuPDF)

Image extraction entrypoint:

- [`backend/docstruct/content/image_extractor.py`](backend/docstruct/content/image_extractor.py)

Key responsibilities:

- Extracts embedded raster images and vector diagram clusters.
- Uses the table bounding boxes from the table extractor to avoid double-capturing table borders as diagrams/images.
- Inserts inline image markers into node text to preserve placement for Markdown output.

## Output Formats

### JSON Output

JSON serializer:

- [`backend/docstruct/serializers/json_serializer.py`](backend/docstruct/serializers/json_serializer.py)

Notable behavior:

- Confidence values are rounded to 4 decimals.
- JSON does not contain internal image marker strings because `DocNode.to_dict()` strips them.

### Markdown Output

Markdown serializer:

- [`backend/docstruct/serializers/markdown_serializer.py`](backend/docstruct/serializers/markdown_serializer.py)

Notable behavior:

- Adds a frontmatter section at the top.
- Renders each node as a heading using node depth (bounded to 6 heading levels).
- Replaces inline image markers with `assets/images/...` Markdown image links.
- Includes tables:
  - If a valid table markdown string exists, it is emitted as a GFM table.
  - Otherwise, a table image is linked (if present).

## Security and Operational Considerations

This project is currently structured as a **single-user tool-style service**:

- The API uses an in-memory `jobs` dict (not persistent storage).
- There is no authentication layer in the API routes shown here.

Key operational aspects:

1. **CORS**
   - The API allows browser origins for local development:
     - `http://localhost:5173` and `http://127.0.0.1:5173`.
2. **Asset path traversal protection**
   - `GET /asset/{job_id}/{asset_path:path}` resolves `candidate = (base_dir / asset_path).resolve()` and ensures `base_dir.resolve()` is within `candidate.parents`.
   - Requests that escape the job directory are rejected with HTTP `400` (`Invalid asset path`).
3. **Secrets handling**
   - OpenRouter API secrets are read from environment variables:
     - `OPENROUTER_API_KEY`
     - optional `DOCSTRUCT_VLM_MODEL` and `DOCSTRUCT_VLM_DPI`
   - `.env` files must not be committed to GitHub.
4. **Async job lifecycle and TTL purge**
   - A startup background task runs an in-process TTL purge loop:
     - checks every 5 minutes (`asyncio.sleep(300)`)
     - removes jobs older than 1 hour (`cutoff = now - 3600`)
     - deletes the job temp directory via best-effort `shutil.rmtree(..., ignore_errors=True)`

