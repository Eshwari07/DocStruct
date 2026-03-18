from __future__ import annotations

from typing import List

from docstruct.core.schema import Span


def rule_based_heading_score(span: Span, median_font_size: float, median_line_height: float) -> float:
    """
    Simple rule-based heading score as described in the implementation plan.
    """
    score = 0.0

    if span.font_size > median_font_size * 1.1:
        score += 0.3
    if span.is_bold:
        score += 0.2
    if span.word_count < 12:
        score += 0.15
    if not span.text.strip().endswith((".", "!", "?")):
        score += 0.1
    if span.space_above > median_line_height:
        score += 0.15
    if span.has_numbering:
        score += 0.2

    return min(score, 1.0)


def score_headings(spans: List[Span], median_font_size: float, median_line_height: float) -> None:
    """
    Populate heading_score on spans in-place using the rule-based scorer.
    """
    for span in spans:
        span.heading_score = rule_based_heading_score(span, median_font_size, median_line_height)

