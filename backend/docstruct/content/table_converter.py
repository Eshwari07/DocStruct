from __future__ import annotations

from typing import List


def table_to_markdown(table_data: List[List[str]]) -> str:
    """
    Convert a simple 2D list of strings into a GitHub-flavoured markdown table.

    First row is treated as header.
    """
    if not table_data:
        return ""

    header = table_data[0]
    separator = ["-" * max(3, len(h)) for h in header]
    rows = table_data[1:]

    lines: List[str] = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(separator) + " |")

    for row in rows:
        padded = row + [""] * (len(header) - len(row))
        lines.append("| " + " | ".join(padded[: len(header)]) + " |")

    return "\n".join(lines)

