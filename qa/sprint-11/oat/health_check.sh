#!/usr/bin/env bash
# Run from Git Bash on Windows or Bash on a host with curl.
set -euo pipefail
cd "$(dirname "$0")"
API_BASE=${API_BASE:-http://localhost:5002}
REPORT_DIR=${REPORT_DIR:-./reports}
mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/health-$(date -u +%Y%m%dT%H%M%SZ)-$$.txt"
exec > >(tee "$REPORT") 2>&1
for route in health ready; do
  status=$(curl --silent --show-error --max-time 35 --output /dev/null --write-out '%{http_code}' "$API_BASE/$route")
  echo "GET /$route HTTP $status"
  [[ "$status" == 200 ]]
done
echo 'ESTADO=Aprobado (normal health only)'
