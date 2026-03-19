from __future__ import annotations

import bisect
from collections import defaultdict
from typing import Dict, List, Tuple

from docstruct.core.schema import DocumentTree, DocNode, Span


def populate_text_for_pdf(
    tree: DocumentTree,
    all_spans: List[Span],
    heading_spans: List[Span],
    heading_nodes: List[DocNode],
) -> None:
    """
    Populate ``node.text`` for every section in a slow-path PDF tree.

    Algorithm
    ---------
    1. Build *heading anchors* — ``(page, effective_column, y1, node)`` — from
       the heading spans that were promoted to tree nodes.  Full-width headings
       (``column == -1``) are duplicated into both column 0 and column 1 so they
       act as dividers for all body text below them.
    2. Sort anchors by ``(page, column, y1)`` and use ``bisect`` to answer:
       "which heading is immediately above this body span?" in O(log n).
    3. Accumulate body spans per owning node, grouping consecutive spans that
       share the same ``(page, block_index)`` into paragraphs joined with ``" "``,
       separated by ``"\\n\\n"`` at block boundaries.
    """
    if not heading_spans or not heading_nodes:
        return

    heading_span_ids = set(id(s) for s in heading_spans)

    # --- 1. Build column-aware heading anchors ---
    anchors: List[Tuple[int, int, float, DocNode]] = []  # (page, col, y1, node)

    for span, node in zip(heading_spans, heading_nodes):
        page = span.page
        y1 = span.bbox[3]

        if span.column == -1:
            anchors.append((page, 0, y1, node))
            anchors.append((page, 1, y1, node))
        else:
            anchors.append((page, span.column, y1, node))

    anchors.sort(key=lambda a: (a[0], a[1], a[2]))
    anchor_keys = [(a[0], a[1], a[2]) for a in anchors]

    # --- 2. Spatial lookup via binary search ---
    def _find_owning_node(span_page: int, span_col: int, span_y0: float) -> DocNode | None:
        key = (span_page, span_col, span_y0)
        idx = bisect.bisect_right(anchor_keys, key) - 1
        if idx < 0:
            return None
        return anchors[idx][3]

    # --- 3. Assign body spans to nodes ---
    node_body: Dict[str, List[Span]] = defaultdict(list)

    for span in all_spans:
        if id(span) in heading_span_ids:
            continue

        col = span.column if span.column >= 0 else 0
        node = _find_owning_node(span.page, col, span.bbox[1])
        if node is None:
            # Body text above the very first heading (metadata / title area) — skip
            continue
        node_body[node.id].append(span)

    # --- 4. Paragraph grouping and text assembly ---
    for node in tree.flat_list():
        body_spans = node_body.get(node.id)
        if not body_spans:
            continue

        body_spans.sort(key=lambda s: (s.page, max(s.column, 0), s.bbox[1]))

        paragraphs: List[str] = []
        current_lines: List[str] = []
        prev_block_key: Tuple[int, int] | None = None  # (page, block_index)

        for span in body_spans:
            block_key = (span.page, span.block_index)
            if prev_block_key is not None and block_key != prev_block_key:
                paragraphs.append(" ".join(current_lines))
                current_lines = []
            current_lines.append(span.text.strip())
            prev_block_key = block_key

        if current_lines:
            paragraphs.append(" ".join(current_lines))

        node.text = "\n\n".join(p for p in paragraphs if p)
