# Sprint 8 — Zahid: PBL-02 y PBL-13

Fecha de validación: 2026-10-08. Rama de entrega: `sprints/zahid-sprint-8`.

## Alcance corregido y reutilización

Fuente: **DOC-20260919-WA0000(1).xlsx**, hojas `PBL`, `Tareas` y
`Sprint planning`. El Sprint 2 del Excel corresponde al Sprint 8 de Azure.
Zahid tiene **PBL-02 (5 puntos)** y **PBL-13 (3 puntos revisados)**: diez tareas,
ocho puntos. La reducción de PBL-13 reutiliza PBL-02 y la matriz de PBL-43.
El estado cerrado del tablero no se toma como evidencia de implementación.

Se comparó `sprints/zahid-sprint-7` (`2ba3482`) con `main` (`fd8dc6c`).
La API, el motor, el esquema v1, las pantallas y gran parte de sus pruebas ya
estaban integrados. Esta entrega reutiliza ese trabajo y completa las brechas
observadas. La planificación corregida reemplaza la anterior; no se incorporan
funcionalidades de otros sprints ni se cuenta dos veces el desarrollo existente.

## T1/T2 — análisis y diseño

La web usa `services/sparkService.js` y las pantallas de `pages/spark`.
El blueprint `routes/spark.py`, registrado en `app.py` bajo `/api/v1/spark`,
consulta `services/spark_service.py`; los trabajos persisten en `spark_jobs`.
El trabajador proyecta datos sin identificadores y ejecuta `spark_engine.py`
en un subproceso PySpark. Flask/PyMongo y el runtime Java 17/PySpark 3.5.7
son dependencias existentes. Solo se añade `rfc3339-validator==0.1.4` a las
dependencias de pruebas: `jsonschema` omite la comprobación `date-time` si
falta ese verificador opcional. Las pruebas negativas detectan esa ausencia.

Se mantienen los cuatro tipos: `analytics`, `met`, `clinical`, `unsupervised`.
Se conserva el flujo `idle → pending → running → completed | failed`, el
control de trabajos duplicados, el timeout, la recuperación por expiración y
el último resultado correcto durante reintentos. POST no acepta parámetros.

Brechas encontradas y solución:

1. Spark comprobaba solamente firma/rol del JWT. Ahora comprueba también la
   existencia, actividad y rol actual de la cuenta. Una cuenta eliminada o
   desactivada recibe 401; un administrador degradado recibe 403. Se mantiene
   el sobre JSON Spark, incluso ante fallo de Mongo (503). La consulta proyecta
   únicamente actividad y rol. Se conserva compatibilidad con IDs numéricos.
2. Overview leía resultado y estado separadamente. Ahora construye cada entrada
   desde una sola lectura del documento para evitar mezclar dos momentos del
   mismo trabajo. No promete una transacción global entre los cuatro análisis.
3. Si el ejecutor rechazaba un trabajo, faltaba `finished_at`. Ahora se registra
   el fin del intento fallido, se conserva el resultado anterior y se permite
   reintentar. La actualización exige el mismo ID y estado pendiente.
4. La serialización sustituía zonas horarias sin convertir el instante.
   Los valores conscientes de zona ahora se convierten a UTC; las fechas naive
   de PyMongo se interpretan como UTC. Se documenta y verifica `date-time`.
5. Una imagen descargada después de desmontar la pantalla conservaba su URL
   de objeto. Ahora se libera tanto al terminar tarde como al desmontar.

Los esquemas de resultado, estado, error, imágenes, ejecución y overview siguen
en `contracts/v1/api.schema.json`, versión `1.0`. Las anotaciones `date-time`
precisan las fechas ya documentadas; no se eliminan campos ni cambian tipos.
El validador de pruebas activa `FormatChecker` para comprobarlas realmente.

## T3/T4 — trazabilidad de implementación e integración

| Tarea | Trabajo reutilizado y cierre de este incremento |
|---|---|
| PBL-02-T1 | Arquitectura y endpoints previos; análisis de brechas y restricciones en esta entrega. |
| PBL-02-T2 | Flujo persistente existente; diseño de autorización vigente, snapshot de overview y fallo del ejecutor. |
| PBL-02-T3 | Endpoints registrados existentes; correcciones en `routes/spark.py` y `services/spark_service.py`. |
| PBL-02-T4 | Consumidor y permisos existentes; integración de revocación/rol actual con errores JSON, fechas UTC y regresión web. |
| PBL-02-T5 | Ciclos de vida, roles y regresión existentes; nuevos casos de cuenta, Mongo, ejecutor, overview y CORS en `tests/test_sprint8_zahid.py`. |
| PBL-13-T1 | Revisión del contrato v1, productores, consumidores, imágenes vacías y compatibilidad. |
| PBL-13-T2 | Esquemas previos reutilizados; diseño de fechas verificables y conservación de recursos de imágenes. |
| PBL-13-T3 | Anotaciones de fechas y validación real de formato; corrección del consumidor de imágenes. |
| PBL-13-T4 | Validación de las salidas de los cuatro tipos con PySpark real contra el contrato y pruebas de React. |
| PBL-13-T5 | Esquemas positivos/negativos, fechas inválidas, versión incompatible, imágenes y regresión completa; evidencia adjunta. |

| Método y ruta bajo `/api/v1` | Respuesta satisfactoria | Errores comunes |
|---|---|---|
| GET `/spark/overview` | 200, `spark_overview` | 401, 403, 503 |
| GET `/spark/{type}` | 200, `spark_result`; vacío con `available=false` | 400, 401, 403, 503 |
| GET `/spark/status/{type}` | 200, `spark_status` | 400, 401, 403, 503 |
| POST `/spark/run/{type}` | 202 nuevo / 200 ya activo, `spark_run` | 400, 401, 403, 503 |

Son 13 combinaciones documentadas de ruta/tipo. OPTIONS permite la negociación
CORS sin JWT y no inicia trabajos. Las pruebas cubren todas las combinaciones.

El contrato `image` define `filename`, `name` y URL relativa bajo `/spark/images/`.
El motor actual entrega estadísticas/tablas con `visualizations=[]`; **no genera
imágenes ni anuncia una ruta de imágenes implementada**. Los ejemplos de imagen
son sintéticos para validar el contrato y su consumidor, no evidencia de un
endpoint real de imágenes. No se añade generación de gráficos al alcance.

## T5 — validación y entrega

Véase [evidencia-zahid.md](evidencia-zahid.md) para resultados, entorno y comandos.
Se prueban Flask y el trabajador real con datos sintéticos aislados; Mongo se
sustituye por mongomock. La revisión de cambios y pruebas es local automatizada;
la revisión humana del equipo, el SIT con Mongo real y la aprobación/despliegue
siguen correspondiendo al equipo. No se declara una validación en producción.

La entrega se publica solamente en la rama indicada. No crea PR, no fusiona
`main` y no modifica el estado del tablero Azure.
