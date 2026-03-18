import json
import mimetypes
import time
import uuid
from pathlib import Path
from urllib.request import Request, urlopen


def main() -> None:
    base = "http://127.0.0.1:8000"
    file_path = Path(
        r"c:\Users\EshwariGone\projects\DocStruct\DocumentParser\testfiles\sample.md"
    )
    content = file_path.read_bytes()

    boundary = "----docstruct" + uuid.uuid4().hex
    crlf = "\r\n"

    mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"

    parts: list[bytes] = []
    parts.append(
        (
            f"--{boundary}{crlf}"
            f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"{crlf}'
            f"Content-Type: {mime}{crlf}{crlf}"
        ).encode("utf-8")
        + content
        + crlf.encode("utf-8")
    )
    parts.append(
        (
            f"--{boundary}{crlf}"
            f'Content-Disposition: form-data; name="ocr"{crlf}{crlf}'
            f"false{crlf}"
        ).encode("utf-8")
    )
    body = b"".join(parts) + f"--{boundary}--{crlf}".encode("utf-8")

    req = Request(base + "/extract", data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Content-Length", str(len(body)))

    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    job_id = data["job_id"]
    print(f"job_id={job_id}")

    st: dict | None = None
    for _ in range(200):
        with urlopen(base + f"/status/{job_id}") as resp:
            st = json.loads(resp.read().decode("utf-8"))
        if st["status"] != "processing":
            break
        time.sleep(0.1)

    if not st:
        raise SystemExit("No status returned")
    print("status=", st)

    if st["status"] != "complete":
        raise SystemExit("Job did not complete")

    with urlopen(base + f"/result/{job_id}") as resp:
        res = json.loads(resp.read().decode("utf-8"))

    nodes = res["document"].get("nodes", [])
    md = res.get("markdown", "")
    print("nodes=", len(nodes))
    print("markdown_prefix=", md[:120].replace("\n", "\\n"))

    with urlopen(base + f"/file/{job_id}") as resp:
        fb = resp.read(64)
    print("file_bytes_prefix=", fb)


if __name__ == "__main__":
    main()

