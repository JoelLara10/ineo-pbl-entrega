# OftalCore — cierre técnico de PBL-22 y PBL-27

Fecha: 21 de octubre de 2026. Sprint 9 de Azure (Sprint 3 del PBL).
Responsable de las historias: Jesús. Correcciones e integración realizadas con asistencia de Codex por autorización de Joel.

Este registro y [la evidencia estructurada](PBL-27_ejecucion_corregida.json) actualizan los resultados de ejecución y cobertura de los documentos Word originales. El archivo de PBL-27 contiene ahora **25 casos parametrizados**, no 23. Los documentos originales se conservan como antecedentes.

## Objetivo, precondiciones y datos

Comprobar autenticación, permisos, validación de archivos y Analytics antes de integrar la API, y conservar el guardado e historial del Balance Hídrico. Se usa Python 3.12, las dependencias de `requirements.txt` y `requirements-test.txt`, MongoDB sintético mediante `mongomock`, tokens de prueba y carpetas `tmp_path`; no se requieren cuentas reales ni servicios externos para estos casos. El motor Spark real se valida separadamente en CI.

## Casos y resultados de PBL-27 (Azure #428, tareas #447–451)

| Caso | Datos/acción | Resultado esperado y obtenido | Casos aprobados |
| --- | --- | --- | ---: |
| CP-UT-001 | Credenciales válidas, incorrectas y ausentes; servicio de login simulado | HTTP 200 con token solo para válidas; 401/400 con error controlado | 3 |
| CP-UT-002 | Listado de usuarios con admin, médico, enfermero y estudios; carga con roles no autorizados | Admin 200; roles denegados 403; persistencia no invocada al denegar | 6 |
| CP-UT-003 | PDF/PNG/DOCX, sin extensión, EXE, doble extensión; carga válida, ausente y nombre vacío | Extensiones según lista permitida; carga válida guarda bytes y observaciones en carpeta temporal; archivo inseguro/missing produce 400 sin archivo ni persistencia | 11 |
| CP-UT-004 | Agregaciones vacías, parciales y válidas; roles no autorizados | Esquema estable, listas vacías sin datos inventados, valores exactos y promedio redondeado; 403 sin ejecutar el servicio en roles denegados | 5 |

Rutas verificadas según el registro real de Flask: `/api/v1/auth/login`, `/api/v1/auth/users`, `/api/v1/25/upload` y `/api/v1/clinical`. Analytics ejecuta el servicio real con agregaciones de base de datos simuladas por colección; no se sustituye el resultado final del servicio por el valor esperado.

## PBL-22 (Azure #308, tareas #399–401)

Se integraron secciones diferenciadas de entradas y salidas, etiquetas y unidades, totales en vivo y balance neto. Se conservan el encabezado reciente de develop, observaciones, la ruta de guardado y la recarga del historial. Tres pruebas aprobadas verifican estado inicial, cálculo 750 ml − 350 ml = 400 ml y envío/recarga mediante `/appointments/25/fluid-balance`.

## Ejecución y cobertura

- Backend completo: **254 aprobadas, 8 omitidas, 0 fallidas**.
- PBL-27: **25/25 aprobadas**.
- Web completa: **114/114 aprobadas en 24 archivos**, con `npm test -- --maxWorkers=2`.
- `npm run check:i18n`, `npm run lint`, `npm run build` y `npm run check:bundle`: correctos. Lint conserva una advertencia previa en configuración de usuarios.
- Cobertura de líneas de `routes`, `services` y `middleware`: **40.40%** (2163/5354). Desglose por módulo y huellas SHA-256 del código en el JSON adjunto. Esta cifra describe ese alcance, no una garantía de cobertura funcional de todos los módulos.
- Las ocho pruebas omitidas corresponden al motor Spark real; se ejecutan por separado en GitHub Actions con Java 17 y PySpark. La ejecución local no se presenta como evidencia del motor real.

Reproducir desde `backend/api_hospital`:

```bash
python -m pip install -r requirements.txt -r requirements-test.txt
python -m pytest -q --cov=routes --cov=services --cov=middleware --cov-report=term --cov-report=json:coverage.json --junitxml=test-results.xml
```

Evidencia automática adicional: [PR #66](https://github.com/JoelLara10/ineo-pbl-entrega/pull/66), [API CI](https://github.com/JoelLara10/ineo-pbl-entrega/actions/runs/39539644543), [Web CI](https://github.com/JoelLara10/ineo-pbl-entrega/actions/runs/39539644624) y sus artefactos JUnit. Los estados definitivos de los checks se consultan en el PR.

## Defectos corregidos e integración

Se completó la prueba de archivo inseguro que antes solo instalaba un mock sin enviar solicitud ni comprobar resultados. Se incorporó CP-UT-004 y la comprobación de carga válida y permisos. Se resolvieron los seis conflictos con develop conservando su package.json, pruebas y validaciones de Sprint 8 vigentes, y combinando el formulario actual con PBL-22. La historia y autoría previa de sprint-3 se conserva como segundo padre del commit de integración.

Conclusión: los casos CP-UT-001 a CP-UT-004 y las tres verificaciones de PBL-22 tienen evidencia automatizada versionada. La promoción sigue el orden rama de corrección → develop → qa mediante pull requests.
