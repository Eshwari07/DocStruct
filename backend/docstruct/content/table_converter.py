from __future__ import annotations

import re
from typing import List, Tuple


def _clean_cell(text: str) -> str:
    """Normalise a single table cell value for safe GFM rendering."""
    # Collapse internal newlines / carriage returns to a single space
    text = re.sub(r"[\r\n]+", " ", text)
    # Collapse runs of whitespace
    text = re.sub(r" {2,}", " ", text)
    text = text.strip()
    # Escape pipe characters so they don't break GFM column delimiters
    text = text.replace("|", r"\|")
    return text


def _is_empty_row(row: List[str]) -> bool:
    return all(c == "" for c in row)


def _col_widths(rows: List[List[str]], n_cols: int) -> List[int]:
    """Return the maximum display width for each column across all rows."""
    widths = [3] * n_cols  # minimum 3 chars for the separator
    for row in rows:
        for i, cell in enumerate(row[:n_cols]):
            widths[i] = max(widths[i], len(cell))
    return widths


def table_to_markdown(table_data: List[List[str]]) -> str:
    """
    Convert a 2-D list of strings into a GitHub-Flavoured Markdown table.

    - First row is treated as the header.
    - Cells are sanitised: pipes escaped, newlines collapsed.
    - Entirely-empty rows are skipped.
    - All rows are padded/truncated to the header column count.
    - Columns are width-padded for readability in raw markdown.
    """
    if not table_data:
        return ""

    # Clean every cell
    cleaned: List[List[str]] = [
        [_clean_cell(c) for c in row] for row in table_data
    ]

    # Drop rows that are entirely empty after cleaning
    cleaned = [row for row in cleaned if not _is_empty_row(row)]
    if not cleaned:
        return ""

    header_row = cleaned[0]
    n_cols = len(header_row)
    if n_cols == 0:
        return ""

    data_rows = cleaned[1:]

    # Pad or truncate every row to the header column count
    def _normalise(row: List[str]) -> List[str]:
        if len(row) < n_cols:
            return row + [""] * (n_cols - len(row))
        return row[:n_cols]

    header_row = _normalise(header_row)
    data_rows = [_normalise(r) for r in data_rows]

    # Re-filter data rows that are entirely empty after normalisation
    data_rows = [r for r in data_rows if not _is_empty_row(r)]

    all_rows = [header_row] + data_rows
    widths = _col_widths(all_rows, n_cols)

    def _fmt_row(row: List[str]) -> str:
        cells = [cell.ljust(widths[i]) for i, cell in enumerate(row)]
        return "| " + " | ".join(cells) + " |"

    separator = "| " + " | ".join("-" * w for w in widths) + " |"

    lines: List[str] = [_fmt_row(header_row), separator]
    for row in data_rows:
        lines.append(_fmt_row(row))

    return "\n".join(lines)


def table_to_markdown_and_parts(
    table_data: List[List[str]],
) -> Tuple[List[str], List[List[str]], str]:
    """
    Like table_to_markdown but also returns the cleaned headers and data rows
    so callers can populate a TableBlock without re-parsing the markdown.

    Returns: (headers, rows, markdown_string)
    """
    if not table_data:
        return [], [], ""

    cleaned: List[List[str]] = [
        [_clean_cell(c) for c in row] for row in table_data
    ]
    cleaned = [row for row in cleaned if not _is_empty_row(row)]
    if not cleaned:
        return [], [], ""

    header_row = cleaned[0]
    n_cols = len(header_row)
    if n_cols == 0:
        return [], [], ""

    data_rows = cleaned[1:]

    def _normalise(row: List[str]) -> List[str]:
        if len(row) < n_cols:
            return row + [""] * (n_cols - len(row))
        return row[:n_cols]

    header_row = _normalise(header_row)
    data_rows = [_normalise(r) for r in data_rows]
    data_rows = [r for r in data_rows if not _is_empty_row(r)]

    all_rows = [header_row] + data_rows
    widths = _col_widths(all_rows, n_cols)

    def _fmt_row(row: List[str]) -> str:
        cells = [cell.ljust(widths[i]) for i, cell in enumerate(row)]
        return "| " + " | ".join(cells) + " |"

    separator = "| " + " | ".join("-" * w for w in widths) + " |"
    lines: List[str] = [_fmt_row(header_row), separator]
    for row in data_rows:
        lines.append(_fmt_row(row))

    return header_row, data_rows, "\n".join(lines)
