from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from docstruct.core.schema import DocumentTree


def to_json(tree: DocumentTree, indent: int = 2) -> str:
    """
    Serialise a DocumentTree to a JSON string.

    - confidence rounded to 4 decimal places
    - nulls preserved
    - does not mutate the input tree
    """
    data = tree.to_dict()

    def _round_confidence_in_node(node_dict: dict) -> None:
        if "confidence" in node_dict and node_dict["confidence"] is not None:
            node_dict["confidence"] = round(float(node_dict["confidence"]), 4)
        for child in node_dict.get("children", []):
            _round_confidence_in_node(child)

    for node in data.get("document", {}).get("nodes", []):
        _round_confidence_in_node(node)

    return json.dumps(data, indent=indent, ensure_ascii=False)


def save_json(tree: DocumentTree, path: Union[str, Path], indent: int = 2) -> None:
    """
    Serialise a DocumentTree and write it to disk.
    """
    json_str = to_json(tree, indent=indent)
    path = Path(path)
    path.write_text(json_str, encoding="utf-8")

