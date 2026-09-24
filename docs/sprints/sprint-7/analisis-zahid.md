# Sprint 7 — análisis y diseño de Zahid

El Sprint 1 del Excel corresponde al Sprint 7 de Azure. Base: `0493083` de main.
Azure no fue accesible desde esta sesión; el Excel adjunto es la fuente de alcance.

## Trazabilidad y decisiones previas a implementar

| Historia/tarea | Alcance y archivos |
|---|---|
| PBL-02 T1–T4 | Blueprint `/api/v1/spark`, servicio, ejecutor PySpark; overview, ejecución, estado y resultados |
| PBL-13 T1–T4 | Contrato JSON Schema v1, estados, errores e imágenes; pruebas HTTP |
| PBL-26 T1–T2 | Fixtures Mongo aisladas, semilla repetible, configuración e instrucciones de restablecimiento |
| PBL-30 | Incluida por la hoja «Próximo sprint» aunque PBL/Tareas la sitúan en Sprint 4. Contratos de auth, pacientes, estudios, Analytics y Spark; CI |
| PBL-05 T5 | Validación de claves estáticas y dinámicas de Spark en español/inglés |

La web existente espera objetos sin envoltura `data`: overview por tipo, `available`,
`timestamp`, `visualizations`, estado con `running` y respuesta de ejecución con
`status`. Se conserva ese formato. Los nuevos campos se añaden sin eliminar los existentes.

No hay scripts ni motor Spark en main ni en feature/spark-sprint-7. Se implementan
agregados reales: general sobre atenciones, MET como evolución temporal (definición
de la traducción existente), clínico como estadística descriptiva de signos vitales,
y PCA/K-Means exploratorio sobre signos completos. No se asignan diagnósticos ni
riesgos clínicos. Se excluyen nombres, expedientes, CURP y texto libre del procesador.

Los trabajos usan Mongo para resultados y exclusión atómica por tipo. Un ejecutor
local acotado invoca PySpark en subproceso con límite de tiempo; consultas HTTP no
esperan el análisis. Trabajos interrumpidos caducan y permiten reintento. Cada
actualización exige el identificador del trabajo para impedir sobrescrituras tardías.

Casos límite: vacío, signos parciales/no numéricos, muestras insuficientes o constantes,
tipo desconocido, token faltante/inválido, rol denegado, doble ejecución, Mongo caído,
motor ausente, timeout, reinicio del proceso y protección de resultados anteriores.

Las pruebas integran Flask, servicios, JWT y Mongo simulado; una prueba separada
ejecuta Java/PySpark real. No equivalen a un despliegue verificado en Render ni a UAT.
