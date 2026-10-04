# PBL-08-T4 — Integración y revisión

**Historia:** PBL-08  
**Tarea:** T4 — Conectar con módulos relacionados, permisos, traducciones, estados y errores  
**Fecha:** 2026-10-04  
**Responsable:** Jaime Díaz González  
**Rama:** `sprints/jaime-sprint-7`

## Checklist de integración

| Área | Resultado |
|---|---|
| Ruta `/admin/spark/met` | Sin cambio; sigue admin/administrativo |
| Sidebar MET | Sin cambio de permisos |
| Estados pending/processing/empty/failed/offline/403/401 | Heredados de `SparkAnalysisScreen` |
| i18n ES/EN | Claves `spark.met.*` presentes |
| Contrato `/spark/met` y `/spark/run/met` | Forma JSON sin cambio; MET ahora ejecutable |
| Regresión clinical | Render genérico intacto cuando `type !== 'met'` |
| Médico | Sigue sin ver tarjeta/ruta MET |

## Revisión de código

- Panel solo deriva KPIs en cliente; no altera el job ni la proyección.
- Detalle técnico reutiliza `DataObject` exportado desde `SparkDataViews`.
- CSS namespaced bajo `.spark-`.

## Definición de terminado

- [x] Integración funcional documentada
- [x] Revisión de permisos/traducciones/estados completada