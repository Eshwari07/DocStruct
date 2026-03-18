from __future__ import annotations

from pathlib import Path
from typing import List

import pdfplumber  # type: ignore[import]

from docstruct.content.table_converter import table_to_markdown
from docstruct.core.schema import DocumentTree


def extract_tables_from_pdf(tree: DocumentTree, file_path: Path) -> None:
    """
    Best-effort table extraction for PDFs.

    Strategy:
    - For each page, run pdfplumber's extract_tables()
    - Convert to markdown and append into the deepest node containing that page
    """
    try:
        pdf = pdfplumber.open(str(file_path))
    except Exception:
        return

    with pdf:
        for page_num in range(1, len(pdf.pages) + 1):
            page = pdf.pages[page_num - 1]
            try:
                tables = page.extract_tables() or []
            except Exception:
                continue

            if not tables:
                continue

            target = _find_deepest_node_for_page(tree, page_num)
            if not target:
                continue

            md_blocks: List[str] = []
            for idx, t in enumerate(tables, start=1):
                # Normalize values
                table_data = [[(c or "").strip() for c in (row or [])] for row in (t or [])]
                md = table_to_markdown(table_data)
                if not md.strip():
                    continue
                md_blocks.append(f"Table (p.{page_num}, #{idx}):\n\n{md}")

            if not md_blocks:
                continue

            block = "\n\n".join(md_blocks).strip()
            if target.text.strip():
                target.text = target.text.rstrip() + "\n\n" + block
            else:
                target.text = block


def _find_deepest_node_for_page(tree: DocumentTree, page: int):
    best = None
    best_depth = -1
    for node in tree.flat_list():
        if node.pages and node.pages.physical_start <= page <= node.pages.physical_end:
            if node.depth > best_depth:
                best = node
                best_depth = node.depth
    return best

