# Desde la raíz del repo, con las dependencias del README y requirements-test instaladas.
$ErrorActionPreference = 'Stop'
Push-Location backend/api_hospital
try {
    $env:PYTHONUTF8='1'
    python -m pytest tests/test_sprint9_uat_readiness.py -q
    if ($LASTEXITCODE) { throw 'UAT prerequisites failed' }
    python -m pytest -q -k 'not test_memory_limit_v2_is_respected and not test_pressure_kills_child and not test_deadline_stops_the_whole_analysis_process' --junitxml=../../evidence/sprint-9-jaime-fix/backend.xml
    if ($LASTEXITCODE) { throw 'Backend regression failed' }
} finally { Pop-Location }
Push-Location frontend/clinica-web-react
try {
    npm test -- --maxWorkers=1 --testTimeout=15000 --reporter=default --reporter=junit --outputFile=../../evidence/sprint-9-jaime-fix/frontend.xml
    if ($LASTEXITCODE) { throw 'Frontend regression failed' }
    npm run check:i18n
    npm run lint
    npm run build
    npm run check:bundle
} finally { Pop-Location }
# Simulación visual: iniciar MongoDB aislado en 127.0.0.1:27029 con un dbpath vacío.
# Terminal API: cd backend/api_hospital; python -m testing.uat_server
# Terminal web: cd frontend/clinica-web-react
# $env:VITE_API_URL='http://127.0.0.1:5019/api/v1'; npm run dev -- --host 127.0.0.1 --port 5189 --strictPort
# Usuarios sintéticos enfermeria.test y administrativo.test, contraseña de testing.seed.
# En Linux ejecutar también la suite completa y la integración Java/PySpark de CI.
