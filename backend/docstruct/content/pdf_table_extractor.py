"""
PDF table extraction — multi-strategy pdfplumber approach.

Extraction order per page:
  1. lines+lines   (bordered tables, financial statements, regulatory grids)
  2. text+text     (borderless/alignment tables, research papers, healthcare)
  3. lines+text    (mixed/partially-bordered, common in SEC filings)

Results from all three strategies are merged, deduplicated, quality-filtered,
enriched with caption text, and stored as TableBlock objects on the deepest
DocNode whose page range covers that page.

The function also returns a per-page dict of bounding boxes so the image
extractor can avoid re-capturing table regions as vector diagrams.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # pymupdf — used only for caption detection
import pdfplumber  # type: ignore[import]

from docstruct.content.table_converter import table_to_markdown_and_parts
from docstruct.core.schema import DocumentTree, TableBlock

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Caption-detection patterns
# ---------------------------------------------------------------------------
_CAPTION_RE = re.compile(
    r"(table\s*\d+[\.:)]?|exhibit\s*\d+[\.:)]?|tbl\.?\s*\d+)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Quality-filter thresholds
# ---------------------------------------------------------------------------
_MIN_ROWS = 2          # including header
_MIN_COLS = 2
_MAX_COLS = 20         # tables with >20 cols are almost always false positives
_MAX_EMPTY_RATIO = 0.70  # discard if >70% of cells are empty
_MIN_AVG_CELL_LEN = 3   # avg cell length below this → likely word-split artefact
_MAX_FRAGMENT_RATIO = 0.35  # if >35% cells look like word fragments, reject

# ---------------------------------------------------------------------------
# Deduplication threshold
# ---------------------------------------------------------------------------
_OVERLAP_THRESHOLD = 0.80  # bbox intersection / union ratio

# ---------------------------------------------------------------------------
# pdfplumber strategy presets
# ---------------------------------------------------------------------------
_STRATEGY_CONFIGS: List[Tuple[str, dict]] = [
    (
        "lines",
        {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "edge_min_length_prefilter": 0.5,
            "snap_tolerance": 3,
            "intersection_tolerance": 3,
        },
    ),
    (
        "text",
        {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "min_words_vertical": 8,   # high threshold greatly reduces prose false-positives
            "min_words_horizontal": 2,
            "snap_tolerance": 3,
            "intersection_tolerance": 3,
        },
    ),
    (
        "mixed",
        {
            "vertical_strategy": "lines",
            "horizontal_strategy": "text",
            "edge_min_length_prefilter": 0.3,
            "snap_tolerance": 3,
            "intersection_tolerance": 3,
            "min_words_horizontal": 1,
        },
    ),
]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def extract_tables_from_pdf(
    tree: DocumentTree,
    file_path: Path,
) -> Dict[int, List[Tuple[float, float, float, float]]]:
    """
    Extract tables from every page and attach them as TableBlock objects to
    the appropriate DocNode.

    Returns a dict mapping physical page number → list of (x0, y0, x1, y1)
    bounding boxes of all found tables.  The image extractor uses this to
    avoid treating table borders as vector diagrams.
    """
    table_bboxes: Dict[int, List[Tuple[float, float, float, float]]] = {}

    try:
        plumber_pdf = pdfplumber.open(str(file_path))
    except Exception as exc:
        logger.warning("pdfplumber could not open %s: %s", file_path, exc)
        return table_bboxes

    try:
        fitz_doc = fitz.open(str(file_path))
    except Exception as exc:
        logger.warning("fitz could not open %s for caption scan: %s", file_path, exc)
        fitz_doc = None

    with plumber_pdf:
        n_pages = len(plumber_pdf.pages)
        for page_num in range(1, n_pages + 1):
            plumber_page = plumber_pdf.pages[page_num - 1]
            fitz_page = fitz_doc.load_page(page_num - 1) if fitz_doc else None

            raw_tables = _extract_page_tables(plumber_page)
            if not raw_tables:
                continue

            deduplicated = _deduplicate(raw_tables)
            qualified = [t for t in deduplicated if _passes_quality(t["data"])]
            if not qualified:
                continue

            page_bbox_list: List[Tuple[float, float, float, float]] = []
            target = _find_deepest_node_for_page(tree, page_num)

            for idx, table_info in enumerate(qualified, start=1):
                table_id = f"p{page_num}_t{idx}"
                bbox = table_info["bbox"]
                page_bbox_list.append(bbox)

                caption = (
                    _find_caption(fitz_page, bbox)
                    if fitz_page is not None
                    else ""
                )
                headers, rows, md = table_to_markdown_and_parts(table_info["data"])
                if not md:
                    continue

                block = TableBlock(
                    table_id=table_id,
                    caption=caption,
                    page=page_num,
                    headers=headers,
                    rows=rows,
                    markdown=md,
                    extraction_method=table_info["method"],
                )

                if target is not None:
                    target.tables.append(block)
                else:
                    logger.debug(
                        "No node found for page %d — table %s orphaned",
                        page_num, table_id,
                    )

            if page_bbox_list:
                table_bboxes[page_num] = page_bbox_list

    if fitz_doc:
        fitz_doc.close()

    return table_bboxes


# ---------------------------------------------------------------------------
# Per-page extraction
# ---------------------------------------------------------------------------

def _extract_page_tables(
    page: "pdfplumber.page.Page",
) -> List[Dict]:
    """
    Run all three strategy configs on a single pdfplumber page.
    Returns a flat list of dicts: {data, bbox, method}.
    """
    results: List[Dict] = []
    for method, settings in _STRATEGY_CONFIGS:
        try:
            tables = page.extract_tables(table_settings=settings) or []
        except Exception as exc:
            logger.debug("Strategy %s failed on page: %s", method, exc)
            continue

        # pdfplumber doesn't expose per-table bbox from extract_tables() directly.
        # We use find_tables() to get bbox, then match by index.
        try:
            found = page.find_tables(table_settings=settings) or []
        except Exception:
            found = []

        for i, raw_data in enumerate(tables):
            if raw_data is None:
                continue
            normalized = [
                [(c or "").strip() for c in (row or [])]
                for row in raw_data
            ]
            bbox: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
            if i < len(found):
                try:
                    b = found[i].bbox
                    bbox = (b[0], b[1], b[2], b[3])
                except Exception:
                    pass
            results.append({"data": normalized, "bbox": bbox, "method": method})

    return results


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def _bbox_iou(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float]) -> float:
    """Intersection-over-union of two (x0,y0,x1,y1) rectangles."""
    ix0 = max(a[0], b[0])
    iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2])
    iy1 = min(a[3], b[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _empty_ratio(data: List[List[str]]) -> float:
    total = sum(len(r) for r in data)
    if total == 0:
        return 1.0
    empty = sum(1 for r in data for c in r if c == "")
    return empty / total


def _deduplicate(tables: List[Dict]) -> List[Dict]:
    """
    Remove near-duplicate tables produced by different strategies.
    When two tables overlap by > _OVERLAP_THRESHOLD, keep the one with
    the fewer empty cells (higher information density).
    """
    kept: List[Dict] = []
    for candidate in tables:
        dominated = False
        for i, existing in enumerate(kept):
            iou = _bbox_iou(candidate["bbox"], existing["bbox"])
            if iou >= _OVERLAP_THRESHOLD:
                # Keep whichever has fewer empty cells
                if _empty_ratio(candidate["data"]) < _empty_ratio(existing["data"]):
                    kept[i] = candidate
                dominated = True
                break
        if not dominated:
            kept.append(candidate)
    return kept


# ---------------------------------------------------------------------------
# Quality filter
# ---------------------------------------------------------------------------

def _avg_cell_len(data: List[List[str]]) -> float:
    cells = [c for r in data for c in r if c]
    if not cells:
        return 0.0
    return sum(len(c) for c in cells) / len(cells)


def _fragment_ratio(data: List[List[str]]) -> float:
    """
    Estimate what fraction of non-empty cells look like word fragments.
    Two signals:
      1. Short strings (≤4 chars) starting with lowercase — classic char split.
      2. Any-length strings starting with a lowercase letter in the header row
         — indicates paragraph text was split mid-sentence into columns.
    """
    non_empty = [c for r in data for c in r if c]
    if not non_empty:
        return 0.0
    short_fragments = sum(
        1 for c in non_empty if len(c) <= 4 and c[0].islower()
    )
    header_cells = [c for c in (data[0] if data else []) if c]
    header_fragments = sum(
        1 for c in header_cells if c[0].islower()
    )
    return (short_fragments + header_fragments) / max(len(non_empty), 1)


def _has_cross_cell_word_splits(data: List[List[str]]) -> bool:
    """
    Return True if adjacent cells in multiple rows appear to form split words.

    Two patterns are checked for each adjacent (a, b) cell pair:
    1. Mixed-case split: a ends with alpha AND b starts with lowercase
       (catches 'Submiss'+'ion', 'Ma'+'tters')
    2. ALLCAPS split: a ends uppercase AND b starts uppercase AND the
       boundary word on at least one side is very short (≤3 chars)
       (catches 'AP'+'PLE INC.', 'N'+'ON-EMPLOYEE')

    If ≥2 rows show any split pattern we reject the table as prose artefact.
    """
    split_rows = 0
    # Skip entirely-empty rows so we inspect 10 rows that actually have content
    non_empty_rows = [r for r in data if any(c for c in r)]
    sample = non_empty_rows[:10]
    for row in sample:
        non_empty = [c for c in row if c]
        for i in range(len(non_empty) - 1):
            a = non_empty[i].rstrip()
            b = non_empty[i + 1].lstrip()
            if not a or not b:
                continue
            # Pattern 1: lowercase-start continuation
            if a[-1].isalpha() and b[0].islower():
                split_rows += 1
                break
            # Pattern 2: ALLCAPS with short boundary word
            if a[-1].isupper() and b[0].isupper():
                last_word_a = a.split()[-1] if a.split() else a
                first_word_b = b.split()[0] if b.split() else b
                if min(len(last_word_a), len(first_word_b)) <= 3:
                    split_rows += 1
                    break
    return split_rows >= 2


def _passes_quality(data: List[List[str]]) -> bool:
    if len(data) < _MIN_ROWS:
        return False
    max_cols = max((len(r) for r in data), default=0)
    if max_cols < _MIN_COLS:
        return False
    if max_cols > _MAX_COLS:
        return False
    if _empty_ratio(data) > _MAX_EMPTY_RATIO:
        return False
    if _avg_cell_len(data) < _MIN_AVG_CELL_LEN:
        return False
    if _fragment_ratio(data) > _MAX_FRAGMENT_RATIO:
        return False
    if _has_cross_cell_word_splits(data):
        return False
    # Reject tables where the header row itself is mostly empty (≥50% blank)
    # — real tables have mostly non-empty column headers.
    header = data[0]
    if header:
        header_empty = sum(1 for c in header if not c) / len(header)
        if header_empty >= 0.50:
            return False
    return True


# ---------------------------------------------------------------------------
# Caption detection (via PyMuPDF)
# ---------------------------------------------------------------------------

def _find_caption(
    page: "fitz.Page",
    bbox: Tuple[float, float, float, float],
) -> str:
    """
    Search a 40pt strip *above* the table bbox for a caption/label line.
    Falls back to a 40pt strip *below* if nothing found above.
    """
    x0, y0, x1, y1 = bbox
    page_rect = page.rect

    def _text_in_strip(strip_y0: float, strip_y1: float) -> str:
        search = fitz.Rect(x0, strip_y0, x1, strip_y1) & page_rect
        if search.is_empty:
            return ""
        words = page.get_text("words")
        nearby = [w[4] for w in words if fitz.Rect(w[:4]).intersects(search)]
        return " ".join(nearby).strip()

    # Try above first
    above_text = _text_in_strip(y0 - 40, y0)
    if above_text and _CAPTION_RE.search(above_text):
        return above_text

    # Try below
    below_text = _text_in_strip(y1, y1 + 40)
    if below_text and _CAPTION_RE.search(below_text):
        return below_text

    return ""


# ---------------------------------------------------------------------------
# Tree navigation
# ---------------------------------------------------------------------------

def _find_deepest_node_for_page(
    tree: DocumentTree, page: int
) -> Optional[object]:
    best = None
    best_depth = -1
    for node in tree.flat_list():
        if node.pages and node.pages.physical_start <= page <= node.pages.physical_end:
            if node.depth > best_depth:
                best = node
                best_depth = node.depth
    return best
