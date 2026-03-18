from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import List, Tuple

import fitz  # type: ignore[import]  # pymupdf

from docstruct.core.schema import (
    DocumentTree,
    DocNode,
    PageRange,
    SourceFormat,
    ExtractionPath,
)
from docstruct.parsers.base import BaseParser


class PdfParser(BaseParser):
    """
    PDF parser — Phase 1 fast path via PDF outline/bookmarks.

    Slow path (untagged PDFs) will be implemented later in the extraction layer.
    """

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
                # Best-effort: never fail the entire parse due to text extraction on one page.
                continue

            if sum(len(c) for c in chunks) >= max_chars:
                break

        joined = "\n\n".join(chunks).strip()
        if len(joined) > max_chars:
            joined = joined[:max_chars].rstrip()
        return joined

    def parse(self) -> DocumentTree:
        doc = fitz.open(self.file_path)  # type: ignore[arg-type]
        try:
            total_pages = doc.page_count

            toc: List[Tuple[int, str, int]] = doc.get_toc(simple=True) or []
            root_nodes: List[DocNode] = []

            if not toc:
                # No outline: return a single-node tree with best-effort text.
                pages = PageRange(
                    physical_start=1,
                    physical_end=total_pages if total_pages > 0 else 1,
                    logical_start=None,
                    logical_end=None,
                )
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

