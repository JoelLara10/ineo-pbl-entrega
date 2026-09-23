# PBL-26-T5 — Resultados del ambiente y datos de prueba

**Épica:** Aceptación y liberación controlada  
**Feature:** Ambiente y datos de prueba  
**Historia:** Como equipo de desarrollo, queremos un ambiente y datos de prueba reproducibles para ejecutar validaciones sin utilizar expedientes reales.  
**Criterio:** El ambiente se levanta mediante instrucciones versionadas; los datos son sintéticos, repetibles, aislados y pueden restablecerse.  
**Tarea:** T5 — Ejecutar la suite, corregir defectos, registrar resultados y vincular la evidencia.  
**Sprint:** 7  
**Responsable:** Jaime Díaz González  
**Rama:** `sprints/jaime-sprint-7`  
**Fecha de ejecución:** 2026-09-23  
**Estado:** Aprobada (26 passed)

---

## 1. Objetivo de T5

No reimplementar T1–T4. Comprobar que el ambiente sintético **existe, corre, se restaura y no usa expedientes reales**; corregir los defectos que impidan el criterio; dejar evidencia trazable.

## 2. Qué se ejecutó

| Suite | Comando | Resultado |
|---|---|---|
| Ambiente sintético | `pytest -v tests/test_sprint1_environment.py` | 5 passed |
| Auth / pacientes / enfermería / Spark | `pytest -v tests/test_auth.py tests/test_patients.py tests/test_nursing.py tests/test_spark_clinical.py` | 21 passed |
| **Total API** | ver log adjunto | **26 passed, 0 failed, 0 warnings** |

Log versionado: `evidence/jaime/pbl-26/pytest-ambiente.txt`

Variables usadas (aisladas):

```text
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=hospital_test
SECRET_KEY=ci-test-secret-key-min-32-characters
JWT_SECRET_KEY=ci-test-jwt-secret-key-min-32-chars
```

No se conectó a Atlas ni a `hospital_db` / `ineo_db2`. No se cargaron expedientes reales.

## 3. Criterio de aceptación vs evidencia

| Criterio | Cómo se cumple | Evidencia |
|---|---|---|
| Instrucciones versionadas | `backend/api_hospital/tests/README.md` + CI `api-ci.yml` | Archivos en git |
| Datos sintéticos | IDs `USR-TEST-*`, `PAC-TEST-*`, `EST-TEST-*`; nombres “Paciente Sintético …” | `tests/fixtures/sprint1_data.json` |
| Repetibles | Fixture JSON fijo; cada test recibe `deepcopy` | `conftest.py` → `synthetic_data` |
| Aislados | `MONGO_DB=hospital_test`; prueba que rechaza DBs de producción | `test_test_database_name_is_isolated_from_production` |
| Restablecibles | Un test vacía `users`/`patients`; el siguiente vuelve a ver 5 usuarios | `test_fixture_is_restored_for_every_test` + `test_fixture_cleanup_returns_original_data` |

## 4. Defectos encontrados al ejecutar y corrección

| ID | Defecto | Impacto en el criterio | Corrección |
|---|---|---|---|
| D1 | Fixture usaba rol `enfermeria`; la API exige `enfermero` | Usuario de prueba no pasaría `role_required` de notas | Rol `enfermero` en el JSON |
| D2 | Faltaba usuario `administrativo` (sí está en `docs/manual-tecnico/pruebas.md`) | “Usuarios por rol” incompleto | Usuario `USR-TEST-ADMINIST` |
| D3 | `JWT_SECRET_KEY` de CI tenía 18 bytes → warning RFC 7518 | Suite ruidosa; secreto de prueba inválido | Clave ≥ 32 caracteres en CI y `conftest.py` |
| D4 | `web-ci.yml` no disparaba en `sprints/**` | La rama de sprint no corría la suite web | Trigger `sprints/**` |
| D5 | No había runbook versionado junto a las pruebas | Criterio “instrucciones versionadas” débil | `tests/README.md` |

Los casos positivos/negativos de auth (400, 401) y Spark (403 a `enfermero` en clínico) **siguen pasando** con el fixture corregido.

## 5. Matriz de casos T5

| ID | Caso | Tipo | Resultado |
|---|---|---|---|
| AMB-01 | Roles sintéticos completos y relaciones paciente–estudio | Positivo | Aprobado |
| AMB-02 | Prefijo `TEST` en usuarios, pacientes y estudios | Límite / dato | Aprobado |
| AMB-03 | Mutar fixture no contamina la prueba siguiente | Restauración | Aprobado |
| AMB-04 | `MONGO_DB` de prueba ≠ producción | Aislamiento | Aprobado |
| AMB-05 | App real registra auth, patients, studies/exams y spark | Integración | Aprobado |
| API-01 | `GET /health` → 200 | Positivo | Aprobado |
| API-02 | Login vacío → 400 | Negativo | Aprobado |
| API-03 | Token inválido → 401 | Negativo / permiso | Aprobado |
| API-04 | Pacientes y gestión sin token → 401 | Permiso | Aprobado |
| API-05 | Notas de enfermería GET/POST sin token → 401 | Permiso | Aprobado |
| SPK-01 | Spark clínico: pending, run, conflict, completed, empty, failed, 400, 401, 403 | Positivo / negativo | Aprobado |

## 6. Archivos tocados en T5

```text
backend/api_hospital/tests/fixtures/sprint1_data.json
backend/api_hospital/tests/test_sprint1_environment.py
backend/api_hospital/tests/conftest.py
backend/api_hospital/tests/README.md
.github/workflows/api-ci.yml
.github/workflows/web-ci.yml
docs/sprints/sprint-7/pbl-26-t5-resultados-ambiente-prueba.md
evidence/jaime/pbl-26/resultados.md
evidence/jaime/pbl-26/pytest-ambiente.txt
```

## 7. Vínculo con la historia

Esta evidencia cierra **T5** de la historia de ambiente de prueba (PBL-26 / feature *Ambiente y datos de prueba*).  
T1–T4 (diseño, fixtures, casos, CI) ya existían en Sprint 1 (`test_sprint1_environment.py`, `sprint1_data.json`, `api-ci.yml`) y se reutilizan. T5 **ejecuta**, **corrige** y **registra**.

## 8. Cómo repetir

Ver `backend/api_hospital/tests/README.md`.
