from __future__ import annotations

import datetime as _dt
import statistics
from pathlib import Path
from typing import List, Optional, Tuple

import fitz  # type: ignore[import]  # pymupdf

from docstruct.core.config import DocStructConfig
from docstruct.core.schema import (
    DocumentTree,
    DocNode,
    PageRange,
    Span,
    SourceFormat,
    ExtractionPath,
)
from docstruct.parsers.base import BaseParser
from docstruct.extraction.span_extractor import PdfSpanExtractor
from docstruct.extraction.heading_classifier import score_headings
from docstruct.extraction.numbering_detector import detect_numbering, parse_numbering
from docstruct.extraction.tree_builder import build_tree, HeadingCandidate
from docstruct.content.text_populator import populate_text_for_pdf


class PdfParser(BaseParser):
    """
    PDF parser — fast path via PDF outline/bookmarks, slow path via
    font/layout heading detection for untagged PDFs.
    """

    def __init__(self, file_path: Path, config: Optional[DocStructConfig] = None):
        super().__init__(file_path)
        self.config = config or DocStructConfig()

    def _extract_text_for_pages(
        self, doc: "fitz.Document", page_start: int, page_end: int, *, max_chars: int = 15000
    ) -> str:
        """
        Extract plain text for the inclusive 1-based page range.
        Keep output bounded to avoid returning extremely large payloads.
        """
        start_idx = max(0, page_start - 1)
        end_idx = max(start_idx, min(doc.page_count - 1, page_end - 1))

        chunks: List[str] = []
        for page_idx in range(start_idx, end_idx + 1):
            try:
                page = doc.load_page(page_idx)
                txt = page.get_text("text") or ""
                txt = txt.strip()
                if txt:
                    chunks.append(txt)
            except Exception:
                continue

            if sum(len(c) for c in chunks) >= max_chars:
                break

        joined = "\n\n".join(chunks).strip()
        if len(joined) > max_chars:
            joined = joined[:max_chars].rstrip()
        return joined

    def _single_node_fallback(self, doc: "fitz.Document", total_pages: int) -> DocumentTree:
        """Fallback for truly unstructured documents — returns a single root node."""
        pages = PageRange(
            physical_start=1,
            physical_end=total_pages if total_pages > 0 else 1,
            logical_start=None,
            logical_end=None,
        )
        assert pages.physical_start >= 1, f"Invalid page start: {pages.physical_start}"

        root = DocNode(
            title=str(self.file_path.stem),
            text=self._extract_text_for_pages(doc, pages.physical_start, pages.physical_end),
            pages=pages,
            confidence=0.6,
            images=[],
            children=[],
        )
        tree = DocumentTree(
            source_file=str(self.file_path.name),
            source_format=SourceFormat.PDF,
            total_pages=total_pages,
            extracted_at=_dt.datetime.utcnow().isoformat() + "Z",
            extraction_path=ExtractionPath.FAST,
            nodes=[root],
        )
        tree.finalise()
        return tree

    def _assign_levels(self, spans: List[Span], median_font_size: float) -> List[Span]:
        """
        Assign heading levels to spans that pass the heading threshold.

        Level assignment strategy:
        - Rank unique (font_size, is_bold) combinations descending
          (larger size first, bold before non-bold at same size)
        - Map each rank to a level (1 = most prominent), capped at 6
        - Numbering depth overrides when available
        """
        threshold = self.config.heading_threshold
        max_words = self.config.max_heading_words

        heading_spans = [
            s for s in spans
            if s.heading_score >= threshold and s.word_count <= max_words
        ]

        if not heading_spans:
            return []

        unique_styles: List[Tuple[float, bool]] = sorted(
            {(s.font_size, s.is_bold) for s in heading_spans},
            key=lambda t: (t[0], t[1]),
            reverse=True,
        )
        style_to_level = {style: min(rank, 6) for rank, style in enumerate(unique_styles, start=1)}

        for span in heading_spans:
            base_level = style_to_level[(span.font_size, span.is_bold)]

            if span.has_numbering:
                parsed = parse_numbering(span.numbering_str)
                if parsed is not None:
                    numbering_level = min(len(parsed), 6)
                    span.assigned_level = numbering_level
                    continue

            span.assigned_level = base_level

        return heading_spans

    def _slow_path_parse(self, doc: "fitz.Document", total_pages: int) -> DocumentTree:
        """Heading detection via font/layout signals for PDFs without a TOC."""
        extractor = PdfSpanExtractor(self.file_path)
        spans = extractor.extract()

        if not spans:
            return self._single_node_fallback(doc, total_pages)

        font_sizes = [s.font_size for s in spans if s.font_size > 0]
        line_heights = [s.line_height for s in spans if s.line_height > 0]
        median_font_size = statistics.median(font_sizes) if font_sizes else 12.0
        median_line_height = statistics.median(line_heights) if line_heights else 14.0

        detect_numbering(spans)
        score_headings(spans, median_font_size, median_line_height)

        heading_spans = self._assign_levels(spans, median_font_size)

        candidates = [
            HeadingCandidate(
                level=s.assigned_level,
                title=s.text.strip(),
                pages=PageRange(
                    physical_start=s.page,
                    physical_end=s.page,
                ),
                confidence=round(s.heading_score, 4),
            )
            for s in heading_spans
        ]

        if len(candidates) < self.config.fast_path_min_headings:
            return self._single_node_fallback(doc, total_pages)

        root_nodes = build_tree(candidates, total_pages, slow_path=True)

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

    def parse(self) -> DocumentTree:
        doc = fitz.open(self.file_path)  # type: ignore[arg-type]
        try:
            total_pages = doc.page_count

            toc: List[Tuple[int, str, int]] = doc.get_toc(simple=True) or []
            root_nodes: List[DocNode] = []

            if not toc:
                return self._slow_path_parse(doc, total_pages)

            # Add front-matter node for pages before first TOC entry (no data loss).
            page_starts = [entry[2] for entry in toc]
            first_start = min(page_starts) if page_starts else 1
            if first_start > 1:
                fm_pages = PageRange(
                    physical_start=1,
                    physical_end=first_start - 1,
                    logical_start=None,
                    logical_end=None,
                )
                root_nodes.append(
                    DocNode(
                        title="Front matter",
                        text=self._extract_text_for_pages(doc, fm_pages.physical_start, fm_pages.physical_end),
                        pages=fm_pages,
                        confidence=0.9,
                        images=[],
                        children=[],
                    )
                )

            # Pre-compute end pages for each TOC entry using next sibling (same or higher level).
            page_ends: List[int] = []
            for idx, (level, title, page_start) in enumerate(toc):
                end_page = total_pages
                for lookahead_idx in range(idx + 1, len(toc)):
                    la_level, _, la_page = toc[lookahead_idx]
                    if la_level <= level:
                        end_page = max(page_start, la_page - 1)
                        break
                page_ends.append(end_page)

            stack: List[tuple[int, DocNode]] = []

            for (level, title, page_start), page_end in zip(toc, page_ends):
                pages = PageRange(
                    physical_start=page_start,
                    physical_end=page_end,
                    logical_start=None,
                    logical_end=None,
                )

                node = DocNode(
                    title=title.strip(),
                    text=self._extract_text_for_pages(doc, page_start, page_end),
                    pages=pages,
                    confidence=1.0,
                    images=[],
                    children=[],
                )

                # Stack-based tree construction based on outline levels
                while stack and stack[-1][0] >= level:
                    stack.pop()

                if stack:
                    stack[-1][1].add_child(node)
                else:
                    root_nodes.append(node)

                stack.append((level, node))

            tree = DocumentTree(
                source_file=str(self.file_path.name),
                source_format=SourceFormat.PDF,
                total_pages=total_pages,
                extracted_at=_dt.datetime.utcnow().isoformat() + "Z",
                extraction_path=ExtractionPath.FAST,
                nodes=root_nodes,
            )
            tree.finalise()
            return tree
        finally:
            doc.close()
