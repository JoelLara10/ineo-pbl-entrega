# Evidencia — Zahid, Sprint 8

Ejecución local del 2026-10-08 sobre la rama `sprints/zahid-sprint-8`,
base `fd8dc6c`. Alcance y trazabilidad: [entrega-zahid.md](entrega-zahid.md).

## Resultados observados

| Verificación | Resultado |
|---|---|
| API completa, incluyendo Spark real | **179 aprobadas, 0 fallos, 0 errores, 0 omitidas** |
| Frontend | **76 aprobadas en 14 archivos** |
| Lint web | Aprobado (`oxlint`) |
| Traducciones | Todas las claves estáticas presentes en español e inglés |
| Compilación web de producción | Aprobada (`vite build`) |
| Integridad del diff | `git diff --check` aprobado |

Desglose del reporte JUnit de API (duración total: 43.013 segundos):

| Suite | Pruebas aprobadas |
|---|---:|
| `tests.test_auth` | 13 |
| `tests.test_nursing` | 2 |
| `tests.test_patients` | 2 |
| `tests.test_spark_contract` | 71 |
| `tests.test_spark_engine` | 7 |
| `tests.test_sprint1_environment` | 4 |
| `tests.test_sprint1_proxy_endpoints` | 2 |
| `tests.test_sprint7_jesus` | 9 |
| `tests.test_sprint8_zahid` | 69 |

Las siete pruebas de `test_spark_engine` ejecutaron Java/PySpark real: los cuatro
tipos, datos vacíos/parciales/constantes, subproceso y recorrido HTTP → trabajador
→ resultado. Los cuatro resultados reales se validaron contra el esquema v1.
El resto de integración API usa Flask y Mongo sintético mediante mongomock.
Las pruebas web usan servicios simulados; no son un recorrido de navegador
contra una API desplegada.

Hubo 299 avisos de deprecación de dependencias/código existente, principalmente
`datetime.utcnow()` del middleware compartido. No hubo fallos ni pruebas omitidas.
No se ejecutó SIT con Mongo real ni un despliegue en producción.

## Entorno y reproducción

Python 3.12.14, Java 17.0.20, PySpark 3.5.7, Node 24.19.0.
Dependencias del repositorio y su lockfile. `rfc3339-validator==0.1.4` está fijado
en `requirements-test.txt` para que `FormatChecker` valide fechas; las pruebas
negativas fallan si esa validación no está activa.

Desde `backend/api_hospital`, en un entorno virtual con Java 17 disponible:

```bash
python -m pip install -r requirements.txt -r requirements-test.txt -r requirements-spark.txt
RUN_SPARK_TESTS=1 SPARK_LOCAL_IP=127.0.0.1 python -m pytest -q --junitxml=sprint8-api-results.xml
```

Desde `frontend/clinica-web-react`:

```bash
npm ci
npm test
npm run lint
npm run check:i18n
npm run build
```

`tests/conftest.py` fija una base `ineo_test_pytest`, datos sintéticos y una clave
exclusiva de prueba. No requiere credenciales reales ni modifica producción.
Los workflows existentes `api-ci.yml` y `web-ci.yml` incluyen `sprints/**`;
la API publica su evidencia JUnit y tiene un job separado de Spark real.
Este documento registra la ejecución local, no presupone el resultado de CI.

## Fuente de planificación

Archivo: `DOC-20260919-WA0000(1).xlsx`.
SHA-256: `fcdb6764b0844479006bf0bbf8e4a84c02cbe5ccbd4f0cd0c65a443e9b924501`.
Hojas consultadas: PBL, Tareas y Sprint planning. PBL-02: 5 puntos;
PBL-13: 3 puntos ajustados. La aprobación humana y el cierre del tablero
corresponden al equipo; esta entrega prepara los cambios para revisión.
