from __future__ import annotations

import re
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
        lines.append(_render_text_with_images(node.text).strip())
        lines.append("")

    # Render structured tables extracted from this node's page range
    for tbl in node.tables:
        if not tbl.markdown:
            # We'll handle fallback rendering further below.
            pass

        # Header line: caption (if any) or generic label, plus provenance
        if tbl.caption:
            header = f"**{tbl.caption}**"
        else:
            header = f"**Table {tbl.table_id}**"
        meta = f"*(p.{tbl.page}, {tbl.extraction_method} strategy)*"
        lines.append(f"{header} {meta}")
        lines.append("")

        if tbl.is_valid_table and tbl.markdown:
            lines.append(tbl.markdown)
            lines.append("")
            continue

        # Structured markdown wasn't trustworthy; fall back to rendered image.
        if tbl.path:
            label = tbl.caption or tbl.table_id
            lines.append(f"![{label}]({tbl.path})")
            lines.append("")

        # If we don't have either markdown or an image, we omit representation.

    used_filenames = {m.group(1) for m in IMG_MARKER_RE.finditer(node.text or "")}

    # Only render images not already represented by inline markers.
    remaining_images = []
    for img in node.images:
        if not img.path:
            continue
        filename = Path(img.path).name
        if filename not in used_filenames:
            remaining_images.append(img)

    for img in sorted(remaining_images, key=lambda im: (im.page, im.y0)):
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


IMG_MARKER_RE = re.compile(r"\{\{IMG:([^|}]*)\|([^|}]*)\|([^}]*)\}\}")


def _render_text_with_images(text: str) -> str:
    """
    Replace internal image markers inside `node.text` with real markdown images.
    """

    def _replace(m: re.Match[str]) -> str:
        filename = (m.group(1) or "").strip()
        label = (m.group(2) or "").strip()
        caption = (m.group(3) or "").strip()

        if not filename:
            return ""

        if not label:
            label = caption or "image"

        out = f"![{label}](assets/images/{filename})"
        if caption:
            out += f"\n*{caption}*"
        return out

    return IMG_MARKER_RE.sub(_replace, text or "")

