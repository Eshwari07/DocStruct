from __future__ import annotations

import argparse
from pathlib import Path

from docstruct.pipeline import DocStructPipeline
from docstruct.serializers.json_serializer import save_json
from docstruct.serializers.markdown_serializer import save_markdown


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="docstruct", description="DocStruct document structure extractor")
    parser.add_argument("file", help="Path to input document")
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=".",
        help="Directory to write outputs (default: current directory)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "markdown", "both"],
        default="both",
        help="Output format (default: both)",
    )

    args = parser.parse_args(argv)

    input_path = Path(args.file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pipeline = DocStructPipeline()
    tree = pipeline.process(input_path, artifact_dir=output_dir)

    stem = input_path.stem
    if args.format in ("json", "both"):
        save_json(tree, output_dir / f"{stem}.docstruct.json")
    if args.format in ("markdown", "both"):
        save_markdown(tree, output_dir / f"{stem}.docstruct.md")


if __name__ == "__main__":
    main()

