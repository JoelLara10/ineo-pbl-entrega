#!/usr/bin/env python3
"""Validate a Sprint 11 technical evidence package without inventing results."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from xml.etree import ElementTree
from pathlib import Path


REQUIRED_CASES = (
    "CP-S11-CI-01",
    "CP-S11-CI-02",
    "CP-S11-CI-03",
    "CP-S11-CI-04",
    "CP-S11-SIT-01",
    "CP-S11-OAT-03",
    "CP-S11-OAT-04",
    "CP-S11-CI-05",
)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"Evidence package directory not found: {root}"]
    for case_id in REQUIRED_CASES:
        case_dir = root / case_id
        if not case_dir.is_dir():
            errors.append(f"{case_id}: missing case directory")
            continue
        docs = [path for path in case_dir.glob("*.docx") if _valid_docx(path)]
        if not docs:
            errors.append(f"{case_id}: missing valid Word case record (.docx)")
        if not any(_valid_png(path) for path in case_dir.rglob("*.png")):
            errors.append(f"{case_id}: missing valid screenshot (.png)")
        if not any(_valid_result(path) for path in case_dir.rglob("*.xml")) and not list(case_dir.rglob("*.json")):
            errors.append(f"{case_id}: missing raw result (.xml or .json)")
        result_file = case_dir / "result.txt"
        if not result_file.is_file() or not result_file.read_text(encoding="utf-8", errors="replace").strip():
            errors.append(f"{case_id}: missing result.txt with observed outcome")
    return errors


def _valid_docx(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path) as archive:
            return "word/document.xml" in archive.namelist()
    except (OSError, zipfile.BadZipFile):
        return False


def _valid_png(path: Path) -> bool:
    try:
        with path.open("rb") as stream:
            return stream.read(8) == b"\x89PNG\r\n\x1a\n"
    except OSError:
        return False


def _valid_result(path: Path) -> bool:
    try:
        ElementTree.parse(path)
        return True
    except (OSError, ElementTree.ParseError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--json", dest="json_file", type=Path, help="write machine-readable validation result")
    args = parser.parse_args()
    errors = validate(args.package_dir)
    report = {"package": str(args.package_dir), "valid": not errors, "required_cases": list(REQUIRED_CASES), "errors": errors}
    if args.json_file:
        args.json_file.parent.mkdir(parents=True, exist_ok=True)
        args.json_file.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        print("Evidence package INVALID")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"Evidence package VALID: {len(REQUIRED_CASES)} case records contain required files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
