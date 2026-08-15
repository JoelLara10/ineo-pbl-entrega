# Evidencia final de validación de la API

## 1. Información general

| Elemento | Detalle |
| --- | --- |
| Responsable | Zahid |
| Componente validado | Backend Flask de INEO Hospital |
| Sprint | Sprint 6 — Cierre |
| Trabajo complementario | Pruebas y automatización pendientes del Sprint 5 |
| Framework de pruebas | pytest 8.4.2 |
| Herramienta de cobertura | pytest-cov 7.0.0 |
| Versión usada en integración continua | Python 3.12 |
| Rama de trabajo | `sprints/api` |
| Fecha de validación | 14 de agosto de 2026 |

## 2. Objetivo de la validación

El objetivo fue comprobar que la API pudiera iniciar correctamente en un entorno de pruebas y que los endpoints principales rechazaran solicitudes sin credenciales o con tokens inválidos. También se configuró una validación automática para que estas comprobaciones se ejecuten en cada actualización de la rama de API y en cada Pull Request dirigido a `main`.

La validación se concentró en tres áreas:

1. Disponibilidad básica de la aplicación Flask.
2. Validación de credenciales y tokens de autenticación.
3. Protección de las operaciones de pacientes, administración y Enfermería.

## 3. Archivos incorporados

```text
backend/api_hospital/tests/
├── __init__.py
├── conftest.py
├── test_auth.py
├── test_patients.py
└── test_nursing.py

.github/workflows/api-ci.yml
backend/api_hospital/requirements.txt
evidence/zahid/resultados-api.md
```

En `requirements.txt` se agregaron las dependencias necesarias para ejecutar las pruebas y calcular la cobertura:

```text
pytest==8.4.2
pytest-cov==7.0.0
```

## 4. Preparación del entorno de pruebas

En `tests/conftest.py` se configuraron dos fixtures:

- `app`: crea una instancia aislada de la aplicación mediante `create_app()` y activa el modo `TESTING`.
- `client`: genera el cliente de pruebas de Flask para realizar solicitudes HTTP sin levantar un servidor externo.

Durante la revisión de `app.py` confirmé que `create_app()` no recibe un diccionario de configuración. Por esa razón, la configuración de pruebas se aplica después de crear la instancia Flask.

También se sustituye temporalmente `init_scheduler` durante pytest. Esto evita que las tareas automáticas de respaldo permanezcan ejecutándose en segundo plano y permite que las pruebas terminen de forma controlada.

## 5. Matriz de casos de prueba

| ID | Módulo | Método y endpoint | Datos utilizados | Resultado esperado | Resultado obtenido | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| API-TEST-001 | Estado de la API | `GET /health` | Sin cuerpo | HTTP 200 y `status: ok` | HTTP 200 y `status: ok` | Aprobado |
| API-TEST-002 | Autenticación | `POST /api/v1/auth/login` | JSON vacío `{}` | HTTP 400 por credenciales faltantes | HTTP 400 y mensaje de error | Aprobado |
| API-TEST-003 | Autenticación | `GET /api/v1/auth/me` | `Bearer token-invalido` | HTTP 401 por token inválido | HTTP 401 y mensaje de error | Aprobado |
| API-TEST-004 | Pacientes | `GET /api/v1/patients` | Sin encabezado de autorización | HTTP 401 | HTTP 401: `Token no proporcionado` | Aprobado |
| API-TEST-005 | Administrativo | `GET /api/v1/gestion-pacientes` | Sin encabezado de autorización | HTTP 401 | HTTP 401: `Token no proporcionado` | Aprobado |
| API-TEST-006 | Enfermería | `GET /api/v1/appointments/1/nursing-notes` | Sin encabezado de autorización | HTTP 401 | HTTP 401: `Token no proporcionado` | Aprobado |
| API-TEST-007 | Enfermería | `POST /api/v1/appointments/1/nursing-notes` | Nota de control sin token | HTTP 401 antes de guardar información | HTTP 401: `Token no proporcionado` | Aprobado |

## 6. Verificación de la ruta de Enfermería

Durante la preparación de las pruebas se revisó el mapa de rutas generado por Flask. Aunque el blueprint está definido en `medical.py`, la ruta efectiva registrada para las notas de Enfermería es:

```text
/api/v1/appointments/<id_atencion>/nursing-notes
```

Por lo tanto, las pruebas utilizan:

```text
/api/v1/appointments/1/nursing-notes
```

Esta comprobación evitó utilizar una ruta inventada como `/api/v1/enfermeria` o incluir incorrectamente `/medical` en la URL.

## 7. Ejecución de pytest

Comando configurado para la validación:

```bash
cd backend/api_hospital
pytest -v --cov=. --cov-report=term-missing
```

Resultado registrado:

```text
collected 7 items

tests/test_auth.py::test_health_endpoint_reports_api_available PASSED
tests/test_auth.py::test_login_requires_credentials PASSED
tests/test_auth.py::test_current_user_rejects_invalid_token PASSED
tests/test_nursing.py::test_nursing_notes_read_requires_authentication PASSED
tests/test_nursing.py::test_nursing_notes_write_requires_authentication PASSED
tests/test_patients.py::test_patients_requires_authentication PASSED
tests/test_patients.py::test_administrative_patients_requires_authentication PASSED

7 passed
```

### Resumen cuantitativo

| Métrica | Resultado |
| --- | ---: |
| Pruebas recopiladas | 7 |
| Pruebas aprobadas | 7 |
| Pruebas fallidas | 0 |
| Tasa de aprobación | 100% |
| Cobertura inicial del backend completo | 26% |

El 26% representa una línea base sobre todo el backend. El alcance de esta entrega está centrado en disponibilidad, autenticación y acceso protegido; no pretende cubrir todavía todos los servicios, reportes, respaldos, generación de PDF ni operaciones que dependen de datos almacenados en MongoDB.

## 8. Integración continua con GitHub Actions

El workflow se colocó en la ubicación reconocida por GitHub Actions:

```text
.github/workflows/api-ci.yml
```

El proceso automatizado realiza las siguientes actividades:

1. Descarga el contenido del repositorio.
2. Configura Python 3.12.
3. Instala las dependencias de `requirements.txt`.
4. Compila los archivos Python para detectar errores de sintaxis.
5. Ejecuta pytest y genera el reporte de cobertura.

La automatización se activa con actualizaciones en `main`, en ramas `sprint-*`, en `sprints/**` y en Pull Requests dirigidos a `main`.

### Resultado observado en GitHub

| Verificación | Resultado | Tiempo registrado |
| --- | --- | ---: |
| `INEO API CI / Validate Flask API (push)` | Correcto | 39 s |
| `INEO API CI / Validate Flask API (pull_request)` | Correcto | 38 s |
| Conflictos con la rama base | Sin conflictos | — |

GitHub mostró el estado **All checks have passed**, confirmando que la instalación, compilación y ejecución automatizada de las pruebas terminaron correctamente.

## 9. Análisis de seguridad

Los resultados comprueban que:

- El endpoint de autenticación no acepta una solicitud sin usuario y contraseña.
- Un token inválido no permite consultar la información del usuario actual.
- Los listados de pacientes no quedan expuestos sin autenticación.
- La gestión administrativa de pacientes rechaza accesos anónimos.
- Las notas de Enfermería no se pueden leer sin token.
- Una nota de Enfermería no se puede registrar sin autenticación, por lo que la solicitud se detiene antes de acceder a MongoDB o modificar información clínica.

No se utilizaron pacientes reales, contraseñas reales, tokens válidos ni archivos `.env`. Los casos se diseñaron para verificar el control de acceso sin consultar ni modificar datos clínicos.

## 10. Consideraciones técnicas

- Las pruebas se ejecutan oficialmente con Python 3.12, que es la versión configurada en GitHub Actions.
- El intento local con Python 3.13 presentó una incompatibilidad de compilación con `pydantic_core==2.6.3`; esto no representa un error funcional de la API ni del workflow.
- MongoDB no necesita estar activo para estos siete casos porque las solicitudes no autorizadas son rechazadas antes de llegar a la capa de datos.
- Las tareas automáticas del scheduler permanecen desactivadas únicamente durante pytest y conservan su funcionamiento normal al iniciar la API fuera del entorno de pruebas.

## 11. Historias relacionadas

- `QA-002`: validación automatizada de la API.
- `QA-003`: integración continua y evidencia de resultados.
- `SEC-001`: comprobación de autenticación y protección de endpoints.

## 12. Conclusión

Con esta validación confirmé que la API puede inicializarse correctamente en el entorno automatizado y que los endpoints evaluados aplican los controles de autenticación antes de permitir el acceso a información clínica o administrativa.

Las siete pruebas finalizaron satisfactoriamente y GitHub Actions confirmó el mismo comportamiento tanto en el evento `push` como en el Pull Request. Con esto queda establecida una base de pruebas repetible para detectar errores de disponibilidad y seguridad en cambios posteriores del backend.

Como trabajo posterior se recomienda ampliar la cobertura con una base de datos de prueba aislada para validar altas, consultas y actualizaciones autorizadas, sin utilizar información clínica real.
