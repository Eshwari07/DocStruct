from __future__ import annotations

from typing import Dict, Optional

import re


ROMAN_RE = re.compile(r"^(x{0,3})(ix|iv|v?i{0,3})$", re.IGNORECASE)
PAGE_NUM_RE = re.compile(r"^\d+$")


def detect_logical_page_numbers(page_texts: Dict[int, str]) -> Dict[int, Optional[str]]:
    """
    For each physical page, try to find the printed page number.

    Checks top 3 and bottom 3 non-empty lines. Returns a mapping
    physical_page -> logical_page (string) or None.
    """
    result: Dict[int, Optional[str]] = {}
    for phys, text in page_texts.items():
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if len(lines) > 6:
            candidates = lines[:3] + lines[-3:]
        else:
            candidates = lines

        logical: Optional[str] = None
        for candidate in candidates:
            if PAGE_NUM_RE.match(candidate):
                logical = candidate
                break
            if ROMAN_RE.match(candidate):
                logical = candidate.lower()
                break

        result[phys] = logical
    return result

