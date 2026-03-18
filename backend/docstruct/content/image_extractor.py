from __future__ import annotations

import logging
import re
from pathlib import Path

import fitz  # pymupdf

from docstruct.core.schema import DocumentTree, ImageRef

logger = logging.getLogger(__name__)

_FIGURE_LABEL_RE = re.compile(
    r"(fig(?:ure)?\.?\s*\d+(?:\.\d+)?|table\s*\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

# Minimum fraction of page area an image must occupy to be kept.
_MIN_AREA_RATIO = 0.015   # 1.5% of page — filters bullets/borders
# Minimum number of drawing paths to consider a page "diagram-rich"
_MIN_DRAWING_PATHS = 8
# Minimum fraction of page area covered by vector drawings
_MIN_VECTOR_AREA_RATIO = 0.04


def extract_images_from_pdf(
    tree: DocumentTree, file_path: Path, output_dir: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(file_path))
    try:
        for page_num in range(1, doc.page_count + 1):
            page = doc.load_page(page_num - 1)
            page_rect = page.rect
            page_area = page_rect.width * page_rect.height

            target = _find_deepest_node_for_page(tree, page_num)
            if not target:
                continue

            # ── Strategy 1: embedded raster XObjects ──────────────────
            image_list = page.get_images(full=True)
            seen_xrefs: set[int] = set()
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

                    # Find bbox for this xref to filter tiny images
                    img_bbox = _get_image_bbox(page, xref)
                    if img_bbox:
                        img_area = img_bbox.width * img_bbox.height
                        if page_area > 0 and img_area / page_area < _MIN_AREA_RATIO:
                            continue  # skip decorative/tiny image

                    fname = f"p{page_num}_raster_{img_index + 1}.{img_ext}"
                    img_path = output_dir / fname
                    img_path.write_bytes(img_bytes)

                    caption, label = _find_caption(page, img_bbox)
                    target.images.append(
                        ImageRef(label=label, caption=caption, path=f"assets/{fname}")
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

            # Compute tight bounding box around all drawings
            diagram_rect = fitz.Rect(
                min(r.x0 for r in rects) - 4,
                min(r.y0 for r in rects) - 4,
                max(r.x1 for r in rects) + 4,
                max(r.y1 for r in rects) + 4,
            ) & page_rect  # clip to page

            diag_area = diagram_rect.width * diagram_rect.height
            if page_area > 0 and diag_area / page_area < _MIN_AREA_RATIO:
                continue

            try:
                mat = fitz.Matrix(2.0, 2.0)  # 2× for legibility
                pix = page.get_pixmap(matrix=mat, clip=diagram_rect, alpha=False)
                fname = f"p{page_num}_diagram.png"
                img_path = output_dir / fname
                pix.save(str(img_path))

                caption, label = _find_caption(page, diagram_rect)
                target.images.append(
                    ImageRef(label=label, caption=caption, path=f"assets/{fname}")
                )
            except Exception as exc:
                logger.warning(
                    "Failed to render vector diagram page=%d: %s", page_num, exc
                )
    finally:
        doc.close()


def _get_image_bbox(page: fitz.Page, xref: int) -> fitz.Rect | None:
    """Return the bbox of an image XObject on the page, or None."""
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

