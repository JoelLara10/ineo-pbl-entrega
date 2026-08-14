# Manual técnico — Estado de integración Spark

**Sistema:** INEO — React y API Hospital  
**Sprint:** 5 — Calidad, Seguridad y Spark  
**Responsable:** Jesús  
**Fecha de revisión:** 14 de agosto de 2026  
**Estado:** Integración frontend presente; backend Spark no disponible en la versión revisada

## 1. Objetivo

Documentar de forma verificable el alcance actual del módulo analítico y evitar presentar como terminada una integración que todavía no funciona de extremo a extremo.

## 2. Componentes encontrados

El frontend contiene:

```text
src/pages/spark/SparkDashboard.jsx
src/pages/spark/AnalyticsScreen.jsx
src/pages/spark/MetAnalyticsScreen.jsx
src/pages/spark/ClinicalAnalyticsScreen.jsx
src/pages/spark/UnsupervisedAnalyticsScreen.jsx
src/pages/spark/SparkAnalysisScreen.jsx
src/services/sparkService.js
```

El servicio espera estas rutas:

| Método | Ruta esperada |
|---|---|
| GET | `/api/v1/spark/overview` |
| GET | `/api/v1/spark/analytics` |
| GET | `/api/v1/spark/met` |
| GET | `/api/v1/spark/clinical` |
| GET | `/api/v1/spark/unsupervised` |
| POST | `/api/v1/spark/run/{type}` |
| GET | `/api/v1/spark/status/{type}` |

## 3. Estado real del backend

En la API revisada no existen `routes/spark.py` ni `services/spark_service.py`, y `app.py` no registra un blueprint Spark. En consecuencia, las solicitudes anteriores producirán 404 y el módulo no puede considerarse funcional de extremo a extremo.

El dashboard web captura el error de `overview` y muestra un objeto vacío. Esto evita que la página falle por completo, pero no equivale a disponer de resultados analíticos.

## 4. Funciones planeadas por la interfaz

| Tipo | Propósito visible |
|---|---|
| `analytics` | Indicadores y análisis general |
| `met` | Métricas o resultados del análisis MET |
| `clinical` | Analítica clínica |
| `unsupervised` | PCA y agrupamiento no supervisado |

Estas funciones describen la intención del frontend. No se documentan como resultados ejecutados mientras falten los endpoints y el procesamiento correspondiente.

## 5. Contrato mínimo recomendado

`GET /spark/overview` debería responder sin información clínica sensible:

```json
{
  "analytics": { "available": false },
  "met": { "available": false },
  "clinical": { "available": false },
  "unsupervised": { "available": false }
}
```

`POST /spark/run/{type}` debería validar el tipo, iniciar un trabajo controlado y devolver un identificador. `GET /spark/status/{type}` debería informar `pending`, `running`, `completed` o `failed` sin bloquear la solicitud HTTP durante todo el procesamiento.

## 6. Requisitos para completar la integración

1. Incorporar y registrar el blueprint bajo `/api/v1/spark`.
2. Implementar un servicio que inicialice Spark de forma controlada.
3. Definir fuente de datos, esquema, variables y limpieza.
4. Aplicar autorización, preferentemente `admin` y roles analíticos definidos.
5. Excluir identificadores directos y datos innecesarios.
6. Guardar resultados reproducibles con fecha, parámetros y versión.
7. Implementar estados y manejo de fallos.
8. Agregar pruebas unitarias, de integración y de rendimiento.
9. Validar que el frontend muestre pendiente, ejecución, éxito y error.

## 7. Análisis no supervisado esperado

Para PCA y K-Means se debe documentar:

- variables incluidas y reglas de nulos;
- estandarización de características;
- varianza explicada de PCA;
- selección de componentes;
- elección de `K` mediante inercia y silueta;
- semilla aleatoria para reproducibilidad;
- tamaño e interpretación de cada clúster;
- advertencia de que los grupos no constituyen diagnósticos médicos.

No deben publicarse métricas, gráficas o cantidades que no procedan de una ejecución real.

## 8. Pruebas de aceptación pendientes

| ID | Prueba | Estado actual |
|---|---|---|
| SPK-001 | API responde `overview` | Bloqueada: endpoint ausente |
| SPK-002 | Ejecutar cada tipo permitido | Bloqueada: servicio ausente |
| SPK-003 | Consultar estado | Bloqueada: endpoint ausente |
| SPK-004 | Descargar o mostrar resultado | Bloqueada: no hay resultado backend |
| SPK-005 | Rechazar tipo inválido | Bloqueada |
| SPK-006 | Denegar usuario sin permiso | Bloqueada |
| SPK-007 | Reproducir PCA/K-Means | Bloqueada |

## 9. Criterio de terminación

Spark solo podrá marcarse como terminado cuando el backend esté incorporado, los endpoints respondan, al menos una ejecución real produzca resultados verificables, las pruebas de seguridad pasen y la interfaz consuma esos resultados sin datos simulados.

