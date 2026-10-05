# PBL-08-T4 — Integración y revisión

**Historia:** PBL-08  
**Tarea:** T4 — Conectar con módulos relacionados, permisos, traducciones, estados y errores  
**Fecha:** 2026-10-04  
**Responsable:** Jaime Díaz González  
**Rama limpia:** `fix/jaime-sprint-2-clean`

## Checklist de integración

| Área | Resultado |
|---|---|
| Ruta `/admin/spark/met` | Conservada dentro del bloque exclusivo de administrador |
| Sidebar MET | Conserva el control de acceso de administrador |
| Estados pending/processing/empty/failed/offline/403/401 | Heredados de `SparkAnalysisScreen` |
| i18n ES/EN | Claves `spark.met.*` presentes |
| Contrato `/spark/met` y `/spark/run/met` | Forma JSON y ejecución vigentes sin cambios de backend |
| Regresión clinical | Render genérico intacto cuando `type !== 'met'` |
| Médico | Sigue sin ver tarjeta/ruta MET |

## Revisión de código

- Panel solo deriva KPIs en cliente; no altera el job ni la proyección.
- Detalle técnico reutiliza `DataObject` exportado desde `SparkDataViews`.
- CSS aislado en `MetOperationalPanel.css` y namespaced bajo `.spark-met-panel`.

## Definición de terminado

- [x] Integración funcional documentada
- [x] Revisión de permisos/traducciones/estados completada
