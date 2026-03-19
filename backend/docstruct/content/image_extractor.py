from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import fitz  # pymupdf

from docstruct.core.schema import DocumentTree, ImageRef

logger = logging.getLogger(__name__)

_FIGURE_LABEL_RE = re.compile(
    r"(fig(?:ure)?\.?\s*\d+(?:\.\d+)?|table\s*\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

# Minimum fraction of page area an image must occupy to be kept.
_MIN_AREA_RATIO = 0.03  # 3% of page — filters logos/borders better

# Minimum pixel dimensions (helps drop tiny icons).
_MIN_PIXEL_DIM = 80

# Skip header/footer zones where publisher logos/page numbers usually live.
_HEADER_FOOTER_FRAC = 0.07  # top/bottom 7% of page height

# Aspect ratio filtering to drop long thin rules or banners.
_MIN_ASPECT_RATIO = 0.14
_MAX_ASPECT_RATIO = 7.0

# "Inline text rendered as vector" guard for diagram extraction.
_TEXT_DENSITY_THRESHOLD = 0.40  # skip bbox where >40% looks like PDF text

# Minimum number of drawing paths to consider a page "diagram-rich"
_MIN_DRAWING_PATHS = 8
# Minimum fraction of page area covered by vector drawings
_MIN_VECTOR_AREA_RATIO = 0.04

# Extra padding to avoid clipping axis labels / arrowheads.
_CLIP_PADDING = 3.0

# Clustering tolerance for `page.cluster_drawings()` (tighter = more clusters).
_CLUSTER_X_TOLERANCE = 5
_CLUSTER_Y_TOLERANCE = 5

# IoU threshold above which a diagram region is considered "already a table"
_TABLE_OVERLAP_THRESHOLD = 0.40

_ASSET_PATH_PREFIX = "assets/images"
_IMG_MARKER_PREFIX = "{{IMG:"
_IMG_MARKER_SUFFIX = "}}"


def _sanitize_marker_field(value: str) -> str:
    """
    Sanitize marker fields so JSON/markdown parsing can't break.

    Marker format uses `|` separators, so we must not allow `|` inside fields.
    """
    v = " ".join((value or "").split())
    v = v.replace("|", "/")
    v = v.replace(_IMG_MARKER_PREFIX, "").replace(_IMG_MARKER_SUFFIX, "")
    return v.strip()


def _make_img_marker(filename: str, label: str, caption: str) -> str:
    return (
        f"{_IMG_MARKER_PREFIX}{filename}|"
        f"{_sanitize_marker_field(label)}|"
        f"{_sanitize_marker_field(caption)}{_IMG_MARKER_SUFFIX}"
    )


def _rect_iou(a: fitz.Rect, b: Tuple[float, float, float, float]) -> float:
    """Intersection-over-union between a fitz.Rect and a raw bbox tuple."""
    bx0, by0, bx1, by1 = b
    ix0 = max(a.x0, bx0)
    iy0 = max(a.y0, by0)
    ix1 = min(a.x1, bx1)
    iy1 = min(a.y1, by1)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area_a = a.width * a.height
    area_b = (bx1 - bx0) * (by1 - by0)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _overlaps_table(
    rect: fitz.Rect,
    table_bboxes: List[Tuple[float, float, float, float]],
) -> bool:
    """Return True if rect significantly overlaps any known table bbox."""
    return any(
        _rect_iou(rect, tb) >= _TABLE_OVERLAP_THRESHOLD
        for tb in table_bboxes
    )


def _estimate_text_density(page: fitz.Page, rect: fitz.Rect) -> float:
    """
    Approximate "how text-heavy" a region is by summing intersection areas
    of PDF-extractable word bboxes within `rect`.
    """
    if rect.width <= 0 or rect.height <= 0:
        return 1.0

    words = page.get_text("words")
    if not words:
        return 0.0

    text_area = 0.0
    for w in words:
        # words format: x0, y0, x1, y1, word, block_no, line_no, word_no
        wrect = fitz.Rect(w[:4])
        if not wrect.intersects(rect):
            continue
        inter = wrect & rect
        if inter.width > 0 and inter.height > 0:
            text_area += inter.width * inter.height

    return text_area / (rect.width * rect.height) if rect.width > 0 else 1.0


def _normalize_ws(text: str) -> str:
    return " ".join((text or "").split())


def _block_text(block: dict[str, Any]) -> str:
    # PyMuPDF dict format: type 0 blocks contain lines/spans with "text"
    out_parts: List[str] = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            t = span.get("text", "")
            if t:
                out_parts.append(t)
    return _normalize_ws("".join(out_parts))


def _try_insert_marker_into_node_text(
    *,
    node: Any,
    img_bbox: fitz.Rect,
    marker: str,
    text_blocks: List[Tuple[float, str]],
) -> bool:
    """
    Best-effort insertion: find nearest text block above `img_bbox` and insert
    marker after the corresponding paragraph in `node.text`.
    """
    # Nearest previous block by bottom edge.
    candidates = [tb for (y1, tb) in text_blocks if y1 <= img_bbox.y0 + 1.0]
    if not candidates:
        return False

    anchor_source = candidates[-1]
    if not anchor_source:
        return False

    anchor_source = _normalize_ws(anchor_source)
    if not anchor_source:
        return False

    words = anchor_source.split(" ")
    last_word = words[-1] if words else ""
    anchor_variants = []
    if len(anchor_source) > 20:
        anchor_variants.append(anchor_source[-60:])
        anchor_variants.append(anchor_source[-40:])
    if last_word:
        anchor_variants.append(last_word)

    for anchor in anchor_variants:
        if len(anchor) < 3:
            continue
        idx = node.text.find(anchor)
        if idx == -1:
            continue
        insert_at = node.text.find("\n\n", idx)
        if insert_at == -1:
            insert_at = len(node.text)
        else:
            insert_at += 2
        node.text = node.text[:insert_at] + f"\n\n{marker}\n\n" + node.text[insert_at:]
        return True

    return False


def _is_valid_raster_image(
    *,
    img_bbox: Optional[fitz.Rect],
    page_rect: fitz.Rect,
    base_image: dict[str, Any],
) -> bool:
    page_area = page_rect.width * page_rect.height
    if page_area <= 0:
        return False

    width_px = int(base_image.get("width", 0) or 0)
    height_px = int(base_image.get("height", 0) or 0)
    if width_px < _MIN_PIXEL_DIM or height_px < _MIN_PIXEL_DIM:
        return False

    aspect = (width_px / height_px) if height_px > 0 else 0.0
    if aspect < _MIN_ASPECT_RATIO or aspect > _MAX_ASPECT_RATIO:
        return False

    bpc = int(base_image.get("bpc", 8) or 8)
    if bpc < 2:
        return False

    # If we can't locate bbox, we can't apply area/position checks.
    if img_bbox is None or img_bbox.width <= 0 or img_bbox.height <= 0:
        return True

    img_area = img_bbox.width * img_bbox.height
    if img_area / page_area < _MIN_AREA_RATIO:
        return False

    centroid_y = (img_bbox.y0 + img_bbox.y1) / 2.0
    if centroid_y < page_rect.height * _HEADER_FOOTER_FRAC:
        return False
    if centroid_y > page_rect.height * (1.0 - _HEADER_FOOTER_FRAC):
        return False

    return True


def extract_images_from_pdf(
    tree: DocumentTree,
    file_path: Path,
    output_dir: Path,
    table_bboxes: Optional[Dict[int, List[Tuple[float, float, float, float]]]] = None,
) -> None:
    """
    Extract embedded raster images and vector diagrams from a PDF and attach
    them as ImageRef objects to the corresponding DocNodes.

    table_bboxes (optional): mapping of page_num → list of (x0,y0,x1,y1)
        tuples returned by extract_tables_from_pdf().  Any vector-diagram
        region that substantially overlaps a known table bbox is skipped to
        avoid re-capturing table borders as a "diagram" image.
    """
    if table_bboxes is None:
        table_bboxes = {}

    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(file_path))
    try:
        for page_num in range(1, doc.page_count + 1):
            page = doc.load_page(page_num - 1)
            page_rect = page.rect
            page_area = page_rect.width * page_rect.height
            page_table_bboxes = table_bboxes.get(page_num, [])

            target = _find_deepest_node_for_page(tree, page_num)
            if not target:
                continue

            # Precompute text blocks for inline marker anchoring.
            text_blocks: List[Tuple[float, str]] = []
            try:
                raw_blocks = page.get_text("dict").get("blocks", [])
                for b in raw_blocks:
                    if b.get("type") != 0:
                        continue
                    bbox = b.get("bbox")
                    if not bbox:
                        continue
                    y1 = float(bbox[3])
                    t = _block_text(b)
                    if t:
                        text_blocks.append((y1, t))
                # Keep ascending order by y1 for "nearest previous"
                text_blocks.sort(key=lambda x: x[0])
            except Exception:
                text_blocks = []

            # ── Strategy 1: embedded raster XObjects ──────────────────
            image_list = page.get_images(full=True)
            seen_xrefs: set[int] = set()
            raster_index = 0
            for img_index, img in enumerate(image_list):
                xref = img[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)
                try:
                    base_image = doc.extract_image(xref)
                    if not base_image:
                        continue
                    img_bytes = base_image["image"]
                    img_ext = base_image.get("ext", "png")

                    img_bbox = _get_image_bbox(page, xref)
                    if not _is_valid_raster_image(
                        img_bbox=img_bbox, page_rect=page_rect, base_image=base_image
                    ):
                        continue

                    raster_index += 1
                    fname = f"p{page_num}_img_{raster_index}.{img_ext}"
                    img_path = output_dir / fname
                    img_path.write_bytes(img_bytes)

                    caption, label = _find_caption(page, img_bbox)

                    # File path stored for API usage.
                    stored_path = f"{_ASSET_PATH_PREFIX}/{fname}"

                    if img_bbox is not None:
                        bbox_tuple = (img_bbox.x0, img_bbox.y0, img_bbox.x1, img_bbox.y1)
                        y0, y1 = img_bbox.y0, img_bbox.y1
                    else:
                        bbox_tuple = (0.0, 0.0, 0.0, 0.0)
                        y0, y1 = 0.0, 0.0

                    target.images.append(
                        ImageRef(
                            label=label,
                            caption=caption,
                            path=stored_path,
                            page=page_num,
                            y0=float(y0),
                            y1=float(y1),
                            bbox=bbox_tuple,
                            image_type="raster",
                            width_px=int(base_image.get("width", 0) or 0),
                            height_px=int(base_image.get("height", 0) or 0),
                        )
                    )

                    # Inline placement for markdown: insert an internal marker.
                    if img_bbox is not None:
                        marker = _make_img_marker(fname, label, caption)
                        _try_insert_marker_into_node_text(
                            node=target,
                            img_bbox=img_bbox,
                            marker=marker,
                            text_blocks=text_blocks,
                        )
                except Exception as exc:
                    logger.warning(
                        "Failed to extract raster image xref=%s page=%d: %s",
                        xref, page_num, exc,
                    )

            # ── Strategy 2: vector/diagram content ────────────────────
            # Pages with many drawing paths likely contain diagrams,
            # flowcharts, or charts that get_images() will miss entirely.
            drawings = page.get_drawings()
            if not drawings:
                continue

            rects = [d["rect"] for d in drawings if d.get("rect")]
            if len(rects) < _MIN_DRAWING_PATHS:
                continue

            vector_area = sum(r.width * r.height for r in rects)
            if page_area > 0 and vector_area / page_area < _MIN_VECTOR_AREA_RATIO:
                continue

            # Cluster drawings so we don't render the entire page region.
            try:
                cluster_bboxes = page.cluster_drawings(
                    x_tolerance=_CLUSTER_X_TOLERANCE,
                    y_tolerance=_CLUSTER_Y_TOLERANCE,
                )
            except Exception as exc:
                logger.warning("Failed cluster_drawings page=%d: %s", page_num, exc)
                cluster_bboxes = []

            if not cluster_bboxes:
                continue

            # Keep cluster processing stable/deterministic.
            cluster_bboxes = sorted(cluster_bboxes, key=lambda r: (r.y0, r.x0))
            vec_index = 0
            mat = fitz.Matrix(2.0, 2.0)  # 2× for legibility

            for cluster_bbox in cluster_bboxes:
                if not cluster_bbox:
                    continue

                # Clip padding to avoid cutting diagram labels.
                padded = fitz.Rect(
                    cluster_bbox.x0 - _CLIP_PADDING,
                    cluster_bbox.y0 - _CLIP_PADDING,
                    cluster_bbox.x1 + _CLIP_PADDING,
                    cluster_bbox.y1 + _CLIP_PADDING,
                ) & page_rect
                if padded.width <= 0 or padded.height <= 0:
                    continue

                diag_area = padded.width * padded.height
                if page_area > 0 and diag_area / page_area < _MIN_AREA_RATIO:
                    continue

                if page_table_bboxes and _overlaps_table(
                    padded, page_table_bboxes
                ):
                    continue

                # Guard against extracting text-heavy regions (fixes "text in image").
                text_density = _estimate_text_density(page, padded)
                if text_density > _TEXT_DENSITY_THRESHOLD:
                    continue

                try:
                    pix = page.get_pixmap(matrix=mat, clip=padded, alpha=False)
                    vec_index += 1
                    fname = f"p{page_num}_vec_{vec_index}.png"
                    img_path = output_dir / fname
                    pix.save(str(img_path))

                    caption, label = _find_caption(page, padded)
                    stored_path = f"{_ASSET_PATH_PREFIX}/{fname}"

                    target.images.append(
                        ImageRef(
                            label=label,
                            caption=caption,
                            path=stored_path,
                            page=page_num,
                            y0=float(padded.y0),
                            y1=float(padded.y1),
                            bbox=(padded.x0, padded.y0, padded.x1, padded.y1),
                            image_type="vector",
                            width_px=int(pix.width),
                            height_px=int(pix.height),
                        )
                    )

                    marker = _make_img_marker(fname, label, caption)
                    _try_insert_marker_into_node_text(
                        node=target,
                        img_bbox=padded,
                        marker=marker,
                        text_blocks=text_blocks,
                    )
                except Exception as exc:
                    logger.warning(
                        "Failed to render vector cluster page=%d: %s",
                        page_num,
                        exc,
                    )
    finally:
        doc.close()


def _get_image_bbox(page: fitz.Page, xref: int) -> fitz.Rect | None:
    """Return the bbox of an image XObject on the page, or None."""
    # Prefer get_image_info() because it reliably reports placement bboxes
    # for raster XObjects (even when they are not present in get_text("dict")).
    try:
        for info in page.get_image_info(xrefs=True):
            if info.get("xref") == xref:
                bbox = info.get("bbox")
                if bbox:
                    return fitz.Rect(bbox)
    except Exception:
        pass

    # Fallback: best-effort scan through text dict blocks.
    for block in page.get_text("dict").get("blocks", []):
        if block.get("type") == 1 and block.get("xref") == xref:
            return fitz.Rect(block["bbox"])
    return None


def _find_caption(
    page: fitz.Page, img_bbox: fitz.Rect | None
) -> tuple[str, str]:
    """
    Search for caption text in a 60pt strip below the image.
    Returns (caption_text, figure_label).
    """
    if img_bbox is None:
        return "", ""
    search_rect = fitz.Rect(
        img_bbox.x0,
        img_bbox.y1,
        img_bbox.x1,
        img_bbox.y1 + 60,
    ) & page.rect

    words = page.get_text("words")
    nearby = [
        w[4] for w in words if fitz.Rect(w[:4]).intersects(search_rect)
    ]
    if not nearby:
        return "", ""

    caption = " ".join(nearby)
    match = _FIGURE_LABEL_RE.search(caption)
    label = match.group(1) if match else ""
    return caption, label


def _find_deepest_node_for_page(tree: DocumentTree, page: int):
    best = None
    best_depth = -1
    for node in tree.flat_list():
        if (
            node.pages
            and node.pages.physical_start <= page <= node.pages.physical_end
        ):
            if node.depth > best_depth:
                best = node
                best_depth = node.depth
    return best

