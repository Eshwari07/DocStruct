# Approach A: Slow-Path Heading Detection for Untagged PDFs
## Prompt for Implementation

---

## Context & Goal

You are working on **DocStruct**, a local document structure extraction pipeline. The backend is Python/FastAPI. The frontend is React/TypeScript. The relevant backend package is at `backend/docstruct/`.

**The problem:** When a PDF has no bookmarks/TOC (e.g., SEC EDGAR filings, legal documents, scanned reports), `PdfParser.parse()` collapses the entire document into a single root node covering all pages. This makes the output structurally useless — all text is one blob, no hierarchy, no navigation. The root cause is that the slow-path heading detection machinery already exists in the codebase but is **completely orphaned** — it is never called from anywhere in the pipeline.

**Your goal:** Wire in the slow-path heading detection for the no-TOC fallback in `PdfParser`, producing a properly structured `DocumentTree` from font/layout signals rather than bookmarks.

---

## Existing Files — Read These First

Before writing any code, read and understand every one of these files. They define all the types, interfaces, and partial implementations you must use and complete:

**Core schema** — `backend/docstruct/core/schema.py`
- `Span` dataclass: all fields, especially `heading_score: float = 0.0` and `assigned_level: int = 0`
- `DocNode` dataclass: `title`, `text`, `pages`, `confidence`, `images`, `tables`, `children`
- `DocumentTree` dataclass and its `finalise()` method
- `PageRange` dataclass
- `ExtractionPath` enum: `FAST`, `SLOW`, `MIXED`

**Config** — `backend/docstruct/core/config.py`
- `DocStructConfig`: `heading_threshold: float = 0.65`, `max_heading_words: int = 20`, `fast_path_min_headings: int = 2`

**Span extraction** — `backend/docstruct/extraction/span_extractor.py`
- `PdfSpanExtractor.extract()` — returns `List[Span]` from a PDF file
- Note: spans have `page` (1-based), `bbox`, `font_size`, `is_bold`, `font_name`, `word_count`, `space_above`, `line_height`

**Heading scoring** — `backend/docstruct/extraction/heading_classifier.py`
- `rule_based_heading_score(span, median_font_size, median_line_height) -> float`
- `score_headings(spans, median_font_size, median_line_height) -> None` — mutates spans in-place

**Numbering detection** — `backend/docstruct/extraction/numbering_detector.py`
- `detect_numbering(spans) -> None` — mutates spans in-place, sets `has_numbering` and `numbering_str`
- `parse_numbering(numbering_str) -> Optional[List[int]]`

**Tree building** — `backend/docstruct/extraction/tree_builder.py`
- `HeadingCandidate` dataclass: `level: int`, `title: str`, `pages: PageRange`, `confidence: float`
- `build_tree(candidates, total_pages, slow_path=True) -> List[DocNode]`

**Text population** — `backend/docstruct/content/text_populator.py`
- `populate_text_for_pdf(tree, spans) -> None` — assigns body text to nodes by page range

**PDF parser** — `backend/docstruct/parsers/pdf_parser.py`
- The `PdfParser` class — this is the primary file you will modify
- The `if not toc:` branch is what you will replace

**Pipeline** — `backend/docstruct/pipeline.py`
- `DocStructPipeline.process()` — orchestrates parser + image/table extraction
- Currently passes no config to parsers

---

## Exact Problems to Fix

### Problem 1: The no-TOC branch creates one useless node
In `pdf_parser.py`, when `toc` is empty the code does:
```python
if not toc:
    root = DocNode(title=str(self.file_path.stem), text=self._extract_text_for_pages(...), ...)
    tree = DocumentTree(..., nodes=[root])
    tree.finalise()
    return tree
```
This needs to be replaced with the slow-path flow described below.

### Problem 2: `physical_start: -1` bug
The front-matter node guard runs even in the no-TOC branch in some edge cases, producing `physical_start = 0 - 1 = -1`. Audit this and fix it — the no-TOC branch must always produce `physical_start >= 1`.

### Problem 3: Slow-path machinery is never called
`PdfSpanExtractor`, `score_headings`, `detect_numbering`, `build_tree`, and `populate_text_for_pdf` are all implemented but never invoked from the pipeline or the parser. You will wire them in.

### Problem 4: `assigned_level` is never populated on `Span`
`score_headings()` fills `heading_score` but nothing assigns `assigned_level`. You need to implement the level-assignment logic (see spec below).

### Problem 5: `DocStructConfig` is never passed to parsers
`PdfParser.__init__` only takes `file_path`. Config exists but isn't threaded through. You need to optionally accept and use it.

---

## Implementation Spec

### Step 1: Update `PdfParser.__init__` to accept optional config

```python
def __init__(self, file_path: Path, config: Optional[DocStructConfig] = None):
    super().__init__(file_path)
    self.config = config or DocStructConfig()
```

### Step 2: Replace the no-TOC branch with slow-path detection

The `if not toc:` block should become:

```python
if not toc:
    slow_tree = self._slow_path_parse(doc, total_pages)
    doc.close()
    return slow_tree
```

### Step 3: Implement `_slow_path_parse(self, doc, total_pages) -> DocumentTree`

This method must do the following in order:

**3a. Extract spans**
```python
extractor = PdfSpanExtractor(self.file_path)
spans = extractor.extract()
```

**3b. Compute medians for scoring**
```python
import statistics
font_sizes = [s.font_size for s in spans if s.font_size > 0]
line_heights = [s.line_height for s in spans if s.line_height > 0]
median_font_size = statistics.median(font_sizes) if font_sizes else 12.0
median_line_height = statistics.median(line_heights) if line_heights else 14.0
```

**3c. Run numbering detection then scoring**
```python
detect_numbering(spans)
score_headings(spans, median_font_size, median_line_height)
```

**3d. Assign heading levels**

Implement this logic as a private method `_assign_levels(spans, median_font_size)`:

- Collect only spans where `heading_score >= self.config.heading_threshold`
- Filter out spans where `word_count > self.config.max_heading_words`
- From the candidate heading spans, collect all unique font sizes, sorted descending
- Map each font size to a level (1 = largest, 2 = second largest, etc.) using `statistics.quantiles` or simple rank — cap at level 6
- Special case: if a span has `has_numbering=True` and `parse_numbering()` returns a list, use the length of that list as a strong hint for level (e.g. `[1]` → level 1, `[1, 2]` → level 2, `[1, 2, 3]` → level 3)
- Assign `span.assigned_level` in-place for all heading-candidate spans
- Return the filtered list of heading spans

**3e. Build heading candidates**

For each heading span (after level assignment), build a `HeadingCandidate`:
```python
HeadingCandidate(
    level=span.assigned_level,
    title=span.text.strip(),
    pages=PageRange(
        physical_start=span.page,
        physical_end=span.page,  # tree_builder resolves end pages
    ),
    confidence=round(span.heading_score, 4),
)
```

**3f. Check minimum heading count**

```python
if len(candidates) < self.config.fast_path_min_headings:
    # Truly unstructured doc — fall back to single node
    return self._single_node_fallback(doc, total_pages)
```

**3g. Build tree**
```python
root_nodes = build_tree(candidates, total_pages, slow_path=True)
```

**3h. Build DocumentTree and populate body text**
```python
tree = DocumentTree(
    source_file=str(self.file_path.name),
    source_format=SourceFormat.PDF,
    total_pages=total_pages,
    extracted_at=_dt.datetime.utcnow().isoformat() + "Z",
    extraction_path=ExtractionPath.SLOW,
    nodes=root_nodes,
)
tree.finalise()
populate_text_for_pdf(tree, spans)
return tree
```

**3i. Extract `_single_node_fallback` as its own method**

Move the current single-node code into `_single_node_fallback(self, doc, total_pages)` so it can be called from both branches. Critically, hardcode `physical_start=1` here — never compute it from TOC page numbers.

### Step 4: Fix the `physical_start: -1` bug

In the existing TOC path, the front-matter node is created with:
```python
if first_start > 1:
    fm_pages = PageRange(physical_start=1, physical_end=first_start - 1, ...)
```
This is correct. But verify the single-node fallback also uses `physical_start=1` unconditionally. Add a guard:
```python
assert pages.physical_start >= 1, f"Invalid page start: {pages.physical_start}"
```

### Step 5: Update `DocStructPipeline._get_parser` to pass config

```python
def _get_parser(self, fmt: SourceFormat, path: Path, config: Optional[DocStructConfig] = None) -> BaseParser:
    if fmt == SourceFormat.PDF:
        return PdfParser(path, config=config)
    ...
```

And update `process()` to accept and pass config:
```python
def process(self, file_path, *, artifact_dir=None, config=None) -> DocumentTree:
    ...
    parser = self._get_parser(fmt, path, config=config)
    ...
```

---

## Imports Required in `pdf_parser.py`

Add these imports (they are all already implemented in the codebase):

```python
import statistics
from typing import List, Tuple, Optional
from docstruct.core.config import DocStructConfig
from docstruct.extraction.span_extractor import PdfSpanExtractor
from docstruct.extraction.heading_classifier import score_headings
from docstruct.extraction.numbering_detector import detect_numbering, parse_numbering
from docstruct.extraction.tree_builder import build_tree, HeadingCandidate
from docstruct.content.text_populator import populate_text_for_pdf
```

---

## Correctness Constraints — Do Not Violate These

1. **The fast path (PDF with TOC) must not change.** The `if toc:` branch should be untouched except for the front-matter `-1` bug fix and refactoring the single-node code into `_single_node_fallback`.

2. **`tree.finalise()` must always be called before `populate_text_for_pdf`.** `finalise()` assigns `id`, `section_id`, `depth`, and `node_type` — `populate_text_for_pdf` depends on `depth` being set.

3. **`doc.close()` must still be called in all branches.** The existing `try/finally: doc.close()` pattern in the TOC path must be preserved. The slow path runs `PdfSpanExtractor` which opens the file independently — that's fine, it manages its own handle.

4. **`ExtractionPath` must reflect actual path taken.** Fast path with TOC → `ExtractionPath.FAST`. Slow path with heading classifier → `ExtractionPath.SLOW`. Single-node fallback → `ExtractionPath.FAST` with `confidence=0.6` (keep existing behavior).

5. **Level assignment must be deterministic and stable.** Don't use random tie-breaking. If two font sizes are equal, use `is_bold` as a tiebreaker (bold = higher level / lower number = more prominent).

6. **Don't import `scikit-learn`** for the slow path — `DocStructConfig.font_cluster_k_range` suggests k-means was planned but not implemented. Use the simpler font-size rank approach described above. Don't introduce new dependencies.

7. **`populate_text_for_pdf` uses `heading_score >= 0.65` to skip heading spans** — body text is everything below that threshold. This is already implemented correctly. Do not change `text_populator.py`.

8. **Handle empty spans gracefully.** If `extractor.extract()` returns an empty list (e.g., scanned/image-only PDF), fall through to `_single_node_fallback`.

---

## Expected Behavior After Fix

For the Apple Inc. 8-K SEC filing (20 pages, no TOC), the output should produce nodes roughly like:

```
[SLOW path]
├── PDF Copy of Submission on SEC EDGAR system   (p.1)
├── FORM 8-K / CURRENT REPORT                   (p.2)
├── Item 5.07 Submission of Matters to a Vote    (p.3)
├── Item 9.01 Financial Statements and Exhibits  (p.3)
└── APPLE INC. NON-EMPLOYEE DIRECTOR STOCK PLAN  (p.5)
    ├── 1. PURPOSES                              (p.5)
    ├── 2. ADMINISTRATION                        (p.5)
    ├── 3. SHARES AVAILABLE; LIMITS              (p.6)
    ├── 4. RESTRICTED STOCK UNITS                (p.6–p.9)
    ├── 5. OPTIONS                               (p.7–p.8)
    ...
    └── 12. DEFINITIONS                          (p.12)
```

Each node should have its body text populated from the spans between it and the next heading, not the full document text.

---

## Files to Modify

| File | Change |
|------|--------|
| `backend/docstruct/parsers/pdf_parser.py` | Primary: add `_slow_path_parse`, `_assign_levels`, `_single_node_fallback`, update `__init__` |
| `backend/docstruct/pipeline.py` | Minor: thread `config` through `process()` and `_get_parser()` |
| `backend/docstruct/core/config.py` | No changes needed |
| `backend/docstruct/extraction/span_extractor.py` | No changes needed |
| `backend/docstruct/extraction/heading_classifier.py` | No changes needed |
| `backend/docstruct/extraction/numbering_detector.py` | No changes needed |
| `backend/docstruct/extraction/tree_builder.py` | No changes needed |
| `backend/docstruct/content/text_populator.py` | No changes needed |

Do **not** modify the frontend. Do **not** modify `backend/main.py`. Do **not** change the existing fast-path logic.

---

## Validation Checklist

After implementing, verify:

- [ ] A PDF with TOC still produces `ExtractionPath.FAST` and the same tree structure as before
- [ ] A PDF without TOC produces `ExtractionPath.SLOW` and multiple nodes (not one blob)
- [ ] `physical_start` is always `>= 1` in all output nodes
- [ ] `tree.finalise()` is called before `populate_text_for_pdf` in all code paths
- [ ] `doc.close()` is called in all branches (check `try/finally`)
- [ ] An image-only/scanned PDF (no extractable text) gracefully falls back to single-node
- [ ] `ExtractionPath.SLOW` shows correctly in the frontend StatusBar and in the JSON/markdown output
