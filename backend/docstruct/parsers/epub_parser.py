from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from ebooklib import epub  # type: ignore[import]

from docstruct.core.schema import (
    DocumentTree,
    DocNode,
    PageRange,
    SourceFormat,
    ExtractionPath,
)
from docstruct.parsers.base import BaseParser
from docstruct.parsers.html_parser import _strip_numbering


class EpubParser(BaseParser):
    """
    Fast-path EPUB parser.

    - Uses EPUB spine (reading order) to process HTML documents
    - Uses heading tags (h1–h6) inside each item to build sections
    - Treats each spine item as a logical page for PageRange
    """

    def parse(self) -> DocumentTree:
        book = epub.read_epub(str(self.file_path))

        spine_items = [item for item in book.get_items() if item.get_type() == epub.ITEM_DOCUMENT]  # type: ignore[attr-defined]
        root_nodes: List[DocNode] = []

        page_index = 0
        for item in spine_items:
            page_index += 1
            html = item.get_content().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            body = soup.body or soup
            page_range = PageRange(
                physical_start=page_index,
                physical_end=page_index,
                logical_start=None,
                logical_end=None,
            )

            stack: List[tuple[int, DocNode]] = []

            for el in body.descendants:
                if not getattr(el, "name", None):
                    continue
                tag = el.name.lower()
                if tag in {f"h{i}" for i in range(1, 7)}:
                    depth = int(tag[1])
                    title_text = _strip_numbering(el.get_text(strip=True))
                    node = DocNode(
                        title=title_text,
                        text="",
                        pages=page_range,
                        confidence=1.0,
                        images=[],
                        children=[],
                    )

                    while stack and stack[-1][0] >= depth:
                        stack.pop()

                    if stack:
                        stack[-1][1].add_child(node)
                    else:
                        root_nodes.append(node)

                    stack.append((depth, node))
                elif tag in {"p", "div", "ul", "ol", "pre", "code", "blockquote", "table"}:
                    if not stack:
                        continue
                    current_node = stack[-1][1]
                    text = el.get_text(" ", strip=True)
                    if text:
                        if current_node.text:
                            current_node.text += "\n\n" + text
                        else:
                            current_node.text = text

        total_pages = max(page_index, 1)
        tree = DocumentTree(
            source_file=str(self.file_path.name),
            source_format=SourceFormat.EPUB,
            total_pages=total_pages,
            extracted_at=_dt.datetime.utcnow().isoformat() + "Z",
            extraction_path=ExtractionPath.FAST,
            nodes=root_nodes,
        )
        tree.finalise()
        return tree

