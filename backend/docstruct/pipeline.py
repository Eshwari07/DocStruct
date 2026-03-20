from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Callable, Optional

import fitz

from docstruct.core.config import DocStructConfig
from docstruct.core.schema import DocumentTree, ExtractionPath, SourceFormat
from docstruct.parsers.base import BaseParser
from docstruct.parsers.pdf_parser import PdfParser
from docstruct.parsers.docx_parser import DocxParser
from docstruct.parsers.html_parser import HtmlParser, MarkdownParser
from docstruct.parsers.epub_parser import EpubParser
from docstruct.parsers.pptx_parser import PptxParser
from docstruct.content.image_extractor import extract_images_from_pdf
from docstruct.content.pdf_table_extractor import extract_tables_from_pdf

logger = logging.getLogger(__name__)


def _pdf_has_usable_outline(file_path: Path) -> bool:
    """Return True if the PDF has at least 2 TOC / bookmark entries."""
    try:
        with fitz.open(str(file_path)) as doc:
            toc = doc.get_toc(simple=True)
            return len(toc) >= 2
    except Exception:
        return False


def _vlm_available() -> bool:
    """Return True if an OpenRouter API key is configured."""
    return bool(os.environ.get("OPENROUTER_API_KEY", "").strip())


class DocStructPipeline:
    """
    High-level entry point for DocStruct.

    Responsibilities:
    - Detect source format from file extension
    - Route to the appropriate parser (fast / slow / VLM)
    - Return a finalised DocumentTree
    """

    FORMAT_MAP = {
        ".pdf": SourceFormat.PDF,
        ".docx": SourceFormat.DOCX,
        ".doc": SourceFormat.DOCX,
        ".html": SourceFormat.HTML,
        ".htm": SourceFormat.HTML,
        ".md": SourceFormat.MARKDOWN,
        ".markdown": SourceFormat.MARKDOWN,
        ".epub": SourceFormat.EPUB,
        ".pptx": SourceFormat.PPTX,
        ".ppt": SourceFormat.PPTX,
        # Image formats — VLM path only
        ".png": SourceFormat.IMAGE,
        ".jpg": SourceFormat.IMAGE,
        ".jpeg": SourceFormat.IMAGE,
        ".tiff": SourceFormat.IMAGE,
        ".tif": SourceFormat.IMAGE,
    }

    def process(
        self,
        file_path: str | Path,
        *,
        artifact_dir: Optional[Path] = None,
        config: Optional[DocStructConfig] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> DocumentTree:
        path = Path(file_path)
        fmt = self._detect_format(path)
        use_vlm = False

        if fmt == SourceFormat.IMAGE:
            if not _vlm_available():
                raise ValueError(
                    "Image files require VLM processing but OPENROUTER_API_KEY is not set."
                )
            use_vlm = True

        elif fmt == SourceFormat.PDF:
            has_outline = _pdf_has_usable_outline(path)
            if not has_outline and _vlm_available():
                logger.info("PDF has no usable outline — routing to VLM path.")
                use_vlm = True
            elif not has_outline:
                logger.warning(
                    "PDF has no outline and VLM is unavailable — falling back to heuristic slow path."
                )

        if use_vlm:
            from docstruct.parsers.vlm_parser import VlmParser
            parser = VlmParser(
                path,
                source_format=fmt,
                progress_callback=progress_callback,
            )
            tree = parser.parse()

            if fmt == SourceFormat.PDF and artifact_dir is not None:
                assets_images_dir = artifact_dir / "assets" / "images"
                tables_dir = artifact_dir / "assets" / "tables"

                vlm_table_count = sum(len(n.tables) for n in tree.flat_list())

                if vlm_table_count > 0:
                    logger.debug(
                        "VLM found %d tables; skipping pdfplumber table extraction.",
                        vlm_table_count,
                    )
                    extract_images_from_pdf(
                        tree, path, assets_images_dir, table_bboxes={}
                    )
                else:
                    logger.debug("VLM found no tables; running pdfplumber as fallback.")
                    table_bboxes = extract_tables_from_pdf(
                        tree, path, output_dir=tables_dir
                    )
                    extract_images_from_pdf(
                        tree, path, assets_images_dir, table_bboxes=table_bboxes
                    )

            return tree

        parser = self._get_parser(fmt, path, config=config)
        tree = parser.parse()

        if fmt == SourceFormat.PDF and artifact_dir is not None:
            assets_images_dir = artifact_dir / "assets" / "images"
            tables_dir = artifact_dir / "assets" / "tables"
            table_bboxes = extract_tables_from_pdf(
                tree, path, output_dir=tables_dir
            )
            extract_images_from_pdf(
                tree, path, assets_images_dir, table_bboxes=table_bboxes
            )
        return tree

    def _detect_format(self, path: Path) -> SourceFormat:
        suffix = path.suffix.lower()
        fmt = self.FORMAT_MAP.get(suffix)
        if fmt is None:
            raise ValueError(f"Unsupported file format: {suffix or '<no extension>'}")
        return fmt

    def _get_parser(self, fmt: SourceFormat, path: Path, config: Optional[DocStructConfig] = None) -> BaseParser:
        if fmt == SourceFormat.PDF:
            return PdfParser(path, config=config)
        if fmt == SourceFormat.DOCX:
            return DocxParser(path)
        if fmt == SourceFormat.HTML:
            return HtmlParser(path)
        if fmt == SourceFormat.MARKDOWN:
            return MarkdownParser(path)
        if fmt == SourceFormat.EPUB:
            return EpubParser(path)
        if fmt == SourceFormat.PPTX:
            return PptxParser(path)
        raise ValueError(f"No parser implemented for format: {fmt.value}")

