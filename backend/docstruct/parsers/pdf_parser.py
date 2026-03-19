from __future__ import annotations

import datetime as _dt
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

    # ------------------------------------------------------------------
    # Heading level assignment with false-positive filters
    # ------------------------------------------------------------------

    def _assign_levels(
        self,
        spans: List[Span],
        median_font_size: float,
        *,
        page_widths: Optional[Dict[int, float]] = None,
        page_heights: Optional[Dict[int, float]] = None,
    ) -> List[Span]:
        """
        Assign heading levels to spans that pass the heading threshold.

        Filters (Phase 1d / Problem 3):
        - Skip email addresses, URLs, very short text
        - Skip likely metadata (centred text in the top zone of page 1
          above the first numbered heading)
        - Apply a stricter score threshold for un-numbered spans
        """
        base_threshold = self.config.heading_threshold
        strict_threshold = self.config.unnumbered_heading_threshold
        max_words = self.config.max_heading_words
        min_words = self.config.min_heading_word_count
        meta_page = self.config.metadata_zone_page
        meta_frac = self.config.metadata_zone_fraction

        first_numbered_y: Optional[float] = None
        for s in spans:
            if s.has_numbering and s.heading_score >= base_threshold:
                first_numbered_y = s.bbox[1]
                break

        page1_height = (page_heights or {}).get(meta_page, 792.0)
        meta_zone_y = page1_height * meta_frac

        pre_filtered: List[Span] = []
        for s in spans:
            text = s.text.strip()

            if "@" in text:
                continue
            if text.startswith(("http", "www.", "doi:")):
                continue
            if len(text) <= 2:
                continue
            if s.word_count < min_words:
                continue
            if s.word_count > max_words:
                continue

            effective_threshold = base_threshold if s.has_numbering else strict_threshold
            if s.heading_score < effective_threshold:
                continue

            if (
                s.page == meta_page
                and not s.has_numbering
                and page_widths
            ):
                pw = page_widths.get(s.page, 612.0)
                x_center = (s.bbox[0] + s.bbox[2]) / 2.0
                page_center = pw / 2.0
                is_centered = abs(x_center - page_center) < 0.15 * pw
                in_meta_zone = s.bbox[1] < meta_zone_y

                above_first_numbered = (
                    first_numbered_y is not None and s.bbox[1] < first_numbered_y
                )
                if is_centered and in_meta_zone and above_first_numbered:
                    continue

            pre_filtered.append(s)

        if not pre_filtered:
            return []

        # ---- style-rank → level mapping ----
        unique_styles: List[Tuple[float, bool]] = sorted(
            {(s.font_size, s.is_bold) for s in pre_filtered},
            key=lambda t: (t[0], t[1]),
            reverse=True,
        )
        style_to_level = {
            style: min(rank, 6) for rank, style in enumerate(unique_styles, start=1)
        }

        for span in pre_filtered:
            base_level = style_to_level[(span.font_size, span.is_bold)]

            if span.has_numbering:
                parsed = parse_numbering(span.numbering_str)
                if parsed is not None:
                    numbering_level = min(len(parsed), 6)
                    span.assigned_level = numbering_level
                    continue

            span.assigned_level = base_level

        return pre_filtered

    # ------------------------------------------------------------------
    # Slow path — heading detection via font / layout signals
    # ------------------------------------------------------------------

    def _slow_path_parse(self, doc: "fitz.Document", total_pages: int) -> DocumentTree:
        extractor = PdfSpanExtractor(self.file_path)
        spans, page_widths = extractor.extract()

        if not spans:
            return self._single_node_fallback(doc, total_pages)

        page_heights: Dict[int, float] = {
            i + 1: float(doc.load_page(i).rect.height) for i in range(doc.page_count)
        }

        font_sizes = [s.font_size for s in spans if s.font_size > 0]
        line_heights = [s.line_height for s in spans if s.line_height > 0]
        median_font_size = statistics.median(font_sizes) if font_sizes else 12.0
        median_line_height = statistics.median(line_heights) if line_heights else 14.0

        detect_numbering(spans)
        score_headings(spans, median_font_size, median_line_height)

        heading_spans = self._assign_levels(
            spans,
            median_font_size,
            page_widths=page_widths,
            page_heights=page_heights,
        )

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

        # Build heading_span → DocNode mapping (non-phantom nodes in DFS
        # order correspond 1:1 with heading_spans / candidates).
        real_nodes = [n for n in tree.flat_list() if not n._is_phantom]
        heading_nodes: List[DocNode]
        if len(real_nodes) == len(heading_spans):
            heading_nodes = real_nodes
        else:
            heading_nodes = real_nodes[: len(heading_spans)]

        populate_text_for_pdf(tree, spans, heading_spans, heading_nodes)
        return tree

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def parse(self) -> DocumentTree:
        doc = fitz.open(self.file_path)  # type: ignore[arg-type]
        try:
            total_pages = doc.page_count

            toc: List[Tuple[int, str, int]] = doc.get_toc(simple=True) or []
            root_nodes: List[DocNode] = []

            if not toc:
                return self._slow_path_parse(doc, total_pages)

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
