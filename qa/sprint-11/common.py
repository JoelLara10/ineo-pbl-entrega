"""Original command evidence and explicit machine-readable case outcomes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evidence/sprint-11/zahid'
OUT.mkdir(parents=True, exist_ok=True)

def run(label, args, cwd=ROOT, expected=(0,), env=None):
    target = OUT / 'logs' / (label + '.txt')
    target.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                            text=True, encoding='utf-8', errors='replace')
    target.write_text('COMMAND: ' + subprocess.list2cmdline([str(a) for a in args]) +
                      '\nEXIT: ' + str(result.returncode) + '\n' + result.stdout + result.stderr,
                      encoding='utf-8')
    print(label, 'exit', result.returncode, flush=True)
    if result.returncode not in expected:
        raise RuntimeError(f'{label}: exit={result.returncode}; see {target.relative_to(ROOT)}')
    return result

def record(case, title, steps, status='Aprobado', detail=None):
    path = OUT / 'cases' / (case + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    value = dict(case=case, title=title, status=status, steps=steps, detail=detail,
                 executed_utc=datetime.now(timezone.utc).isoformat(),
                 tested_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                 executor='Agente Codex bajo solicitud de Marcelino Zahid Galicia Bonifacio',
                 owner='Marcelino Zahid Galicia Bonifacio', reviewer='Jesús — revisión pendiente',
                 environment='QA local aislado; datos sintéticos')
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')
    return value

def manifest():
    rows = []
    for path in sorted(OUT.rglob('*')):
        if path.is_file() and path.name != 'manifest.json':
            rows.append(dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size,
                             sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (OUT/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
