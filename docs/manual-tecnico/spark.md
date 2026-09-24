# Manual técnico — Spark

## Actualización Sprint 7

El backend ya incorpora rutas, contratos versionados, procesamiento PySpark real,
persistencia de estados/resultados y pruebas. Consultar:

- [Contrato v1](../../contracts/v1/README.md)
- [Ambiente reproducible y requisitos Java/PySpark](../sprints/sprint-7/ambiente-pruebas.md)
- [Análisis y alcance de Zahid](../sprints/sprint-7/analisis-zahid.md)
- [Entrega y evidencia](../sprints/sprint-7/entrega-zahid.md)

El despliegue en producción y UAT no forman parte de esta actualización.

---

## Diagnóstico histórico — Sprint 5 (anterior a esta implementación)


**Sistema:** INEO — React y API Hospital  
**Sprint:** 7  
**Historia:** PBL-03 — Ejecutar el análisis clínico y visualizar sus resultados  
**Fecha de actualización:** 22 de septiembre de 2026  
**Estado:** Flujo clínico extremo a extremo implementado (run → status → result)

## 1. Objetivo

Documentar el contrato y el alcance real del módulo Spark tras PBL-03, con énfasis en el tipo `clinical`.

## 2. Componentes

### Frontend

```text
src/pages/spark/SparkDashboard.jsx
src/pages/spark/ClinicalAnalyticsScreen.jsx
src/pages/spark/SparkAnalysisScreen.jsx
src/services/sparkService.js
src/router/AppRouter.jsx          # rutas y roles
src/components/layout/Sidebar.jsx # menú
src/i18n/locales/es.json | en.json
```

### Backend

```text
backend/api_hospital/routes/spark.py
backend/api_hospital/services/spark_service.py
backend/api_hospital/app.py                    # register_blueprint(.../spark)
backend/api_hospital/services/analytics_service.py  # get_clinical_analytics()
```

## 3. Contrato HTTP (`/api/v1/spark`)

| Método | Ruta | Roles | Descripción |
|---|---|---|---|
| GET | `/spark/overview` | admin, administrativo, medico | Resumen `available` / `state` por tipo |
| POST | `/spark/run/clinical` | admin, administrativo, medico | Inicia job asíncrono → 202 |
| GET | `/spark/status/clinical` | admin, administrativo, medico | `pending` \| `processing` \| `completed` \| `failed` |
| GET | `/spark/clinical` | admin, administrativo, medico | Resultado agregado (datos reales de Mongo) |
| POST | `/spark/run/{otro}` | — | 400 no implementado en PBL-03 |

`POST /run` responde:

```json
{ "status": { "state": "processing", "running": true, "type": "clinical", ... } }
```

`GET /status` responde el objeto de estado **en la raíz** (sin anidar en `status`).

## 4. Estados del criterio de aceptación

| Criterio | `state` API | UI (i18n) |
|---|---|---|
| Pendiente | `pending` | `spark.states.pending` |
| Procesando | `processing` + `running: true` | `spark.states.processing` |
| Completado | `completed` + `available: true` | datos + `spark.states.completed` |
| Fallido | `failed` | `spark.states.failed` + log |

Estados auxiliares de red/permiso: `offline`, `forbidden` (403), `unauthorized` (401), `conflict` (409).

## 5. Permisos (PBL-03-T4)

| Superficie | admin | administrativo | medico | otros |
|---|---|---|---|---|
| UI `/admin/spark` | sí | sí | sí (solo tarjeta clínica) | no |
| UI `/admin/spark/clinical` | sí | sí | sí | no |
| UI analytics / met / unsupervised | sí | sí | no | no |
| API `run` / `status` / `clinical` | sí | sí | sí | 403 |

## 6. Fuente de datos

`AnalyticsService.get_clinical_analytics()` sobre Mongo:

- `top_diagnosis`
- `age_distribution`
- `average_stay_days`

Persistencia del job: colección `spark_jobs` (un documento por `type`).

No se incluye PySpark en el runtime del MVP; el criterio exige **datos reales**, no el motor Spark.

## 7. Pruebas de aceptación

| ID | Prueba | Estado |
|---|---|---|
| SPK-001 | API responde `overview` | Implementado (clinical) |
| SPK-002 | Ejecutar `clinical` | Implementado |
| SPK-003 | Consultar estado | Implementado |
| SPK-004 | Mostrar resultado | Implementado |
| SPK-005 | Rechazar tipo inválido / no implementado | Implementado (400) |
| SPK-006 | Denegar rol sin permiso | Implementado (403) |
| SPK-007 | PCA / K-Means | Fuera de alcance PBL-03 |

## 8. Cómo verificar

```bash
# API
cd backend/api_hospital
pytest -v tests/test_spark_clinical.py

# Web
cd frontend/clinica-web-react
npm test
```

Flujo manual: login admin o médico → `/admin/spark/clinical` → pendiente → ejecutar → procesando → completado con datos (o vacío si Mongo no tiene agregados).

