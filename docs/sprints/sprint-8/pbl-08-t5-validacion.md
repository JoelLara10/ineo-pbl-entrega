# PBL-08-T5 — Validación de criterios

**Historia:** PBL-08  
**Tarea:** T5 — Pruebas funcionales y de regresión  
**Fecha:** 2026-10-04  
**Responsable:** Jaime Díaz González  

## Criterio de aceptación

> Los indicadores se relacionan con decisiones y mantienen acceso al dato detallado.

| Verificación | Cómo | Resultado esperado |
|---|---|---|
| KPIs operativos visibles | Ejecutar MET con datos en `atencion` → abrir `/admin/spark/met` | Total, días activos, pico, promedio |
| Pista de decisión | Observar textos bajo cada KPI | `decision.highLoad` / `stableLoad` / `improveCapture` |
| Detalle técnico | Expandir “Ver detalle técnico…” | Grilla con summary/metrics/quality |
| Estados previos | Sin job / procesando / fallo | Mismos estados PBL-03/04 |
| Regresión clinical | `/admin/spark/clinical` | Sin panel MET; grilla genérica |
| i18n | Cambiar ES↔EN | Textos operativos traducidos |
| Test estático | `npm test -- --run src/tests/pbl08-met.test.js` | Pass |

## Comandos

```bash
cd frontend/clinica-web-react
npm install
npm test -- --run src/tests/pbl08-met.test.js
```

Resultado final: prueba específica, suite completa, lint, build e i18n aprobados en la rama limpia.
