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
    with urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["job_id"]


def main() -> None:
    base = "http://127.0.0.1:8000"
    pdf_path = Path(
        r"c:\Users\EshwariGone\projects\DocStruct\DocumentParser\testuploads\cvpr2012.pdf"
    )
    job_id = upload(pdf_path)

    st = None
    for _ in range(600):
        with urlopen(base + f"/status/{job_id}") as resp:
            st = json.loads(resp.read().decode("utf-8"))
        if st["status"] != "processing":
            break
        time.sleep(0.2)

    if not st:
        raise SystemExit("no status")

    print("status", st["status"], "total_pages", st.get("total_pages"))
    if st["status"] != "complete":
        raise SystemExit("job did not complete")

    with urlopen(base + f"/result/{job_id}") as resp:
        res = json.loads(resp.read().decode("utf-8"))

    root_nodes = res["document"].get("nodes", [])
    img_count = 0
    text_len = 0
    first_asset = None

    def walk(n: dict) -> None:
        nonlocal img_count, text_len, first_asset
        text_len += len((n.get("text") or ""))
        imgs = n.get("images") or []
        img_count += len(imgs)
        if first_asset is None and imgs:
            first_asset = imgs[0].get("path")
        for c in n.get("children") or []:
            walk(c)

    for n in root_nodes:
        walk(n)

    print("root_nodes", len(root_nodes), "images", img_count, "text_len", text_len)

    if first_asset:
        with urlopen(base + f"/asset/{job_id}/{first_asset}", timeout=30) as resp:
            b = resp.read(16)
        print("asset_ok", first_asset, "prefix_len", len(b))
    else:
        print("no_assets")


if __name__ == "__main__":
    main()

