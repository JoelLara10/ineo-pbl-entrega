# PBL-03-T4 — Permisos, traducciones, estados y errores

**Historia:** PBL-03  
**Tarea:** T4 — Conectar la implementación con módulos relacionados; permisos, traducciones, estados y manejo de errores  
**Diseño:** `docs/sprints/sprint-7/pbl-03-t2-diseno-flujo-clinico.md`  
**Código base:** T3 (`spark_service`, `routes/spark`, `SparkAnalysisScreen`)  
**Fecha:** 22 de septiembre de 2026  
**Responsable:** Jaime Díaz González
**Rama:** `feature/pbl-03-analisis-clinico`

## Alcance de T4

| Área | Qué se hace |
|---|---|
| Permisos UI | Médico accede a `/admin/spark` y `/admin/spark/clinical` |
| Menú | Sidebar: médico solo ve entrada clínica; admin/administrativo ven los 4 módulos |
| Dashboard | `SparkDashboard` filtra tarjetas por rol |
| i18n | Claves `pending`, `completed`, `forbidden`, `unauthorized`, `conflict` en ES y EN |
| Estados UI | Criterio: Pendiente / Procesando / Completado / Fallido |
| Errores HTTP | 401 → unauthorized; 403 → forbidden; 409 → conflict + refresh |
| Docs | `docs/manual-tecnico/spark.md` refleja el flujo clínico implementado |
| Evidencia | Plantilla + capturas en `evidence/<nombre>/pbl-03/` |
| Tests | `pbl03-t4.test.js` + ajuste de prueba de Joel si aplica |

## Fuera de T4

- No reimplementar el job backend (ya está en T3).
- No añadir PySpark.
- No abrir analytics/met/unsupervised al médico.

## Archivos a aplicar

| Archivo del paquete | Destino en el repo |
|---|---|
| `SparkAnalysisScreen.jsx` | `frontend/clinica-web-react/src/pages/spark/SparkAnalysisScreen.jsx` |
| `SparkDashboard.jsx` | `frontend/clinica-web-react/src/pages/spark/SparkDashboard.jsx` |
| `AppRouter.spark-snippet.jsx` | Integrar en `src/router/AppRouter.jsx` |
| `Sidebar.spark-snippet.jsx` | Integrar en `src/components/layout/Sidebar.jsx` |
| `spark-states-es.json` | Fusionar en `src/i18n/locales/es.json` → `spark.states` |
| `spark-states-en.json` | Fusionar en `src/i18n/locales/en.json` → `spark.states` |
| `pbl03-t4.test.js` | `frontend/clinica-web-react/src/tests/pbl03-t4.test.js` |
| `spark.md` | `docs/manual-tecnico/spark.md` |
| `resultados.md` | `evidence/<tu-nombre>/pbl-03/resultados.md` |
| `pbl-03-t4-implementacion.md` | `docs/sprints/sprint-7/pbl-03-t4-implementacion.md` |

### i18n: cómo fusionar

En `es.json` y `en.json`, dentro de `"spark": { "states": { ... } }`:

1. Añade las claves nuevas: `pending`, `completed`, `forbidden`, `unauthorized`, `conflict`.
2. Actualiza títulos de `processing` / `failed` si quieres alinearlos al criterio (“Procesando”, “Fallido”).
3. **Conserva** `notRun` para no romper la paridad histórica de Joel; la pantalla T4 usa `pending`.

### Prueba de Joel (`sprint1-joel.test.js`)

Si falla por `spark.states.notRun.action`, actualiza esa expectativa a:

```js
expect(analysis).toContain('spark.states.pending.action');
// o acepta ambas:
// expect(analysis.includes('pending.action') || analysis.includes('notRun.action')).toBe(true);
```

## Commit sugerido

```bash
git add \
  frontend/clinica-web-react/src/pages/spark/SparkAnalysisScreen.jsx \
  frontend/clinica-web-react/src/pages/spark/SparkDashboard.jsx \
  frontend/clinica-web-react/src/router/AppRouter.jsx \
  frontend/clinica-web-react/src/components/layout/Sidebar.jsx \
  frontend/clinica-web-react/src/i18n/locales/es.json \
  frontend/clinica-web-react/src/i18n/locales/en.json \
  frontend/clinica-web-react/src/tests/pbl03-t4.test.js \
  frontend/clinica-web-react/src/tests/sprint1-joel.test.js \
  docs/manual-tecnico/spark.md \
  docs/sprints/sprint-7/pbl-03-t4-implementacion.md \
  evidence/<tu-nombre>/pbl-03/

git commit -m "feat(pbl-03): conectar permisos, traducciones y manejo de errores del análisis clínico"
git push
```

## Después de T4

1. Completar capturas en `evidence/.../pbl-03/`.
2. Commit de evidencia si las capturas van aparte:  
   `docs(pbl-03): agregar evidencia de estados pendiente, procesando, completado y fallido`
3. Abrir **Pull Request** a `main` con las 4 tareas (T1–T4).
4. No hagas merge tú mismo si el flujo del equipo lo prohíbe.
