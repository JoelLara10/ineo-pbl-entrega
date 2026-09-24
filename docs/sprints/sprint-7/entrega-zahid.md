# Entrega de Zahid — Sprint 7

Fecha: 24 de septiembre de 2026. Rama: `sprints/zahid-sprint-7`.
Base: `0493083` de main. El primer sprint del Excel se trata como Sprint 7.

## Implementado

| Historia / tarea | Entrega |
|---|---|
| PBL-02 T1–T4 | Análisis, diseño, blueprint autenticado, overview, resultado, ejecución y estado para los cuatro módulos; resultados reales con PySpark |
| PBL-13 T1–T4 | Contratos JSON Schema v1 de estados, errores, resultados e imágenes; preservación del formato consumido por React; pruebas HTTP |
| PBL-26 T1–T2 | Fixtures con Mongo aislado, semilla reproducible con colecciones reales, reset protegido, usuarios por rol, Dockerfile y Compose de pruebas |
| PBL-30 | Contratos automatizados de login, listado agrupado de pacientes, conteos de estudios, dashboard Analytics y Spark; CI publica JUnit |
| PBL-05 T5 | Pruebas de claves estáticas/dinámicas de Spark y renderizado bilingüe; etiquetas de los resultados incorporados |

PBL-30 se incluye porque aparece asignada a Zahid en «Próximo sprint», aunque
PBL/Tareas la sitúan en Sprint 4. Azure no pudo leerse; no se modificaron sus tareas.
Las tareas de aceptación/revisión asignadas a otras personas no se dan por firmadas.

## Integración

- El POST devuelve de inmediato un trabajo; el GET informa su progreso.
- Mongo conserva estados, resultados y exclusión atómica de solicitudes repetidas.
- Se controlan errores, timeout, reinicios y actualizaciones tardías de trabajos viejos.
- No se transfieren identificadores de pacientes al motor ni se simulan resultados.
- MET usa evolución temporal; clínico es descriptivo; PCA/K-Means es exploratorio.
- La pantalla Spark maneja errores del polling y evita leer resultados nulos.
- Se mantienen las rutas y formatos existentes de los demás módulos.

## Evidencia ejecutada

Entorno: Linux, Python 3.12.14, Java 17, PySpark 3.5.7; datos exclusivamente sintéticos.

| Verificación | Resultado |
|---|---|
| Suite backend completa con `RUN_SPARK_TESTS=1` | 85 aprobadas, 0 fallidas, 0 omitidas |
| Motor PySpark | Cuatro tipos, vacío, datos parciales/constantes, subproceso real y recorrido HTTP → trabajador → resultado |
| Cobertura de routes.spark, services.spark_service y services.spark_engine | 88% combinada; no representa cobertura de toda la API |
| Tests React/Vitest | 21 aprobadas |
| `npm run lint` | Aprobado |
| `npm run build` | Aprobado |
| Compilación Python y `git diff --check` | Aprobados |

JUnit backend: [sprint7-backend.xml](../../../evidence/zahid/sprint7-backend.xml).
Comandos reproducibles: [ambiente-pruebas.md](ambiente-pruebas.md).
Contrato: [contracts/v1](../../../contracts/v1/README.md).
Los avisos de deprecación de bibliotecas/middleware existentes no hicieron fallar las pruebas.

## Límites de esta validación

Mongo se simuló con mongomock durante pytest; el procesamiento Java/PySpark sí fue
real. Docker/Compose se versiona, pero no se ejecutó aquí porque Docker no está
disponible. No se validaron Render, datos de producción, navegación visual de extremo
a extremo ni aceptación de usuarios. Las verificaciones no certifican ausencia
absoluta de errores ni sustituyen esas etapas.

Para ejecutar Spark en un servidor hacen falta Java 17 y requirements-spark.txt;
el despliegue normal existente no se modifica automáticamente. Hay guía y contenedor
de prueba con ese runtime. No se crearon PR ni fusiones a main en esta entrega.
