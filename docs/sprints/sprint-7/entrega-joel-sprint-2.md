# Entrega de Joel — Sprint 2 del PBL (Azure Sprint 7)

## PBL-03 · Ejecutar análisis clínico con Spark (5 puntos)

| Tarea | Evidencia implementada |
| --- | --- |
| T1 Analizar flujo | Se documentaron los estados `idle`, `pending`, `processing`, `completed` y `failed`, y el contrato usado por `sparkService`. |
| T2 Diseñar experiencia | La vista comunica carga, ejecución, actualización, resultado vacío, desconexión y fallo; cada estado ofrece una acción pertinente. |
| T3 Desarrollar | `SparkAnalysisScreen.jsx` consume resultados y estado clínico, ejecuta el trabajo y actualiza la interfaz mientras está en curso. |
| T4 Integrar | Se usan `GET /spark/clinical`, `GET /spark/status/clinical` y `POST /spark/run/clinical`; los resultados reales se representan por secciones. |
| T5 Probar | `sprint2-joel.test.jsx` valida resultados, ejecución, procesamiento, fallo y reintento. |

### Criterios cubiertos

- Se distinguen pendiente/procesando, completado y fallido.
- El error devuelto por la API se muestra en pantalla.
- Al completarse, se consultan y muestran los resultados reales.
- El usuario puede actualizar o volver a ejecutar según el estado.

## PBL-23 · Diseño de Cuidados de Enfermería (3 puntos)

| Tarea | Evidencia implementada |
| --- | --- |
| T1 Analizar pantalla | Se conservaron paciente, diagnóstico, objetivos, intervenciones, evaluación, estado, observaciones e historial. |
| T2 Desarrollar diseño | `EnfermeriaCareScreen.jsx` y `NursingCare.css` usan tarjetas, campos, botones, estados visibles, foco accesible y rejilla adaptable a móvil. |
| T3 Probar | La prueba verifica consulta, estado vacío, opciones traducidas, captura, guardado y recuperación ante error del historial. |

### Criterios cubiertos

- Conserva las operaciones existentes de consulta y registro.
- Mantiene navegación y jerarquía visual coherentes con Enfermería.
- Todos los textos agregados existen en español e inglés.
- La rejilla pasa de dos columnas a una en pantallas pequeñas y los botones ocupan el ancho disponible.

## Cómo verificar

Desde `frontend/clinica-web-react`:

```bash
npm test -- --run src/tests/sprint2-joel.test.jsx
npm run lint
npm run build
```
