from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import fitz  # type: ignore[import]  # pymupdf

from docstruct.core.schema import Span, SourceFormat


def _detect_columns(spans: List[Span], page_width: float) -> int:
    """Estimate column count (1 or 2) from the x-center distribution of body-length spans."""
    x_centers = [
        (s.bbox[0] + s.bbox[2]) / 2
        for s in spans
        if s.word_count > 3
    ]
    if len(x_centers) < 20:
        return 1

    left = sum(1 for x in x_centers if x < page_width * 0.45)
    right = sum(1 for x in x_centers if x > page_width * 0.55)
    center = len(x_centers) - left - right

    if center < 0.1 * len(x_centers) and left > 10 and right > 10:
        return 2
    return 1


def _assign_columns(
    spans: List[Span],
    page_widths: Dict[int, float],
    *,
    enable: bool = True,
) -> None:
    """Detect per-page column layout and set ``span.column`` in-place."""
    if not enable:
        return

    page_spans: Dict[int, List[Span]] = defaultdict(list)
    for s in spans:
        page_spans[s.page].append(s)

    for page_num, pspans in page_spans.items():
        pw = page_widths.get(page_num, 612.0)
        n_cols = _detect_columns(pspans, pw)
        if n_cols < 2:
            continue
        mid = pw * 0.52
        for s in pspans:
            span_width = s.bbox[2] - s.bbox[0]
            if span_width > pw * 0.65:
                s.column = -1
            elif s.bbox[0] < pw * 0.08:
                s.column = 0
            elif (s.bbox[0] + s.bbox[2]) / 2.0 < mid:
                s.column = 0
            else:
                s.column = 1


@dataclass
class PdfSpanExtractor:
    """
    Extracts **line-level** Span objects from a PDF using pymupdf.

    Each visual line (all typographic spans joined) becomes one Span, which is
    the correct semantic unit for heading detection and body-text grouping.
    Block indices are preserved for downstream paragraph assembly.
    """

    file_path: Path

    def extract(self) -> Tuple[List[Span], Dict[int, float]]:
        """Return ``(spans, page_widths)`` where *page_widths* maps 1-based page → width."""
        doc = fitz.open(self.file_path)  # type: ignore[arg-type]
        spans: List[Span] = []
        page_widths: Dict[int, float] = {}

        try:
            for page_index in range(doc.page_count):
                page = doc.load_page(page_index)
                page_num = page_index + 1
                page_widths[page_num] = float(page.rect.width)

                blocks = page.get_text("dict")["blocks"]
                prev_bottom = 0.0

                for block_idx, block in enumerate(blocks):
                    if block.get("type", 0) != 0:
                        continue  # skip image blocks

                    for line in block.get("lines", []):
                        raw_spans = line.get("spans", [])
                        if not raw_spans:
                            continue

                        line_text = " ".join(
                            s.get("text", "").strip()
                            for s in raw_spans
                            if s.get("text", "").strip()
                        )
                        if not line_text.strip():
                            continue

                        line_bbox = tuple(line.get("bbox", (0.0, 0.0, 0.0, 0.0)))
                        x0, y0, x1, y1 = line_bbox
                        line_height = y1 - y0

                        space_above = max(0.0, y0 - prev_bottom) if prev_bottom else 0.0

                        font_size = max(
                            (float(s.get("size", 0)) for s in raw_spans),
                            default=0.0,
                        )

                        is_bold = any(
                            bool(s.get("flags", 0) & 0b10000)
                            or "bold" in (s.get("font", "") or "").lower()
                            for s in raw_spans
                        )
                        is_italic = any(
                            bool(s.get("flags", 0) & 0b00010)
                            or "italic" in (s.get("font", "") or "").lower()
                            or "oblique" in (s.get("font", "") or "").lower()
                            for s in raw_spans
                        )

                        is_caps = line_text.isupper() and any(
                            ch.isalpha() for ch in line_text
                        )

                        font_name = raw_spans[0].get("font", "") or ""

                        s = Span(
                            text=line_text,
                            word_count=len(line_text.split()),
                            font_size=font_size,
                            is_bold=is_bold,
                            is_italic=is_italic,
                            is_caps=is_caps,
                            font_name=font_name,
                            bbox=line_bbox,  # type: ignore[arg-type]
                            space_above=space_above,
                            space_below=0.0,
                            line_height=line_height,
                            page=page_num,
                            has_numbering=False,
                            numbering_str="",
                            is_standalone=True,
                            source_format=SourceFormat.PDF.value,
                            block_index=block_idx,
                        )
                        spans.append(s)
                        prev_bottom = y1

            _assign_columns(spans, page_widths)
        finally:
            doc.close()

        return spans, page_widths
