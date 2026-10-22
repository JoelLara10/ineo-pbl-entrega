# Ejecutar desde la raíz del repositorio con dependencias instaladas.
# Datos sintéticos aislados por tests/conftest.py. No requiere credenciales reales.
$ErrorActionPreference = 'Stop'
Push-Location frontend/clinica-web-react
try {
    npm test -- --maxWorkers=1 --testTimeout=15000 --reporter=default --reporter=junit --outputFile=../../evidence/sprint-9-jaime-review/frontend-final.xml
    if ($LASTEXITCODE) { throw 'Frontend tests failed' }
    npm run check:i18n
    npm run lint
    npm run build
    npm run check:bundle
} finally { Pop-Location }
Push-Location backend/api_hospital
try {
    $env:PYTHONUTF8='1'
    python -m pytest tests/test_sprint9_uat_readiness.py -q -rx --junitxml=../../evidence/sprint-9-jaime-review/uat-readiness.xml
    python -m pytest -q -k 'not test_memory_limit_v2_is_respected and not test_pressure_kills_child and not test_deadline_stops_the_whole_analysis_process' --junitxml=../../evidence/sprint-9-jaime-review/backend-portable.xml
} finally { Pop-Location }
# En Linux ejecutar también la suite completa con Java/PySpark disponibles.
