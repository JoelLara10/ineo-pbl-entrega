#!/usr/bin/env python3
"""Create and verify a SHA-256 manifest for a built web artifact.

This helper supports a local promotion simulation. It does not deploy to QA.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def files_in(root: Path) -> list[Path]:
    if not root.is_dir():
        raise ValueError(f"Artifact directory not found: {root}")
    return sorted(path for path in root.rglob("*") if path.is_file())


def manifest(root: Path) -> dict[str, object]:
    entries = [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256(path), "size": path.stat().st_size}
        for path in files_in(root)
    ]
    if not entries:
        raise ValueError(f"Artifact directory is empty: {root}")
    return {"algorithm": "sha256", "files": entries}


def write_manifest(root: Path, output: Path) -> dict[str, object]:
    data = manifest(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def verify(root: Path, manifest_path: Path) -> None:
    expected = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = manifest(root)
    if actual != expected:
        raise ValueError("Artifact verification failed: file list, size, or SHA-256 differs")


def copy_and_verify(source: Path, destination: Path, manifest_path: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    verify(destination, manifest_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    make = subparsers.add_parser("manifest", help="write artifact SHA-256 manifest")
    make.add_argument("artifact_dir", type=Path)
    make.add_argument("manifest_file", type=Path)
    check = subparsers.add_parser("verify", help="verify artifact against a manifest")
    check.add_argument("artifact_dir", type=Path)
    check.add_argument("manifest_file", type=Path)
    copy = subparsers.add_parser("copy-verify", help="copy artifact and verify the copied bytes")
    copy.add_argument("artifact_dir", type=Path)
    copy.add_argument("destination", type=Path)
    copy.add_argument("manifest_file", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "manifest":
            data = write_manifest(args.artifact_dir, args.manifest_file)
            print(f"Manifest written: {len(data['files'])} files")
        elif args.command == "verify":
            verify(args.artifact_dir, args.manifest_file)
            print("Artifact matches SHA-256 manifest")
        else:
            copy_and_verify(args.artifact_dir, args.destination, args.manifest_file)
            print("Local promotion copy matches tested artifact SHA-256 manifest")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
