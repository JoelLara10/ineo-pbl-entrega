# Contratos INEO v1 — Sprints 7 y 8

Fuente ejecutable: `api.schema.json` (JSON Schema 2020-12). Versión Spark `1.0`.
Campos nuevos compatibles son aditivos; eliminar requeridos o cambiar tipos exige
una nueva versión y actualización conjunta de proveedor/consumidor.

| Método y ruta bajo `/api/v1` | Esquema | HTTP |
|---|---|---|
| POST `/auth/login` | auth_login / error | 200, 400 sin credenciales, 401 credenciales inválidas |
| GET `/patients` | patients / error | 200, 401 |
| GET `/studies/counts` | studies_counts / error | 200, 401 |
| GET `/analytics/dashboard` | analytics / error | 200, 401 |
| GET `/spark/overview` | spark_overview | 200 |
| GET `/spark/{type}` | spark_result | 200 |
| POST `/spark/run/{type}` | spark_run | 202 nuevo, 200 trabajo ya activo |
| GET `/spark/status/{type}` | spark_status | 200 |

Spark exige token Bearer y rol `admin` en todas sus rutas (OPTIONS permite CORS).
También consulta la cuenta vigente: eliminada/desactivada → 401; rol actual
distinto de administrador → 403. Fallos de esa consulta → 503 JSON.
Los tipos son `analytics`, `met`, `clinical`, `unsupervised`. Errores Spark:
401 `unauthorized`, 403 `forbidden`, 400 `invalid_type`/`invalid_request`,
503 `unavailable`. Cuerpo: `contract_version`, `error` (texto), `code` (estable).
El POST no acepta parámetros. Nunca se reciben comandos, rutas ni código del cliente.

## Semántica de estado y resultados

`idle → pending → running → completed | failed`.
La web consume `status` en el POST y el objeto de estado directo en GET.
`running=true` tanto en pending como running. Se devuelve `job_id` y fechas UTC.
Las fechas no nulas cumplen `date-time` (RFC 3339) y se serializan en UTC.
Un rechazo del ejecutor registra `failed` y `finished_at`, sin borrar el resultado
previo; el siguiente POST puede reintentar. Overview usa un mismo documento
para disponibilidad y estado de cada tipo.
Un segundo POST durante un trabajo devuelve el mismo ID y no encola otro.
Los resultados de la última ejecución correcta permanecen disponibles durante
reintentos y errores. La pantalla muestra primero el estado actual del trabajo.
Un resultado vacío es 200/`available=false`; no equivale a un error ni a una serie inventada.
`timestamp` corresponde al resultado, no al último intento fallido.

Resultado común: `contract_version`, `available`, `timestamp`, `summary`, `metrics`,
`clusters`, `pca`, `quality`, `visualizations`. Las secciones que no aplican son
objetos/arreglos vacíos. `quality` informa filas de origen, utilizadas y excluidas.

Imágenes: contrato `image` con `filename`, `name`, `url` relativa autenticada bajo
`/spark/images/`. Este incremento entrega tablas/estadísticas y
`visualizations=[]`; no anuncia URLs de imágenes inexistentes.

## Datos y algoritmos

| Tipo | Colección / variables | Resultado |
|---|---|---|
| analytics | atencion: status | Total y conteos por estado |
| met | atencion: fecha_ing | Conteo por día de ingreso; se excluyen fechas no interpretables |
| clinical | signos_vitales: fc, fr, temp, spo2 | Cantidad, media, mínimo y máximo por medición |
| unsupervised | Las cuatro mediciones completas | Estandarización, PCA 2 componentes, K-Means semilla 7 |

MET sigue la descripción existente de la interfaz: desempeño/evolución temporal.
El análisis clínico es descriptivo, no un clasificador de riesgo. Los grupos no son
diagnósticos. Para K-Means se requieren ≥4 filas completas y ≥3 filas distintas;
se evalúan K=2..min(4, distintos−1), eligiendo la mayor silueta. Se entrega inercia,
silueta, varianza explicada, componentes, medias originales y tamaños por grupo.
No se publican puntos individuales ni identificadores de pacientes.

No se imputan datos faltantes. Los valores no numéricos, booleanos y no finitos se
convierten en nulos; los numéricos finitos se describen tal como están registrados,
sin validación clínica añadida. Una fila clínica se usa si tiene alguna medición;
cada media informa su propio número de observaciones.
El rango MET cubre todas las fechas registradas; este incremento no filtra periodos.
Se rechazan conjuntos mayores de 20,000 filas, sin truncamiento silencioso.

## Compatibilidad verificada

`/patients` conserva el contrato agrupado de `routes/administrative.py`:
`summary`, `pagination`, `groups`. No se reemplaza por el modelo paginado de otro
blueprint. Estudios y Analytics conservan las rutas fallback actuales del sistema.
Los contratos de estos módulos cubren esos endpoints representativos, no todo el API.

`tests/test_spark_contract.py` valida JSON, códigos, roles y transiciones con Flask
y datos Mongo sintéticos. `tests/test_spark_engine.py` ejecuta PySpark real y un
recorrido HTTP → trabajador → resultado. CI ejecuta ambas suites y publica JUnit.
La prueba consumidor de React verifica rutas, formatos y propagación de errores.
La integración de base de datos en pytest usa mongomock; no sustituye SIT con Mongo real.

## Cierre de Sprint 8

La planificación corregida asigna PBL-02/PBL-13 a Zahid. Véase
[la entrega y trazabilidad](../../docs/sprints/sprint-8/entrega-zahid.md).
`tests/test_sprint8_zahid.py` amplía la regresión con revocación de cuentas,
rol vigente, fallo de ejecutor, snapshot de overview, CORS y casos inválidos
de fechas/imágenes. La validación de esquemas habilita `FormatChecker`;
las salidas reales de los cuatro motores se comprueban contra `spark_result`.
