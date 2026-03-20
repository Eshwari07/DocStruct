from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class DocType(str, Enum):
    AUTO = "auto"
    LEGAL = "legal"
    ACADEMIC = "academic"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    FORM = "form"
    GENERAL = "general"


@dataclass
class DocStructConfig:
    # Slow path heading detection
    heading_threshold: float = 0.65
    unnumbered_heading_threshold: float = 0.80
    max_heading_words: int = 20
    min_heading_word_count: int = 1
    font_cluster_k_range: Tuple[int, int] = (2, 6)

    # Multi-column layout
    enable_column_detection: bool = True

    # Paragraph grouping
    paragraph_y_gap_factor: float = 1.5

    # Metadata zone (title/author region on first page)
    metadata_zone_page: int = 1
    metadata_zone_fraction: float = 0.25

    # OCR
    ocr_enabled: bool = False
    ocr_engine: str = "tesseract"  # or "paddleocr"
    ocr_language: str = "eng"

    # Output
    output_images: bool = True
    image_format: str = "png"
    include_phantoms: bool = False

    # Performance
    max_pages: Optional[int] = None
    timeout_sec: Optional[int] = 60

    # Routing
    fast_path_min_headings: int = 2

    # Document type (VLM prompt routing)
    doc_type: DocType = DocType.AUTO

