"""Read-only availability check for the public login pages used in Sprint 11."""

from __future__ import annotations

import json
import os
from pathlib import Path

import requests


URLS = (
    "https://ineo-web-qa.vercel.app/login",
    "https://clinica-ocular-ten.vercel.app/login",
)


def main() -> None:
    report_dir = os.environ.get("REPORT_DIR")
    if not report_dir:
        raise SystemExit("REPORT_DIR no está configurado por Jenkins.")

    results = []
    for url in URLS:
        response = requests.get(url, timeout=20, allow_redirects=True)
        response.raise_for_status()
        if response.status_code != 200:
            raise SystemExit(f"HTTP inesperado en {url}: {response.status_code}")
        if "OftalCore" not in response.text:
            raise SystemExit(f"No se encontró el título OftalCore en {url}")

        results.append(
            {
                "url": url,
                "status_code": response.status_code,
                "final_url": response.url,
                "check": "Página pública de acceso disponible; sin autenticación ni flujo API.",
            }
        )

    output = Path(report_dir) / "public-login-smoke.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    for result in results:
        print(f"HTTP {result['status_code']} {result['final_url']}")


if __name__ == "__main__":
    main()
