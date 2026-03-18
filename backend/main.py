from __future__ import annotations

import asyncio
import shutil
import tempfile
import time
import uuid
import mimetypes
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from docstruct.serializers.markdown_serializer import to_markdown


app = FastAPI(title="DocStruct API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store (local single-user tool)
jobs: Dict[str, Dict[str, Any]] = {}

@app.on_event("startup")
async def _start_purge_task():
    asyncio.create_task(_purge_old_jobs())


async def _purge_old_jobs():
    while True:
        await asyncio.sleep(300)  # check every 5 minutes
        cutoff = time.time() - 3600  # 1 hour TTL
        stale = [
            jid
            for jid, j in list(jobs.items())
            if float(j.get("created_at", 0)) < cutoff
        ]
        for jid in stale:
            _cleanup_job(jid)
            jobs.pop(jid, None)


def _make_job_dir(job_id: str) -> Path:
    root = Path(tempfile.gettempdir()) / "docstruct" / job_id
    root.mkdir(parents=True, exist_ok=True)
    return root


def _cleanup_job(job_id: str) -> None:
    job = jobs.get(job_id)
    if not job:
        return
    tmp_dir = job.get("tmp_dir")
    if isinstance(tmp_dir, (str, Path)):
        try:
            shutil.rmtree(str(tmp_dir), ignore_errors=True)
        except Exception:
            # Best-effort cleanup; never fail the API due to cleanup.
            pass


def _run_extraction(job_id: str) -> None:
    from docstruct.pipeline import DocStructPipeline  # local import fine

    local_pipeline = DocStructPipeline()

    job = jobs[job_id]
    file_path = Path(job["file_path"])
    tmp_dir = Path(job["tmp_dir"])
    start = time.time()

    try:
        import fitz

        # Peek at page count before starting so the progress bar has
        # a denominator immediately.
        try:
            with fitz.open(str(file_path)) as _doc:
                jobs[job_id]["total_pages"] = _doc.page_count
        except Exception:
            # non-PDF or unreadable — denominator stays 0
            pass

        tree = local_pipeline.process(file_path, artifact_dir=tmp_dir)
        elapsed_seconds = time.time() - start

        document = tree.to_dict().get("document", tree.to_dict())
        markdown = to_markdown(tree)

        jobs[job_id]["status"] = "complete"
        jobs[job_id]["progress_page"] = tree.total_pages
        jobs[job_id]["total_pages"] = tree.total_pages
        jobs[job_id]["elapsed_seconds"] = elapsed_seconds
        jobs[job_id]["result"] = {
            "document": document,
            "markdown": markdown,
            "stats": {
                "total_nodes": len(tree.flat_list()),
                "extraction_path": tree.extraction_path.value,
                "elapsed_seconds": elapsed_seconds,
                "total_pages": tree.total_pages,
            },
        }
    except Exception as e:
        elapsed_seconds = time.time() - start
        jobs[job_id]["status"] = "error"
        jobs[job_id]["elapsed_seconds"] = elapsed_seconds
        jobs[job_id]["error"] = str(e)


@app.post("/extract", status_code=202)
async def extract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    ocr: bool = False,
    max_pages: Optional[int] = None,
):
    # Note: ocr/max_pages are accepted to match the plan; the initial pipeline ignores them.
    _ = (ocr, max_pages)

    job_id = str(uuid.uuid4())
    tmp_dir = _make_job_dir(job_id)

    # Save the uploaded file to disk for the pipeline and /file serving.
    suffix = Path(file.filename).suffix
    saved_path = tmp_dir / f"upload{suffix}"

    contents = await file.read()
    saved_path.write_bytes(contents)

    jobs[job_id] = {
        "status": "processing",
        "filename": file.filename,
        "file_size_bytes": len(contents),
        "file_path": str(saved_path),
        "tmp_dir": str(tmp_dir),
        "progress_page": 0,
        "total_pages": 0,
        "elapsed_seconds": 0.0,
        "error": None,
        "result": None,
        "created_at": time.time(),
    }

    background_tasks.add_task(_run_extraction, job_id)

    return {
        "job_id": job_id,
        "status": "processing",
        "filename": file.filename,
        "file_size_bytes": len(contents),
    }


@app.get("/status/{job_id}")
async def status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] == "processing":
        job["elapsed_seconds"] = time.time() - float(job.get("created_at", time.time()))

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress_page": int(job.get("progress_page", 0)),
        "total_pages": int(job.get("total_pages", 0)),
        "elapsed_seconds": float(job.get("elapsed_seconds", 0.0)),
    }


@app.get("/result/{job_id}")
async def result(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] == "error":
        raise HTTPException(
            status_code=500,
            detail=job.get("error") or "Extraction failed with unknown error.",
        )
    if job["status"] != "complete":
        raise HTTPException(
            status_code=409,
            detail=f"Job is not complete (status={job['status']}).",
        )

    return job["result"]


@app.get("/file/{job_id}")
async def file(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    file_path = Path(job["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Uploaded file missing")

    media_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(
        path=str(file_path),
        media_type=media_type or "application/octet-stream",
        filename=job.get("filename"),
    )


@app.get("/asset/{job_id}/{asset_path:path}")
async def asset(job_id: str, asset_path: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    base_dir = Path(job["tmp_dir"])
    candidate = (base_dir / asset_path).resolve()
    # Prevent path traversal: candidate must be inside base_dir.
    if base_dir.resolve() not in candidate.parents:
        raise HTTPException(status_code=400, detail="Invalid asset path")
    if not candidate.exists():
        raise HTTPException(status_code=404, detail="Asset not found")

    media_type, _ = mimetypes.guess_type(str(candidate))
    return FileResponse(
        path=str(candidate),
        media_type=media_type or "application/octet-stream",
        filename=candidate.name,
    )


@app.delete("/job/{job_id}", status_code=204)
async def delete_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    _cleanup_job(job_id)
    jobs.pop(job_id, None)
    return None

