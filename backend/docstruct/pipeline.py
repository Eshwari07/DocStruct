from __future__ import annotations

from pathlib import Path
from typing import Optional

from docstruct.core.schema import DocumentTree, SourceFormat
from docstruct.parsers.base import BaseParser
from docstruct.parsers.pdf_parser import PdfParser
from docstruct.parsers.docx_parser import DocxParser
from docstruct.parsers.html_parser import HtmlParser, MarkdownParser
from docstruct.parsers.epub_parser import EpubParser
from docstruct.parsers.pptx_parser import PptxParser
from docstruct.content.image_extractor import extract_images_from_pdf
from docstruct.content.pdf_table_extractor import extract_tables_from_pdf


class DocStructPipeline:
    """
    High-level entry point for DocStruct.

    Responsibilities:
    - Detect source format from file extension
    - Route to the appropriate parser
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
    }

    def process(self, file_path: str | Path, *, artifact_dir: Optional[Path] = None) -> DocumentTree:
        path = Path(file_path)
        fmt = self._detect_format(path)
        parser = self._get_parser(fmt, path)
        tree = parser.parse()
        if fmt == SourceFormat.PDF and artifact_dir is not None:
            assets_dir = artifact_dir / "assets"
            # Tables must be extracted first so their bounding boxes can be
            # passed to the image extractor, preventing table borders from
            # being re-captured as vector diagram images.
            table_bboxes = extract_tables_from_pdf(tree, path)
            extract_images_from_pdf(tree, path, assets_dir, table_bboxes=table_bboxes)
        return tree

    def _detect_format(self, path: Path) -> SourceFormat:
        suffix = path.suffix.lower()
        fmt = self.FORMAT_MAP.get(suffix)
        if fmt is None:
            raise ValueError(f"Unsupported file format: {suffix or '<no extension>'}")
        return fmt

    def _get_parser(self, fmt: SourceFormat, path: Path) -> BaseParser:
        if fmt == SourceFormat.PDF:
            return PdfParser(path)
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

