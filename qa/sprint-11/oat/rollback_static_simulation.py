"""Isolated rollback rehearsal for Sprint 11 evidence; never contacts QA/production."""

from __future__ import annotations

import hashlib
import http.server
import json
import shutil
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_: object) -> None:
        pass


def main() -> int:
    repo = Path(__file__).resolve().parents[3]
    dist = repo / "frontend" / "clinica-web-react" / "dist"
    index = dist / "index.html"
    if not index.is_file():
        raise SystemExit(f"Build web no encontrado: {dist}; ejecutar npm run build primero")

    with tempfile.TemporaryDirectory(prefix="s11-rollback-") as tmp:
        root = Path(tmp)
        stable = root / "stable"
        candidate = root / "candidate"
        current = root / "current"
        shutil.copytree(dist, stable)
        shutil.copytree(dist, candidate)
        stable_hash = sha256(stable / "index.html")
        (candidate / "index.html").write_text("<!doctype html><title>INVALID CANDIDATE</title>", encoding="utf-8")
        candidate_hash = sha256(candidate / "index.html")
        shutil.copytree(stable, current)

        handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(current), **kwargs)
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}/"

        def smoke() -> tuple[bool, int, str]:
            try:
                with urllib.request.urlopen(base_url, timeout=3) as response:
                    body = response.read().decode("utf-8", errors="replace")
                    ok = response.status == 200 and "assets/" in body and "INVALID CANDIDATE" not in body
                    return ok, response.status, body[:180]
            except urllib.error.HTTPError as error:
                return False, error.code, "HTTP error"

        initial_ok, initial_status, _ = smoke()
        if not initial_ok:
            server.shutdown()
            raise SystemExit("La versión estable no pasó el smoke inicial")

        shutil.rmtree(current)
        shutil.copytree(candidate, current)
        candidate_ok, candidate_status, _ = smoke()
        if candidate_ok:
            server.shutdown()
            raise SystemExit("La candidata inválida fue aceptada inesperadamente")

        start = time.perf_counter()
        shutil.rmtree(current)
        shutil.copytree(stable, current)
        rollback_hash = sha256(current / "index.html")
        recovered_ok, recovered_status, _ = smoke()
        rto_seconds = round(time.perf_counter() - start, 3)
        server.shutdown()
        thread.join(timeout=3)

        result = {
            "case": "CP-S11-OAT-03",
            "execution_type": "isolated local static-artifact rollback rehearsal",
            "qa_or_production_touched": False,
            "database_tested": False,
            "initial_stable_smoke": {"passed": initial_ok, "http_status": initial_status},
            "invalid_candidate_detected": {"passed": not candidate_ok, "http_status": candidate_status, "sha256": candidate_hash},
            "rollback": {"sha256_matches_stable": rollback_hash == stable_hash, "stable_sha256": stable_hash, "restored_sha256": rollback_hash, "rto_seconds": rto_seconds},
            "recovery_smoke": {"passed": recovered_ok, "http_status": recovered_status},
            "overall_passed_for_local_rehearsal": initial_ok and not candidate_ok and rollback_hash == stable_hash and recovered_ok,
            "limitation": "No Vercel/QA deployment, MongoDB, API, alerting, or real user traffic was exercised; obtain a controlled QA rollback before closing the operational acceptance criterion.",
        }
        output = repo / "evidence" / "sprint-11" / "package" / "CP-S11-OAT-03"
        output.mkdir(parents=True, exist_ok=True)
        (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0 if result["overall_passed_for_local_rehearsal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
