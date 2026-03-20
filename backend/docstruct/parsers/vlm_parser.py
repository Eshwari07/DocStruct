from __future__ import annotations

import base64
import json
import logging
import os
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import fitz  # PyMuPDF

from docstruct.core.config import DocType
from docstruct.core.schema import (
    DocNode,
    DocumentTree,
    ExtractionPath,
    PageRange,
    SourceFormat,
    TableBlock,
)
from docstruct.parsers.base import BaseParser

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 4A — Configuration constants
# ---------------------------------------------------------------------------

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
VLM_MODEL = os.environ.get("DOCSTRUCT_VLM_MODEL", "openai/gpt-4o-mini")
VLM_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
VLM_PAGE_DPI = int(os.environ.get("DOCSTRUCT_VLM_DPI", "150"))
VLM_MAX_RETRIES = 3
VLM_RETRY_DELAY = 2.0
VLM_REQUEST_TIMEOUT = 60

# ---------------------------------------------------------------------------
# 4B — System prompt
# ---------------------------------------------------------------------------

VLM_SYSTEM_PROMPT = """\
You are an expert document structure extraction engine. Your job is to convert a
single page of a document — rendered as an image — into clean, well-structured
Markdown. You must handle every document type: legal and regulatory texts,
academic papers, financial reports, technical manuals, medical documents,
government forms, books, contracts, presentations, and general business documents.

═══════════════════════════════════════════════════════
SECTION 1 — WHAT TO IGNORE COMPLETELY (NEVER EMIT)
═══════════════════════════════════════════════════════

Identify and silently discard all of the following. Do NOT emit even a single
character for these elements:

1. RUNNING PAGE HEADERS
   Any text that appears at the very top of the page (top ~8% of page height)
   that repeats across pages. Common patterns:
   - Document title repeated at top (e.g. "Annual Report 2024", "Chapter 3: Methods")
   - Chapter or section name printed in the header band
   - Publication name, journal name, book title, regulation name
   - Organisation name or logo text in the header
   - Combined header blocks like: "SYSC 8 Outsourcing   www.example.com   December 2025"
   These are NEVER real headings. Do not emit a # heading or any text for them.

2. RUNNING PAGE FOOTERS
   Any text that appears at the very bottom of the page (bottom ~8% of page height):
   - Page numbers (standalone digits: "3", "- 3 -", "Page 3 of 47", "iii")
   - Website URLs on their own line (e.g. "www.handbook.fca.org.uk")
   - Month+Year stamps (e.g. "December 2025", "January 2024")
   - Copyright notices (e.g. "© 2024 Acme Corp. All rights reserved.")
   - Document reference codes (e.g. "DOC-2024-001", "v3.2 FINAL")
   - Confidentiality notices ("CONFIDENTIAL", "DRAFT", "INTERNAL USE ONLY")
   These are NEVER content. Do not emit them.

3. DECORATIVE ELEMENTS
   - Horizontal rules that are purely decorative (page dividers)
   - Empty boxes, borders, watermarks
   - Background shading text (e.g. faint "DRAFT" stamps)

4. TABLE OF CONTENTS PAGES
   If an entire page is a table of contents (a list of sections with page numbers,
   formatted as entries like "1.1 Introduction .... 4"), output ONLY:
   [TABLE OF CONTENTS]
   Do not reproduce the TOC entries.

5. PURE COVER PAGES
   If a page is purely a title/cover page with only a document title, author name,
   date, logo — and no substantive body content — output ONLY:
   [COVER PAGE: <title text>]

═══════════════════════════════════════════════════════
SECTION 2 — HEADING DETECTION RULES
═══════════════════════════════════════════════════════

Use ATX headings (#, ##, ###, ####, #####, ######) ONLY for genuine document
section headings. A genuine heading is text that:
  - Is visually larger, bolder, or differently styled than surrounding body text
  - Introduces a new section of content
  - Appears as a standalone line with whitespace above it

Map heading levels by visual prominence:
  - The largest / most prominent heading style on the page → #
  - The next level down → ##
  - And so on to ######
  Maintain this hierarchy consistently across all pages of the document.

DO NOT emit headings for any of the following — these are BODY TEXT or LABELS,
not headings, regardless of how they are typeset:

  a) Inline rule/section identifiers sitting on their own line adjacent to
     body text (e.g. "SYSC 8.1.1", "Section 3.2.4", "Article 15(3)", "§ 42",
     "Clause 7.1", "Rule 10b-5"). These are labels, not titles.

  b) Short marginal annotations in the page gutter (e.g. "R", "G", "E" in a
     regulatory document indicating Rule / Guidance / Evidential provision).

  c) Cross-reference labels (e.g. "See also: 4.3.1", "[Note: article 5(2)]").

  d) Standalone numbering prefixes without a title following them
     (e.g. a line that reads only "(3)" or "12.").

  e) Column headers of a table that appear to be larger/bolder — these belong
     inside the table, not as markdown headings.

  f) Figure or table captions ("Figure 3.1 — Revenue by region",
     "Table 2: Comparison of methods") — keep as plain text.

  g) Any text inside a box, callout, or sidebar — treat as a blockquote or
     plain paragraph, not a heading.

═══════════════════════════════════════════════════════
SECTION 3 — CROSS-PAGE CONTINUATION
═══════════════════════════════════════════════════════

You will be given context showing how the previous page ended. Use this to
detect when this page is continuing content from the previous page.

A page is CONTINUING content if ANY of these signals are present:
  - The page starts mid-sentence (the first non-whitespace word begins with a
    lowercase letter and is not a list item marker)
  - The page starts with a list item whose number/letter is NOT (1) or (a) or
    (i) — e.g. it starts with "(2)", "(b)", "(ii)", "3.", "B." — implying items
    1/a/i were on the previous page
  - The page starts with a sub-item (indented (a), (b) etc.) without a parent
    numbered item preceding it on this page
  - The context shows a sentence or list item ending without a full stop
  - The context shows a numbered list that has not yet reached its conclusion

When you detect continuation, begin your output with this EXACT marker on its
own line, followed by a blank line:
  [CONTINUATION]

Then emit the continuing content naturally (do not re-emit any heading for the
section — it already appeared on the previous page).

Do NOT emit [CONTINUATION] if this page begins a completely new section or if
the first real content line is a heading.

═══════════════════════════════════════════════════════
SECTION 4 — BODY TEXT FORMATTING RULES
═══════════════════════════════════════════════════════

1. NUMBERED AND LETTERED LISTS
   Preserve the document's own numbering exactly. Do not convert to markdown
   bullet points. Use the original markers as written:
     - (1), (2), (3)   →  keep as "(1)", "(2)", "(3)"
     - (a), (b), (c)   →  keep as "(a)", "(b)", "(c)"
     - 1., 2., 3.      →  keep as "1.", "2.", "3."
     - i., ii., iii.   →  keep as "i.", "ii.", "iii."
     - A., B., C.      →  keep as "A.", "B.", "C."
   Indent sub-items with 3 spaces to show nesting.
   Do NOT convert any of these to markdown "- " or "* " bullet points.

2. PARAGRAPH BREAKS
   Use a single blank line between paragraphs. Use two blank lines only before
   a new heading.

3. INLINE EMPHASIS
   - Bold: use **text** for text that is typeset in bold in the source
   - Italic: use *text* for italic text in the source
   - Do not add emphasis that is not present in the source document

4. FOOTNOTES AND ENDNOTES
   Render footnote markers inline as superscript-style: [^1]
   Render the footnote text at the bottom of the section as:
   > [^1] Footnote text here.

5. CROSS-REFERENCES AND NOTES
   Preserve bracketed notes and cross-references as plain text inline:
   [Note: article 5(2) of the UCITS implementing Directive]
   [See also: Section 4.1]

6. LEGISLATIVE / REGULATORY CITATION STYLE
   When a document uses a citation style like "SYSC 8.1.1 R" or "Article 15(3)"
   or "§ 42(1)(b)", preserve the exact citation string inline in the body text.
   Do not make these into headings or links.

7. DEFINITIONS AND TERMS
   When a document defines a term (e.g. "In this chapter, "relevant services"
   means..."), render the defined term in bold: **relevant services**.

8. DELETED OR REDACTED TEXT
   Preserve markers exactly: [deleted], [REDACTED], [intentionally left blank].

9. MULTI-COLUMN BODY TEXT
   If the page has two or more columns of flowing body text (not a table),
   read the columns in the correct reading order (left column fully, then right
   column fully for left-to-right languages). Do NOT format multi-column body
   text as a table.

10. CALL-OUT BOXES / SIDEBARS
    Render as a blockquote:
    > **Box title (if any)**
    > Box content text here.

═══════════════════════════════════════════════════════
SECTION 5 — TABLE DETECTION AND FORMATTING RULES
═══════════════════════════════════════════════════════

A real table has ALL of these properties:
  - Visible grid lines OR consistent column alignment with at least 2 distinct columns
  - A clear header row (first row contains column labels)
  - At least 2 data rows below the header
  - Cells that contain short, discrete values — not flowing prose sentences

Output real tables as GitHub Flavored Markdown:
  | Column A | Column B | Column C |
  |----------|----------|----------|
  | value    | value    | value    |

DO NOT format as a table if ANY of these conditions apply:
  a) The content is flowing prose that happens to be laid out in two columns
     (e.g. a two-column page layout of paragraphs). Multi-column prose → plain
     paragraphs in reading order.
  b) Individual words appear in separate cells — this is a word-split artefact
     from two-column PDF layout. Never create a table from this.
  c) The "table" has only 1 column — render as a plain list instead.
  d) Cells contain full sentences or multiple sentences — likely a prose block,
     not a table. Exception: a "requirements table" where each row is a
     complete requirement is valid.
  e) The header row cells are very long (>80 characters) — this is a prose
     sentence being misread as a table header.
  f) Any cell spans what appears to be a word boundary with adjacent cells
     (e.g. cell 1 = "Submiss", cell 2 = "ion"). This is a broken layout,
     not a table. Reconstruct the text as prose.
  g) The table would have more than 20 columns — almost certainly a false positive.

When in doubt between table and prose, choose PROSE.

For merged/spanning cells: use the content in the first cell and leave
continuation cells empty:
  | Merged header      |         |
  |--------------------|---------|
  | content            | content |

═══════════════════════════════════════════════════════
SECTION 6 — MATHEMATICAL AND SCIENTIFIC CONTENT
═══════════════════════════════════════════════════════

- Inline math: $formula$
- Display math (on its own line, centred): $$formula$$
- Chemical formulas: use plain text or $\\text{H}_2\\text{O}$ style
- Greek letters: use LaTeX in math mode: $\\alpha$, $\\beta$, $\\Delta$
- Subscripts/superscripts in body text: use H₂O or x² if Unicode is clean,
  otherwise $H_2O$ or $x^2$

═══════════════════════════════════════════════════════
SECTION 7 — SPECIAL DOCUMENT TYPES
═══════════════════════════════════════════════════════

LEGAL / REGULATORY DOCUMENTS:
  - Rule/Article/Section identifiers ("Article 15", "SYSC 8.1.1 R", "§ 42"):
    keep inline as plain text, never promote to headings
  - Marginal type indicators (R, G, E, EU, etc.): preserve inline in parentheses
    after the identifier, e.g.: SYSC 8.1.1 *(R)*
  - Amendment markers like [deleted], [substituted]: keep verbatim
  - Indented sub-provisions: use 3-space indentation per level

ACADEMIC / SCIENTIFIC PAPERS:
  - Abstract: render as a blockquote with bold label: **Abstract**
  - Keywords: "**Keywords:** word1, word2, word3"
  - Author affiliations: render as plain text paragraph, not as headings
  - Citation numbers [1], [2,3]: preserve inline
  - Equation numbers on the right margin (3.1): append after the equation:
    $$E = mc^2 \\tag{3.1}$$

FINANCIAL / BUSINESS REPORTS:
  - Financial tables: preserve exactly, including currency symbols and units
  - Percentage values: preserve the % symbol
  - Year ranges and fiscal periods: keep as written
  - Audit opinions and notes: preserve as plain paragraphs

TECHNICAL MANUALS:
  - Code blocks: use triple backtick fences with language identifier
  - Command-line instructions: use bash fences
  - File paths, variable names inline: use backtick notation
  - Warning/Note/Caution boxes: use blockquotes with bold label:
    > **Warning:** content here.

MEDICAL / CLINICAL DOCUMENTS:
  - Drug names: preserve exactly, including dosage units
  - ICD codes, CPT codes: keep as plain text inline
  - Anatomical terms: preserve exactly

FORMS AND QUESTIONNAIRES:
  - Form fields: render as: **Field label:** _______________
  - Checkboxes: render as: - [ ] Option text (unchecked) or - [x] Option text (checked)
  - Drop-down labels: render as: **Field label:** [Select one]

PRESENTATION SLIDES:
  - Slide title → # heading
  - Sub-bullets on a slide → nested list
  - Speaker notes (if visible and clearly separated): render as blockquote:
    > *Speaker notes: ...*

═══════════════════════════════════════════════════════
SECTION 8 — OUTPUT FORMAT RULES
═══════════════════════════════════════════════════════

1. Output ONLY the markdown content. No preamble, no explanation, no commentary.
2. Do NOT wrap output in code fences (no ```markdown or ``` at start/end).
3. Do NOT add a title or heading that was not in the source.
4. Do NOT add any content that was not in the source image.
5. Do NOT hallucinate or infer content that is obscured or unclear — if text is
   genuinely illegible, write: [illegible]
6. Preserve the exact top-to-bottom order of all content as it appears on the page.
7. For completely blank pages or pages with only a page number, output exactly:
   [BLANK PAGE]
   Nothing else.
8. Use UTF-8 characters where appropriate (em-dash —, ellipsis …, curly quotes
   \u201c\u201d, \u2018\u2019). Do not substitute ASCII approximations unless the source uses them.
9. Preserve line breaks within a list item as two trailing spaces + newline when
   a single list item wraps across multiple visual lines in the source."""

# ---------------------------------------------------------------------------
# 4C — Page renderer
# ---------------------------------------------------------------------------


def render_page_to_png(doc: fitz.Document, page_num: int, dpi: int = VLM_PAGE_DPI) -> bytes:
    """Render a single PDF page to PNG bytes at the given DPI."""
    page = doc.load_page(page_num)
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    return pix.tobytes("png")


# ---------------------------------------------------------------------------
# 4D — API caller
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_TABLE_ROW_RE = re.compile(r"^\|.+\|$")
_TABLE_SEP_RE = re.compile(r"^\|[\s:|-]+\|$")

_CODE_FENCE_OPEN_RE = re.compile(r"^```\w*\s*$")
_MID_LIST_RE = re.compile(r"^\((\d+|[a-z]{1,3}|[ivxlcdm]{1,6})\)")
_PREV_LIST_ITEM_RE = re.compile(r"\((\d+|[a-z]{1,3}|[ivxlcdm]{1,6})\)")
_MONTH_YEAR_RE = re.compile(
    r"^(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+\d{4}$",
    re.IGNORECASE,
)
_PAGE_NUMBER_RE = re.compile(r"^-?\s*\d{1,4}\s*-?$")
_PAGE_OF_RE = re.compile(r"^Page\s+\d+\s+of\s+\d+$", re.IGNORECASE)
_ROMAN_NUMERAL_RE = re.compile(r"^[ivxlcdm]+$", re.IGNORECASE)
_EXCESS_BLANK_RE = re.compile(r"\n{3,}")


def _clean_vlm_page_output(md: str) -> str:
    """Post-process VLM response: strip code fences, header/footer artefacts, excess blanks."""
    # Step 1 — Strip wrapping code fences
    text = md.strip()
    if text.startswith("```"):
        first_nl = text.find("\n")
        if first_nl != -1:
            text = text[first_nl + 1:]
        else:
            text = ""
    text = text.strip()
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Step 2 — Strip running header/footer lines
    cleaned_lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if len(stripped) <= 120:
            if "www." in stripped or "http://" in stripped or "https://" in stripped:
                continue
            if _MONTH_YEAR_RE.match(stripped):
                continue
            if _PAGE_NUMBER_RE.match(stripped) or _PAGE_OF_RE.match(stripped):
                continue
            if _ROMAN_NUMERAL_RE.match(stripped) and len(stripped) <= 8:
                continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)

    # Step 3 — Collapse excess blank lines
    text = _EXCESS_BLANK_RE.sub("\n\n", text)

    # Step 4 — Remove heading promotion of running headers
    final_lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            content = stripped.lstrip("#").strip()
            if (
                "www." in content
                or "http://" in content
                or "https://" in content
                or _MONTH_YEAR_RE.match(content)
                or _PAGE_NUMBER_RE.match(content)
            ):
                final_lines.append(content)
                continue
            words = content.split()
            if (
                len(words) <= 3
                and all(len(w) <= 6 for w in words if w.isalpha())
                and any(w.isalpha() for w in words)
                and content.isupper()
            ):
                final_lines.append(content)
                continue
        final_lines.append(line)

    return "\n".join(final_lines).strip()


def call_vlm_api(
    image_png_bytes: bytes,
    *,
    page_num: int = 1,
    prev_page_tail: str = "",
    system_prompt: str = "",
) -> str:
    """Send a page image to OpenRouter and return the markdown response."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "") or VLM_API_KEY
    if not api_key.strip():
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. "
            "VLM processing requires an OpenRouter API key."
        )

    b64_image = base64.b64encode(image_png_bytes).decode("ascii")
    data_uri = f"data:image/png;base64,{b64_image}"

    model = os.environ.get("DOCSTRUCT_VLM_MODEL", "") or VLM_MODEL
    effective_prompt = system_prompt or VLM_SYSTEM_PROMPT

    user_text_parts: list[str] = []
    if prev_page_tail:
        user_text_parts.append(
            "The previous page ended with the following content (for context only — "
            "do not re-extract it, do not repeat it in your output):\n---\n"
            f"{prev_page_tail}\n---\n"
        )
    user_text_parts.append(
        f"Extract all content from this document page (page {page_num}). Return only markdown."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": effective_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": data_uri},
                    },
                    {
                        "type": "text",
                        "text": "\n".join(user_text_parts),
                    },
                ],
            },
        ],
    }

    body = json.dumps(payload).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://docstruct.local",
        "X-Title": "DocStruct",
    }

    last_exc: Optional[Exception] = None
    for attempt in range(1, VLM_MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                OPENROUTER_API_URL, data=body, headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=VLM_REQUEST_TIMEOUT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "VLM API attempt %d/%d for page %d failed: %s",
                attempt, VLM_MAX_RETRIES, page_num, exc,
            )
            if attempt < VLM_MAX_RETRIES:
                time.sleep(VLM_RETRY_DELAY * attempt)

    raise RuntimeError(
        f"VLM API failed after {VLM_MAX_RETRIES} attempts for page {page_num}: {last_exc}"
    )


# ---------------------------------------------------------------------------
# 4D-post — Document type detection and prompt addendum
# ---------------------------------------------------------------------------


def _detect_document_type(first_page_md: str) -> DocType:
    """Classify document type from the first page markdown."""
    text_lower = first_page_md.lower()

    # LEGAL detection
    legal_keywords = [
        "regulation", "shall", "must", "compliance", "authorisation",
        "pursuant", "statutory", "provision", "article", "directive",
    ]
    legal_score = sum(1 for kw in legal_keywords if kw in text_lower)
    if re.search(r"\b[A-Z]{2,8}\s+\d+\.\d+", first_page_md):
        legal_score += 1
    if legal_score >= 3:
        return DocType.LEGAL

    # ACADEMIC detection
    academic_keywords = [
        "abstract", "introduction", "methodology", "references",
        "bibliography", "et al.", "doi:",
    ]
    academic_score = sum(1 for kw in academic_keywords if kw in text_lower)
    if re.search(r"\[\d+(?:,\s*\d+)*\]", first_page_md):
        academic_score += 1
    if academic_score >= 2:
        return DocType.ACADEMIC

    # FINANCIAL detection
    financial_keywords = [
        "revenue", "ebitda", "consolidated", "fiscal year",
        "quarterly", "per share",
    ]
    financial_score = sum(1 for kw in financial_keywords if kw in text_lower)
    if any(sym in first_page_md for sym in ("$", "£", "€", "¥")):
        financial_score += 1
    if financial_score >= 2:
        return DocType.FINANCIAL

    # TECHNICAL detection
    technical_keywords = [
        "api", "endpoint", "parameter", "syntax",
        "version", "deprecated",
    ]
    technical_score = sum(1 for kw in technical_keywords if kw in text_lower)
    if "```" in first_page_md:
        technical_score += 1
    if "> **warning:**" in text_lower or "> **note:**" in text_lower:
        technical_score += 1
    if technical_score >= 2:
        return DocType.TECHNICAL

    # FORM detection
    form_keywords = [
        "___", "[ ]", "[x]", "please tick", "please select",
        "signature", "date:", "name:",
    ]
    form_score = sum(1 for kw in form_keywords if kw in text_lower)
    if form_score >= 2:
        return DocType.FORM

    return DocType.GENERAL


_DOC_TYPE_ADDENDA = {
    DocType.LEGAL: (
        "\n\nADDENDUM — LEGAL / REGULATORY DOCUMENT:\n"
        "This document is a legal or regulatory text. Apply these rules with extra rigour:\n"
        "- Rule identifiers in the margin (e.g. 'Section 3.2 R', 'SYSC 8.1.1 G') are NEVER "
        "headings. Keep them as inline plain text.\n"
        "- Preserve (1)(a)(i) list structure exactly with 3-space indentation per nesting level.\n"
        "- Keep [deleted], [Note: ...], [See also: ...] markers verbatim.\n"
        "- Marginal type indicators (R, G, E) should appear inline in italics: *(R)*.\n"
        "- Indented sub-provisions are critical — preserve every level of indentation.\n"
    ),
    DocType.ACADEMIC: (
        "\n\nADDENDUM — ACADEMIC / SCIENTIFIC PAPER:\n"
        "This document is an academic paper. Apply these rules with extra rigour:\n"
        "- Render the Abstract as a blockquote with **Abstract** label.\n"
        "- Preserve equation numbering: $$E = mc^2 \\tag{3.1}$$\n"
        "- Citation brackets [1], [2,3] must be preserved inline.\n"
        "- Author affiliations are plain text paragraphs, never headings.\n"
        "- Keywords line: **Keywords:** word1, word2, word3.\n"
    ),
    DocType.FINANCIAL: (
        "\n\nADDENDUM — FINANCIAL / BUSINESS REPORT:\n"
        "This document is a financial report. Apply these rules with extra rigour:\n"
        "- Financial tables: preserve currency symbols, units, and decimal precision exactly.\n"
        "- Year column headers and fiscal period labels must be kept as written.\n"
        "- Auditor's opinions and notes are plain paragraphs, not headings.\n"
        "- Percentage values must retain the % symbol.\n"
    ),
    DocType.TECHNICAL: (
        "\n\nADDENDUM — TECHNICAL MANUAL / API DOCUMENTATION:\n"
        "This document is a technical manual. Apply these rules with extra rigour:\n"
        "- Code blocks must use triple backtick fences with the correct language tag.\n"
        "- Warning/Note/Caution boxes: render as blockquotes with bold label.\n"
        "- File paths, variable names, and CLI commands: use `backtick` notation inline.\n"
        "- Version numbers and deprecated markers must be preserved exactly.\n"
    ),
    DocType.FORM: (
        "\n\nADDENDUM — FORM / QUESTIONNAIRE:\n"
        "This document is a form or questionnaire. Apply these rules with extra rigour:\n"
        "- Render checkboxes as: - [ ] Option (unchecked) or - [x] Option (checked).\n"
        "- Render field blanks as: **Label:** _______________\n"
        "- Instructional text in forms is body text, never headings.\n"
        "- Drop-down fields: **Label:** [Select one]\n"
    ),
    DocType.GENERAL: "",
}


def _get_doc_type_addendum(doc_type: DocType) -> str:
    """Return a short addendum string for the given document type."""
    return _DOC_TYPE_ADDENDA.get(doc_type, "")


# ---------------------------------------------------------------------------
# 4E-pre-0 — Heuristic continuation detection
# ---------------------------------------------------------------------------


def _detect_heuristic_continuation(page_md: str, prev_tail: str) -> bool:
    """Return True if the page appears to be a continuation of the previous page."""
    if not prev_tail:
        return False

    lines = page_md.split("\n")
    first_content_line = ""
    for line in lines:
        stripped = line.strip()
        if stripped:
            first_content_line = stripped
            break

    if not first_content_line:
        return False

    # Condition 1 — Mid-list start
    m = _MID_LIST_RE.match(first_content_line)
    if m:
        current_item = m.group(1)
        prev_items = _PREV_LIST_ITEM_RE.findall(prev_tail)
        if prev_items:
            try:
                cur_num = int(current_item)
                prev_num = int(prev_items[-1])
                if cur_num > prev_num:
                    return True
            except ValueError:
                if current_item != "a" and current_item != "i":
                    return True

    # Condition 2 — Mid-sentence start
    first_char = ""
    for ch in page_md:
        if not ch.isspace():
            first_char = ch
            break
    if first_char and first_char.islower():
        tail_stripped = prev_tail.rstrip()
        if tail_stripped and tail_stripped[-1] not in ".!?:":
            return True

    # Condition 3 — Incomplete previous tail
    tail_stripped = prev_tail.rstrip()
    if tail_stripped:
        last_char = tail_stripped[-1]
        if last_char in ";,":
            return True
        if last_char.isalpha() and not tail_stripped.endswith(("etc", "al", "eg", "ie")):
            words = tail_stripped.split()
            if words and not words[-1][-1] in ".!?:;,)":
                pass

    return False


def _preserve_list_indentation(text: str) -> str:
    """Strip trailing whitespace per-line but preserve leading indent for list items."""
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            result.append(line.rstrip())
        else:
            result.append("")
    return "\n".join(result).strip()


# ---------------------------------------------------------------------------
# 4E-pre — VLM table false-positive filter
# ---------------------------------------------------------------------------


def _is_valid_vlm_table(headers: List[str], rows: List[List[str]]) -> bool:
    """Return True only if a VLM-emitted GFM table passes quality checks."""
    non_empty_headers = [h for h in headers if h.strip()]

    # CHECK 1 — Minimum dimensions
    if len(non_empty_headers) < 2:
        return False
    if len(rows) < 1:
        return False
    max_cols = max(len(headers), *(len(r) for r in rows)) if rows else len(headers)
    if max_cols < 2:
        return False

    # CHECK 2 — Header sanity
    avg_header_len = (
        sum(len(h) for h in non_empty_headers) / len(non_empty_headers)
        if non_empty_headers
        else 0
    )
    if avg_header_len > 80:
        return False
    for h in non_empty_headers:
        if h and h[0].islower():
            return False

    # CHECK 3 — Word-split detection
    word_split_count = 0
    for row in (rows[:8] if len(rows) > 8 else rows):
        non_empty_cells = [(idx, c) for idx, c in enumerate(row) if c.strip()]
        for k in range(len(non_empty_cells) - 1):
            _, cell_a = non_empty_cells[k]
            _, cell_b = non_empty_cells[k + 1]
            if cell_a and cell_b and cell_a[-1].isalpha() and cell_b[0].islower():
                word_split_count += 1
    if word_split_count >= 2:
        return False

    # CHECK 4 — Column count sanity
    if max_cols > 20:
        return False

    # CHECK 5 — Empty cell ratio
    all_cells = list(headers)
    for row in rows:
        all_cells.extend(row)
    total_count = len(all_cells)
    empty_count = sum(1 for c in all_cells if not c.strip())
    if len(rows) > 1 and total_count > 0 and (empty_count / total_count) > 0.75:
        return False

    # CHECK 6 — Truncation detection
    if len(rows) > 4:
        short_or_dot_count = 0
        for c in all_cells:
            stripped = c.strip()
            if len(stripped) <= 2 and stripped:
                short_or_dot_count += 1
            elif stripped.endswith(".") and len(stripped) <= 3:
                short_or_dot_count += 1
        if short_or_dot_count >= 3:
            return False

    return True


# ---------------------------------------------------------------------------
# 4E — Markdown-to-DocumentTree parser
# ---------------------------------------------------------------------------


def _parse_pages_to_tree(
    page_markdowns: List[Tuple[int, str]],
    source_file: str,
    source_format: SourceFormat,
    total_pages: int,
) -> DocumentTree:
    """Parse per-page markdown strings into a structured DocumentTree."""
    tree = DocumentTree(
        source_file=source_file,
        source_format=source_format,
        total_pages=total_pages,
        extracted_at=datetime.now(timezone.utc).isoformat(),
        extraction_path=ExtractionPath.VLM,
    )

    # Stack-based tree construction (same principle as HtmlParser)
    root_sentinel = DocNode(title="__root__")
    stack: List[Tuple[int, DocNode]] = [(0, root_sentinel)]

    current_text_lines: List[str] = []
    current_page: int = 1
    current_tables: List[TableBlock] = []
    table_counter_by_page: dict[int, int] = {}

    def _flush_text():
        nonlocal current_text_lines, current_tables
        if not stack:
            return
        _, top_node = stack[-1]
        if top_node is root_sentinel and not tree.nodes:
            pass
        text = _preserve_list_indentation("\n".join(current_text_lines))
        if text:
            if top_node.text:
                top_node.text += "\n\n" + text
            else:
                top_node.text = text
        for tbl in current_tables:
            top_node.tables.append(tbl)
        current_text_lines = []
        current_tables = []

    def _extract_tables_from_lines(lines: List[str]) -> Tuple[List[str], List[TableBlock]]:
        """Detect GFM tables in lines and extract them as TableBlock objects."""
        result_lines: List[str] = []
        tables: List[TableBlock] = []
        i = 0
        while i < len(lines):
            if (
                _TABLE_ROW_RE.match(lines[i])
                and i + 1 < len(lines)
                and _TABLE_SEP_RE.match(lines[i + 1])
            ):
                table_lines = [lines[i], lines[i + 1]]
                j = i + 2
                while j < len(lines) and _TABLE_ROW_RE.match(lines[j]):
                    table_lines.append(lines[j])
                    j += 1

                page_key = current_page
                table_counter_by_page.setdefault(page_key, 0)
                table_counter_by_page[page_key] += 1
                tid = f"p{page_key}_t{table_counter_by_page[page_key]}"

                raw_headers = [
                    c.strip() for c in table_lines[0].strip("|").split("|")
                ]
                raw_rows = []
                for tl in table_lines[2:]:
                    raw_rows.append(
                        [c.strip() for c in tl.strip("|").split("|")]
                    )

                if _is_valid_vlm_table(raw_headers, raw_rows):
                    tbl = TableBlock(
                        table_id=tid,
                        page=page_key,
                        headers=raw_headers,
                        rows=raw_rows,
                        markdown="\n".join(table_lines),
                    )
                    tables.append(tbl)
                else:
                    all_table_cells = [raw_headers] + raw_rows
                    for row_cells in all_table_cells:
                        prose_line = " ".join(
                            c.strip() for c in row_cells if c.strip()
                        )
                        if prose_line:
                            result_lines.append(prose_line)
                i = j
            else:
                result_lines.append(lines[i])
                i += 1
        return result_lines, tables

    for page_num, md_text in page_markdowns:
        current_page = page_num
        if not md_text or md_text.strip() in ("[BLANK PAGE]", ""):
            for _, sn in stack:
                if sn is not root_sentinel and sn.pages:
                    if page_num > sn.pages.physical_end:
                        sn.pages.physical_end = page_num
            continue

        # --- [CONTINUATION] handling (Change C) ---
        stripped_md = md_text.lstrip()
        if stripped_md.startswith("[CONTINUATION]"):
            has_open_node = len(stack) > 1
            if has_open_node:
                _flush_text()
                continuation_text = stripped_md[len("[CONTINUATION]"):].lstrip("\n")

                _, current_node = stack[-1]
                cont_lines = continuation_text.split("\n")
                _, cont_tables = _extract_tables_from_lines(cont_lines)
                for tbl in cont_tables:
                    current_node.tables.append(tbl)

                if current_node.text:
                    if current_node.text.rstrip().endswith((")", ".", ";")):
                        current_node.text = current_node.text.rstrip() + "\n\n" + continuation_text
                    else:
                        current_node.text = current_node.text.rstrip() + "\n" + continuation_text.lstrip()
                else:
                    current_node.text = continuation_text

                for level_in_stack, sn in stack:
                    if sn is root_sentinel:
                        continue
                    if sn.pages and page_num > sn.pages.physical_end:
                        sn.pages.physical_end = page_num
                continue

        page_lines = md_text.split("\n")
        non_heading_lines, page_tables = _extract_tables_from_lines(page_lines)
        current_tables.extend(page_tables)

        for line in non_heading_lines:
            hm = _HEADING_RE.match(line)
            if hm:
                _flush_text()
                level = len(hm.group(1))
                title = hm.group(2).strip()

                while len(stack) > 1 and stack[-1][0] >= level:
                    stack.pop()

                node = DocNode(
                    title=title,
                    pages=PageRange(
                        physical_start=page_num,
                        physical_end=page_num,
                    ),
                )

                parent = stack[-1][1]
                if parent is root_sentinel:
                    tree.nodes.append(node)
                else:
                    parent.add_child(node)

                stack.append((level, node))
            else:
                current_text_lines.append(line)

        for level_in_stack, sn in stack:
            if sn is root_sentinel:
                continue
            if sn.pages is None:
                continue
            if page_num > sn.pages.physical_end:
                sn.pages.physical_end = page_num

    _flush_text()

    if not tree.nodes:
        all_text = "\n\n".join(md for _, md in page_markdowns if md.strip())
        fallback_node = DocNode(
            title=Path(source_file).stem,
            text=all_text,
            pages=PageRange(physical_start=1, physical_end=total_pages),
        )
        tree.nodes.append(fallback_node)

    tree.finalise()

    def _clamp_child_page_ranges(nodes: List[DocNode]) -> None:
        for node in nodes:
            if node.children and node.pages:
                for child in node.children:
                    if child.pages:
                        child.pages.physical_end = min(
                            child.pages.physical_end,
                            node.pages.physical_end,
                        )
                _clamp_child_page_ranges(node.children)

    _clamp_child_page_ranges(tree.nodes)

    return tree


# ---------------------------------------------------------------------------
# 4F — VlmParser class
# ---------------------------------------------------------------------------


class VlmParser(BaseParser):
    """Parse documents by rendering pages as images and calling a VLM via OpenRouter."""

    def __init__(
        self,
        file_path: Path,
        source_format: SourceFormat = SourceFormat.PDF,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        doc_type: DocType = DocType.AUTO,
    ):
        super().__init__(file_path)
        self.source_format = source_format
        self.progress_callback = progress_callback
        self._requested_doc_type = doc_type
        self._detected_doc_type: DocType = DocType.GENERAL

    def parse(self) -> DocumentTree:
        if self.source_format == SourceFormat.IMAGE:
            return self._parse_image()
        return self._parse_pdf()

    def _parse_pdf(self) -> DocumentTree:
        doc = fitz.open(str(self.file_path))
        total = doc.page_count
        page_markdowns: List[Tuple[int, str]] = []
        prev_tail: str = ""

        # If doc_type is explicitly set, use it for all pages
        forced_type = (
            self._requested_doc_type
            if self._requested_doc_type != DocType.AUTO
            else None
        )
        effective_prompt = VLM_SYSTEM_PROMPT
        if forced_type:
            self._detected_doc_type = forced_type
            effective_prompt = VLM_SYSTEM_PROMPT + _get_doc_type_addendum(forced_type)

        for i in range(total):
            page_num = i + 1
            try:
                png_bytes = render_page_to_png(doc, i)
                md = call_vlm_api(
                    png_bytes,
                    page_num=page_num,
                    prev_page_tail=prev_tail,
                    system_prompt=effective_prompt,
                )
            except Exception as exc:
                logger.error("Failed to process page %d: %s", page_num, exc)
                md = f"[ERROR: Could not process page {page_num}]"

            md = _clean_vlm_page_output(md)

            # After page 1, detect document type and build targeted prompt
            if page_num == 1 and not forced_type:
                self._detected_doc_type = _detect_document_type(md)
                addendum = _get_doc_type_addendum(self._detected_doc_type)
                if addendum:
                    effective_prompt = VLM_SYSTEM_PROMPT + addendum
                    logger.debug(
                        "Detected document type: %s", self._detected_doc_type.value
                    )

            # Heuristic continuation detection as fallback
            if (
                prev_tail
                and not md.lstrip().startswith("[CONTINUATION]")
                and _detect_heuristic_continuation(md, prev_tail)
            ):
                logger.debug("Heuristic continuation detected for page %d.", page_num)
                md = "[CONTINUATION]\n\n" + md

            page_markdowns.append((page_num, md))
            prev_tail = md[-500:] if len(md) > 500 else md

            if self.progress_callback:
                self.progress_callback(page_num, total)

        doc.close()

        return _parse_pages_to_tree(
            page_markdowns,
            source_file=self.file_path.name,
            source_format=self.source_format,
            total_pages=total,
        )

    def _parse_image(self) -> DocumentTree:
        img_bytes = self.file_path.read_bytes()

        suffix = self.file_path.suffix.lower()
        if suffix not in (".png",):
            pix = fitz.Pixmap(str(self.file_path))
            png_bytes = pix.tobytes("png")
        else:
            png_bytes = img_bytes

        try:
            md = call_vlm_api(png_bytes, page_num=1)
            md = _clean_vlm_page_output(md)
        except Exception as exc:
            logger.error("Failed to process image %s: %s", self.file_path.name, exc)
            md = f"[ERROR: Could not process image {self.file_path.name}]"

        if self.progress_callback:
            self.progress_callback(1, 1)

        return _parse_pages_to_tree(
            [(1, md)],
            source_file=self.file_path.name,
            source_format=SourceFormat.IMAGE,
            total_pages=1,
        )
