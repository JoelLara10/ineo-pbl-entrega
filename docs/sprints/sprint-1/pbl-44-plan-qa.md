# PBL-44 — Plan de calidad del Sprint 1

## Aprobación y alcance

El Product Owner solicitó completar y cerrar el Sprint 1 conforme al PBL final. Este plan cubre PBL-01, PBL-05, PBL-07, PBL-15, PBL-26, PBL-28, PBL-43 y PBL-44. La aprobación final queda registrada mediante la aceptación y fusión del PR de cierre.

## Responsables y evidencias

| Historia | Responsable | Nivel y casos | Evidencia requerida |
| --- | --- | --- | --- |
| PBL-01 | Joel | Rutas y autorización de cinco vistas Spark | Prueba de router y navegación |
| PBL-05 | Jesús | Traducción ES/EN de títulos, botones, secciones y estados | Pruebas dinámicas de pantalla |
| PBL-07 | Jaime | Tarjetas y gráfica explicada de Analytics general | Prueba RTL del panel |
| PBL-15 | Jesús | Claves usadas contra `es.json` y `en.json` | Script y prueba negativa |
| PBL-26 | Zahid | Ambiente, roles, datos sintéticos, aislamiento y reinicio | Fixtures y pruebas backend |
| PBL-28 | Joel | Éxito, carga, vacío, error, eventos, servicios e i18n | Suite React Testing Library |
| PBL-43 | Zahid | URL base, proxy, CORS, permisos y códigos HTTP | Matriz y pruebas de integración |
| PBL-44 | Jaime | Trazabilidad, defectos y liberación | Este plan y resultados de CI |

## Datos y ambientes

- Backend: Python, `mongomock`, base aislada `ineo_test_pytest` y fixture `sprint1_data.json`.
- Web: Vitest, jsdom y React Testing Library con servicios simulados.
- Datos: identificadores `TEST`, usuarios sintéticos por rol y relaciones repetibles.
- CI: instalación limpia, lint, pruebas, build web, pruebas API y Spark real con datos sintéticos.
- Ninguna prueba requiere expedientes reales ni secretos de producción.

## Matriz de ejecución

| Nivel | Objetivo | Entrada | Resultado esperado |
| --- | --- | --- | --- |
| UT web | Componentes, estados e i18n | Mocks controlados | Render y acciones correctas |
| Integración API | Rutas, permisos, contratos y CORS | App Flask aislada | Códigos y JSON esperados |
| Regresión | Funciones existentes | Suite completa | Cero fallos |
| Build | Artefacto desplegable | Dependencias bloqueadas | Compilación exitosa |
| Spark real | Compatibilidad de motor | Datos sintéticos | Ejecución sin error |

## Gestión de defectos

Cada defecto debe registrar historia/caso, severidad, ambiente, pasos, resultado esperado/actual, responsable, corrección, commit y evidencia de reejecución. Un defecto bloqueante impide liberar. Los defectos altos requieren corrección o aceptación explícita del PO; los medios y bajos deben quedar planificados.

## Criterios de entrada

1. Historias y criterios aprobados en el PBL final.
2. Dependencias instalables y configuración de prueba disponible.
3. Datos sintéticos restaurables.
4. Rama actualizada desde `main` y sin secretos.

## Criterios de salida y liberación

1. Todas las tareas y criterios de las ocho historias tienen evidencia versionada.
2. Pruebas web y API, lint y build terminan correctamente.
3. No existen defectos bloqueantes o altos abiertos.
4. La matriz PBL-43 y este plan están vinculados al PR.
5. El PO revisa y fusiona el PR de cierre; esa acción constituye la aprobación de liberación.

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| API o Spark no disponibles | Estados accionables, reintento y pruebas de fallo |
| Traducción incompleta | Validador automático PBL-15 |
| Regresión visual | RTL, lint, build y revisión de evidencia |
| Datos sensibles | Fixtures sintéticos aislados |
| Contrato incompatible | Esquema versionado y pruebas de integración |
