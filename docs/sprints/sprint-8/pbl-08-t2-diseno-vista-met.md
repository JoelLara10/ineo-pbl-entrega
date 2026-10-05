
# PBL-08-T2 — Diseño técnico: vista MET en lenguaje operativo

**Sistema:** Sistema de Gestión Clínica INEO  
**Historia:** PBL-08  
**Tarea:** T2 — Definir componentes, contrato, flujo de datos, estados y manejo de errores  
**Fecha:** 2026-10-04  
**Responsable:** Jaime Díaz González  
**Estado:** Listo para implementar

---

## 1. Objetivo de diseño

Rediseñar la presentación de resultados MET para que un responsable de hospital vea:

1. **Indicadores claros** (KPIs) en lenguaje de operación.
2. **Relación con decisiones** (pista por indicador).
3. **Acceso al detalle** sin perder el dato agregado del contrato.

No se cambia el contrato HTTP ni la forma del JSON de resultado; solo la capa de presentación. Se habilita la ejecución MET en backend porque el motor ya existe.

---

## 2. Componentes

### 2.1 Existentes (conservar)

```text
MetAnalyticsScreen.jsx          → type="met"
SparkAnalysisScreen.jsx         → estados, run, polling, toolbar
sparkService.js                 → sin cambios de API
routes/spark.py                 → sin cambios de rutas
spark_engine.py                 → cálculo MET ya implementado
AppRouter / Sidebar             → permisos admin/administrativo
Estados PBL-03/04               → pending, processing, empty, failed, offline...