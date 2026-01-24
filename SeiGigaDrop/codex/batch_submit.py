#!/usr/bin/env python3
"""Create a batch payload from Codex drop files for submission workflows."""

from __future__ import annotations

import argparse
import json
import pathlib
import time
from typing import Any, Iterable


def _expand_paths(paths: Iterable[str]) -> list[pathlib.Path]:
    expanded: list[pathlib.Path] = []
    for raw in paths:
        path = pathlib.Path(raw)
        if path.is_dir():
            expanded.extend(sorted(path.rglob("*.json")))
        else:
            expanded.append(path)
    return expanded


def _load_json(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_batch(paths: Iterable[pathlib.Path], *, source: str) -> dict[str, Any]:
    items = []
    for path in paths:
        items.append(
            {
                "path": str(path),
                "payload": _load_json(path),
            }
        )
    return {
        "batchSource": source,
        "batchTimestamp": int(time.time()),
        "batchCount": len(items),
        "items": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Codex batch payload.")
    parser.add_argument(
        "inputs",
        nargs="+",
        help="JSON files or directories to include in the batch payload.",
    )
    parser.add_argument(
        "--source",
        default="SeiGigaDrop",
        help="Source label to attach to the batch payload.",
    )
    parser.add_argument("--out", help="Write the batch payload to this JSON file.")
    args = parser.parse_args()

    paths = _expand_paths(args.inputs)
    if not paths:
        raise SystemExit("No JSON inputs found to batch.")

    batch = build_batch(paths, source=args.source)
    output = json.dumps(batch, indent=2, sort_keys=True)
    if args.out:
        out_path = pathlib.Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
        print(f"Wrote batch payload with {len(paths)} items to {out_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
