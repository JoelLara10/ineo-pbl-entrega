# Sprint 9 (Azure) — entrega de Joel

## Alcance

Esta entrega cubre las historias asignadas a Joel en el PBL final:

- **PBL-09 (5 puntos):** panel clínico de riesgos, tendencias y distribución.
- **PBL-16 (3 puntos):** carga diferida y división de código para vistas pesadas.

## PBL-09 — trazabilidad de tareas

| Tarea | Evidencia |
|---|---|
| PBL-09-T1 | Normalización de métricas clínicas y reglas explícitas de riesgo. |
| PBL-09-T2 | Tarjetas con valor, unidad y nivel textual Alto/Medio/Normal. |
| PBL-09-T3 | Distribución agregada de alertas por nivel. |
| PBL-09-T4 | Vista de mínimo, promedio y máximo con contexto clínico. |
| PBL-09-T5 | Pruebas de accesibilidad semántica y de los tres niveles de riesgo. |

La información no depende únicamente del color: cada tarjeta muestra el nivel como texto, conserva contraste y expone encabezados y etiquetas accesibles.

## PBL-16 — trazabilidad de tareas

| Tarea | Evidencia |
|---|---|
| PBL-16-T1 | Inventario y separación de pantallas pesadas en el enrutador. |
| PBL-16-T2 | Importaciones dinámicas con `React.lazy` y fallback con `Suspense`. |
| PBL-16-T3 | Prueba automatizada de carga bajo demanda y validación mediante build de producción. |

## Validación esperada

Desde `frontend/clinica-web-react`:

```bash
npm test
npm run lint
npm run check:i18n
npm run build
```

El build de Vite debe generar chunks separados para las pantallas cargadas bajo demanda. La integración sigue el flujo `feature/joel-sprint9-pbl09-pbl16` → `develop` → `qa`.

## Correcciones y verificación del 20/10/2026

Se corrigió el contrato `temp`, se sustituyeron las barras fijas por rangos calculados y tendencias diarias reales, y se verificó el grafo de carga diferida mediante manifiesto de Vite. Análisis y evidencia T1–T5 en `revision-tecnica-joel-zahid.md`. La aprobación registrada es técnica automatizada; no reemplaza la UAT de Jaime.
