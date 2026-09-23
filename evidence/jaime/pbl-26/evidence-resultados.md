# Evidencia PBL-26-T5 — Ambiente y datos de prueba

Documento operativo. El informe completo está en:

`docs/sprints/sprint-7/pbl-26-t5-resultados-ambiente-prueba.md`

**Historia:** Ambiente de prueba reproducible, sintético, aislado y restablecible.  
**Tarea:** T5 — Ejecutar suite, corregir defectos, registrar resultados.  
**Responsable:** Jaime Díaz González  
**Fecha:** 2026-09-23  
**Rama:** `sprints/jaime-sprint-7`

## Resultado

```text
26 passed in 2.75s
0 failed
0 warnings
```

Log: `evidence/jaime/pbl-26/pytest-ambiente.txt`

## Comando

```bash
cd backend/api_hospital
export MONGO_URI=mongodb://localhost:27017/
export MONGO_DB=hospital_test
export SECRET_KEY=ci-test-secret-key-min-32-characters
export JWT_SECRET_KEY=ci-test-jwt-secret-key-min-32-chars
python -m pytest -v tests/test_sprint1_environment.py \
  tests/test_auth.py tests/test_patients.py tests/test_nursing.py tests/test_spark_clinical.py
```

## Defectos corregidos

1. Rol de enfermería del fixture: `enfermeria` → `enfermero` (el que usa la API).
2. Usuario `administrativo` añadido.
3. JWT de CI alargado a ≥ 32 caracteres.
4. CI web ahora corre en ramas `sprints/**`.
5. Runbook versionado en `backend/api_hospital/tests/README.md`.

Sin PHI ni expedientes reales.
