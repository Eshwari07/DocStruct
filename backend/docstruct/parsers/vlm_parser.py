from __future__ import annotations

import base64
import json
import logging
import os
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import fitz  # PyMuPDF

from docstruct.core.schema import (
    DocNode,
    DocumentTree,
    ExtractionPath,
    PageRange,
    SourceFormat,
    TableBlock,
)
from docstruct.parsers.base import BaseParser

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 4A — Configuration constants
# ---------------------------------------------------------------------------

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
VLM_MODEL = os.environ.get("DOCSTRUCT_VLM_MODEL", "openai/gpt-4o-mini")
VLM_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
VLM_PAGE_DPI = int(os.environ.get("DOCSTRUCT_VLM_DPI", "150"))
VLM_MAX_RETRIES = 3
VLM_RETRY_DELAY = 2.0
VLM_REQUEST_TIMEOUT = 60

# ---------------------------------------------------------------------------
# 4B — System prompt
# ---------------------------------------------------------------------------

VLM_SYSTEM_PROMPT = """\
You are a precise document structure extraction engine.

Given an image of a document page, extract ALL content
and return ONLY valid markdown.

Rules:
1. Use ATX headings (#, ##, etc.) matching visual hierarchy.
   Larger/bolder text = higher level heading.
2. Extract body text exactly as written.
3. For tables: output as GitHub Flavored Markdown tables.
4. For math formulas: use LaTeX ($formula$ or $$formula$$).
5. For lists: preserve as markdown bullet or numbered lists.
6. IGNORE: page numbers, running headers/footers, watermarks.
7. IGNORE table of contents pages — output nothing for ToC.
8. If blank or page number only: output [BLANK PAGE]
9. Output ONLY markdown. No explanations or commentary."""

# ---------------------------------------------------------------------------
# 4C — Page renderer
# ---------------------------------------------------------------------------


def render_page_to_png(doc: fitz.Document, page_num: int, dpi: int = VLM_PAGE_DPI) -> bytes:
    """Render a single PDF page to PNG bytes at the given DPI."""
    page = doc.load_page(page_num)
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    return pix.tobytes("png")


# ---------------------------------------------------------------------------
# 4D — API caller
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_TABLE_ROW_RE = re.compile(r"^\|.+\|$")
_TABLE_SEP_RE = re.compile(r"^\|[\s:|-]+\|$")


def call_vlm_api(image_png_bytes: bytes, *, page_num: int = 1) -> str:
    """Send a page image to OpenRouter and return the markdown response."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "") or VLM_API_KEY
    if not api_key.strip():
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. "
            "VLM processing requires an OpenRouter API key."
        )

    b64_image = base64.b64encode(image_png_bytes).decode("ascii")
    data_uri = f"data:image/png;base64,{b64_image}"

    model = os.environ.get("DOCSTRUCT_VLM_MODEL", "") or VLM_MODEL

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": VLM_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": data_uri},
                    },
                    {
                        "type": "text",
                        "text": f"Extract all content from this document page (page {page_num}). Return only markdown.",
                    },
                ],
            },
        ],
    }

    body = json.dumps(payload).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://docstruct.local",
        "X-Title": "DocStruct",
    }

    last_exc: Optional[Exception] = None
    for attempt in range(1, VLM_MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                OPENROUTER_API_URL, data=body, headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=VLM_REQUEST_TIMEOUT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "VLM API attempt %d/%d for page %d failed: %s",
                attempt, VLM_MAX_RETRIES, page_num, exc,
            )
            if attempt < VLM_MAX_RETRIES:
                time.sleep(VLM_RETRY_DELAY * attempt)

    raise RuntimeError(
        f"VLM API failed after {VLM_MAX_RETRIES} attempts for page {page_num}: {last_exc}"
    )


# ---------------------------------------------------------------------------
# 4E — Markdown-to-DocumentTree parser
# ---------------------------------------------------------------------------


def _parse_pages_to_tree(
    page_markdowns: List[Tuple[int, str]],
    source_file: str,
    source_format: SourceFormat,
    total_pages: int,
) -> DocumentTree:
    """Parse per-page markdown strings into a structured DocumentTree."""
    tree = DocumentTree(
        source_file=source_file,
        source_format=source_format,
        total_pages=total_pages,
        extracted_at=datetime.now(timezone.utc).isoformat(),
        extraction_path=ExtractionPath.VLM,
    )

    # Stack-based tree construction (same principle as HtmlParser)
    root_sentinel = DocNode(title="__root__")
    stack: List[Tuple[int, DocNode]] = [(0, root_sentinel)]

    current_text_lines: List[str] = []
    current_page: int = 1
    current_tables: List[TableBlock] = []
    table_counter_by_page: dict[int, int] = {}

    def _flush_text():
        nonlocal current_text_lines, current_tables
        if not stack:
            return
        _, top_node = stack[-1]
        if top_node is root_sentinel and not tree.nodes:
            pass
        text = "\n".join(current_text_lines).strip()
        if text:
            if top_node.text:
                top_node.text += "\n\n" + text
            else:
                top_node.text = text
        for tbl in current_tables:
            top_node.tables.append(tbl)
        current_text_lines = []
        current_tables = []

    def _extract_tables_from_lines(lines: List[str]) -> Tuple[List[str], List[TableBlock]]:
        """Detect GFM tables in lines and extract them as TableBlock objects."""
        result_lines: List[str] = []
        tables: List[TableBlock] = []
        i = 0
        while i < len(lines):
            if (
                _TABLE_ROW_RE.match(lines[i])
                and i + 1 < len(lines)
                and _TABLE_SEP_RE.match(lines[i + 1])
            ):
                table_lines = [lines[i], lines[i + 1]]
                j = i + 2
                while j < len(lines) and _TABLE_ROW_RE.match(lines[j]):
                    table_lines.append(lines[j])
                    j += 1

                page_key = current_page
                table_counter_by_page.setdefault(page_key, 0)
                table_counter_by_page[page_key] += 1
                tid = f"p{page_key}_t{table_counter_by_page[page_key]}"

                raw_headers = [
                    c.strip() for c in table_lines[0].strip("|").split("|")
                ]
                raw_rows = []
                for tl in table_lines[2:]:
                    raw_rows.append(
                        [c.strip() for c in tl.strip("|").split("|")]
                    )

                tbl = TableBlock(
                    table_id=tid,
                    page=page_key,
                    headers=raw_headers,
                    rows=raw_rows,
                    markdown="\n".join(table_lines),
                )
                tables.append(tbl)
                i = j
            else:
                result_lines.append(lines[i])
                i += 1
        return result_lines, tables

    for page_num, md_text in page_markdowns:
        current_page = page_num
        if not md_text or md_text.strip() in ("[BLANK PAGE]", ""):
            for _, sn in stack:
                if sn is not root_sentinel and sn.pages:
                    sn.pages.physical_end = page_num
            continue

        page_lines = md_text.split("\n")
        non_heading_lines, page_tables = _extract_tables_from_lines(page_lines)
        current_tables.extend(page_tables)

        for line in non_heading_lines:
            hm = _HEADING_RE.match(line)
            if hm:
                _flush_text()
                level = len(hm.group(1))
                title = hm.group(2).strip()

                while len(stack) > 1 and stack[-1][0] >= level:
                    stack.pop()

                node = DocNode(
                    title=title,
                    pages=PageRange(
                        physical_start=page_num,
                        physical_end=page_num,
                    ),
                )

                parent = stack[-1][1]
                if parent is root_sentinel:
                    tree.nodes.append(node)
                else:
                    parent.add_child(node)

                stack.append((level, node))
            else:
                current_text_lines.append(line)

        for _, sn in stack:
            if sn is not root_sentinel and sn.pages:
                sn.pages.physical_end = page_num

    _flush_text()

    if not tree.nodes:
        all_text = "\n\n".join(md for _, md in page_markdowns if md.strip())
        fallback_node = DocNode(
            title=Path(source_file).stem,
            text=all_text,
            pages=PageRange(physical_start=1, physical_end=total_pages),
        )
        tree.nodes.append(fallback_node)

    tree.finalise()
    return tree


# ---------------------------------------------------------------------------
# 4F — VlmParser class
# ---------------------------------------------------------------------------


class VlmParser(BaseParser):
    """Parse documents by rendering pages as images and calling a VLM via OpenRouter."""

    def __init__(
        self,
        file_path: Path,
        source_format: SourceFormat = SourceFormat.PDF,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ):
        super().__init__(file_path)
        self.source_format = source_format
        self.progress_callback = progress_callback

    def parse(self) -> DocumentTree:
        if self.source_format == SourceFormat.IMAGE:
            return self._parse_image()
        return self._parse_pdf()

    def _parse_pdf(self) -> DocumentTree:
        doc = fitz.open(str(self.file_path))
        total = doc.page_count
        page_markdowns: List[Tuple[int, str]] = []

        for i in range(total):
            page_num = i + 1
            try:
                png_bytes = render_page_to_png(doc, i)
                md = call_vlm_api(png_bytes, page_num=page_num)
            except Exception as exc:
                logger.error("Failed to process page %d: %s", page_num, exc)
                md = f"[ERROR: Could not process page {page_num}]"
            page_markdowns.append((page_num, md))

            if self.progress_callback:
                self.progress_callback(page_num, total)

        doc.close()

        return _parse_pages_to_tree(
            page_markdowns,
            source_file=self.file_path.name,
            source_format=self.source_format,
            total_pages=total,
        )

    def _parse_image(self) -> DocumentTree:
        img_bytes = self.file_path.read_bytes()

        suffix = self.file_path.suffix.lower()
        if suffix not in (".png",):
            pix = fitz.Pixmap(str(self.file_path))
            png_bytes = pix.tobytes("png")
        else:
            png_bytes = img_bytes

        try:
            md = call_vlm_api(png_bytes, page_num=1)
        except Exception as exc:
            logger.error("Failed to process image %s: %s", self.file_path.name, exc)
            md = f"[ERROR: Could not process image {self.file_path.name}]"

        if self.progress_callback:
            self.progress_callback(1, 1)

        return _parse_pages_to_tree(
            [(1, md)],
            source_file=self.file_path.name,
            source_format=SourceFormat.IMAGE,
            total_pages=1,
        )
