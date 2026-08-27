"""Command-line interface for PublicFormKit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import convert_form


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="공공서식을 JSON Schema와 접근 가능한 HTML 초안으로 변환합니다.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("publicform-output"))
    args = parser.parse_args(argv)
    try:
        result = convert_form(args.source, args.output_dir)
    except (OSError, ValueError) as error:
        print(f"publicformkit: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["field_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
