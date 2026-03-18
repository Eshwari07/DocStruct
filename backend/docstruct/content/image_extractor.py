from __future__ import annotations

from pathlib import Path
from typing import List

import fitz  # type: ignore[import]  # pymupdf

from docstruct.core.schema import DocumentTree, ImageRef


def extract_images_from_pdf(tree: DocumentTree, file_path: Path, output_dir: Path) -> None:
    """
    Extract images from a PDF and attach them to the deepest node whose page range
    contains the image's page.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(file_path)  # type: ignore[arg-type]

    for page_num in range(1, doc.page_count + 1):
        page = doc.load_page(page_num - 1)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            img_ext = base_image.get("ext", "png")
            img_filename = f"p{page_num}_img{img_index + 1}.{img_ext}"
            img_path = output_dir / img_filename
            img_path.write_bytes(img_bytes)

            # Assign to deepest node whose page range contains page_num
            target = _find_deepest_node_for_page(tree, page_num)
            if not target:
                continue

            if target.images is None:
                target.images = []
            target.images.append(
                ImageRef(
                    label="",
                    caption="",
                    path=f"assets/{img_filename}",
                )
            )


def _find_deepest_node_for_page(tree: DocumentTree, page: int):
    best = None
    best_depth = -1
    for node in tree.flat_list():
        if node.pages and node.pages.physical_start <= page <= node.pages.physical_end:
            if node.depth > best_depth:
                best = node
                best_depth = node.depth
    return best

