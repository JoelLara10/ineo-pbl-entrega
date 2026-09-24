# PBL-04-T1 — Revisión de estados vacíos y errores accionables en Spark

**Sistema:** Sistema de Gestión Clínica INEO  
**Repositorio:** `ineo-pbl-entrega`  
**Rama revisada:** `sprints/jaime-sprint-7` (incluye PBL-03)  
**Commit base:** `597ecfc` — `feat(pbl-03): conectar permisos, traducciones y manejo de errores del análisis clínico parte front`  
**Feature:** Acceso, servicios, ejecución y navegación de Spark  
**Historia:** PBL-04 (estados vacíos y errores accionables)  
**Tarea:** T1 — Revisar código, dependencias, datos y restricciones. Documentar los cambios **antes de programar**.  
**Sprint:** 7  
**Fecha de revisión:** 2026-09-23  
**Estado:** Completada (solo documentación; sin cambios de código)

> Completar antes de subir: **Responsable:** Jaime Díaz González **Rol:** SM/Desarrollador

---

## 1. Objetivo

Identificar qué existe, qué se confunde y qué no debe romperse para que la UI Spark:

1. Distinga **sin ejecutar**, **sin datos**, **sin conexión**, **procesando** y **fallo**.
2. Ofrezca **una acción clara** en cada uno de esos estados.
3. No presente un 403, un 400 “no implementado” o un 404 como si fueran “sin datos”.

Esta tarea **no implementa código**. Es insumo obligatorio de T2 (diseño) y T3 (programación).

---

## 2. Historia y criterio de aceptación

**Historia**

> Como usuario, quiero mensajes claros cuando no haya datos o exista un error para saber qué hacer, para comprender el estado y saber qué acción realizar.

**Criterio**

> Se diferencia **sin ejecutar**, **sin datos**, **sin conexión**, **procesando** y **fallo**; cada estado ofrece una acción.

**Interpretación verificable**

| Estado de aceptación | Significado | Acción mínima | No debe confundirse con |
|---|---|---|---|
| Sin ejecutar | Nunca se lanzó el análisis (`pending` / `idle`, `available: false`) | Ejecutar ahora | Job terminado vacío |
| Sin datos | El job **terminó** (`completed`) pero no hay indicadores | Volver a ejecutar o actualizar | Nunca ejecutado; error de red |
| Sin conexión | No hay respuesta HTTP (red, API caída, timeout de axios) | Reintentar consulta | 403, 401, 400 de negocio |
| Procesando | `state === 'processing'` o `running: true` | Actualizar (el polling sigue) | Pendiente sin `running` |
| Fallo | `state === 'failed'` | Volver a ejecutar | Offline; vacío; 403 |

Cada estado debe tener **título + explicación + botón**, no solo color.

---

## 3. Alcance de esta revisión

**Dentro de alcance**

- `SparkAnalysisScreen` (los 4 tipos lo reutilizan).
- `SparkDashboard` (overview y tarjetas).
- `sparkService.js` y contrato `/api/v1/spark/*`.
- i18n `spark.states.*` en ES y EN.
- CSS `.spark-state*`.
- Respuestas de `SparkService` (pending / processing / completed+empty / failed).
- Pruebas `sprint1-joel.test.js`, `pbl03-clinical.test.js`, `pbl03-t4.test.js`.

**Fuera de alcance (no se implementa en esta historia)**

- Implementar PySpark ni analytics / MET / unsupervised (siguen 400 “no implementado”).
- Cambiar el motor de job de PBL-03.
- Login, pacientes, SOAP, estudios, respaldos.
- Mostrar o versionar datos clínicos reales.

---

## 4. Método

Revisión estática sobre `sprints/jaime-sprint-7` al commit citado:

- Lectura de `SparkAnalysisScreen.jsx`, `SparkDashboard.jsx`, `sparkService.js`.
- Lectura de `routes/spark.py` y `services/spark_service.py`.
- Cruce con i18n ES/EN y `Spark.css`.
- Cruce con la entrega de Joel (Sprint 1 / PBL-04-T2) y con PBL-03-T1/T4.
- Inventario de pruebas estructurales que T3 no debe romper.

No se usaron secretos ni expedientes reales.

---

## 5. Arquitectura actual (lo que ya existe)

### 5.1 Frontend

| Pieza | Ruta | Rol |
|---|---|---|
| Pantalla de análisis | `frontend/clinica-web-react/src/pages/spark/SparkAnalysisScreen.jsx` | Máquina de estados + acciones |
| Dashboard | `.../SparkDashboard.jsx` | Overview + tarjetas |
| Wrappers | `AnalyticsScreen`, `MetAnalyticsScreen`, `ClinicalAnalyticsScreen`, `UnsupervisedAnalyticsScreen` | Solo pasan `type` |
| Cliente | `src/services/sparkService.js` | GET overview/status/result, POST run |
| i18n | `src/i18n/locales/es.json`, `en.json` → `spark.states` | Títulos, hints, actions |
| Estilos | `src/pages/spark/Spark.css` | `.spark-state`, `-processing`, `-error` |
| Pruebas | `src/tests/sprint1-joel.test.js`, `pbl03-*.test.js` | Cadenas de claves i18n |

### 5.2 Backend (PBL-03)

| Pieza | Contrato |
|---|---|
| `GET /spark/overview` | `{ [type]: { available, state } }` |
| `GET /spark/status/{type}` | `{ state, running, type, log, ... }` |
| `GET /spark/{type}` | `{ available, timestamp, type, ... }` |
| `POST /spark/run/{type}` | 202 + `{ status }` si `clinical`; **400** si analytics/met/unsupervised |

Estados de job: `pending` (sin documento), `processing`, `completed`, `failed`.

`completed` + `available: false` = ejecución real **sin indicadores** (Mongo vacío). Eso es el estado **sin datos** del criterio.

### 5.3 Orden de evaluación actual en `SparkAnalysisScreen`

1. `error` (offline / forbidden / unauthorized / conflict / error)
2. `loading`
3. `isProcessing` (`running` **o** `state === 'processing'`)
4. `state === 'failed'`
5. `isPending` (`!available` y `idle`/`pending`)
6. `!available` → empty
7. resultados

Este orden es correcto para no pintar “sin datos” cuando el job falló o nunca corrió.

---

## 6. Mapeo criterio ↔ código actual

| Criterio | Clave i18n usada hoy | Acción en pantalla | ¿Cumple? |
|---|---|---|---|
| Sin ejecutar | `spark.states.pending` (título **“Pendiente”**) | Ejecutar ahora | Parcial: hay acción, pero el texto del criterio es “sin ejecutar” (`notRun`) |
| Sin datos | `spark.states.empty` | **Actualizar resultados** (`load`) | Parcial: acción débil; recargar no crea datos si Mongo está vacío |
| Sin conexión | `spark.states.offline` + `common.retry` | Reintentar (`load`) | Sí en la pantalla de análisis y en el dashboard |
| Procesando | `spark.states.processing` | Actualizar (`load`) | Sí; hay polling 3 s |
| Fallo | `spark.states.failed` | Volver a ejecutar (`run`) | Sí; log en `<details>` |

Joel (Sprint 1) ya dejó el **cascarón** de estos 5 estados (`notRun`, `empty`, `offline`, `processing`, `failed`). PBL-03-T4 cambió la UI de `notRun` a `pending` y añadió `forbidden` / `unauthorized` / `conflict`.

---

## 7. Hallazgos (huecos reales)

### H1 — “Sin ejecutar” ya no se llama así en la UI (media)

La clave `notRun` sigue en JSON (“Análisis sin ejecutar”) pero **no se usa** en el JSX. El usuario ve **“Pendiente”**. El criterio de esta historia pide diferenciar **sin ejecutar**. Hay dos claves vivas para el mismo caso.

**Riesgo:** reintroducir `notRun` rompe `sprint1-joel.test.js` (ahora espera `pending.action`). Ignorar el texto del criterio deja la historia a medias.

**Dirección T2:** una sola clave visible. Opciones:

- A) Usar `notRun` en UI (alineado al criterio) y actualizar tests a `notRun.action`.
- B) Conservar `pending` y cambiar título/hint a “Análisis sin ejecutar” (cumple el criterio sin revertir PBL-03).
- C) Renderizar `notRun` y dejar `pending` como alias en i18n.

Recomendación: **B** — no revertir el mapeo pending de PBL-03; alinear copy.

### H2 — Dashboard no distingue los 5 estados (alta)

`overview` ya trae `state`, pero las tarjetas solo usan `available`:

- `true` → “Resultados disponibles”
- `false` → “Sin resultados”

No hay badge de procesando, fallido, sin ejecutar ni sin datos. Un job `failed` se ve igual que uno nunca ejecutado.

El dashboard además **sigue pintando tarjetas** debajo del bloque loading/error.

### H3 — Acción de “sin datos” no resuelve el problema (media)

`empty.action` llama a `load()`, no a `run()`. Si el análisis terminó vacío, actualizar vuelve a mostrar vacío. El usuario no sabe que debe **volver a ejecutar** (o que no hay registros en Mongo).

### H4 — Polling traga errores de red (alta para “sin conexión”)

En el `setInterval` de procesando, el `catch` está vacío. Si la API se cae a mitad del job, la UI **permanece en procesando** y nunca pasa a offline.

### H5 — Tipos no implementados se ven como error genérico (alta en navegación Spark)

`POST /run/analytics|met|unsupervised` responde **400** `Tipo de análisis no implementado en PBL-03`.  
`mapHttpError(400)` → `error`. El usuario no ve “sin ejecutar”; ve “No se pudo completar la consulta”.

Esta historia **no** pide implementar esos tipos, pero sí mensajes accionables. Debe quedar un estado propio (p. ej. `notImplemented`) o permanecer en **sin ejecutar** con hint “este módulo aún no se puede ejecutar”, acción Volver al panel — nunca “sin datos”.

### H6 — Completado con `available: true` y secciones vacías (baja)

Si `available` es true pero `hasContent` filtra todo, la pantalla muestra el badge “Completado” y un cuerpo en blanco, sin empty. Hoy el backend pone `available` solo si hay diagnósticos, edades o estancia > 0, así que el caso es raro.

### H7 — Copy atado a “clínico” en claves genéricas (media)

`pending.hint`, `forbidden.hint` y `conflict.hint` hablan de **análisis clínico**. La misma pantalla sirve para analytics/MET/unsupervised.

### H8 — Distinción visual débil (media)

CSS solo marca `spark-state-processing` (azul) y `spark-state-error` (rojo). Pending, empty y offline (si se pintara sin `-error`) se ven iguales: caja blanca. Joel exigió que los estados **no dependan solo del color**, pero título+acción ya cubren eso; igual falta un modificador por estado para evidencia visual.

### H9 — i18n `error` no tiene `hint` ni `action`

Solo `title`. El botón usa `common.retry`. Cumple acción, pero el hint cae al `error` crudo del API o a `loadError`.

### H10 — Pruebas solo estructurales (media)

Nadie monta el componente ni simula axios. T3 debería añadir tests que comprueben que las 5 claves del criterio aparecen **con su `action`**, y que 403/400 no usan `empty`.

---

## 8. Dependencias

| Capa | Dependencia | ¿Nueva? |
|---|---|---|
| UI | `react-i18next`, `axios` (`api.js`), `react-router-dom`, `react-icons/fi` | No |
| Auth | `token_required` + `role_required(admin, administrativo, medico)` | No |
| Datos | Colección `spark_jobs` + `AnalyticsService.get_clinical_analytics()` | No |
| i18n | `spark.states.*` ES/EN con **mismas claves** (PBL-05 / Joel) | No nuevas librerías |

No se requiere librería de empty-states ni de toasts. El patrón existente (bloque `.spark-state` + i18n) basta.

---

## 9. Datos y restricciones

### 9.1 Cómo se distingue empty vs not-run en backend

| Condición | `status.state` | `result.available` | UI correcta |
|---|---|---|---|
| Sin documento en `spark_jobs` | `pending` | `false` | Sin ejecutar |
| Job en curso | `processing` | (result previo o false) | Procesando |
| Job OK con indicadores | `completed` | `true` | Resultados |
| Job OK sin indicadores | `completed` | `false` | Sin datos |
| Job con excepción/timeout | `failed` | `false` + `log` | Fallo |

**Restricción:** no usar `available === false` como único criterio. Eso mezcla sin ejecutar, sin datos y fallo.

### 9.2 Errores HTTP que no son “sin datos”

| Código | Origen | Estado UI correcto | Acción |
|---|---|---|---|
| (sin response) | Red / API caída | `offline` | Reintentar |
| 401 | Token | `unauthorized` | Volver / login |
| 403 | Rol | `forbidden` | Volver |
| 400 tipo inválido | `SparkTypeError` | `error` | Volver al panel |
| 400 no implementado | `SparkNotImplemented` | no mezclar con empty | Volver o hint de no disponible |
| 409 | Job en curso | `conflict` + refresh | Actualizar |
| 404 | Blueprint ausente | `offline` o `error` | Reintentar |
| 500 | Falla interna | `error` | Reintentar |

### 9.3 Seguridad y producto

- No mostrar stack traces ni URI Mongo en `status.log` (PBL-03 ya recorta a 500 caracteres y una línea).
- No capturar PHI en evidencia.
- No inventar indicadores para “llenar” empty.
- Conservar paridad ES/EN de `Object.keys(spark.states)`.
- Conservar el mapeo PBL-03: `pending` **sin** `running` no es procesando.
- No abrir analytics/MET/unsupervised al médico (PBL-03-T4).

---

## 10. Qué debe cambiar (para T2, no para T1)

| ID | Cambio propuesto | Capa | Prioridad |
|---|---|---|---|
| C1 | Copy de `pending` = “Análisis sin ejecutar” (criterio) sin quitar la clave `pending` | i18n | Alta |
| C2 | Dashboard: badge según `overview[type].state` + `available` (5 estados) | React | Alta |
| C3 | Empty: acción primaria **Volver a ejecutar** (`run`); secundaria Actualizar | React + i18n | Alta |
| C4 | Polling: si `getStatus` falla sin response → `offline` | React | Alta |
| C5 | 400 `SparkNotImplemented` → estado `notImplemented` (título/hint/action) o pending con hint específico | React + i18n + API | Alta |
| C6 | Clases CSS `spark-state-pending`, `-empty`, `-offline`, `-failed` | CSS | Media |
| C7 | Quitar “clínico” de hints genéricos | i18n | Media |
| C8 | Dashboard: no renderizar tarjetas si `loading` o `error` | React | Baja |
| C9 | Tests: 5 estados del criterio + acción; 403/400 ≠ empty | Vitest | Alta |
| C10 | `error.hint` y `error.action` en ES/EN | i18n | Baja |

**No cambiar en esta historia:** `SparkService` clínico (run/status/result), permisos, rutas, PySpark.

---

## 11. Impacto en pruebas existentes

| Prueba | Qué exige hoy | Cómo no romperla |
|---|---|---|
| `sprint1-joel.test.js` PBL-04-T2 | `pending.action`, `empty.action`, `failed.action`, `processing.hint`, `common.retry`, dashboard `offline.hint` | Conservar esas cadenas en el JSX |
| `pbl03-clinical.test.js` | `pending` ≠ processing; mismas actions | No volver a `running \|\| pending \|\| processing` |
| `pbl03-t4.test.js` | `pending`/`completed`/`forbidden`/`conflict`; paridad ES/EN | Si se añade `notImplemented`, añadirlo en **ambos** JSON |
| `test_spark_clinical.py` | Contrato API clínico | No tocar salvo un campo extra opcional en overview |

---

## 12. Relación con trabajo previo

| Origen | Qué dejó | Qué falta para esta historia |
|---|---|---|
| Sprint 1 Joel PBL-04-T2 | Cascarón UI de 5 estados + acciones | Pegarlo al backend real y al dashboard |
| Sprint 1 Joel PBL-05 | Paridad i18n | Copy genérico (no solo clínico) |
| PBL-03 T3 | Job real pending→processing→completed/failed | Empty vs pending vs failed con datos reales |
| PBL-03 T4 | pending/completed, 401/403/409, médico | Textos “sin ejecutar”; dashboard; polling offline; tipos no implementados |

Esta historia **no** vuelve a inventar la máquina de estados. **Corrige mensajes, distinción y acciones** ahora que el API existe.

---

## 13. Plan de tareas siguientes

| Tarea | Entregable | Programar |
|---|---|---|
| **T1 (esta)** | Este documento | No |
| **T2** | Contrato UI: tabla estado × título × hint × acción × fuente de datos × CSS; copy ES/EN; flujo dashboard vs pantalla | No |
| **T3** | Aplicar C1–C9 sobre patrones actuales | Sí |
| **T4** | Conectar i18n/permisos/errores restantes, evidencia de los 5 estados, PR | Sí (cierre) |

---

## 14. Git (solo documentación)

Rama (continuar la de Spark o abrir una de historia):

```text
sprints/jaime-sprint-7
# o, si el equipo pide rama por historia:
feature/pbl-04-estados-spark
```

Archivo:

```text
docs/sprints/sprint-7/pbl-04-t1-revision-estados-vacios.md
```

```bash
git checkout sprints/jaime-sprint-7
git pull
# copiar este markdown a docs/sprints/sprint-7/
git add docs/sprints/sprint-7/pbl-04-t1-revision-estados-vacios.md
git commit -m "docs(pbl-04): documentar revisión de estados vacíos y errores accionables de Spark"
git push -u origin HEAD
```

---

## 15. Conclusión

Los **cinco estados del criterio ya existen** en `SparkAnalysisScreen` tras Joel + PBL-03, cada uno con botón. **No están terminados** porque:

1. El copy de “sin ejecutar” se diluyó en “Pendiente”.
2. El dashboard aplana todo a “con/sin resultados”.
3. “Sin datos” solo recarga.
4. Un corte de red en el polling no pasa a “sin conexión”.
5. analytics/MET/unsupervised caen en error genérico.

T1 queda cerrada con este documento. **No se programa hasta registrar T2.**
