# PBL-03-T1 — Revisión del flujo de ejecución, estado y carga del resultado clínico

**Sistema:** Sistema de Gestión Clínica INEO  
**Historia:** PBL-03 — Ejecutar el análisis clínico y visualizar sus resultados  
**Tarea:** T1 — Revisar código, dependencias, datos y restricciones. Documentar los cambios **antes de programar**.  
**Sprint:** 7  
**Repositorio:** `ineo-pbl-entrega`  
**Rama base revisada:** `main`  
**Commit revisado:** `0493083769ae48982eeca15db517eb0a4f9187ca`  
**Fecha de revisión:** 22 de septiembre de 2026  
**Responsable:** Jaime Diaz Gonzalez
**Estado:** Documentado. **Sin cambios de código en esta tarea.**

---

## 1. Objetivo

Identificar, con evidencia en el código de `main`, qué existe, qué falta y qué se debe corregir para que el flujo de **ejecución**, **consulta de estado** y **carga del resultado clínico** cumpla el criterio de aceptación:

> La interfaz cambia entre pendiente, procesando, completado y fallido; al completarse muestra datos reales.

Esta revisión no implementa el arreglo. Los cambios de diseño quedan para PBL-03-T2 y la programación para PBL-03-T3.

---

## 2. Historia y alcance

| Campo | Valor |
|---|---|
| Enunciado | Como usuario clínico, quiero ejecutar el análisis clínico y visualizar sus resultados al terminar, para apoyar decisiones clínicas con información procesada. |
| Módulo UI | Analítica Spark → Analítica clínica |
| Ruta web | `/admin/spark/clinical` |
| Componente | `ClinicalAnalyticsScreen` delega en `SparkAnalysisScreen` con `type="clinical"` |
| Criterio | Estados `pendiente`, `procesando`, `completado`, `fallido`; en completado, datos reales |

**Dentro de PBL-03**

- Arrancar el análisis clínico.
- Consultar su estado.
- Cargar y mostrar el resultado cuando termine.
- Representar los cuatro estados del criterio.

**Fuera de PBL-03 (no modificar salvo impacto directo)**

- Analítica general (`analytics`), MET (`met`) y no supervisado (`unsupervised`), excepto `overview` si comparte contrato.
- Flujos de pacientes, médico, enfermería, estudios, facturación y respaldos.
- Rediseño visual del sistema.

---

## 3. Código revisado

### 3.1 Frontend

| Archivo | Hallazgo |
|---|---|
| `frontend/clinica-web-react/src/pages/spark/ClinicalAnalyticsScreen.jsx` | Wrapper. Solo renderiza `<SparkAnalysisScreen type="clinical" />`. |
| `frontend/clinica-web-react/src/pages/spark/SparkAnalysisScreen.jsx` | Orquesta carga, ejecución, polling cada 3 s y pintado de estados/resultados. |
| `frontend/clinica-web-react/src/pages/spark/SparkDashboard.jsx` | Panel; llama `GET /spark/overview` y muestra si hay resultados. |
| `frontend/clinica-web-react/src/services/sparkService.js` | Cliente HTTP del contrato Spark. |
| `frontend/clinica-web-react/src/services/api.js` | Axios, `VITE_API_URL` o `http://<host>:5001/api/v1`, Bearer JWT. |
| `frontend/clinica-web-react/src/router/AppRouter.jsx` | Rutas Spark solo si `admin` o `administrativo`. |
| `frontend/clinica-web-react/src/components/layout/Sidebar.jsx` | Menú Spark con la misma restricción de rol. |
| `frontend/clinica-web-react/src/i18n/locales/es.json` y `en.json` | Claves `spark.*` (títulos, botones, estados). |
| `frontend/clinica-web-react/src/tests/sprint1-joel.test.js` | Prueba estructural de rutas y estados Spark (PBL-01/PBL-04/PBL-05). |
| `frontend/clinica-web-react/src/spark/*` | Copia antigua. **El router no la importa.** Riesgo de divergencia. |

### 3.2 Backend

| Archivo | Hallazgo |
|---|---|
| `backend/api_hospital/app.py` | Registra auth, patients, medical, analytics, studies, exams, billing, backup, performance. **No registra Spark.** |
| `backend/api_hospital/routes/spark.py` | **No existe.** |
| `backend/api_hospital/services/spark_service.py` | **No existe.** |
| `backend/api_hospital/routes/analytics.py` | `GET /analytics/clinical` síncrono, roles `admin` y `medico`. No es el contrato de la pantalla Spark. |
| `backend/api_hospital/services/analytics_service.py` | `get_clinical_analytics()` agrega Mongo: diagnósticos, edad, estancia. |
| `backend/api_hospital/middleware/auth_middleware.py` | `token_required` y `role_required`. 401 sin/ inválido token; 403 sin rol. |
| `backend/api_hospital/scheduler/jobs.py` | APScheduler solo para respaldos automáticos. No hay worker de análisis. |
| `backend/api_hospital/tests/` | Hay `test_auth`, `test_patients`, `test_nursing`, `test_sprint1_environment`. **No hay pruebas Spark.** |
| `backend/api_hospital/requirements.txt` | Flask, pymongo, pandas, numpy. **No incluye `pyspark`.** |

### 3.3 Documentación previa

| Documento | Qué aporta a T1 |
|---|---|
| `docs/manual-tecnico/spark.md` | Contrato esperado `/api/v1/spark/*` y confirma backend ausente (Sprint 5). |
| `docs/sprints/sprint-5/resultados-pruebas.md` | SPK-001 a SPK-007 bloqueadas. |
| `docs/pbl/matriz-trazabilidad.md` | `ANA-001` pendiente de evidencia final. |
| `docs/sprints/sprint-1/entrega-joel.md` | UI Spark y estados ya trabajados en frontend (PBL-01, PBL-04, PBL-05). |

La documentación de Spark está desfasada respecto al frontend de sprint 7 (estados con acción), pero **el hueco del backend se mantiene**.

---

## 4. Dependencias

### 4.1 Runtime

| Capa | Dependencia | Uso en PBL-03 |
|---|---|---|
| Web | React 19, React Router 7, axios, i18next | Pantalla, rutas, cliente HTTP, textos |
| API | Flask 2.3, Flask-CORS, PyJWT, pymongo | Endpoints, auth, Mongo |
| Datos | MongoDB (`MONGO_URI`, `MONGO_DB`) | Fuente del análisis clínico |
| Cálculo disponible | pandas, numpy | Agregaciones/postproceso sin Spark |
| Cálculo planeado y ausente | PySpark | No está instalado ni configurado |
| Jobs | APScheduler | Solo backups; reutilizable como patrón de fondo, no como análisis clínico |

### 4.2 Entorno local

| Variable | Dónde | Observación |
|---|---|---|
| `VITE_API_URL` | frontend `.env.local` | Debe ser `http://localhost:5001/api/v1` |
| `MONGO_URI` | backend `.env` | Por defecto `mongodb://localhost:27017/` |
| `MONGO_DB` | backend `.env` | `.env.example` usa `hospital_db`; `config.py` cae a `ineo_db2` si falta `.env` |
| `SECRET_KEY` / `JWT_SECRET_KEY` | backend `.env` | Deben coincidir con `auth_middleware` |
| `PORT` | backend | `5001` |

**Restricción:** no versionar `.env`, secretos, `venv/`, `node_modules/`, respaldos ni datos clínicos reales.

### 4.3 CI

- Web: `npm ci`, `npm run lint`, `npm test`, `npm run build`.
- API: `compileall` + `pytest`.
- Cualquier cambio de T3/T4 debe seguir pasando estas puertas.

---

## 5. Datos

### 5.1 Contrato que espera el frontend (`sparkService.js`)

| Método | Ruta relativa a `/api/v1` | Uso |
|---|---|---|
| GET | `/spark/overview` | Semáforo del dashboard |
| POST | `/spark/run/clinical` | Inicia el análisis |
| GET | `/spark/status/clinical` | Polling de estado |
| GET | `/spark/clinical` | Carga del resultado |
| GET | `{path}` blob | Imágenes de `visualizations` |

### 5.2 Forma de resultado que ya pinta `SparkAnalysisScreen`

El front ignora `available`, `timestamp` y `visualizations` como secciones y pinta el resto si tiene contenido:

```json
{
  "available": true,
  "timestamp": "2026-09-22T12:00:00",
  "top_diagnosis": [{ "diagnosis": "J18.9", "count": 12 }],
  "age_distribution": [{ "range": "30", "count": 8 }],
  "average_stay_days": 3.4,
  "visualizations": []
}
```

Esa forma coincide con `AnalyticsService.get_clinical_analytics()`, que hoy devuelve:

- `top_diagnosis` desde colección `diagnosticos`
- `age_distribution` desde `atencion` ⨝ `pacientes`
- `average_stay_days` desde `expedientes` ⨝ `atencion`

**No incluye** `available` ni `timestamp`. El endpoint actual no sirve tal cual a la pantalla Spark.

### 5.3 Colecciones tocadas

`diagnosticos`, `atencion`, `pacientes`, `expedientes`.

Campos usados: `diagnostico_principal`, `Id_exp`, `fecnac`, `id_atencion`, `fecha_alta`, `fecha_ing`.

### 5.4 Restricciones de datos

- Prohibido persistir o commitear nombres, expedientes o estudios reales.
- El resultado mostrado debe ser **agregado** (conteos, rangos, promedios), no listados identificables.
- Pruebas: fixture `tests/fixtures/sprint1_data.json` (ids `TEST`), ya usado por CI.
- Si Mongo no tiene datos: estado `completed` con `available: false` (vacío), **no** inventar métricas.
- Si el job falla: `failed` + `log` técnico, sin stack con secretos.

---

## 6. Flujo actual (as-is)

```text
Usuario (admin/administrativo)
    → /admin/spark/clinical
    → SparkAnalysisScreen type=clinical
        1. GET /spark/clinical
        2. GET /spark/status/clinical
        3. POST /spark/run/clinical   (botón Ejecutar)
        4. si status.running: GET /spark/status/clinical cada 3 s
        5. cuando running=false: recarga resultados
```

### 6.1 Qué ocurre hoy

`app.py` no registra `/spark/*`. Flask responde **404** `{ "error": "Recurso no encontrado" }`.

`load()` captura el error y la UI muestra `spark.states.error` u `offline`. El botón Ejecutar llama `run()` y vuelve a fallar. **No hay pendiente real, ni procesando de un job, ni completado con datos.**

`GET /api/v1/analytics/clinical` sí existe, pero:

- es síncrono (bloquea hasta terminar);
- no guarda estado de job;
- no habla el contrato `available` / `state` / `running`;
- no es llamado por `sparkService`.

### 6.2 Mapa de estados UI vs criterio

| Criterio PBL-03 | `status.state` actual | Clave i18n | ¿Cumple? |
|---|---|---|---|
| Pendiente | `idle` (y a veces se confunde con `empty`) | `spark.states.notRun` | Parcial. El nombre no es `pending`/`pendiente`. |
| Procesando | `running === true` o `pending`/`processing` | `spark.states.processing` | Preparado en UI; no hay backend que lo emita. |
| Completado | implícito: `data.available` y sin error | no hay `spark.states.completed` | Parcial. Muestra datos, pero no nombra el estado. |
| Fallido | `failed` | `spark.states.failed` | Preparado en UI; no hay backend que lo emita. |
| (extra) Cargando | `loading` local | `spark.states.loading` | Auxiliar de red; no es estado del job. |
| (extra) Sin conexión | error sin `response` | `spark.states.offline` | Manejo de red; conservar. |
| (extra) Vacío | `!available` y no `idle` | `spark.states.empty` | Útil si el job termina sin datos. |

El front **ya distingue** varios casos (trabajo de PBL-04). El defecto de PBL-03 no es “crear la pantalla”, es **conectar ejecución + estado + resultado real** y alinear nombres con el criterio.

---

## 7. Permisos y contradicción de rol

| Superficie | Roles permitidos |
|---|---|
| Rutas `/admin/spark/*` | `admin`, `administrativo` |
| Sidebar Spark | `admin`, `administrativo` |
| `GET /analytics/clinical` | `admin`, `medico` |
| Historia PBL-03 | “usuario clínico” |

Un médico no entra a `/admin/spark/clinical` aunque el endpoint clínico de analytics sí lo autoriza. T2 debe fijar el rol. Recomendación de esta revisión: **`admin` y `medico`** para el flujo clínico, sin abrir Spark a `enfermero` ni `estudios`.

---

## 8. Restricciones técnicas para el arreglo

1. Conservar `sparkService` y las rutas `/spark/run/{type}`, `/spark/status/{type}`, `/spark/clinical`.
2. No bloquear el `POST /run` hasta terminar el cálculo; el job debe ser asíncrono (hilo o scheduler) y el HTTP debe volver con estado `processing`.
3. Reutilizar `token_required` + `role_required`. No inventar otro esquema de auth.
4. Reutilizar `AnalyticsService.get_clinical_analytics()` como fuente de datos clínicos, envolviéndola con `available`, `timestamp` y persistencia de estado.
5. No añadir `pyspark` en T3 salvo decisión explícita del equipo: no está en `requirements.txt` ni en el despliegue actual (Render/Python 3.11). Un job controlado con pandas/Mongo cumple “datos reales” del criterio.
6. No romper las pruebas de Joel (`sprint1-joel.test.js`): si se renombra `notRun` → `pending`, hay que actualizar esa prueba en T4.
7. No usar `src/spark/` (copia muerta). Toda corrección va en `src/pages/spark/`.
8. No devolver identificadores de paciente en el payload Spark.
9. Tipos distintos de `clinical` pueden seguir respondiendo `available: false` si no son parte de esta historia.
10. Mensajes de error de API en JSON `{ "error": "..." }`, patrón ya usado por Flask.

---

## 9. Brechas a corregir (backlog de T2/T3/T4)

| ID | Brecha | Tarea |
|---|---|---|
| G-01 | No existen `routes/spark.py` ni `services/spark_service.py`. | T3 |
| G-02 | `app.py` no registra blueprint Spark. | T3 |
| G-03 | `POST /spark/run/clinical` y `GET /spark/status/clinical` no existen. | T3 |
| G-04 | `GET /spark/clinical` no existe; el front no usa `/analytics/clinical`. | T3 |
| G-05 | Estados del criterio no están alineados (`notRun` vs `pending`; no hay `completed`). | T2 / T3 / T4 |
| G-06 | Un 404 se muestra como error/offline, no como “servicio Spark ausente” accionable de forma estable. | T3 / T4 |
| G-07 | Conflicto de roles: historia clínica vs UI admin/administrativo. | T2 / T4 |
| G-08 | i18n no tiene `spark.states.pending` ni `spark.states.completed`. | T4 |
| G-09 | No hay pruebas API del flujo clínico Spark. | T3 / T4 |
| G-10 | `get_clinical_analytics()` no entrega `available`/`timestamp` ni maneja job. | T3 |
| G-11 | Carpeta duplicada `src/spark/`. | T4 (limpiar o documentar) |
| G-12 | Manual `spark.md` y matriz `ANA-001` desactualizados. | T4 |

---

## 10. Cambios previstos (solo diseño; no programar en T1)

1. **Contrato Spark para `clinical`:** run asíncrono, status con `pending | processing | completed | failed`, result con datos agregados reales.
2. **Servicio de job:** persistir estado y último resultado por tipo (`clinical`) en memoria controlada o colección `spark_jobs`.
3. **Fuente de datos:** `AnalyticsService.get_clinical_analytics()` sobre Mongo de prueba, nunca datos productivos en Git.
4. **UI:** mapear los cuatro estados del criterio; al `completed` pintar las secciones reales; al `failed` mostrar `status.log` y acción de reintento (ya existe el bloque).
5. **Seguridad e i18n:** roles acordados, claves ES/EN pares, 401/403/409/500 cubiertos.
6. **Pruebas y evidencia:** pytest del flujo y capturas de los cuatro estados, sin PHI.

Detalle de JSON, diagrama y manejo de errores → **PBL-03-T2**.

---

## 11. Cómo se verificó esta revisión

Revisión estática sobre `main` en `0493083`:

- `backend/api_hospital/routes/` no contiene `spark.py`.
- `backend/api_hospital/services/` no contiene `spark_service.py`.
- `app.py` no registra blueprint Spark.
- `requirements.txt` no declara PySpark.
- `SparkAnalysisScreen.jsx` sí implementa run, polling y estados.
- `sparkService.js` apunta a `/spark/*`.
- `GET /analytics/clinical` existe y es otro contrato.

No se usaron datos clínicos reales ni secretos de producción.

---

## 12. Conclusión de T1

La historia **está esbozada en frontend** (pantalla, cliente, traducciones y estados de UI), pero **no está implementada de extremo a extremo**. El bloqueo es la ausencia del backend de jobs Spark y el desalineamiento entre `/analytics/clinical` y el contrato que consume la pantalla.

PBL-03 no consiste en “crear el módulo desde cero”. Consiste en **corregir ejecución, status y carga de resultado**, con datos reales al completar, sin romper el resto de Spark ni los patrones Flask/React existentes.

**T1 queda cerrada con este documento.** No se programa hasta registrar T2.

---

## 13. Evidencia de T1

| Entregable | Ruta |
|---|---|
| Esta revisión | `docs/sprints/sprint-7/pbl-03-t1-revision-flujo-clinico.md` |
| Commit esperado | `docs(pbl-03): documentar revisión del flujo de análisis clínico` |
| Rama | `feature/pbl-03-analisis-clinico` |

Captura opcional recomendada (sin datos reales): pantalla `/admin/spark/clinical` mostrando error/offline por 404. Guardarla después, en T4, junto con los cuatro estados ya corregidos.
