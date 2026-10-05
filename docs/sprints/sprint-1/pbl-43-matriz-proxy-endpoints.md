# PBL-43 — Matriz de proxy y endpoints

## Configuración verificada

| Elemento | Valor o regla | Evidencia |
| --- | --- | --- |
| URL base web | `VITE_API_URL`; si no existe, `http(s)://<host>:5001/api/v1` | `frontend/clinica-web-react/src/services/api.js` |
| Prefijo API | `/api/v1` | `backend/api_hospital/config.py` |
| Proxy/autenticación | Axios agrega `Authorization: Bearer <token>` | `frontend/clinica-web-react/src/services/api.js` |
| CORS | Orígenes configurados, credenciales, `Authorization` y `Content-Type` | `backend/api_hospital/app.py` y `config.py` |
| Error común | JSON con campo `error`; Spark agrega `code` y `contract_version` | manejadores de Flask y `routes/spark.py` |

## Matriz crítica de rutas

| Ruta | Método | Permiso | 200/202 | 401 | 403 | 404 |
| --- | --- | --- | --- | --- | --- | --- |
| `/health` | GET | Público | Sí | N/A | N/A | N/A |
| `/api/v1/auth/login` | POST | Público | Sí | Credenciales inválidas | N/A | N/A |
| `/api/v1/patients` | GET | Usuario autenticado | Sí | Sin token | Según rol | Ruta inexistente |
| `/api/v1/studies/counts` | GET | Usuario autenticado | Sí | Sin token | Según rol | Ruta inexistente |
| `/api/v1/analytics/dashboard` | GET | Usuario autenticado | Sí | Sin token | Según rol | Ruta inexistente |
| `/api/v1/spark/overview` | GET | Admin | Sí | Sin token | Rol no admin | Ruta inexistente |
| `/api/v1/spark/{tipo}` | GET | Admin | Sí | Sin token | Rol no admin | Ruta inexistente |
| `/api/v1/spark/status/{tipo}` | GET | Admin | Sí | Sin token | Rol no admin | Ruta inexistente |
| `/api/v1/spark/run/{tipo}` | POST | Admin | 200/202 | Sin token | Rol no admin | Ruta inexistente |

Tipos Spark admitidos: `analytics`, `met`, `clinical` y `unsupervised`.

## Evidencia automatizada

`tests/test_sprint1_proxy_endpoints.py` valida 200, 401, 403, 404 y preflight CORS. `tests/test_spark_contract.py` recorre todos los métodos, tipos, permisos y contratos Spark. Los incidentes de tiempo de espera, expiración, ejecución duplicada y mensajes sensibles están cubiertos por las pruebas de contrato y motor.

## Resultado

La web y la API comparten el prefijo versionado, el origen local de Vite está permitido y los endpoints críticos responden con autenticación y códigos coherentes. No quedan incidencias bloqueantes conocidas para el Sprint 1.
