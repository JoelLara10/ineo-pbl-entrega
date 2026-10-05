# PBL-08-T1 — Análisis: rediseño de la vista MET y traducción a lenguaje operativo

**Sistema:** Sistema de Gestión Clínica INEO  
**Repositorio:** `ineo-pbl-entrega`  
**Rama limpia:** `fix/jaime-sprint-2-clean`
**Historia:** PBL-08 — Interpretar métricas MET sin términos innecesariamente técnicos  
**Tarea:** T1 — Revisar código actual, dependencias, datos y restricciones. Documentar antes de programar.  
**Sprint:** 2 / Azure Sprint 8
**Fecha:** 2026-10-04  
**Responsable:** Jaime Díaz González  
**Estado:** Completada (solo documentación; sin cambios de código en esta tarea)

---

## 1. Objetivo

Identificar qué existe hoy en la vista MET, qué datos produce el backend, qué dependencias y restricciones aplican, y qué casos límite deben contemplarse para:

1. Traducir métricas MET a **lenguaje operativo** (decisión hospitalaria).
2. Relacionar cada indicador con una **decisión** posible.
3. Mantener **acceso al dato detallado** (criterio de aceptación).

Esta tarea **no implementa código**. Es insumo de T2 (diseño) y T3 (desarrollo).

---

## 2. Historia y criterio de aceptación

**Historia**

> Como responsable del hospital, quiero interpretar las métricas MET sin términos innecesariamente técnicos, para tomar decisiones con indicadores claros.

**Criterio**

> Los indicadores se relacionan con decisiones y mantienen acceso al dato detallado.

**Interpretación verificable**

| Elemento de aceptación | Significado | Evidencia mínima |
|---|---|---|
| Lenguaje operativo | Títulos y textos orientados a gestión (carga, demanda, actividad), no a jerga Spark/ML | UI muestra “Actividad por día”, “Día de mayor carga”, etc. |
| Relación con decisiones | Cada bloque KPI incluye una pista de decisión | Texto tipo “si la carga es alta, planificar refuerzo” |
| Acceso al detalle | El dato crudo/agregado sigue disponible | Sección expandible “Ver detalle técnico” o equivalente |

---

## 3. Código y arquitectura actual

### 3.1 Frontend

| Archivo | Rol actual |
|---|---|
| `pages/spark/MetAnalyticsScreen.jsx` | Wrapper: `<SparkAnalysisScreen type="met" />` |
| `pages/spark/SparkAnalysisScreen.jsx` | Pantalla genérica para analytics/met/clinical/unsupervised |
| `pages/spark/SparkDashboard.jsx` | Tarjeta MET en overview para administrador |
| `services/sparkService.js` | `GET /spark/met`, `POST /spark/run/met`, status |
| `i18n/locales/es.json` / `en.json` | `spark.types.met`, `spark.sections.*`, `spark.fields.*` |
| `router/AppRouter.jsx` | Ruta `/admin/spark/met` exclusiva para administrador |
| `Sidebar.jsx` | Entrada MET controlada por el rol administrador |

**Problema principal:** la pantalla MET reutiliza el render genérico (`DataObject` / `prettyKey`). Las claves (`summary`, `metrics`, `day`, `count`, `quality`) se muestran como grilla técnica, sin marco de decisión ni priorización de KPIs.

### 3.2 Backend

| Archivo | Rol |
|---|---|
| `routes/spark.py` | Blueprint `/spark/*` |
| `services/spark_service.py` | Jobs y proyección; `TYPES` incluye `met` y el contrato ya está operativo |
| `services/spark_engine.py` | Ya calcula MET: `groupBy('day').count()`, `summary.total`, `quality` |

**Fuente de datos MET:** colección `atencion`, proyección `{ day ← fecha_ing, status ∈ {ABIERTA,CERRADA,OTRO} }`. Sin identificadores de paciente.

**Forma del resultado MET:**

```json
{
  "available": true,
  "summary": { "total": N },
  "metrics": [ { "day": "YYYY-MM-DD", "count": k }, ... ],
  "quality": { "source_rows": S, "used_rows": U, "excluded_rows": E },
  "contract_version": "1.0",
  "timestamp": "...",
  "visualizations": []
}
