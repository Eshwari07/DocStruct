"""
End-to-end integration tests for DocStruct pipeline.

Requires the test PDFs to be present at the paths below.
Run from the repo root: pytest backend/tests/test_integration.py -v
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

# Resolve test PDFs relative to this file so CWD doesn't matter.
BACKEND_DIR = Path(__file__).resolve().parents[1]  # .../backend
EDPB_PDF = BACKEND_DIR / "testfiles" / "EDPB.pdf"
SYSC_PDF = BACKEND_DIR / "testfiles" / "SYSC_8_Outsourcing.pdf"
if not SYSC_PDF.exists():
    # Actual test fixture filename in this repo
    SYSC_PDF = BACKEND_DIR / "testfiles" / "SYSC 8 Outsourcing.pdf"

skip_edpb = pytest.mark.skipif(
    not EDPB_PDF.exists(), reason=f"EDPB PDF not found at {EDPB_PDF}"
)
skip_sysc = pytest.mark.skipif(
    not SYSC_PDF.exists(), reason=f"SYSC PDF not found at {SYSC_PDF}"
)


# ──────────────────────────────────────────────────────────────────
# Schema / serialisation sanity (no PDF needed)
# ──────────────────────────────────────────────────────────────────


def test_schema_finalise_ids():
    """section_ids and flat ids must be assigned correctly."""

    from docstruct.core.schema import (
        DocumentTree,
        DocNode,
        ExtractionPath,
        SourceFormat,
    )
    import datetime

    root = DocNode(title="Root")
    child1 = DocNode(title="Child 1")
    child2 = DocNode(title="Child 2")
    grandchild = DocNode(title="Grandchild")
    root.add_child(child1)
    root.add_child(child2)
    child1.add_child(grandchild)

    tree = DocumentTree(
        source_file="test.pdf",
        source_format=SourceFormat.PDF,
        total_pages=5,
        extracted_at=datetime.datetime.utcnow().isoformat() + "Z",
        extraction_path=ExtractionPath.FAST,
        nodes=[root],
    )
    tree.finalise()

    flat = tree.flat_list()
    assert flat[0].section_id == "1"
    assert flat[1].section_id == "1.1"
    assert flat[3].section_id == "1.2"
    assert flat[0].id == "0001"
    assert flat[1].id == "0002"
    assert flat[2].id == "0003"  # grandchild
    assert flat[3].id == "0004"  # child2


def test_schema_node_types():
    from docstruct.core.schema import (
        DocNode,
        DocumentTree,
        NodeType,
        SourceFormat,
        ExtractionPath,
    )
    import datetime

    root = DocNode(title="Root")
    child = DocNode(title="Child")
    root.add_child(child)

    tree = DocumentTree(
        source_file="t.pdf",
        source_format=SourceFormat.PDF,
        total_pages=1,
        extracted_at="2026-01-01T00:00:00Z",
        extraction_path=ExtractionPath.FAST,
        nodes=[root],
    )
    tree.finalise()

    assert root.node_type == NodeType.PARENT
    assert child.node_type == NodeType.CHILD


def test_json_serialisation_round_trip():
    """to_dict() must produce valid JSON that matches schema."""
    from docstruct.core.schema import (
        DocNode,
        DocumentTree,
        ExtractionPath,
        PageRange,
        SourceFormat,
    )

    root = DocNode(
        title="Introduction",
        text="Some text here.",
        pages=PageRange(physical_start=1, physical_end=3),
        confidence=1.0,
    )
    tree = DocumentTree(
        source_file="report.pdf",
        source_format=SourceFormat.PDF,
        total_pages=3,
        extracted_at="2026-01-01T00:00:00Z",
        extraction_path=ExtractionPath.FAST,
        nodes=[root],
    )
    tree.finalise()

    d = tree.to_dict()
    json_str = json.dumps(d)  # must not raise
    parsed = json.loads(json_str)

    doc = parsed["document"]
    assert doc["source_file"] == "report.pdf"
    assert doc["total_pages"] == 3
    assert len(doc["nodes"]) == 1
    node = doc["nodes"][0]
    assert node["id"] == "0001"
    assert node["section_id"] == "1"
    assert node["title"] == "Introduction"
    # Private fields must NOT appear in serialised output
    assert "_parent" not in node
    assert "_is_phantom" not in node


# ──────────────────────────────────────────────────────────────────
# EDPB PDF tests
# ──────────────────────────────────────────────────────────────────


@skip_edpb
def test_edpb_parses_without_error():
    from docstruct.pipeline import DocStructPipeline

    pipeline = DocStructPipeline()
    tree = pipeline.process(EDPB_PDF)
    assert tree is not None
    assert tree.total_pages > 0
    assert len(tree.nodes) > 0


@skip_edpb
def test_edpb_expected_sections():
    """The EDPB document has a clear TOC — all top-level sections must be found."""
    from docstruct.pipeline import DocStructPipeline

    pipeline = DocStructPipeline()
    tree = pipeline.process(EDPB_PDF)
    flat = tree.flat_list()
    titles_lower = [n.title.lower() for n in flat]

    assert any("introduction" in t for t in titles_lower), (
        f"Missing Introduction. Found: {titles_lower}"
    )
    assert any("scope" in t for t in titles_lower), (
        f"Missing Scope section. Found: {titles_lower}"
    )
    assert any(
        ("objective" in t or "article 48" in t) for t in titles_lower
    ), f"Missing Article 48 objective section. Found: {titles_lower}"
    assert any(
        ("5.1" in n.section_id or "article 6" in n.title.lower()) for n in flat
    ), "Missing Section 5.1 (Compliance with Article 6)"
    assert any(
        ("annex" in t or "practical" in t) for t in titles_lower
    ), f"Missing Annex. Found: {titles_lower}"


@skip_edpb
def test_edpb_no_inverted_page_ranges():
    """physical_start must never be greater than physical_end for any node."""
    from docstruct.pipeline import DocStructPipeline

    pipeline = DocStructPipeline()
    tree = pipeline.process(EDPB_PDF)
    for node in tree.flat_list():
        if node.pages:
            assert node.pages.physical_start <= node.pages.physical_end, (
                f"Node '{node.title}' has inverted page range: "
                f"{node.pages.physical_start}–{node.pages.physical_end}"
            )


@skip_edpb
def test_edpb_annex_image_extracted():
    """
    The Annex (page 13) contains a flowchart drawn as vector graphics.
    After applying the image extractor fix, it must produce at least one image.
    """
    from docstruct.pipeline import DocStructPipeline

    pipeline = DocStructPipeline()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        tree = pipeline.process(EDPB_PDF, artifact_dir=tmp_path)
        flat = tree.flat_list()

        annex_nodes = [
            n
            for n in flat
            if "annex" in n.title.lower() or "practical" in n.title.lower()
        ]

        assert annex_nodes, "No Annex node found — structure extraction may have failed"
        annex = annex_nodes[0]

        assert len(annex.images) > 0, (
            f"Annex node '{annex.title}' has no images. "
            "Expected the flowchart to be extracted as a vector diagram."
        )
        for img in annex.images:
            img_file = tmp_path / "assets" / Path(img.path).name
            assert img_file.exists(), f"Image file does not exist on disk: {img_file}"


@skip_edpb
def test_edpb_sections_have_text():
    """Every non-front-matter node must have non-empty text."""
    from docstruct.pipeline import DocStructPipeline

    pipeline = DocStructPipeline()
    tree = pipeline.process(EDPB_PDF)

    empty_nodes = [
        n
        for n in tree.flat_list()
        if not n.text.strip() and "front matter" not in n.title.lower()
    ]
    # Allow up to 2 empty nodes (e.g. pure heading nodes with no body)
    assert len(empty_nodes) <= 2, (
        f"{len(empty_nodes)} nodes have empty text: " + str([n.title for n in empty_nodes])
    )


# ──────────────────────────────────────────────────────────────────
# SYSC 8 PDF tests
# ──────────────────────────────────────────────────────────────────


@skip_sysc
def test_sysc_parses_without_error():
    from docstruct.pipeline import DocStructPipeline

    pipeline = DocStructPipeline()
    tree = pipeline.process(SYSC_PDF)
    assert tree is not None
    assert tree.total_pages > 0


@skip_sysc
def test_sysc_expected_sections():
    """SYSC 8 must contain its key regulatory sections."""
    from docstruct.pipeline import DocStructPipeline

    pipeline = DocStructPipeline()
    tree = pipeline.process(SYSC_PDF)
    flat = tree.flat_list()
    titles_lower = [n.title.lower() for n in flat]
    all_text = " ".join(n.text for n in flat)

    assert any("outsourcing" in t for t in titles_lower), "Missing outsourcing section"
    assert any("general" in t for t in titles_lower), "Missing general requirements section"
    assert "SYSC 8.1" in all_text, "Rule references (SYSC 8.1.x) missing from extracted text"


@skip_sysc
def test_sysc_tables_extracted():
    """
    SYSC 8.1.-2 contains a table (Subject / Applicable rule).
    After applying the table extraction fix, at least one node
    must have markdown table syntax in its text.
    """
    from docstruct.pipeline import DocStructPipeline

    pipeline = DocStructPipeline()
    tree = pipeline.process(SYSC_PDF)
    flat = tree.flat_list()

    nodes_with_tables = [
        n
        for n in flat
        if "|" in n.text and ("---" in n.text or "--|" in n.text)
    ]
    assert len(nodes_with_tables) > 0, (
        "No markdown tables found in any node. "
        "Expected at least the Subject/Applicable rule table from SYSC 8.1.-2"
    )


@skip_sysc
def test_sysc_no_inverted_page_ranges():
    from docstruct.pipeline import DocStructPipeline

    pipeline = DocStructPipeline()
    tree = pipeline.process(SYSC_PDF)
    for node in tree.flat_list():
        if node.pages:
            assert node.pages.physical_start <= node.pages.physical_end, (
                f"Node '{node.title}' inverted: "
                f"{node.pages.physical_start}–{node.pages.physical_end}"
            )


# ──────────────────────────────────────────────────────────────────
# FastAPI endpoint tests
# ──────────────────────────────────────────────────────────────────


def test_api_error_result_returns_500():
    """
    When extraction fails, GET /result/{job_id} must return HTTP 500
    with the actual error detail — not 409 with a generic message.
    """
    from fastapi.testclient import TestClient
    import sys
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))
    from main import app

    client = TestClient(app)

    # Manually inject a failed job
    from main import jobs

    jobs["test-fail-job"] = {
        "status": "error",
        "filename": "test.pdf",
        "file_size_bytes": 0,
        "file_path": "/nonexistent/test.pdf",
        "tmp_dir": "/tmp",
        "progress_page": 0,
        "total_pages": 0,
        "elapsed_seconds": 0.1,
        "error": "Could not open file: /nonexistent/test.pdf",
        "result": None,
        "created_at": 0,
    }

    response = client.get("/result/test-fail-job")
    assert response.status_code == 500, (
        f"Expected 500 for failed job, got {response.status_code}"
    )
    assert "Could not open file" in response.json().get("detail", ""), (
        "Error detail not propagated to client"
    )


def test_api_result_409_when_processing():
    """GET /result for a still-processing job must return 409."""
    from fastapi.testclient import TestClient
    import time
    from main import app, jobs

    client = TestClient(app)
    jobs["test-processing-job"] = {
        "status": "processing",
        "filename": "test.pdf",
        "file_size_bytes": 0,
        "file_path": "/tmp/test.pdf",
        "tmp_dir": "/tmp",
        "progress_page": 0,
        "total_pages": 0,
        "elapsed_seconds": 0.0,
        "error": None,
        "result": None,
        "created_at": time.time(),
    }

    response = client.get("/result/test-processing-job")
    assert response.status_code == 409

