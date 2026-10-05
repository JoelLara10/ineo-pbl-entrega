# PBL-21-T1 — Análisis: unificar diseño de Valoración de Enfermería

**Historia:** PBL-21  
**Rama limpia:** `fix/jaime-sprint-2-clean`
**Fecha:** 2026-10-04  
**Responsable:** Jaime Díaz González  

## Objetivo
Unificar encabezado, secciones, campos, botones, espaciado y respuesta móvil de **Valoración de Enfermería** con el patrón aprobado (Signos Vitales / Nota), **sin cambiar la lógica**.

## Criterio de aceptación
> Conserva todas sus funciones y validaciones; visualmente sigue el patrón aprobado de enfermería.

## Situación actual
| Aspecto | Assessment (antes) | Patrón aprobado |
|---|---|---|
| Encabezado | Gradiente simple | Gradiente + sombra + eyebrow |
| Campos | Solo placeholder | Label + input |
| Botones | Fila básica | Primary / secondary en footer |
| Historial | Lista plana | Cards + grid de métricas |
| Responsive | Grid auto-fit | Mismo criterio + padding de página |

## Archivos afectados
- `EnfermeriaAssessmentScreen.jsx` (solo UI)
- `es.json` / `en.json` (claves de presentación)
- Docs T1–T3 y evidencia

## Fuera de alcance
- Endpoints `/nursing-assessment`
- Campos del payload
- Validaciones de backend
- Permisos de rol

## Casos límite
- Sin paciente → mensaje, sin submit
- Historial vacío / cargando
- Error de guardado → alert existente
- Móvil < 640px → grid apilable
