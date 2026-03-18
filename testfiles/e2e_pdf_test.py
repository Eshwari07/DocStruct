import json
import mimetypes
import time
import uuid
from pathlib import Path
from urllib.request import Request, urlopen


def upload(file_path: Path) -> str:
    base = "http://127.0.0.1:8000"
    content = file_path.read_bytes()
    boundary = "----docstruct" + uuid.uuid4().hex
    crlf = "\r\n"

    mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    body = (
        (
            f"--{boundary}{crlf}"
            f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"{crlf}'
            f"Content-Type: {mime}{crlf}{crlf}"
        ).encode("utf-8")
        + content
        + crlf.encode("utf-8")
        + f"--{boundary}--{crlf}".encode("utf-8")
    )

    req = Request(base + "/extract", data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Content-Length", str(len(body)))
    with urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["job_id"]


def main() -> None:
    base = "http://127.0.0.1:8000"
    pdf_path = Path(
        r"c:\Users\EshwariGone\projects\DocStruct\DocumentParser\testuploads\cvpr2012.pdf"
    )
    job_id = upload(pdf_path)
    print(f"job_id={job_id}")

    st: dict | None = None
    for _ in range(600):
        with urlopen(base + f"/status/{job_id}") as resp:
            st = json.loads(resp.read().decode("utf-8"))
        if st["status"] != "processing":
            break
        time.sleep(0.2)

    print("status=", st)
    if not st or st["status"] != "complete":
        raise SystemExit("Job did not complete")

    with urlopen(base + f"/result/{job_id}") as resp:
        res = json.loads(resp.read().decode("utf-8"))

    nodes = res["document"].get("nodes", [])
    print("root_nodes=", len(nodes))
    if nodes:
        txt = nodes[0].get("text") or ""
        print("first_text_len=", len(txt))
        prefix = txt[:200].replace("\n", "\\n")
        safe = prefix.encode("utf-8", "backslashreplace").decode("utf-8")
        print("first_text_prefix=", safe)

    md = res.get("markdown", "")
    print("markdown_prefix=", md[:200].replace("\n", "\\n"))


if __name__ == "__main__":
    main()

