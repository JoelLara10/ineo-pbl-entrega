from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from sprint11_artifact import copy_and_verify, write_manifest
from validate_sprint11_evidence import REQUIRED_CASES, validate


class ArtifactManifestTests(unittest.TestCase):
    def test_copy_has_same_hash_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "dist"
            source.mkdir()
            (source / "index.html").write_text("tested build", encoding="utf-8")
            manifest = base / "artifact.json"
            write_manifest(source, manifest)
            copy_and_verify(source, base / "qa-simulation", manifest)
            self.assertEqual((base / "qa-simulation" / "index.html").read_text(encoding="utf-8"), "tested build")

    def test_tampered_copy_is_rejected(self) -> None:
        from sprint11_artifact import verify

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "dist"
            source.mkdir()
            (source / "index.html").write_text("tested build", encoding="utf-8")
            manifest = base / "artifact.json"
            write_manifest(source, manifest)
            (source / "index.html").write_text("changed after test", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                verify(source, manifest)


class EvidenceValidatorTests(unittest.TestCase):
    def test_complete_package_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for case_id in REQUIRED_CASES:
                case = root / case_id
                case.mkdir()
                with zipfile.ZipFile(case / "record.docx", "w") as docx:
                    docx.writestr("word/document.xml", "<document/>")
                (case / "evidence.png").write_bytes(b"\x89PNG\r\n\x1a\n")
                (case / "result.xml").write_text("<testsuite/>", encoding="utf-8")
                (case / "result.txt").write_text("Observed fixture result", encoding="utf-8")
            self.assertEqual(validate(root), [])

    def test_incomplete_package_names_missing_case_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = root / REQUIRED_CASES[0]
            first.mkdir()
            errors = validate(root)
            self.assertTrue(any("Word case record" in error for error in errors))
            self.assertTrue(any("screenshot" in error for error in errors))
            self.assertTrue(any("result.txt" in error for error in errors))
            self.assertTrue(any(f"{REQUIRED_CASES[1]}: missing case directory" == error for error in errors))


if __name__ == "__main__":
    unittest.main()
