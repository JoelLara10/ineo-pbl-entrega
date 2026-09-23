# Ambiente de prueba (datos sintéticos)

Instrucciones versionadas para levantar y restablecer el ambiente de validación **sin expedientes reales**.

## Variables

| Variable | Valor de prueba | No usar |
|---|---|---|
| `MONGO_URI` | `mongodb://localhost:27017/` | URI de producción / Atlas con datos reales |
| `MONGO_DB` | `hospital_test` | `hospital_db`, `ineo_db2` |
| `SECRET_KEY` | secreto ≥ 32 caracteres | secretos de producción |
| `JWT_SECRET_KEY` | secreto ≥ 32 caracteres | `ci-test-jwt-secret-key` (18 bytes, RFC 7518) |

## Cómo ejecutar

Desde `backend/api_hospital`:

```bash
export MONGO_URI=mongodb://localhost:27017/
export MONGO_DB=hospital_test
export SECRET_KEY=ci-test-secret-key-min-32-characters
export JWT_SECRET_KEY=ci-test-jwt-secret-key-min-32-chars

python -m pytest -v tests/test_sprint1_environment.py
python -m pytest -v --cov=. --cov-report=term-missing
```

CI (`.github/workflows/api-ci.yml`) usa las mismas variables y `MONGO_DB=hospital_test`.

## Datos

- Fixture: `tests/fixtures/sprint1_data.json`
- Identificadores con prefijo `TEST`
- Roles: `admin`, `administrativo`, `medico`, `enfermero`, `estudios`
- Pacientes y estudios sintéticos ligados por `patient_id`

`conftest.py` entrega una **copia nueva** (`deepcopy`) en cada prueba. Mutar el fixture en un test no afecta al siguiente.

## Restauración

No hay que limpiar Mongo a mano para estas pruebas: el fixture no escribe a la base. Las pruebas de API que tocan Spark usan un store en memoria (`MemorySparkJobs`).
