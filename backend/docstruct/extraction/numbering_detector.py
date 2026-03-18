from __future__ import annotations

import re
from typing import List, Optional

from docstruct.core.schema import Span


NUMBERING_RE = re.compile(
    r"^("
    r"(?:\d+\.){1,5}\d*\.?\s+"
    r"|[A-Z]\.\s+"
    r"|\([a-zA-Z\d]+\)\s+"
    r"|(?:Chapter|Section|Part|Appendix|Article)\s+[\dA-Z]+"
    r")",
    re.IGNORECASE,
)


def detect_numbering(spans: List[Span]) -> None:
    """
    Populate has_numbering and numbering_str on spans in-place.
    """
    for span in spans:
        m = NUMBERING_RE.match(span.text)
        if m:
            span.has_numbering = True
            span.numbering_str = m.group(0)
        else:
            span.has_numbering = False
            span.numbering_str = ""


def parse_numbering(numbering_str: str) -> Optional[List[int]]:
    """
    Parse numbering prefix into a list of integers, where possible.
    """
    numbering_str = numbering_str.strip()

    m = re.match(r"(?:Chapter|Section|Part|Appendix|Article)\s+([\dA-Z]+)", numbering_str, re.IGNORECASE)
    if m:
        token = m.group(1)
        if token.isdigit():
            return [int(token)]
        if token.isalpha() and len(token) == 1:
            return [ord(token.upper()) - ord("A") + 1]

    # 1.2.3 style
    m = re.match(r"((?:\d+\.)+\d*)", numbering_str)
    if m:
        parts = m.group(1).strip(".").split(".")
        return [int(p) for p in parts if p.isdigit()]

    # A. / (a) / (1)
    m = re.match(r"^[A-Z]\.", numbering_str)
    if m:
        ch = numbering_str[0]
        return [ord(ch) - ord("A") + 1]

    m = re.match(r"^\(([a-zA-Z\d]+)\)", numbering_str)
    if m:
        token = m.group(1)
        if token.isdigit():
            return [int(token)]
        if token.isalpha() and len(token) == 1:
            return [ord(token.upper()) - ord("A") + 1]

    return None

