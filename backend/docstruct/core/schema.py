from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, List, Optional, Dict, Any


class NodeType(str, Enum):
    ROOT = "root"
    PARENT = "parent"
    CHILD = "child"


class ExtractionPath(str, Enum):
    FAST = "fast"
    SLOW = "slow"
    MIXED = "mixed"


class SourceFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "markdown"
    EPUB = "epub"
    PPTX = "pptx"
    IMAGE = "image"


@dataclass
class ImageRef:
    label: str = ""
    caption: str = ""
    path: str = ""


@dataclass
class TableBlock:
    """Structured representation of a single extracted table."""
    table_id: str                                      # e.g. "p3_t1"
    caption: str = ""                                  # e.g. "Table 1: Revenue Summary"
    page: int = 0                                      # physical page number
    headers: List[str] = field(default_factory=list)   # first row treated as headers
    rows: List[List[str]] = field(default_factory=list) # data rows (excluding header)
    markdown: str = ""                                 # pre-computed GFM table string
    extraction_method: str = ""                        # "lines", "text", "mixed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_id": self.table_id,
            "caption": self.caption,
            "page": self.page,
            "headers": self.headers,
            "rows": self.rows,
            "markdown": self.markdown,
            "extraction_method": self.extraction_method,
        }


@dataclass
class PageRange:
    physical_start: int
    physical_end: int
    logical_start: Optional[str] = None
    logical_end: Optional[str] = None


@dataclass
class DocNode:
    title: str
    text: str = ""
    pages: PageRange | None = None
    confidence: float = 1.0
    images: List[ImageRef] = field(default_factory=list)
    tables: List[TableBlock] = field(default_factory=list)
    children: List["DocNode"] = field(default_factory=list)

    # Assigned during finalisation
    id: str = ""
    section_id: str = ""
    depth: int = 1
    node_type: NodeType = NodeType.CHILD

    # Internal bookkeeping (not serialised)
    _parent: Optional["DocNode"] = field(default=None, repr=False, compare=False)
    _is_phantom: bool = field(default=False, repr=False, compare=False)

    def add_child(self, node: "DocNode") -> None:
        node._parent = self
        self.children.append(node)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def iter_all(self) -> Iterator["DocNode"]:
        yield self
        for child in self.children:
            yield from child.iter_all()

    def recompute_type(self) -> None:
        if self._parent is None:
            self.node_type = NodeType.ROOT
        elif self.children:
            self.node_type = NodeType.PARENT
        else:
            self.node_type = NodeType.CHILD

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "section_id": self.section_id,
            "depth": self.depth,
            "node_type": self.node_type.value,
            "title": self.title,
            "text": self.text,
            "pages": {
                "physical_start": self.pages.physical_start if self.pages else None,
                "physical_end": self.pages.physical_end if self.pages else None,
                "logical_start": self.pages.logical_start if self.pages else None,
                "logical_end": self.pages.logical_end if self.pages else None,
            }
            if self.pages
            else {
                "physical_start": None,
                "physical_end": None,
                "logical_start": None,
                "logical_end": None,
            },
            "confidence": float(self.confidence),
            "images": [
                {
                    "label": img.label,
                    "caption": img.caption,
                    "path": img.path,
                }
                for img in self.images
            ],
            "tables": [tbl.to_dict() for tbl in self.tables],
            "children": [child.to_dict() for child in self.children],
        }


@dataclass
class Span:
    # Content
    text: str
    word_count: int

    # Typography
    font_size: float
    is_bold: bool
    is_italic: bool
    is_caps: bool
    font_name: str

    # Geometry
    bbox: tuple[float, float, float, float]
    space_above: float
    space_below: float
    line_height: float

    # Location
    page: int

    # Pre-computed signals
    has_numbering: bool
    numbering_str: str
    is_standalone: bool

    # Source metadata
    source_format: str

    # Filled by classifier
    heading_score: float = 0.0
    assigned_level: int = 0


@dataclass
class DocumentTree:
    source_file: str
    source_format: SourceFormat
    total_pages: int
    extracted_at: str
    extraction_path: ExtractionPath
    nodes: List[DocNode] = field(default_factory=list)

    def finalise(self) -> None:
        self._assign_section_ids()
        self._assign_flat_ids()
        for node in self.flat_list():
            node.recompute_type()

    def _assign_section_ids(self) -> None:
        def walk(nodes: List[DocNode], prefix: str = "") -> None:
            for index, node in enumerate(nodes, start=1):
                node.section_id = f"{prefix}{index}" if prefix else str(index)
                node.depth = node.section_id.count(".") + 1
                walk(node.children, f"{node.section_id}.")

        walk(self.nodes)

    def _assign_flat_ids(self) -> None:
        counter = 0
        for node in self.flat_list():
            counter += 1
            node.id = f"{counter:04d}"

    def get_by_id(self, node_id: str) -> Optional[DocNode]:
        for node in self.flat_list():
            if node.id == node_id:
                return node
        return None

    def get_by_section_id(self, section_id: str) -> Optional[DocNode]:
        for node in self.flat_list():
            if node.section_id == section_id:
                return node
        return None

    def flat_list(self) -> List[DocNode]:
        result: List[DocNode] = []
        for node in self.nodes:
            result.extend(list(node.iter_all()))
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document": {
                "source_file": self.source_file,
                "source_format": self.source_format.value,
                "total_pages": self.total_pages,
                "extracted_at": self.extracted_at,
                "extraction_path": self.extraction_path.value,
                "nodes": [node.to_dict() for node in self.nodes],
            }
        }

    def remove_phantoms(self) -> None:
        def filter_children(node: DocNode) -> None:
            node.children = [child for child in node.children if not child._is_phantom]
            for child in node.children:
                filter_children(child)

        self.nodes = [node for node in self.nodes if not node._is_phantom]
        for node in self.nodes:
            filter_children(node)

