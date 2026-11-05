$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot\..\..\.."
$out = Join-Path $root "evidence\sprint-10\CP-S10-SAST-04"
New-Item -ItemType Directory -Force -Path $out | Out-Null
Push-Location $root
try {
  npm --prefix frontend/clinica-web-react audit --audit-level=high --json | Tee-Object "$out\npm-audit.json"
  python -m pip_audit -r backend/api_hospital/requirements.txt -f json -o "$out\pip-audit.json"
  python -m bandit -r backend/api_hospital -f json -o "$out\bandit.json"
  git grep -n -I -E "(BEGIN (RSA|OPENSSH) PRIVATE KEY|password\s*=\s*['\"][^'\"]+|api[_-]?key\s*=)" -- . ':!qa/sprint-10/fixtures' | Tee-Object "$out\secret-scan.txt"
} finally { Pop-Location }

