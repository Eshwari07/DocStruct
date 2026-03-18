from __future__ import annotations

from pathlib import Path
from typing import List, Union

from docstruct.core.schema import DocumentTree, DocNode


def _frontmatter(tree: DocumentTree) -> str:
    return "\n".join(
        [
            "---",
            f"source_file: {tree.source_file}",
            f"source_format: {tree.source_format.value}",
            f"total_pages: {tree.total_pages}",
            f"extracted_at: {tree.extracted_at}",
            f"extraction_path: {tree.extraction_path.value}",
            "---",
        ]
    )


def _node_to_md(node: DocNode) -> List[str]:
    lines: List[str] = []
    hashes = "#" * min(node.depth, 6)
    lines.append(f"{hashes} {node.section_id} · {node.title}")

    if node.pages is not None:
        page_start = node.pages.physical_start
        page_end = node.pages.physical_end
    else:
        page_start = ""
        page_end = ""

    lines.append(
        f"<!-- id:{node.id} "
        f"pages:{page_start}-{page_end} "
        f"confidence:{node.confidence:.2f} "
        f"type:{node.node_type.value} -->"
    )
    lines.append("")

    if node.text.strip():
        lines.append(node.text.strip())
        lines.append("")

    for img in node.images:
        if img.path:
            label = img.label or img.caption or "image"
            lines.append(f"![{label}]({img.path})")
            if img.caption:
                lines.append(f"*{img.caption}*")
            lines.append("")

    for child in node.children:
        lines.extend(_node_to_md(child))

    return lines


def to_markdown(tree: DocumentTree) -> str:
    parts: List[str] = [_frontmatter(tree), ""]
    for node in tree.nodes:
        parts.extend(_node_to_md(node))
    return "\n".join(parts)


def save_markdown(tree: DocumentTree, path: Union[str, Path]) -> None:
    md = to_markdown(tree)
    path = Path(path)
    path.write_text(md, encoding="utf-8")

