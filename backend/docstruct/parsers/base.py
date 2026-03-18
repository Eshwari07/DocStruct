from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from docstruct.core.schema import DocumentTree


class BaseParser(ABC):
    """
    Abstract base class for all format-specific parsers.

    Responsibilities:
    - Build a DocumentTree with nodes (no responsibility for ID assignment)
    - Set source_file, source_format, total_pages, extracted_at, extraction_path
    - Call tree.finalise() before returning
    - Never write files or call serializers
    """

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)

    @abstractmethod
    def parse(self) -> DocumentTree:
        """
        Parse the input file and return a fully initialised DocumentTree.
        Implementations must call tree.finalise() before returning.
        """
        raise NotImplementedError

