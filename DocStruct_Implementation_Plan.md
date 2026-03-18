# DocStruct — Comprehensive Implementation Plan
**For review + implementation by Opus**  
Version 1.0 | March 2026

---

## Table of Contents

1. [System Vision & Goals](#1-system-vision--goals)
2. [What This System Is NOT](#2-what-this-system-is-not)
3. [Output Schema (Locked)](#3-output-schema-locked)
4. [High-Level Architecture](#4-high-level-architecture)
5. [Layer 0 — Input Ingestion & Format Detection](#5-layer-0--input-ingestion--format-detection)
6. [Layer 1 — Unified Span Extraction](#6-layer-1--unified-span-extraction)
7. [Layer 2 — Routing: Fast Path vs Slow Path](#7-layer-2--routing-fast-path-vs-slow-path)
8. [Layer 3A — Fast Path: Deterministic Tree Construction](#8-layer-3a--fast-path-deterministic-tree-construction)
9. [Layer 3B — Slow Path: Heuristic Heading Detection](#9-layer-3b--slow-path-heuristic-heading-detection)
10. [Layer 4 — Fault-Tolerant Tree Builder](#10-layer-4--fault-tolerant-tree-builder)
11. [Layer 5 — ID Assignment & Tree Finalisation](#11-layer-5--id-assignment--tree-finalisation)
12. [Layer 6 — Content & Media Extraction](#12-layer-6--content--media-extraction)
13. [Layer 7 — Serialization (JSON + Markdown)](#13-layer-7--serialization-json--markdown)
14. [Format-Specific Parser Details](#14-format-specific-parser-details)
15. [Data Contracts & Interfaces](#15-data-contracts--interfaces)
16. [Algorithms Reference](#16-algorithms-reference)
17. [Configuration & Extensibility](#17-configuration--extensibility)
18. [Error Handling Strategy](#18-error-handling-strategy)
19. [Testing Strategy](#19-testing-strategy)
20. [Project Structure](#20-project-structure)
21. [Dependency Matrix](#21-dependency-matrix)
22. [Build Phases & Milestones](#22-build-phases--milestones)
23. [Known Hard Problems & Design Decisions](#23-known-hard-problems--design-decisions)
24. [Prompt for Opus Implementation](#24-prompt-for-opus-implementation)

---

## 1. System Vision & Goals

### What DocStruct Does

DocStruct is a **format-agnostic, LLM-free document structure extraction pipeline**. Given any document file, it produces a **hierarchical tree** where every node represents a section or subsection of that document. The tree captures the logical outline of the document — its headings, their nesting relationships, their content, and their physical location in the file.

### Core Value Proposition

- **Zero API cost**: No calls to OpenAI, Anthropic, or any external service
- **Zero inference latency**: Runs entirely on local CPU, no GPU required
- **Zero data leakage**: Documents never leave the machine
- **Offline-capable**: Works in air-gapped, privacy-sensitive, high-throughput environments
- **Multi-format**: One unified pipeline for PDF, DOCX, HTML, Markdown, EPUB, PPTX

### The Gap Being Filled

Every existing tool does part of this job:
- `pdfplumber`, `python-docx`, `BeautifulSoup` → extract raw text/spans but produce no hierarchy
- `Apache Tika` → raw text + metadata, no nesting
- `Docling` / `Unstructured.io` → flat element lists, no tree structure
- `GROBID` → hierarchical but scientific papers only
- `PageIndex (VectifyAI)` → produces a tree but requires OpenAI API

DocStruct adds exactly one abstraction on top of the existing ecosystem: **the logical structure tree with traceable IDs**. It does not replace these tools — it builds on top of them.

### Primary Use Cases

1. **RAG (Retrieval-Augmented Generation)**: Chunk documents by section rather than arbitrary token windows. Section IDs enable citation traceability back to the original document.
2. **Document navigation**: Generate a navigable table of contents for any document programmatically.
3. **Document comparison**: Compare section-level structure across document versions.
4. **Search indexing**: Index sections independently for finer-grained search relevance.
5. **Compliance & audit**: Verify that required sections (e.g. regulatory clauses) are present and correctly structured.

---

## 2. What This System Is NOT

Be explicit about these to avoid scope creep during implementation:

- **Not a full-text OCR system**: OCR is a pre-processing dependency (Tesseract/PaddleOCR), not a core function. Scanned PDFs are supported only when an OCR layer is configured.
- **Not a semantic understanding system**: DocStruct detects structure from visual and formatting signals, not meaning. It does not understand whether "Introduction" and "Background" should be at the same level semantically.
- **Not a table extraction system**: Tables are extracted as raw markdown strings inline in `text`. Deep table parsing (cell relationships, multi-header tables) is out of scope.
- **Not a document converter**: It produces a structured JSON/Markdown representation, not a converted copy of the document.
- **Not an LLM wrapper**: There is no LLM in the core extraction loop. An optional LLM validation pass may be added as a separate post-processor, clearly isolated from the main pipeline.

---

## 3. Output Schema (Locked)

This schema is **frozen**. All implementation decisions must produce output conforming to this schema.

### 3.1 JSON Output

```json
{
  "document": {
    "source_file": "annual_report.pdf",
    "source_format": "pdf",
    "total_pages": 42,
    "extracted_at": "2026-03-17T10:30:00Z",
    "extraction_path": "fast",
    "nodes": [
      {
        "id": "0001",
        "section_id": "1",
        "depth": 1,
        "node_type": "parent",
        "title": "Introduction",
        "text": "This report covers annual performance...",
        "pages": {
          "physical_start": 3,
          "physical_end": 5,
          "logical_start": "3",
          "logical_end": "5"
        },
        "confidence": 1.0,
        "images": [
          {
            "label": "Figure 1.1",
            "caption": "System architecture overview",
            "path": "output/annual_report_images/p3_img1.png"
          }
        ],
        "children": [
          {
            "id": "0002",
            "section_id": "1.1",
            "depth": 2,
            "node_type": "child",
            "title": "Background",
            "text": "The project began in 2023...",
            "pages": {
              "physical_start": 3,
              "physical_end": 4,
              "logical_start": "3",
              "logical_end": "4"
            },
            "confidence": 1.0,
            "images": [],
            "children": []
          }
        ]
      }
    ]
  }
}
```

### 3.2 Field Definitions (Canonical)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Zero-padded sequential integer across the whole document in pre-order traversal. Format: `"0001"`, `"0002"`. Assigned by `DocumentTree.finalise()`. Never assigned by a parser directly. |
| `section_id` | string | Hierarchical dotted identifier. `"1"`, `"1.2"`, `"1.2.3"`. Encodes depth and position. Assigned by `DocumentTree.finalise()`. |
| `depth` | integer | 1-based depth level. 1 = top-level section, 2 = subsection, 3 = sub-subsection. Derived from `section_id` dot count. |
| `node_type` | string | `"root"` if depth=1 and no parent. `"parent"` if has children. `"child"` if no children. Recomputed on finalise. |
| `title` | string | Heading text, stripped of leading numbering patterns (e.g. `"1.2 Introduction"` → `"Introduction"`). Preserve original capitalisation. |
| `text` | string | Prose content directly under this heading, **before the first child heading begins**. Tables serialised as inline markdown strings. Empty string if section contains only sub-headings. |
| `pages.physical_start` | integer | 1-based page index as you scroll through the file. Blank pages, TOC pages, and cover pages count. Always set. |
| `pages.physical_end` | integer | Last physical page belonging to this section. For the last section, equals `total_pages`. |
| `pages.logical_start` | string or null | Printed page number in the document (may be `"iv"`, `"A-1"`, `"3"`, or null if not detectable). |
| `pages.logical_end` | string or null | Same as above for end page. |
| `confidence` | float | 0.0–1.0. `1.0` for all fast-path extractions. Classifier probability for slow-path heading detections. Allows downstream consumers to filter low-confidence nodes. |
| `images[].label` | string | Figure label as printed in document, e.g. `"Figure 3.2"`. Empty string if not found. |
| `images[].caption` | string | Caption text found adjacent to the image. Empty string if not found. |
| `images[].path` | string | Relative or absolute path to extracted image file on disk. Empty string if extraction failed. |
| `children` | array | Ordered list of child `DocNode` objects. Empty array for leaf nodes. |

### 3.3 Markdown Output Format

```markdown
---
source_file: annual_report.pdf
source_format: pdf
total_pages: 42
extracted_at: 2026-03-17T10:30:00Z
extraction_path: fast
---

# 1 · Introduction
<!-- id:0001 pages:3-5 confidence:1.0 type:parent -->

This report covers annual performance...

![Figure 1.1](output/annual_report_images/p3_img1.png)
*Figure 1.1 — System architecture overview*

## 1.1 · Background
<!-- id:0002 pages:3-4 confidence:1.0 type:child -->

The project began in 2023...
```

Rules:
- ATX headings (`#`) driven by `depth`. Cap at `######` (h6) for depth > 6.
- Heading line format: `{hashes} {section_id} · {title}`
- Metadata comment on the line immediately after the heading
- Body text rendered verbatim (tables already markdown-formatted)
- Images as `![label](path)` followed by `*caption*` on next line
- Blank line between every logical block

---

## 4. High-Level Architecture

```
Input File
    │
    ▼
┌─────────────────────────────────────────┐
│  Layer 0: Format Detector               │
│  Determines SourceFormat enum           │
│  Routes to correct parser class         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Layer 1: Span Extractor                │
│  Format-specific libraries              │
│  Outputs: list[Span] (unified schema)   │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Layer 2: Router                        │
│  Has structural signals? → FAST PATH    │
│  No signals?             → SLOW PATH    │
└────────┬────────────────────┬───────────┘
         │                    │
         ▼                    ▼
┌────────────────┐   ┌────────────────────┐
│ Layer 3A:      │   │ Layer 3B:          │
│ Fast Path      │   │ Slow Path          │
│ Direct tree    │   │ Font clustering +  │
│ from signals   │   │ Heading classifier │
└────────┬───────┘   └─────────┬──────────┘
         │                     │
         └──────────┬──────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Layer 4: Fault-Tolerant Tree Builder   │
│  Stack algorithm + gap tolerance        │
│  Phantom node insertion for gaps        │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Layer 5: Tree Finalisation             │
│  section_id assignment (dotted)         │
│  id assignment (zero-padded sequential) │
│  node_type recomputation                │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Layer 6: Content & Media Extraction    │
│  Text population per node               │
│  Image extraction → ImageRef objects    │
│  Page range resolution                  │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Layer 7: Serializer                    │
│  JSON serializer                        │
│  Markdown serializer                    │
└─────────────────────────────────────────┘
                  │
                  ▼
          DocumentTree object
          + JSON file
          + Markdown file
          + extracted images/
```

### Design Principles

1. **Parsers only build the tree skeleton.** Content population (text, images, page numbers) happens in Layer 6, after the tree structure is confirmed.
2. **`DocumentTree.finalise()` owns all ID assignment.** Parsers never assign `id` or `section_id`. This separation means the tree can be restructured before finalisation without corrupting IDs.
3. **Confidence is a first-class citizen.** Every node carries a confidence score. Fast-path nodes always get `1.0`. Slow-path nodes get the classifier's probability score. This allows downstream consumers to filter or flag uncertain structure.
4. **Fault tolerance over correctness.** The system must always produce *a* tree, even if it's imperfect. A flat tree with all sections at depth 1 is better than an exception. Use confidence scores to communicate uncertainty rather than failing.
5. **Physical page numbers over logical.** `physical_start`/`physical_end` are always integers starting at 1. Logical page numbers (printed in document) are stored separately and may be null.

---

## 5. Layer 0 — Input Ingestion & Format Detection

### Responsibility
Determine the `SourceFormat` of the input file and instantiate the correct parser.

### Implementation

```python
class DocStructPipeline:
    """Main entry point. Routes input to correct parser."""

    FORMAT_MAP = {
        ".pdf":      SourceFormat.PDF,
        ".docx":     SourceFormat.DOCX,
        ".doc":      SourceFormat.DOCX,   # requires pre-conversion
        ".html":     SourceFormat.HTML,
        ".htm":      SourceFormat.HTML,
        ".md":       SourceFormat.MARKDOWN,
        ".markdown": SourceFormat.MARKDOWN,
        ".epub":     SourceFormat.EPUB,
        ".pptx":     SourceFormat.PPTX,
        ".ppt":      SourceFormat.PPTX,   # requires pre-conversion
        ".png":      SourceFormat.IMAGE,
        ".jpg":      SourceFormat.IMAGE,
        ".jpeg":     SourceFormat.IMAGE,
        ".tiff":     SourceFormat.IMAGE,
        ".tif":      SourceFormat.IMAGE,
    }

    def process(self, file_path: str | Path, output_dir: str | Path = None) -> DocumentTree:
        path = Path(file_path)
        suffix = path.suffix.lower()
        fmt = self.FORMAT_MAP.get(suffix)
        if fmt is None:
            # Fallback: try to detect by MIME type using python-magic
            fmt = self._detect_by_mime(path)
        parser = self._get_parser(fmt, path)
        tree = parser.parse()
        if output_dir:
            self._save_outputs(tree, Path(output_dir))
        return tree
```

### Format Detection Fallback
If file extension is ambiguous or missing, use `python-magic` to detect MIME type:
- `application/pdf` → PDF
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document` → DOCX
- `text/html` → HTML
- `text/markdown` or `text/plain` with markdown content patterns → MARKDOWN

### Legacy Format Handling
- `.doc` files: pre-convert to `.docx` using `LibreOffice --headless --convert-to docx` via subprocess. Fail gracefully if LibreOffice is not installed.
- `.ppt` files: same approach via LibreOffice.

---

## 6. Layer 1 — Unified Span Extraction

### Responsibility
Extract raw text blocks from the source document into a unified `Span` dataclass, regardless of format. Every downstream component works with `Span` objects.

### The Span Dataclass (Canonical Definition)

```python
@dataclass
class Span:
    # Content
    text:        str            # raw text content of this block
    word_count:  int            # len(text.split())

    # Typography
    font_size:   float          # in points. 0.0 if not available (e.g. HTML)
    is_bold:     bool           # font weight > 600 or bold flag set
    is_italic:   bool           # italic flag
    is_caps:     bool           # text == text.upper() and text.isalpha()
    font_name:   str            # font family name, empty string if unavailable

    # Geometry (all in points, origin top-left)
    bbox:          tuple[float,float,float,float]  # (x0, y0, x1, y1)
    space_above:   float        # vertical gap above this span (pts)
    space_below:   float        # vertical gap below this span (pts)
    line_height:   float        # bbox height

    # Location
    page:          int          # 1-based physical page number

    # Pre-computed signals
    has_numbering: bool         # regex matched a numbering pattern
    numbering_str: str          # matched prefix e.g. "1.2.3 "
    is_standalone: bool         # occupies its own line / block (not inline)

    # Source metadata
    source_format: str          # which parser produced this span

    # Filled by classifier (Layer 3B)
    heading_score:  float = 0.0    # 0.0 = body text, 1.0 = definite heading
    assigned_level: int   = 0      # 0 = unassigned, 1-9 = heading level
```

### Span Extraction per Format

**PDF (via pdfplumber or pymupdf):**
Each text block in the PDF dictionary output becomes one Span. The `bbox` is available directly. `space_above` is computed as `this_span.bbox[1] - prev_span.bbox[3]` for spans on the same page. Reset `prev_bottom` to 0 at each page boundary.

**DOCX (via python-docx):**
Each paragraph becomes one Span. Font size from `paragraph.runs[0].font.size` (converted from EMU to points: divide by 12700). `is_bold` from `paragraph.runs[0].font.bold`. Geometry is not available from python-docx — set `bbox = (0, 0, 0, 0)` and `space_above = 0.0`. This is acceptable because DOCX uses the fast path via style names, not font metrics.

**HTML (via BeautifulSoup):**
Each block-level element (p, div, li, etc.) becomes one Span. Font size not reliably available from HTML — set to 0.0. `is_bold` from inline style `font-weight: bold` or `<strong>` wrapper. No geometry available.

**PPTX (via python-pptx):**
Each text frame on each slide becomes one Span. Font size from `run.font.size`. Geometry from `shape.left, shape.top, shape.width, shape.height` (convert EMU to points).

### Numbering Pattern Regex

```python
NUMBERING_RE = re.compile(
    r"^("
    r"(?:\d+\.){1,5}\d*\.?\s+"     # 1.  1.1  1.1.1  1.1.1.1
    r"|[A-Z]\.\s+"                  # A.  B.
    r"|\([a-zA-Z\d]+\)\s+"         # (a)  (1)  (A)
    r"|(?:Chapter|Section|Part|Appendix|Article)\s+[\dA-Z]+"  # Chapter 3
    r")",
    re.IGNORECASE,
)
```

When this regex matches the start of `span.text`, set `has_numbering = True` and `numbering_str` = the matched prefix.

---

## 7. Layer 2 — Routing: Fast Path vs Slow Path

### Responsibility
Inspect the extracted spans and available document metadata to decide whether the document has reliable structural signals (fast path) or requires heuristic analysis (slow path).

### Decision Logic (Pseudocode)

```
function route(document, spans) → "fast" | "slow":

    # Signal 1: PDF with bookmarks/outline
    if document.format == PDF:
        if document.has_outline() and len(document.outline) > 2:
            return "fast"

    # Signal 2: DOCX with heading styles
    if document.format == DOCX:
        heading_paragraphs = count paragraphs with style.name matching "Heading \d+"
        if heading_paragraphs >= 2:
            return "fast"

    # Signal 3: HTML/Markdown with heading tags
    if document.format in (HTML, MARKDOWN):
        heading_spans = count spans where tag in (h1, h2, h3, h4, h5, h6)
        if heading_spans >= 2:
            return "fast"

    # Signal 4: EPUB (always HTML internally)
    if document.format == EPUB:
        return "fast"   # EPUB spine uses heading tags

    # Signal 5: PPTX (always fast — slide titles are deterministic)
    if document.format == PPTX:
        return "fast"

    # No reliable signals found
    return "slow"
```

### Mixed Path
Some documents partially have signals (e.g. a PDF with a partial outline covering only the first half). When detected, log a warning and use fast path for the covered range and slow path for the uncovered range. Set `extraction_path = "mixed"` in the output.

---

## 8. Layer 3A — Fast Path: Deterministic Tree Construction

### Responsibility
Build the heading list directly from structural signals with `confidence = 1.0`.

### Per-Format Logic

#### PDF Fast Path (Bookmark/Outline based)
```
Input: PDF TOC entries as list of [level, title, page_1based]

For each TOC entry (level, title, page):
    1. Create DocNode(title=strip_numbering(title), confidence=1.0)
    2. Set node.pages.physical_start = page
    3. Set node.pages.physical_end = (next entry at same or higher level).page - 1
       OR total_pages if no such entry exists
    4. Pop stack back to entries with depth < level
    5. If stack non-empty: stack.top().add_child(node)
       Else: tree.nodes.append(node)
    6. Push (level, node) onto stack
```

**Important edge case**: PDF page numbers in the outline are 1-based physical page numbers. They may not match printed page numbers (logical). Store both: `physical_start` from outline, `logical_start` from the page's own text (detected by scanning the bottom/top margin of the page for a number).

#### DOCX Fast Path (Paragraph Style based)
```
Input: list of paragraphs with style names

HEADING_STYLE_TO_DEPTH = {
    "heading 1": 1, "heading 2": 2, ..., "heading 9": 9,
    "title": 1,
    "subtitle": 2,
}

For each paragraph:
    style_depth = HEADING_STYLE_TO_DEPTH.get(paragraph.style.name.lower())

    if style_depth is not None:
        Create DocNode(title=strip_numbering(paragraph.text), confidence=1.0)
        Pop stack to depth < style_depth
        Attach to parent or tree.nodes
        Push to stack
    else:
        # Body paragraph — accumulate in text_buffer for current node
        text_buffer.append(paragraph.text)
        # Flush text_buffer to current_node.text when next heading is found
```

**Page tracking in DOCX**: python-docx does not expose rendered page numbers. Approximate by counting `w:pageBreak` and `w:lastRenderedPageBreak` XML elements as you iterate paragraphs. Increment `physical_page` counter on each detected break.

#### HTML/Markdown Fast Path (Heading Tag based)
```
Input: BeautifulSoup parsed HTML element stream

For each element in document order:
    if element.tag in (h1, h2, h3, h4, h5, h6):
        depth = int(element.tag[1])   # h2 → 2
        Create DocNode(title=strip_numbering(element.text), confidence=1.0)
        Pop stack to depth < depth
        Attach to parent or tree.nodes
        Push to stack
    elif element.tag in (p, div, ul, ol, table, pre, code, blockquote):
        Accumulate text into text_buffer for current node
        Extract images from this element
```

**Table handling**: When a `<table>` element is encountered, convert it to a markdown table string (using a helper function) and append to `text_buffer`. Do not create a child node for tables.

#### EPUB Fast Path
EPUB is a ZIP archive containing HTML files and a spine (reading order manifest). Process:
1. Unzip EPUB to temp directory
2. Parse `content.opf` to get spine order (list of HTML file paths in reading order)
3. For each HTML file in spine order, run the HTML fast path
4. Merge trees: top-level sections from each HTML file become children of a root node named after the EPUB title
5. Physical page numbers: EPUB has no fixed pages. Assign sequential "page" numbers by treating each HTML file as one page.

#### PPTX Fast Path
```
Input: python-pptx Presentation object

Create root node: title = presentation.core_properties.title or filename
For each slide (index i, 0-based):
    physical_page = i + 1
    slide_title = get_title_shape(slide).text or f"Slide {i+1}"
    body_text = concatenate all non-title text frames

    Create DocNode(
        title = slide_title,
        text  = body_text,
        pages = PageRange(physical_start=i+1, physical_end=i+1),
        confidence = 1.0
    )

    # Check if this is a section divider (title-only slide, no body text)
    if is_section_divider(slide):
        node.node_type = NodeType.PARENT   # will have subsequent slides as children
        Push as section header in stack
    else:
        Attach as child of current section header (if any) or directly to root
```

**Section divider detection**: A slide is a section divider if it has a title shape, the title text is short (< 8 words), and all other text frames are empty or contain only brief subtitles.

**Image extraction from slides**: Iterate `slide.shapes`, find shapes with `shape.shape_type == MSO_SHAPE_TYPE.PICTURE`, save each picture to `{output_dir}/{stem}_images/slide{n}_img{m}.{ext}`.

---

## 9. Layer 3B — Slow Path: Heuristic Heading Detection

### Responsibility
Detect headings in untagged or visually-formatted documents (primarily untagged PDFs) using three complementary signals: font-metric clustering, numbering pattern detection, and a binary heading classifier.

### Sub-component 1: Font-Metric Clustering

**Goal**: For a given document, identify which font configurations correspond to headings vs body text.

**Algorithm**:
```
Input: list[Span] for entire document

Step 1: Build feature matrix
    For each span, create feature vector:
        [font_size, is_bold (0/1), is_caps (0/1)]

Step 2: Normalize font_size
    font_size_normalized = (font_size - min_font_size) / (max_font_size - min_font_size)
    # This makes font_size relative to document, not absolute

Step 3: KMeans clustering
    Try k = 2, 3, 4, 5 clusters
    Choose k using elbow method (inertia drop) or silhouette score
    Default k = 4 if elbow is ambiguous

Step 4: Rank clusters by prominence
    prominence_score(cluster) = (
        mean_font_size_normalized * 0.6 +
        bold_fraction * 0.3 +
        caps_fraction * 0.1
    )
    Sort clusters by prominence_score descending

Step 5: Assign heading level candidates
    Cluster rank 0 (highest prominence) → candidate level 1 (H1)
    Cluster rank 1                      → candidate level 2 (H2)
    Cluster rank 2                      → candidate level 3 (H3)
    Cluster rank 3+                     → body text (not heading)

    Exception: a cluster with mean_font_size < document_body_font_size
    can never be a heading regardless of rank.

Step 6: Assign heading_score to each span
    For spans in heading clusters: heading_score = prominence_score (0.5–1.0)
    For spans in body cluster: heading_score = 0.0–0.3

Output: dict mapping span → (candidate_level, initial_heading_score)
```

**Important caveat**: Clustering is per-document. The same font size (e.g. 14pt) may be a heading in one document and body text in another. Never use absolute font size thresholds.

### Sub-component 2: Numbering Pattern Detection

**Goal**: Use regex + state machine to detect explicit section numbering. This signal is high-precision when it fires.

**State Machine**:
```
State: current_numbering_context
    - tracks last seen numbering pattern
    - e.g. after seeing "2.3", the next expected patterns are:
      "2.4" (sibling), "2.3.1" (child), "3" (parent sibling)

For each span where has_numbering = True:
    parsed = parse_numbering(span.numbering_str)
    # e.g. "1.2.3 " → [1, 2, 3]

    if is_consistent_with_context(parsed, state):
        span.heading_score = max(span.heading_score, 0.95)
        span.assigned_level = len(parsed)   # depth = number of parts
        Update state
    else:
        # Numbering exists but doesn't fit sequence — may be figure numbers,
        # list items, etc. Do not elevate heading_score.
        pass

Consistency rules:
    [1, 2, 3] after [1, 2, 2]: consistent (increment last part)
    [1, 3] after [1, 2, 4]: consistent (skipped — allowed, not penalised)
    [2] after [1, 2, 4]: consistent (popped back to level 1)
    [1, 2, 3] after [3]: INCONSISTENT (jumped from level 1 to level 3 start)
```

**Numbering parser**:
```python
def parse_numbering(numbering_str: str) -> list[int] | None:
    """
    "1.2.3 "    → [1, 2, 3]
    "Chapter 3" → [3]
    "A."        → [1]   (A=1, B=2, etc.)
    "(b)"       → [2]
    Returns None if pattern is not parseable as hierarchy.
    """
```

### Sub-component 3: Heading Binary Classifier

**Goal**: For each span, predict P(span is a heading) using a 12-feature vector. This is the gating decision — spans above threshold go to tree construction, spans below become body text.

**Feature Vector** (12 features, all numeric):

| # | Feature | Computation | Rationale |
|---|---------|-------------|-----------|
| 1 | `font_size_ratio` | `span.font_size / document_median_font_size` | Relative size, not absolute |
| 2 | `is_bold` | 0 or 1 | Direct signal |
| 3 | `is_caps` | 0 or 1 | Common in headings |
| 4 | `word_count` | `len(span.text.split())` | Headings are short (< 15 words) |
| 5 | `ends_with_punctuation` | 1 if last char in `.!?;:,` | Headings rarely end with punctuation |
| 6 | `space_above_ratio` | `span.space_above / document_median_line_height` | Headings have more space above |
| 7 | `space_below_ratio` | `span.space_below / document_median_line_height` | Headings have more space below |
| 8 | `is_standalone_block` | 1 if span occupies its full line width | Headings fill their line |
| 9 | `numbering_match` | 1 if `has_numbering = True` | Strong signal |
| 10 | `cluster_rank` | Cluster prominence rank (0=highest) | From sub-component 1 |
| 11 | `position_on_page` | `span.bbox[1] / page_height` | Headings often near top of section |
| 12 | `char_count` | `len(span.text)` | Headings are typically < 120 chars |

**Classifier choice**: LightGBM (`lightgbm.LGBMClassifier`). Reasons:
- Fast inference on CPU (microseconds per prediction)
- No GPU required
- Handles small feature vectors efficiently
- Supports `predict_proba` for confidence scores
- Serialisable to a small `.pkl` or `.txt` file

**Training data**: DocHieNet dataset (EMNLP 2024) + manually annotated corpus. Target: 500–1000 annotated spans across diverse document types.

**Threshold**: Default `heading_threshold = 0.65`. Spans with `heading_score >= threshold` proceed to tree construction. Configurable per document type.

**Fallback (no trained model)**: Use rule-based scoring:
```python
def rule_based_heading_score(span, doc_median_size) -> float:
    score = 0.0
    if span.font_size > doc_median_size * 1.1:  score += 0.3
    if span.is_bold:                             score += 0.2
    if span.word_count < 12:                     score += 0.15
    if not span.text.endswith(('.', '!', '?')):  score += 0.1
    if span.space_above > doc_median_line_height: score += 0.15
    if span.has_numbering:                       score += 0.2
    return min(score, 1.0)
```

---

## 10. Layer 4 — Fault-Tolerant Tree Builder

### Responsibility
Given an ordered list of detected headings (from either fast or slow path), construct the `DocNode` hierarchy. Must handle imperfect input without crashing.

### Core Algorithm: Stack-based Tree Construction with Gap Tolerance

```
Input: ordered list of HeadingCandidate(level, title, page, confidence)

stack: list of (level, DocNode)   # stack of open nodes

For each candidate in order:

    # CASE 1: Normal descent (level > stack.top.level)
    # New node is a child of the current top
    if stack is empty or candidate.level > stack[-1].level:
        node = DocNode(title, confidence, pages)
        if stack:
            stack[-1][1].add_child(node)
        else:
            tree.nodes.append(node)
        stack.append((candidate.level, node))

    # CASE 2: Sibling (level == stack.top.level)
    # Pop current top, attach to same parent
    elif candidate.level == stack[-1].level:
        stack.pop()
        node = DocNode(title, confidence, pages)
        if stack:
            stack[-1][1].add_child(node)
        else:
            tree.nodes.append(node)
        stack.append((candidate.level, node))

    # CASE 3: Ascent (level < stack.top.level)
    # Pop until we find the correct parent level
    else:
        while stack and stack[-1].level >= candidate.level:
            stack.pop()
        node = DocNode(title, confidence, pages)
        if stack:
            stack[-1][1].add_child(node)
        else:
            tree.nodes.append(node)
        stack.append((candidate.level, node))

    # CASE 4: GAP DETECTION
    # Slow path only: if candidate.level > stack.top.level + 1,
    # there is a gap (e.g. jumped from H1 to H3 with no H2)
    if slow_path and candidate.level > stack[-1].level + 1:
        # Insert phantom nodes to fill the gap
        for phantom_level in range(stack[-1].level + 1, candidate.level):
            phantom = DocNode(
                title="[implied section]",
                confidence=0.0,         # zero confidence — never real
                is_phantom=True,        # flagged in output
                pages=candidate.pages,  # inherits same page
            )
            stack[-1][1].add_child(phantom)
            stack.append((phantom_level, phantom))
```

### Phantom Nodes
Phantom nodes are inserted when the heading sequence has gaps (e.g. H1 → H3). They:
- Have `confidence = 0.0`
- Have `title = "[implied section]"`
- Have `is_phantom = True` (additional field, omitted from production output by default)
- Are included in the `id` sequence but clearly marked
- Can be stripped in post-processing with `tree.remove_phantoms()`

### Page Range Resolution
After tree construction, each node's `pages.physical_end` must be set:
```
For each node in reverse pre-order:
    if node.is_leaf():
        node.pages.physical_end = (
            next_sibling.pages.physical_start - 1
            OR parent.pages.physical_end
            OR total_pages
        )
    else:
        node.pages.physical_end = max(
            child.pages.physical_end for child in node.children
        )
```

---

## 11. Layer 5 — ID Assignment & Tree Finalisation

### Responsibility
All ID assignment happens here, after the tree structure is finalised. No parser touches IDs.

### Algorithm: `DocumentTree.finalise()`

```
Step 1: Assign section_ids
    _walk(tree.nodes, prefix="")

    function _walk(nodes, prefix):
        for i, node in enumerate(nodes, start=1):
            node.section_id = f"{prefix}{i}" if prefix else str(i)
            node.depth = node.section_id.count(".") + 1
            _walk(node.children, f"{node.section_id}.")

Step 2: Assign flat sequential IDs
    counter = 0
    for node in pre_order_traversal(tree):
        counter += 1
        node.id = f"{counter:04d}"

Step 3: Recompute node_type
    for node in pre_order_traversal(tree):
        if node._parent is None:
            node.node_type = NodeType.ROOT
        elif node.children:
            node.node_type = NodeType.PARENT
        else:
            node.node_type = NodeType.CHILD
```

### Pre-order Traversal
```python
def pre_order(nodes: list[DocNode]) -> Iterator[DocNode]:
    for node in nodes:
        yield node
        yield from pre_order(node.children)
```

---

## 12. Layer 6 — Content & Media Extraction

### Responsibility
Populate `node.text`, `node.images`, and refine `node.pages` after the tree skeleton is built.

### Text Population Strategy

The key rule: **`node.text` contains only the prose directly under that heading, before the first child heading begins.**

```
For the ordered list of all spans in the document:

current_node = None
text_buffer = []

For each span in document order:

    heading_node = tree.get_node_at_page_and_position(span.page, span.bbox)

    if span is a heading (is in headings list):
        # Flush accumulated text to previous node
        if current_node and text_buffer:
            current_node.text = join_and_clean(text_buffer)
            text_buffer.clear()
        current_node = heading_node

    elif current_node is not None:
        # Check: is this span still "above" the first child heading?
        # i.e., does it come before current_node.children[0] in document order?
        if before_first_child(span, current_node):
            text_buffer.append(span.text)
        # else: this span belongs to a child node's text range — skip
```

### Table-to-Markdown Conversion

When a table element (HTML `<table>`, DOCX table, PDF table detected by pdfplumber) is encountered:

```python
def table_to_markdown(table_data: list[list[str]]) -> str:
    """
    table_data: list of rows, each row is list of cell strings
    First row treated as header.
    """
    if not table_data:
        return ""
    header = table_data[0]
    separator = ["-" * max(3, len(h)) for h in header]
    rows = table_data[1:]

    lines = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(separator) + " |")
    for row in rows:
        # Pad short rows
        padded = row + [""] * (len(header) - len(row))
        lines.append("| " + " | ".join(padded[:len(header)]) + " |")
    return "\n".join(lines)
```

Append the result to `text_buffer` inline where the table appears.

### Image Extraction

**PDF images** (via pymupdf):
```python
for page_num, page in enumerate(doc, start=1):
    image_list = page.get_images(full=True)
    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        img_bytes = base_image["image"]
        img_ext = base_image["ext"]
        img_path = output_dir / f"p{page_num}_img{img_index+1}.{img_ext}"
        img_path.write_bytes(img_bytes)

        # Find caption: look for text block immediately below image bbox
        caption = find_caption_near_image(page, img_bbox)
        label   = find_figure_label(caption)   # regex for "Figure X.Y"

        # Assign to the node whose page range contains page_num
        node = tree.get_node_containing_page(page_num)
        if node:
            node.images.append(ImageRef(
                path    = str(img_path),
                label   = label,
                caption = caption,
            ))
```

**Caption detection logic**:
```
1. Get bounding box of image
2. Search for text blocks within 50pts below the image bottom edge
3. If found text matches FIGURE_LABEL_RE (r"fig(?:ure)?\.?\s*\d+"), it's a label
4. Return first such text block as caption
```

**DOCX images** (via python-docx):
```python
for rel in doc.part.rels.values():
    if "image" in rel.reltype:
        img_data = rel.target_part.blob
        img_ext  = rel.target_part.content_type.split("/")[-1]
        # Save and assign to node based on document order position
```

**HTML images**: Already handled during span extraction — `<img src>` paths are preserved directly. If `src` is a relative path, resolve it relative to the HTML file's directory.

**PPTX images**: Extracted from `shape.image.blob` for shapes with type `MSO_SHAPE_TYPE.PICTURE`.

### Caption and Label Regex

```python
FIGURE_LABEL_RE = re.compile(
    r"(fig(?:ure)?\.?\s*\d+(?:\.\d+)?)",
    re.IGNORECASE
)

TABLE_LABEL_RE = re.compile(
    r"(tab(?:le)?\.?\s*\d+(?:\.\d+)?)",
    re.IGNORECASE
)
```

---

## 13. Layer 7 — Serialization (JSON + Markdown)

### JSON Serializer

```python
def to_json(tree: DocumentTree, indent: int = 2) -> str:
    return json.dumps(tree.to_dict(), indent=indent, ensure_ascii=False)
```

`DocumentTree.to_dict()` recursively calls `DocNode.to_dict()` which calls `DocNode.to_dict()` on each child. This produces the nested JSON structure.

**Serialisation rules**:
- `confidence` rounded to 4 decimal places
- `null` for missing logical page numbers (not omitted)
- Empty `children` serialised as `[]`, not omitted
- Empty `images` serialised as `[]`, not omitted
- Empty `text` serialised as `""`, not omitted

### Markdown Serializer

```python
def to_markdown(tree: DocumentTree) -> str:
    parts = [_frontmatter(tree), ""]
    for node in tree.nodes:
        parts.extend(_node_to_md(node))
    return "\n".join(parts)

def _node_to_md(node: DocNode) -> list[str]:
    lines = []
    hashes = "#" * min(node.depth, 6)
    lines.append(f"{hashes} {node.section_id} · {node.title}")
    lines.append(
        f"<!-- id:{node.id} pages:{node.pages.physical_start}-"
        f"{node.pages.physical_end} confidence:{node.confidence:.2f} "
        f"type:{node.node_type.value} -->"
    )
    lines.append("")
    if node.text.strip():
        lines.append(node.text.strip())
        lines.append("")
    for img in node.images:
        if img.path:
            lines.append(f"![{img.label or img.caption or 'image'}]({img.path})")
            if img.caption:
                lines.append(f"*{img.caption}*")
            lines.append("")
    for child in node.children:
        lines.extend(_node_to_md(child))
    return lines
```

---

## 14. Format-Specific Parser Details

### Summary Table

| Format | Library | Path | Heading Signal | Page Numbers | Images |
|--------|---------|------|----------------|-------------|--------|
| PDF (tagged) | pymupdf | Fast | PDF outline/bookmarks | From outline | Extract via xref |
| PDF (untagged) | pdfplumber + pymupdf | Slow | Font clustering + classifier | Physical count | Extract via xref |
| PDF (scanned) | pymupdf + Tesseract | Slow | OCR text → font heuristics | Physical count | Whole page is image |
| DOCX | python-docx | Fast | Paragraph.style.name | Approximate via page breaks | Via part.rels |
| HTML | beautifulsoup4 | Fast | h1-h6 tags | N/A (always 1) | img src= |
| Markdown | markdown + beautifulsoup4 | Fast | ATX/Setext headings | N/A | image links |
| EPUB | ebooklib + beautifulsoup4 | Fast | h1-h6 in spine HTML | File index | img src= |
| PPTX | python-pptx | Fast | Slide title shapes | Slide index | Shape images |
| Image | Tesseract/PaddleOCR | Slow | OCR → font heuristics | Physical count | Whole image |

### EPUB-Specific Notes
1. EPUB is a ZIP file. Use `ebooklib` to extract the spine (reading order).
2. Each spine item is an HTML file. Process in spine order, not alphabetical order.
3. The `toc.ncx` or `nav.xhtml` file provides the EPUB's own TOC — use this as the fast-path signal if present (analogous to PDF bookmarks).
4. Assign physical page numbers as: `page = spine_index + 1`. EPUB has no fixed pagination.
5. Internal links (`href="#section-id"`) can be used to correlate TOC entries with content — advanced feature, Phase 2.

### Scanned PDF / Image Notes
1. Scanned PDFs and image files require OCR as a pre-processing step.
2. Recommended: PaddleOCR (higher accuracy on mixed-language docs) or Tesseract (widely available).
3. OCR outputs text + bounding boxes. Bounding boxes feed directly into the `Span` dataclass.
4. All nodes from OCR output have `confidence` reduced by `0.1` as a baseline OCR uncertainty penalty.
5. Gate behind explicit `--ocr` CLI flag. Do not run OCR silently.

---

## 15. Data Contracts & Interfaces

### Parser Interface (Abstract Base)

```python
class BaseParser(ABC):
    def __init__(self, file_path: Path): ...

    @abstractmethod
    def parse(self) -> DocumentTree:
        """
        Must:
        - Set source_file, source_format, total_pages on tree
        - Build DocNode tree (no IDs, no section_ids)
        - Call tree.finalise() before returning
        - Return the DocumentTree
        Must NOT:
        - Assign node.id or node.section_id
        - Call serializers
        - Write any files
        """
```

### DocumentTree Public API

```python
class DocumentTree:
    def finalise(self) -> None: ...              # assign IDs, recompute types
    def get_by_id(self, id: str) -> DocNode: ... # lookup by flat id
    def get_by_section_id(self, sid: str) -> DocNode: ...
    def flat_list(self) -> list[DocNode]: ...    # pre-order flat list
    def to_dict(self) -> dict: ...               # for JSON serialization
    def remove_phantoms(self) -> None: ...       # strip phantom nodes
```

### DocNode Public API

```python
class DocNode:
    def add_child(self, node: DocNode) -> None: ...
    def is_leaf(self) -> bool: ...
    def iter_all(self) -> Iterator[DocNode]: ...  # pre-order self + descendants
    def recompute_type(self) -> None: ...
    def to_dict(self) -> dict: ...
```

---

## 16. Algorithms Reference

### A. Strip Numbering from Title

```python
STRIP_NUMBERING_RE = re.compile(
    r"^("
    r"(?:\d+\.){1,5}\d*\.?\s+"     # 1.2.3
    r"|[A-Z]\.\s+"                  # A.
    r"|\([a-zA-Z\d]+\)\s+"         # (a)
    r"|(?:Chapter|Section|Part|Appendix)\s+[\dA-Z]+[:\.\s]+"
    r")",
    re.IGNORECASE,
)

def strip_numbering(title: str) -> str:
    return STRIP_NUMBERING_RE.sub("", title).strip()
```

Note: preserve the original numbering in `span.numbering_str` for the numbering state machine. Only the displayed `node.title` is stripped.

### B. Document Median Font Size

```python
def compute_doc_stats(spans: list[Span]) -> dict:
    sizes = [s.font_size for s in spans if s.font_size > 0]
    line_heights = [s.line_height for s in spans if s.line_height > 0]
    return {
        "median_font_size":   statistics.median(sizes) if sizes else 12.0,
        "median_line_height": statistics.median(line_heights) if line_heights else 14.0,
        "max_font_size":      max(sizes) if sizes else 12.0,
        "min_font_size":      min(sizes) if sizes else 12.0,
    }
```

### C. Logical Page Number Detection

```python
def detect_logical_page_numbers(page_texts: dict[int, str]) -> dict[int, str | None]:
    """
    For each physical page, try to find the printed page number.
    Checks top 3 lines and bottom 3 lines of each page.
    Returns dict: physical_page → logical_page_string (or None)
    """
    ROMAN_RE = re.compile(r"^(x{0,3})(ix|iv|v?i{0,3})$", re.IGNORECASE)
    PAGE_NUM_RE = re.compile(r"^\d+$")

    result = {}
    for phys, text in page_texts.items():
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        candidates = lines[:3] + lines[-3:] if len(lines) > 6 else lines
        for candidate in candidates:
            if PAGE_NUM_RE.match(candidate):
                result[phys] = candidate
                break
            if ROMAN_RE.match(candidate):
                result[phys] = candidate.lower()
                break
        else:
            result[phys] = None
    return result
```

### D. Find Node Containing Page

```python
def get_node_containing_page(tree: DocumentTree, page: int) -> DocNode | None:
    """
    Find the deepest node whose page range contains the given physical page.
    Used to assign images and text blocks to the correct node.
    """
    best = None
    best_depth = -1
    for node in tree.flat_list():
        if node.pages.physical_start <= page <= node.pages.physical_end:
            if node.depth > best_depth:
                best = node
                best_depth = node.depth
    return best
```

---

## 17. Configuration & Extensibility

### Config Dataclass

```python
@dataclass
class DocStructConfig:
    # Slow path heading detection
    heading_threshold:    float = 0.65    # classifier cutoff
    max_heading_words:    int   = 20      # spans with more words not considered headings
    font_cluster_k_range: tuple = (2, 6)  # min/max k for KMeans

    # OCR
    ocr_enabled:    bool  = False         # must be explicit opt-in
    ocr_engine:     str   = "tesseract"   # "tesseract" | "paddleocr"
    ocr_language:   str   = "eng"

    # Output
    output_images:  bool  = True          # extract and save images
    image_format:   str   = "png"         # output format for extracted images
    include_phantoms: bool = False        # include phantom nodes in output

    # Performance
    max_pages:   int | None = None        # truncate after N pages (None = all)
    timeout_sec: int | None = 60          # per-document timeout

    # Routing
    fast_path_min_headings: int = 2       # min headings to qualify for fast path
```

### Extensibility Points
- **Custom parsers**: Subclass `BaseParser`, implement `parse()`, register in `FORMAT_MAP`
- **Custom classifiers**: Pass a classifier object implementing `.predict_proba(features)` to `SlowPathProcessor`
- **Custom serializers**: Implement `serialize(tree: DocumentTree) -> str` and pass to pipeline
- **Post-processors**: Chain callables `(DocumentTree) → DocumentTree` after `finalise()`

---

## 18. Error Handling Strategy

### Principles
1. **Always return a tree.** Never raise an exception to the caller unless the file cannot be opened at all. Partial extraction with low confidence is always preferable to failure.
2. **Degrade gracefully.** If the slow path classifier fails, fall back to rule-based scoring. If rule-based scoring fails, return a flat tree with all text in one root node.
3. **Log everything.** Use Python `logging` at DEBUG level for span extraction details, WARNING for degradation events, ERROR for unrecoverable parse failures.

### Degradation Ladder

```
1. Ideal:          Full tree from fast path                     confidence = 1.0
2. Degraded:       Full tree from slow path (classifier)        confidence = 0.65–1.0
3. Further:        Full tree from rule-based heuristics         confidence = 0.3–0.65
4. Minimal:        Flat tree — all text under one root node     confidence = 0.0
5. Empty:          Empty tree with error metadata               (file could not be read)
```

### Specific Error Cases

| Condition | Handling |
|-----------|---------|
| File not found | Raise `FileNotFoundError` immediately |
| Corrupt PDF | Catch pymupdf/pdfplumber exception, return minimal tree with error field |
| Empty document | Return tree with single root node, empty text |
| No headings detected | Return flat tree, all text under root, confidence=0.3 |
| Heading sequence has gaps | Insert phantom nodes, log WARNING |
| Image extraction fails | Log WARNING, continue, leave images=[] for that node |
| OCR not available | Raise `ImportError` with install instructions |
| Timeout | Return partial tree with `timed_out=True` in metadata |

---

## 19. Testing Strategy

### Unit Tests

**Schema tests** (`tests/test_schema.py`):
- `test_finalise_assigns_sequential_ids()`: 3-level tree, verify IDs are 0001/0002/0003...
- `test_section_ids_correct()`: verify `1`, `1.1`, `1.1.1`, `1.2` for a known tree shape
- `test_node_type_computed_correctly()`: root/parent/child assignment
- `test_get_by_id()` and `test_get_by_section_id()`
- `test_flat_list_preorder()`: verify traversal order

**Serializer tests** (`tests/test_serializers.py`):
- `test_json_roundtrip()`: serialize then deserialize, compare
- `test_markdown_heading_levels()`: verify `##` for depth=2
- `test_markdown_frontmatter_present()`

**Parser tests** (one per format, `tests/test_parsers/`):
- Use small real fixture files (committed to repo under `tests/fixtures/`)
- At minimum: one PDF with bookmarks, one DOCX with heading styles, one HTML
- Verify: correct number of top-level nodes, correct nesting of children, non-empty text on leaf nodes

**Algorithm tests** (`tests/test_algorithms.py`):
- `test_strip_numbering()`: "1.2.3 Introduction" → "Introduction"
- `test_numbering_state_machine()`: sequence [1], [1.1], [1.2], [2] is consistent
- `test_phantom_node_insertion()`: H1 → H3 gap inserts one phantom H2
- `test_page_range_resolution()`: verify physical_end is correctly computed

### Integration Tests

- `test_pdf_end_to_end()`: real PDF → JSON output, assert schema validity
- `test_docx_end_to_end()`: real DOCX → JSON + Markdown output
- `test_markdown_end_to_end()`: README-style markdown → tree

### Evaluation Metrics (for benchmark)

```python
def tree_edit_distance(gold: DocumentTree, pred: DocumentTree) -> float:
    """Normalised tree edit distance (0.0 = identical, 1.0 = completely different)"""

def node_f1(gold: DocumentTree, pred: DocumentTree) -> dict:
    """Precision, recall, F1 on heading detection (title match)"""

def level_accuracy(gold: DocumentTree, pred: DocumentTree) -> float:
    """Fraction of correctly detected headings with correct depth level"""

def section_id_exact_match(gold: DocumentTree, pred: DocumentTree) -> float:
    """Fraction of nodes with exactly correct section_id"""
```

---

## 20. Project Structure

```
docstruct/
├── __init__.py                  # version, public API exports
├── pipeline.py                  # DocStructPipeline main entry point
│
├── core/
│   ├── __init__.py
│   ├── schema.py                # DocNode, DocumentTree, Span, ImageRef, PageRange
│   └── config.py                # DocStructConfig dataclass
│
├── parsers/
│   ├── __init__.py
│   ├── base.py                  # BaseParser abstract class
│   ├── pdf_parser.py            # PdfParser (fast + slow path)
│   ├── docx_parser.py           # DocxParser
│   ├── html_parser.py           # HtmlParser + MarkdownParser
│   ├── epub_parser.py           # EpubParser
│   ├── pptx_parser.py           # PptxParser
│   └── image_parser.py          # ImageParser (OCR gate)
│
├── extraction/
│   ├── __init__.py
│   ├── span_extractor.py        # Span extraction per format
│   ├── router.py                # Fast/slow path routing logic
│   ├── fast_path.py             # Deterministic tree construction
│   ├── slow_path.py             # Heuristic pipeline coordinator
│   ├── font_clustering.py       # KMeans font-metric clustering
│   ├── numbering_detector.py    # Regex + state machine
│   ├── heading_classifier.py    # LightGBM classifier wrapper + rule-based fallback
│   └── tree_builder.py          # Fault-tolerant stack-based tree construction
│
├── content/
│   ├── __init__.py
│   ├── text_populator.py        # Populate node.text from spans
│   ├── image_extractor.py       # Extract images, detect captions/labels
│   ├── table_converter.py       # Convert tables to markdown
│   └── page_resolver.py        # Physical + logical page number resolution
│
├── serializers/
│   ├── __init__.py
│   ├── json_serializer.py       # to_json(), save_json()
│   └── markdown_serializer.py   # to_markdown(), save_markdown()
│
├── models/
│   └── heading_classifier.pkl   # Pre-trained LightGBM model (if distributing)
│
├── cli.py                       # Command-line interface
│
└── tests/
    ├── fixtures/                # Small real document samples per format
    ├── test_schema.py
    ├── test_serializers.py
    ├── test_algorithms.py
    └── test_parsers/
        ├── test_pdf_parser.py
        ├── test_docx_parser.py
        ├── test_html_parser.py
        ├── test_epub_parser.py
        └── test_pptx_parser.py
```

---

## 21. Dependency Matrix

| Package | Version | Used For | Required / Optional |
|---------|---------|----------|-------------------|
| `pdfplumber` | >=0.10 | PDF text + table extraction | Required for PDF |
| `pymupdf` (fitz) | >=1.23 | PDF images + outline + fast text | Required for PDF |
| `python-docx` | >=1.0 | DOCX parsing | Required for DOCX |
| `beautifulsoup4` | >=4.12 | HTML/Markdown parsing | Required for HTML/MD |
| `markdown` | >=3.5 | Markdown → HTML conversion | Required for MD |
| `ebooklib` | >=0.18 | EPUB spine + content | Required for EPUB |
| `python-pptx` | >=0.6 | PPTX slide + image extraction | Required for PPTX |
| `scikit-learn` | >=1.3 | KMeans clustering | Required for slow path |
| `lightgbm` | >=4.0 | Heading classifier | Required for slow path |
| `numpy` | >=1.24 | Feature vector operations | Required for slow path |
| `python-magic` | >=0.4 | MIME type detection | Optional (format fallback) |
| `pytesseract` | >=0.3 | OCR for scanned docs | Optional (--ocr flag) |
| `paddleocr` | >=2.7 | Higher-accuracy OCR | Optional (--ocr flag) |
| `lxml` | >=4.9 | HTML/XML parsing backend for BS4 | Optional (performance) |

---

## 22. Build Phases & Milestones

### Phase 1 — Core Schema + Fast Path (Target: 2–3 weeks)
**Goal**: Produce correct output for DOCX, HTML/Markdown, and PDF with bookmarks.

Deliverables:
- [ ] `core/schema.py` complete — all dataclasses, `finalise()`, traversal
- [ ] `serializers/json_serializer.py` — `to_json()`, `save_json()`
- [ ] `serializers/markdown_serializer.py` — `to_markdown()`, `save_markdown()`
- [ ] `parsers/docx_parser.py` — fast path via paragraph styles
- [ ] `parsers/html_parser.py` — fast path via heading tags
- [ ] `parsers/pdf_parser.py` — fast path via PDF outline only (slow path stub)
- [ ] `pipeline.py` — format detection + routing to parsers
- [ ] `cli.py` — basic CLI: `docstruct extract <file> --output-dir <dir>`
- [ ] Unit tests for schema, serializers, DOCX/HTML parsers

Success criterion: Run on 10 real documents (mix of DOCX + HTML + bookmarked PDFs), review JSON/Markdown output manually, all produce valid schema-conformant output.

### Phase 2 — Slow Path Classifier (Target: 3–4 weeks)
**Goal**: Produce reasonable output for untagged PDFs.

Deliverables:
- [ ] `extraction/span_extractor.py` — Span extraction from PDF via pymupdf
- [ ] `extraction/font_clustering.py` — KMeans on font metrics
- [ ] `extraction/numbering_detector.py` — regex + state machine
- [ ] `extraction/heading_classifier.py` — LightGBM + rule-based fallback
- [ ] `extraction/tree_builder.py` — fault-tolerant stack + phantom nodes
- [ ] Training data annotation (minimum 500 spans across 20 diverse PDFs)
- [ ] Model training + serialisation to `models/heading_classifier.pkl`
- [ ] Integration into `pdf_parser.py` slow path

Success criterion: On 10 untagged PDFs, manually review output. Target: heading detection precision > 0.80, tree structure "looks right" to a human reviewer.

### Phase 3 — Remaining Formats + Content Population (Target: 2 weeks)
**Goal**: EPUB, PPTX, image support; full text + image extraction.

Deliverables:
- [ ] `parsers/epub_parser.py`
- [ ] `parsers/pptx_parser.py`
- [ ] `parsers/image_parser.py` (OCR gate)
- [ ] `content/text_populator.py`
- [ ] `content/image_extractor.py`
- [ ] `content/table_converter.py`
- [ ] `content/page_resolver.py`

### Phase 4 — Evaluation + Benchmark (Target: 2–3 weeks)
**Goal**: Measure performance, build benchmark dataset, compare against baselines.

Deliverables:
- [ ] Annotate 30–50 documents per format for gold standard
- [ ] Implement evaluation metrics (tree-edit distance, node F1, level accuracy)
- [ ] Comparison against DocParser, Detect-Order-Construct, rule-based baseline
- [ ] Performance profiling (documents/second per format)
- [ ] README with quick-start, API docs, benchmark results

---

## 23. Known Hard Problems & Design Decisions

### Hard Problem 1: Heading vs Bold Body Text
**Problem**: Decorative pull-quotes, callout boxes, figure captions, "Note:", "Warning:" labels all look like headings by font metrics.  
**Decision**: Feature 5 (`ends_with_punctuation`) and feature 4 (`word_count`) are the most discriminative. A heading rarely ends with a period and rarely exceeds 15 words. Add a feature for "is preceded by a blank line AND followed by a blank line" — this is the strongest signal for decorative text which usually floats in the middle of content.

### Hard Problem 2: Multi-Column PDFs
**Problem**: pdfplumber extracts text left-to-right across the full page width, so column 2 text from row N gets mixed with column 1 text from row N+1.  
**Decision**: Detect two-column layout by checking if the median x-coordinate of text blocks clusters into two distinct groups (left half and right half). If two-column layout is detected, sort spans by: column (left before right), then by y within column. This is a pre-processing step before span extraction.

### Hard Problem 3: DOCX Page Numbers
**Problem**: python-docx does not expose rendered page numbers.  
**Decision**: Use `w:pageBreak` and `w:lastRenderedPageBreak` XML elements as approximate page break markers. Count these to maintain a `physical_page` counter. Document that DOCX page numbers are approximate, not exact.

### Hard Problem 4: Dewey ID vs Original Numbering
**Problem**: If the document says "Section 3.2" but our classifier assigns it as depth 4 in our tree, there's a conflict.  
**Decision**: Always reassign section_ids from scratch based on detected tree structure. Store original numbering in `span.numbering_str` (which is already on the Span). This is consistent and predictable. Users who need original numbering can read `span.numbering_str`.

### Hard Problem 5: Image Assignment to Nodes
**Problem**: An image on page 7 might belong to the section that starts on page 6 and ends on page 9. But page 7 might also be the start of a subsection. Which node gets the image?  
**Decision**: Assign to the **deepest** node whose page range contains the image's page. This is the most specific attribution. If the image's y-coordinate places it above the first child heading on that page, assign to the parent. Otherwise assign to the child.

### Design Decision: `extraction_path = "mixed"`
Some documents have PDF bookmarks that only cover sections 1–3, and sections 4–7 are untagged. In this case, run the fast path for the covered range and the slow path for the uncovered range. Set `extraction_path = "mixed"`. Confidence will be 1.0 for fast-path nodes and < 1.0 for slow-path nodes, allowing the caller to see which parts of the tree were extracted with certainty.

---

## 24. Prompt for Opus Implementation

> You are implementing **DocStruct**, a production-quality, open-source Python library for hierarchical document structure extraction. You have a comprehensive implementation plan available. Your job is to implement it faithfully, one module at a time.
>
> **System summary**: DocStruct takes a document file (PDF, DOCX, HTML, Markdown, EPUB, PPTX, or scanned image) and produces a hierarchical tree where every node represents a section. Each node has: a zero-padded sequential `id` (e.g. `"0003"`), a dotted hierarchical `section_id` (e.g. `"1.2.3"`), a `depth` integer, a `node_type` (`root`/`parent`/`child`), a `title`, `text` (prose directly under that heading before first child), `pages` (physical_start, physical_end, logical_start, logical_end), `confidence` (1.0 for deterministic paths, classifier score for heuristic paths), `images` (label + caption + path), and `children` (recursive list). Output is JSON and Markdown.
>
> **Non-negotiable rules**:
> 1. No LLMs in the extraction loop. No API calls. No internet access required.
> 2. `DocumentTree.finalise()` is the only place where `node.id` and `node.section_id` are assigned. Parsers never assign these.
> 3. `node.text` contains only prose directly under the heading, before the first child heading begins. Never aggregated across children.
> 4. The system must always return a `DocumentTree`. Never raise an exception to the caller. Degrade gracefully: full tree → partial tree → flat tree → empty tree with error metadata.
> 5. Confidence is always set: 1.0 for fast-path (deterministic signals), classifier probability for slow-path.
> 6. Physical page numbers are always integers starting at 1. Logical page numbers (printed numbers) are stored separately and may be null.
>
> **Implementation sequence** (do these in order, do not skip ahead):
>
> **Step 1**: `docstruct/core/schema.py`
> Implement: `NodeType` enum, `ExtractionPath` enum, `SourceFormat` enum, `ImageRef` dataclass, `PageRange` dataclass, `DocNode` dataclass (with `add_child`, `is_leaf`, `iter_all`, `recompute_type`, `to_dict`), `DocumentTree` dataclass (with `finalise`, `_assign_section_ids`, `_assign_flat_ids`, `get_by_id`, `get_by_section_id`, `flat_list`, `to_dict`).
>
> **Step 2**: `docstruct/core/config.py`
> Implement: `DocStructConfig` dataclass with all configuration fields and defaults.
>
> **Step 3**: `docstruct/serializers/json_serializer.py` and `docstruct/serializers/markdown_serializer.py`
> Implement both serializers. Write unit tests immediately after each.
>
> **Step 4**: `docstruct/parsers/base.py`
> Implement the `BaseParser` abstract class.
>
> **Step 5**: `docstruct/parsers/html_parser.py`
> Implement `HtmlParser` (fast path, h1-h6 tags) and `MarkdownParser` (converts to HTML first). This is the simplest parser and validates the pipeline end-to-end before touching PDF.
>
> **Step 6**: `docstruct/parsers/docx_parser.py`
> Implement `DocxParser` (fast path via paragraph styles). Include approximate page tracking via XML page break markers.
>
> **Step 7**: `docstruct/parsers/pdf_parser.py`
> Implement `PdfParser` — fast path only first (PDF outline via pymupdf). Leave slow path as a clearly documented stub. Implement `_extract_spans()` and `Span` dataclass in preparation for Phase 2.
>
> **Step 8**: `docstruct/pipeline.py`
> Implement `DocStructPipeline` — format detection, parser routing, output file writing.
>
> **Step 9**: `docstruct/cli.py`
> Implement CLI: `docstruct extract <file> [--output-dir DIR] [--format json|markdown|both] [--ocr]`
>
> After completing all 9 steps, proceed to Phase 2 (slow path) only when the Phase 1 end-to-end test passes on 5 real documents.
>
> For each module: write the complete implementation, then immediately write the corresponding unit tests. Do not write placeholder or stub code except where explicitly noted (PDF slow path stub in Step 7).
>
> The output schema is locked. Do not deviate from it.

---

*End of DocStruct Implementation Plan v1.0*
