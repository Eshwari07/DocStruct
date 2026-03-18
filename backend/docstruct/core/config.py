from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class DocStructConfig:
    # Slow path heading detection
    heading_threshold: float = 0.65
    max_heading_words: int = 20
    font_cluster_k_range: Tuple[int, int] = (2, 6)

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

