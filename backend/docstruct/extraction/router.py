from __future__ import annotations

from typing import Literal

from docstruct.core.schema import SourceFormat


Route = Literal["fast", "slow"]


def route_document(
    source_format: SourceFormat,
    has_outline: bool,
    heading_count: int,
) -> Route:
    """
    Decide whether to use the fast or slow path for a document.

    This is a simplified version of the pseudocode in the implementation plan.
    """
    if source_format == SourceFormat.PDF and has_outline:
        return "fast"

    if source_format == SourceFormat.DOCX and heading_count >= 2:
        return "fast"

    if source_format in (SourceFormat.HTML, SourceFormat.MARKDOWN) and heading_count >= 2:
        return "fast"

    if source_format == SourceFormat.EPUB:
        return "fast"

    if source_format == SourceFormat.PPTX:
        return "fast"

    return "slow"

