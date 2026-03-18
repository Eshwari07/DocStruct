from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import fitz  # type: ignore[import]  # pymupdf

from docstruct.core.schema import Span, SourceFormat


@dataclass
class PdfSpanExtractor:
    """
    Extracts Span objects from a PDF using pymupdf.
    """

    file_path: Path

    def extract(self) -> List[Span]:
        doc = fitz.open(self.file_path)  # type: ignore[arg-type]
        spans: List[Span] = []

        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            blocks = page.get_text("dict")["blocks"]

            prev_bottom = 0.0
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "") or ""
                        if not text.strip():
                            continue
                        bbox = tuple(span.get("bbox", (0.0, 0.0, 0.0, 0.0)))  # type: ignore[assignment]
                        x0, y0, x1, y1 = bbox
                        line_height = y1 - y0
                        space_above = max(0.0, y0 - prev_bottom) if prev_bottom else 0.0
                        space_below = 0.0  # filled when next span processed on same page

                        font_size = float(span.get("size", 0.0))
                        font_name = span.get("font", "") or ""
                        is_bold = "bold" in font_name.lower()
                        is_italic = "italic" in font_name.lower() or "oblique" in font_name.lower()
                        is_caps = text.isupper() and any(ch.isalpha() for ch in text)

                        s = Span(
                            text=text,
                            word_count=len(text.split()),
                            font_size=font_size,
                            is_bold=is_bold,
                            is_italic=is_italic,
                            is_caps=is_caps,
                            font_name=font_name,
                            bbox=bbox,
                            space_above=space_above,
                            space_below=space_below,
                            line_height=line_height,
                            page=page_index + 1,
                            has_numbering=False,
                            numbering_str="",
                            is_standalone=True,
                            source_format=SourceFormat.PDF.value,
                        )
                        spans.append(s)
                        prev_bottom = y1

        return spans

