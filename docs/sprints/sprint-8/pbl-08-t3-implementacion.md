# PBL-08-T3 — Implementación: rediseño vista MET

**Historia:** PBL-08  
**Tarea:** T3 — Programar rediseño de la vista MET y traducción a lenguaje operativo  
**Rama limpia:** `fix/jaime-sprint-2-clean`
**Fecha:** 2026-10-04  
**Responsable:** Jaime Díaz González  

## Cambios realizados

### Frontend

1. **`MetOperationalPanel.jsx`** (nuevo)  
   - KPIs: total de atenciones, días con actividad, día de mayor carga, promedio diario.  
   - Pistas de decisión (`spark.met.decision.*`).  
   - Lista de actividad por día en lenguaje claro.  
   - `<details>` con `DataObject` para el dato detallado (criterio de aceptación).

2. **`SparkDataViews.jsx`** (nuevo)  
   - Extrae `DataValue` / `DataObject` / helpers para evitar dependencia circular.

3. **`MetAnalyticsScreen.jsx` y `SparkAnalysisScreen.jsx`**
   - La vista MET inyecta `MetOperationalPanel` mediante `ResultsComponent`.
   - Analytics general conserva su panel y los demás tipos mantienen el render genérico.

4. **`MetOperationalPanel.css`**
   - Estilos encapsulados `.spark-kpi-*`, `.spark-decision`, `.spark-met-day-list`, `.spark-met-detail`.

5. **i18n ES/EN**  
   - Bloque `spark.met.*` y descripción operativa de `spark.types.met`.

6. **Test** `src/tests/pbl08-met.test.js`  
   - Estructura, i18n y habilitación backend.

### Backend

7. **`spark_service.py`**  
   - `met` ya forma parte de `TYPES`; no se modifica el backend ni su contrato vigente.

## Criterio de aceptación

- Indicadores relacionados con decisiones: sí (hints por KPI).  
- Acceso al dato detallado: sí (`details` + `DataObject`).

## Definición de terminado

- [x] Cambio en rama
- [x] Funciones no afectadas conservadas (clinical/unsupervised/analytics genéricos)
- [x] Preparado para revisión (T4)
