from __future__ import annotations

from typing import List

from docstruct.core.schema import DocumentTree, Span
from docstruct.extraction.tree_builder import HeadingCandidate, build_tree


def populate_text_for_pdf(tree: DocumentTree, spans: List[Span]) -> None:
    """
    Populate node.text for PDF documents based on detected heading spans.

    This is a simplified implementation that:
    - assumes spans corresponding to headings have heading_score >= 0.65
    - builds a temporary tree from heading candidates and aligns it with the
      existing tree structure by section_id.
    """
    # Build mapping from (page, text) to span for quick lookup if needed
    # For now, we simply aggregate body text into the deepest node whose page range contains it.
    flat_nodes = tree.flat_list()

    def find_node_for_page(page: int) -> List[int]:
        indices: List[int] = []
        for idx, node in enumerate(flat_nodes):
            if node.pages and node.pages.physical_start <= page <= node.pages.physical_end:
                indices.append(idx)
        return indices

    for span in spans:
        # Heuristic: treat spans with low heading_score as body text
        if span.heading_score >= 0.65:
            continue
        candidate_indices = find_node_for_page(span.page)
        if not candidate_indices:
            continue
        # Use the deepest node (last in flat list with matching page range)
        target = flat_nodes[candidate_indices[-1]]
        text = span.text.strip()
        if not text:
            continue
        if target.text:
            target.text += "\n\n" + text
        else:
            target.text = text

