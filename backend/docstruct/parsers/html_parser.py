from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from markdown import markdown as md_to_html

from docstruct.core.schema import (
    DocumentTree,
    DocNode,
    PageRange,
    SourceFormat,
    ExtractionPath,
)
from docstruct.parsers.base import BaseParser


_STRIP_NUMBERING_RE = re.compile(
    r"^("
    r"(?:\d+\.){1,5}\d*\.?\s+"  # 1.2.3
    r"|[A-Z]\.\s+"  # A.
    r"|\([a-zA-Z\d]+\)\s+"  # (a)
    r"|(?:Chapter|Section|Part|Appendix)\s+[\dA-Z]+[:\.\s]+"
    r")",
    re.IGNORECASE,
)


def _strip_numbering(title: str) -> str:
    return _STRIP_NUMBERING_RE.sub("", title).strip()


class HtmlParser(BaseParser):
    """
    Fast-path HTML parser using h1–h6 tags as headings.
    """

    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self._html = self.file_path.read_text(encoding="utf-8", errors="ignore")

    def parse(self) -> DocumentTree:
        soup = BeautifulSoup(self._html, "html.parser")
        body = soup.body or soup

        # Treat entire document as a single logical page
        page_range = PageRange(physical_start=1, physical_end=1)

        root_nodes: List[DocNode] = []
        stack: List[tuple[int, DocNode]] = []

        # Iterate over elements in document order
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

                # Stack-based tree construction
                while stack and stack[-1][0] >= depth:
                    stack.pop()

                if stack:
                    stack[-1][1].add_child(node)
                else:
                    root_nodes.append(node)

                stack.append((depth, node))

            elif tag in {"p", "div", "ul", "ol", "pre", "code", "blockquote", "table"}:
                # Body content appended to the most recent heading node
                if not stack:
                    continue
                current_node = stack[-1][1]
                text = el.get_text(" ", strip=True)
                if text:
                    if current_node.text:
                        current_node.text += "\n\n" + text
                    else:
                        current_node.text = text

        tree = DocumentTree(
            source_file=str(self.file_path.name),
            source_format=SourceFormat.HTML,
            total_pages=1,
            extracted_at=_dt.datetime.utcnow().isoformat() + "Z",
            extraction_path=ExtractionPath.FAST,
            nodes=root_nodes,
        )
        tree.finalise()
        return tree


class MarkdownParser(HtmlParser):
    """
    Markdown parser: converts Markdown to HTML, then uses HtmlParser logic.
    """

    def __init__(self, file_path: Path):
        BaseParser.__init__(self, file_path)  # bypass HtmlParser __init__
        raw_md = self.file_path.read_text(encoding="utf-8", errors="ignore")
        # markdown() returns an HTML fragment; wrap in <html><body> for consistency
        html = md_to_html(raw_md, output_format="html5")
        self._html = f"<html><body>{html}</body></html>"

    def parse(self) -> DocumentTree:
        # Reuse HtmlParser.parse implementation
        soup_parser = HtmlParser(self.file_path)
        soup_parser._html = self._html  # type: ignore[attr-defined]
        tree = soup_parser.parse()
        tree.source_format = SourceFormat.MARKDOWN
        return tree

