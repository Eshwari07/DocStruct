# DocStruct: Complete Diagnosis & Implementation Roadmap

---

## What the new output tells us

The Approach A slow-path is **wired in correctly and running**. The `extraction_path: slow`
confirms the pipeline reached the right code. The tree structure is recognisably correct —
it found `Abstract`, `1. Introduction`, `2. Architecture`, `3. Experiments` with subsections
`3.1`–`3.6`, `4. Conclusion`, `References`. The hierarchy and numbering detection work.

But there are **three deep problems** that make the output unusable as-is:

---

## Problem 1 — Word-Level Text Fragmentation (89% single-word segments)

**What it looks like in output:**
```
Traditional

methods

of

computer

vision

and

machine

learning
```

**Root cause:** `PdfSpanExtractor` iterates at span level:
```python
for span in line.get("spans", []):   # ← word-level
```
In justified and multi-column PDFs, each word is its own span with precise kerning data.
`text_populator` then joins spans with `"\n\n"`, producing gibberish.

**Where to fix:** `backend/docstruct/extraction/span_extractor.py`

**The fix — iterate at LINE level:**
```python
for line in block.get("lines", []):
    # Join all spans in this line into one text string
    line_text = " ".join(
        s.get("text", "").strip()
        for s in line.get("spans", [])
        if s.get("text", "").strip()
    )
    if not line_text.strip():
        continue
    # Use the line's own bbox (not individual span bbox)
    line_bbox = tuple(line.get("bbox", (0.0, 0.0, 0.0, 0.0)))
    # Use dominant font size in the line
    font_size = max((s.get("size", 0) for s in line["spans"]), default=0.0)
    # Bold: check pymupdf span flags (bit 4), not just font name string
    is_bold = any(
        bool(s.get("flags", 0) & 0b10000) or "bold" in s.get("font","").lower()
        for s in line["spans"]
    )
    ...
```

This collapses 462 single-word chunks → ~50 proper lines. Each Span is now a complete
visual line, which is the correct semantic unit for heading detection AND body text.

**Paragraph grouping** (do this in text_populator, not extractor):
Lines within the same pymupdf block belong to the same visual paragraph. After spatial
assignment, group consecutive lines with the same `block_index` (or close Y distance
< 1.5× line_height) by joining with `" "`, separate blocks with `"\n\n"`.

---

## Problem 2 — Text Mis-assignment (7 of 14 nodes have zero text)

**What it looks like:**
- `Abstract` → 0 chars of text
- `1. Introduction` → 0 chars of text  
- `4. Conclusion` → 0 chars of text
- `2. Architecture` → gets ALL page 1 body text (4710 chars)

**Root cause:** `text_populator.py` uses page-range matching:
```python
candidate_indices = find_node_for_page(span.page)
target = flat_nodes[candidate_indices[-1]]  # ← LAST node on page
```
When `Abstract` (p1), `Introduction` (p1), `Architecture` (p1) all share page 1,
**every body span on page 1 goes to `Architecture`** because it appears last in DFS order.

**Where to fix:** `backend/docstruct/content/text_populator.py`
AND the slow-path in `backend/docstruct/parsers/pdf_parser.py`

**The fix — spatial (Y-coordinate) assignment:**

The heading spans have bbox data. A body span at `(page=1, y=320)` belongs to the
heading whose bottom edge (`y1`) is the largest value still below `y=320` on page 1.

New `populate_text_for_pdf` signature:
```python
def populate_text_for_pdf(
    tree: DocumentTree,
    all_spans: List[Span],
    heading_spans: List[Span],   # ← NEW: the spans that became headings
) -> None:
```

New spatial assignment algorithm:
```python
# Build sorted list: (page, y1_of_heading, DocNode)
# heading_spans and tree nodes are in the same order (built together in slow path)
heading_anchors = []
for span, node in zip(heading_spans, heading_nodes_in_order):
    heading_anchors.append((span.page, span.bbox[3], node))  # bbox[3] = y1
# Sort by page then y position
heading_anchors.sort(key=lambda x: (x[0], x[1]))

def find_owning_node(span_page, span_y0):
    """Find the heading directly above this body span."""
    best = None
    for (h_page, h_y1, h_node) in heading_anchors:
        if h_page > span_page:
            break
        if h_page < span_page:
            best = h_node  # last heading on previous page
            continue
        # Same page: heading must end above this span
        if h_y1 <= span_y0:
            best = h_node  # keep updating — we want the closest one above
    return best

for span in all_spans:
    if span.heading_score >= threshold:
        continue
    node = find_owning_node(span.page, span.bbox[1])  # bbox[1] = y0
    if node:
        node.text = (node.text + "\n\n" + span.text).strip()
```

This requires the slow path to pass `heading_spans` to `populate_text_for_pdf`,
which it already has available (the `heading_spans` list from `_assign_levels`).

---

## Problem 3 — False Heading Detection (author names, paper title)

**What it looks like:**
- `Dan Cires¸an, Ueli Meier and J¨urgen Schmidhuber` → detected as heading (node 0001)
- Paper title `Multi-column Deep Neural Networks...` → shows up in body text of Architecture

**Root cause:** Author names in academic papers are often large font, short (≤20 words),
and don't end with punctuation — scoring high on `rule_based_heading_score`.

**Additional heuristics to add in `_assign_levels`:**

```python
# Filter 1: skip spans containing @ (email addresses)
if "@" in span.text:
    continue

# Filter 2: skip spans that are URLs
if span.text.strip().startswith(("http", "www.", "doi:")):
    continue

# Filter 3: skip single punctuation or bracket spans
if len(span.text.strip()) <= 2:
    continue

# Filter 4: skip if span is centered on page 1 AND above the first numbered heading
# (title/author metadata zone)
# Detect centered: |center_x - page_center_x| < 0.15 * page_width
# This requires page width — pass it from the extractor

# Filter 5: if a span has numbering (e.g. "1. Introduction"), 
# boost it as a structural heading. Un-numbered spans need higher score threshold.
# Apply a stricter threshold (e.g. 0.80) for spans without has_numbering=True
if not span.has_numbering:
    effective_threshold = self.config.heading_threshold + 0.15  # 0.80 instead of 0.65
else:
    effective_threshold = self.config.heading_threshold
if span.heading_score < effective_threshold:
    continue
```

The key insight: **numbered headings** (`1. Introduction`, `3.2. NIST SD 19`) are
almost always structural. **Un-numbered spans** that look heading-like are far more
often false positives (author names, captions, column headers). A stricter threshold
for un-numbered spans dramatically reduces noise.

---

## The Full Picture — Document Type Matrix

Every PDF falls into one of these categories. The fix must handle all of them:

| Document Type | TOC? | Layout | Primary Issue | Fix |
|---|---|---|---|---|
| Legal/SEC filings | No | Single-column | Structural collapse | Slow path (done) |
| Academic papers | No | 2-column | Fragmentation + mis-assign | Problems 1+2+3 |
| Technical reports | No | Single-column | Works mostly | Problems 2+3 |
| Books/manuals | Yes | Single-column | Fast path works well | Minor: page ranges |
| Scanned docs | No | N/A | No text layer | OCR (future) |
| PDFs with TOC | Yes | Any | Fast path works | Done |
| Slides exported to PDF | No | Variable | PPTX parser better | Use PPTX format |

---

## Implementation Plan — Ordered by Impact

### Phase 1: Fix the Three Core Bugs (highest ROI)

**1a. Rewrite `PdfSpanExtractor` for line-level extraction**

File: `backend/docstruct/extraction/span_extractor.py`

Change the innermost loop from `for span in line["spans"]` to
`for line in block["lines"]` with span text joining. Also:
- Store `block_index` (block number within page) on each Span — needed for paragraph grouping
- Use pymupdf span flags (`flags & 0b10000`) for bold detection, fall back to font name
- Store the line's `bbox` (not a word's bbox) so spatial assignment is accurate
- `word_count` = `len(line_text.split())` across all joined spans

The `Span` dataclass needs one new field: `block_index: int = 0`
(to enable paragraph grouping downstream).

**1b. Rewrite `populate_text_for_pdf` with spatial assignment**

File: `backend/docstruct/content/text_populator.py`

Change signature to accept `heading_spans: List[Span]` alongside the tree and all spans.
Implement the Y-coordinate based owning-node lookup described above.

Add paragraph grouping: consecutive body spans with the same `block_index` and
`page` → join with `" "` before appending to node text. Different `block_index` → `"\n\n"`.

**1c. Update `_slow_path_parse` to pass heading spans**

File: `backend/docstruct/parsers/pdf_parser.py`

`_slow_path_parse` already has `heading_spans` (the output of `_assign_levels`).
Pass it through to `populate_text_for_pdf`:

```python
populate_text_for_pdf(tree, spans, heading_spans=heading_spans)
```

Also: build the `heading_spans → DocNode` mapping here. After `build_tree` and
`tree.finalise()`, the nodes are in a known order. The heading_spans and tree nodes
were created together, so:

```python
# heading_spans[i] corresponds to the i-th node in DFS flat_list order
# (after phantoms are filtered out)
real_nodes = [n for n in tree.flat_list() if not n._is_phantom]
assert len(real_nodes) == len(candidates)  # candidates = from heading_spans
```

Pass both to `populate_text_for_pdf` as a zipped mapping.

**1d. Tighten heading detection thresholds**

File: `backend/docstruct/parsers/pdf_parser.py` in `_assign_levels`

Apply the stricter threshold for un-numbered spans (0.80 vs 0.65).
Add email/URL/short-text filters.
Result: author names filtered out, fewer false positives.

---

### Phase 2: Multi-Column Layout Handling

Academic 2-column papers need column-order text reconstruction. Without this,
the text WITHIN a node may interleave left and right column content.

**Column detection algorithm:**

```python
def detect_columns(spans: List[Span], page_width: float) -> int:
    """Returns estimated number of columns (1 or 2)."""
    # Look at x-center distribution of body spans
    x_centers = [(s.bbox[0] + s.bbox[2]) / 2 for s in spans 
                 if s.word_count > 3]  # skip short/heading spans
    if not x_centers:
        return 1
    # If bimodal distribution with gap near center → 2 columns
    left = sum(1 for x in x_centers if x < page_width * 0.45)
    right = sum(1 for x in x_centers if x > page_width * 0.55)
    center = len(x_centers) - left - right
    # 2-column if clear bimodal separation
    if center < 0.1 * len(x_centers) and left > 10 and right > 10:
        return 2
    return 1
```

For 2-column PDFs, sort spans by `(page, column_index, y0)` where
`column_index = 0 if bbox_x_center < page_width/2 else 1`. This gives correct
reading order: left column top-to-bottom, then right column top-to-bottom.

Store `column_index` on the Span dataclass (add field `column: int = 0`).
The spatial assignment in text_populator should account for column boundaries
when finding the owning heading.

---

### Phase 3: Heading Hierarchy Improvement

Current level assignment uses font-size ranking. This works for simple documents
but breaks for academic papers where:
- Paper title >> Section heading > Subsection heading > Body text
- But paper title is NOT a structural heading (it's metadata)

**Better level assignment for academic papers:**

After filtering out metadata (title/authors by position heuristic),
apply the numbered heading detection as primary signal:
- `N.` → level 1 (e.g., `1. Introduction`)
- `N.M.` → level 2 (e.g., `3.1. MNIST`)
- `N.M.K.` → level 3
- Un-numbered bold/large → level based on font size rank relative to body text

This is already partially done in `_assign_levels` via `parse_numbering`.
The gap is the over-aggressive metadata detection that creates false level-1 nodes.

---

### Phase 4: `DocStructConfig` Tuning Parameters

Add these fields to `DocStructConfig` so behavior is adjustable without code changes:

```python
@dataclass
class DocStructConfig:
    # Existing fields...
    
    # New Phase 1-2 fields:
    unnumbered_heading_threshold: float = 0.80   # stricter for un-numbered spans
    min_heading_word_count: int = 1              # skip 1-char spans
    max_heading_word_count: int = 20             # existing, rename for clarity
    enable_column_detection: bool = True         # Phase 2
    paragraph_y_gap_factor: float = 1.5          # gap > 1.5× line_height = new paragraph
    metadata_zone_page: int = 1                  # page 1 top zone = likely metadata
    metadata_zone_fraction: float = 0.25         # top 25% of page 1 = metadata zone
```

---

## Files to Modify — Summary

| File | Change | Phase |
|---|---|---|
| `backend/docstruct/extraction/span_extractor.py` | Line-level extraction, block_index field, flags-based bold | 1a |
| `backend/docstruct/content/text_populator.py` | Spatial Y-assignment, paragraph grouping, new signature | 1b |
| `backend/docstruct/parsers/pdf_parser.py` | Pass heading_spans, tighter thresholds in _assign_levels | 1c+1d |
| `backend/docstruct/core/schema.py` | Add `block_index: int = 0` and `column: int = 0` to Span | 1a |
| `backend/docstruct/core/config.py` | New tuning fields | 4 |
| `backend/docstruct/extraction/span_extractor.py` | Column detection utility | 2 |

**No frontend changes needed for any of this.**

---

## What Good Output Should Look Like

After all three Phase 1 fixes, the same research paper should produce:

```
extraction_path: slow
nodes: 12

├── Abstract (p.1)
│     "Traditional methods of computer vision and machine learning
│      cannot match human performance on tasks such as..."
│
├── 1. Introduction (p.1)
│     "The general trend in machine learning is towards larger and
│      more complex models trained with..."
│
├── 2. Architecture (p.1-2)
│     "We use a convolutional neural network architecture with..."
│
└── 3. Experiments (p.2-6)
    ├── 3.1. MNIST (p.3)
    │     "The MNIST dataset consists of 70,000 28×28 pixel..."
    ├── 3.2. NIST SD 19 (p.4)
    │     "This dataset contains..."
    ...
```

Each node has clean paragraph text. No word-per-line fragments. No empty sections.
Author names not present as structural nodes.

---

## One Key Algorithmic Insight

The entire text population problem reduces to one question:

> **Given a body text span at position (page P, y=Y), which section heading owns it?**

Answer: **the heading with the largest `y1` that satisfies `heading.page <= P` AND
`(heading.page < P OR heading.y1 <= Y)`**

This is a 1D nearest-predecessor query on the (page, y) timeline, solvable in O(n log n)
with a sorted list and binary search. It correctly handles:
- Multiple sections on the same page ✓
- Multi-page sections ✓  
- Text that appears before the first heading on a page ✓
- Two-column layout (headings and body in both columns) ✓ (with column awareness)

This single algorithm replacement in `text_populator.py` fixes Problems 1b through 4
simultaneously once the span extractor emits line-level spans.
