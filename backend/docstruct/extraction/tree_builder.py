from __future__ import annotations

from dataclasses import dataclass
from typing import List

from docstruct.core.schema import DocNode, PageRange


@dataclass
class HeadingCandidate:
    level: int
    title: str
    pages: PageRange
    confidence: float


def build_tree(candidates: List[HeadingCandidate], total_pages: int, slow_path: bool = True) -> List[DocNode]:
    """
    Stack-based tree construction with optional phantom node insertion for gaps.
    """
    root_nodes: List[DocNode] = []
    stack: List[tuple[int, DocNode]] = []

    for cand in candidates:
        level = cand.level

        node = DocNode(
            title=cand.title,
            text="",
            pages=cand.pages,
            confidence=cand.confidence,
            images=[],
            children=[],
        )

        # Gap handling (slow path only): insert phantom nodes for skipped levels
        if slow_path and stack and level > stack[-1][0] + 1:
            for phantom_level in range(stack[-1][0] + 1, level):
                phantom = DocNode(
                    title="[implied section]",
                    text="",
                    pages=cand.pages,
                    confidence=0.0,
                    images=[],
                    children=[],
                )
                phantom._is_phantom = True
                stack[-1][1].add_child(phantom)
                stack.append((phantom_level, phantom))

        while stack and stack[-1][0] >= level:
            stack.pop()

        if stack:
            stack[-1][1].add_child(node)
        else:
            root_nodes.append(node)

        stack.append((level, node))

    # Page range resolution (simple pass: ensure physical_end is at least start)
    for node in root_nodes:
        _resolve_page_ranges(node, total_pages)

    return root_nodes


def _resolve_page_ranges(node: DocNode, total_pages: int) -> int:
    """
    Ensure physical_end is set based on children, returning this node's end page.
    """
    if not node.children:
        if node.pages is None:
            node.pages = PageRange(physical_start=1, physical_end=total_pages)
        else:
            if node.pages.physical_end < node.pages.physical_start:
                node.pages.physical_end = node.pages.physical_start
        return node.pages.physical_end

    max_end = 0
    for child in node.children:
        end = _resolve_page_ranges(child, total_pages)
        if end > max_end:
            max_end = end

    if node.pages is None:
        node.pages = PageRange(physical_start=1, physical_end=max_end or total_pages)
    else:
        node.pages.physical_end = max(node.pages.physical_end, max_end or node.pages.physical_end)

    return node.pages.physical_end

