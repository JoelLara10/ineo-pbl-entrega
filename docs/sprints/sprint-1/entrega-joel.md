# Sprint 1 — Entrega de Joel

Responsable: Joel (Product Owner y desarrollador web).

El alcance se determinó cruzando la columna `Sprint` de la hoja `PBL` con la columna `Responsable` de la hoja `Tareas`. No se tomó como asignación individual al responsable general de la historia.

| Tarea | Implementación | Evidencia |
| --- | --- | --- |
| PBL-01-T1 | Revisión de rutas, módulos, dependencias y restricción por rol administrador. | Esta documentación y prueba estructural. |
| PBL-01-T2 | Registro del panel y cuatro rutas Spark en React. | `AppRouter.jsx` y `sprint1-joel.test.js`. |
| PBL-04-T2 | Estados de carga, procesamiento, sin datos, sin conexión y error, cada uno con orientación o acción. | Componentes y estilos de `pages/spark`. |
| PBL-05-T3 | Claves `spark.*`, módulos, secciones, estados, botones y mensajes en español e inglés. | `i18n/locales/es.json` y `en.json`. |
| PBL-26-T4 | Datos sintéticos por rol, relaciones válidas, restauración automática por prueba e integración con rutas reales. | Fixture y `test_sprint1_environment.py`, ejecutados por API CI. |

## Características técnicas

- Las rutas Spark permanecen dentro del bloque autorizado para administrador/administrativo.
- Los estados no dependen únicamente del color: incluyen título, explicación y acción.
- La interfaz no muestra claves técnicas cuando se cambia entre español e inglés.
- Los datos de prueba utilizan identificadores `TEST`, no contienen expedientes reales y se cargan como una copia nueva en cada prueba.
- Los flujos de GitHub Actions ejecutan pruebas web y API en cada pull request dirigido a `main`.

## Verificación local

Web, desde `frontend/clinica-web-react`:

```bash
npm test
npm run lint
npm run build
```

API, desde `backend/api_hospital`:

```bash
pytest -v
```
