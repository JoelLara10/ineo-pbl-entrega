# OftalCore — revisión técnica de Joel y Zahid (Sprint 9)

Fecha: 20 de octubre de 2026. Revisor: Codex, revisión de código y ejecución automatizada solicitadas por Joel. Esta es una aprobación **técnica**, no una firma del PO ni una sesión UAT con usuarios. La aceptación del incremento y el acta UAT de PBL-33 siguen pendientes de Jaime. Jesús mantiene PBL-22 y PBL-27 pendientes. No se integra la rama `feature/sprint9` de Jaime.

## Joel — PBL-09

- **T1 análisis:** contrato real `fc/fr/temp/spo2`, `count/mean/minimum/maximum`, mediciones y fechas faltantes, acceso exclusivo de administrador y resultados históricos. El defecto era no reconocer `temp`, lo que aplicaba el caso por defecto Normal. Se conservan las bandas ya definidas por el proyecto; esta revisión no certifica su validez clínica.
- **T2 diseño:** API → proyección sin identificadores → Spark → resultado agregado → `ClinicalAnalyticsPanel`, dentro de `SparkAnalysisScreen`. Se mantiene `AnalysisMetadata` de Zahid. Las series son opcionales y aditivas: `day/measure/count/mean/minimum/maximum`.
- **T3 implementación:** temperatura reconocida, desconocidos sin clasificación, datos ausentes sin ceros inventados, texto y color, unidades y formatos ES/EN. Distribución rotulada como cantidad de indicadores por promedio, no como pacientes. Marcadores de rango calculados y tendencias diarias reales, con tabla accesible y periodo. Las filas sin fecha aportan a los agregados pero no a la serie temporal.
- **T4 integración:** combinación de Joel y Zahid conservando metadatos. Periodo y tendencia usan UTC sin identificadores. Autenticación y permisos existentes conservados. Prueba HTTP → worker real → Spark y validación del contrato. Resultados históricos sin serie muestran el aviso correspondiente.
- **T5 validación:** regresiones para `temp=39.5`, valores nulos/vacíos/cero observaciones, rangos variables/constantes, traducción, orden temporal y agregación diaria con filas sin fecha. Evidencias JUnit en `evidence/sprint-9-joel-zahid`.

## Joel — PBL-16

- **T1 análisis:** `AppRouter.jsx` ya usa `lazy` y `Suspense` para Analytics, MET, clínico y no supervisado. Se conserva y verifica esa implementación, sin atribuirle una reducción histórica no medida.
- **T2 implementación:** Vite emite manifiesto de producción; `scripts/check-lazy-bundle.mjs` recorre el grafo estático de entrada y falla si una pantalla pesada pasa al paquete inicial.
- **T3 validación:** `npm run build && npm run check:bundle`. Las cuatro pantallas están en entradas dinámicas independientes. Bytes iniciales y diferidos en `bundle.json`; no es un benchmark antes/después. El test del enrutador complementa la comprobación del build.

## Zahid — PBL-06, PBL-11, PBL-25 y PBL-38

- Revisión de persistencia/formato regional, metadatos y compatibilidad histórica, preferencia de idioma autenticada e idempotente, cola permitida por usuario, expiración, errores, eliminación de caché clínica persistente y Service Worker limitado a recursos estáticos.
- PBL-11-T1 y PBL-25-T1..T5 conservan análisis/diseño/integración en `entrega-zahid.md`. La nueva prueba de proyección comprueba el mismo día UTC en periodo y tendencia, sin identificadores.
- PBL-38-T1 (#500) existe en Azure. El reporte contiene todas las historias del Sprint 9 con requisitos exactos. Joel/Zahid tienen casos y revisión técnica explícita. Jaime/Jesús mantienen pendientes sin resultados inventados. `--story` permite aplicar la puerta estricta sólo al alcance solicitado y rechaza historias desconocidas.
- CI regenera evidencia y ejecuta Spark real en Linux/Python 3.12/Java 17. El reporte general permanece pendiente mientras falten entregas y aceptación del resto del equipo.

## Evidencia y límites

Validación local: 111 pruebas frontend y 237 pruebas API aprobadas, incluidas ocho de Spark real. Traducciones, lint y compilación aprobados; una advertencia de lint heredada en UsuariosConfigScreen. XML íntegros y hashes en el reporte. Se emplean bases sintéticas aisladas con mongomock; no se acredita UAT humana ni ejecución sobre la base real de QA/producción.

La entrega técnica puede quedar resuelta para revisión de aceptación. No se certifica el Sprint 9 completo ni se promueve a producción. La UAT y el acta pertenecen al alcance pendiente de Jaime.

El flujo autenticado se verificó además con Flask test_client y Spark real: login → POST de ejecución → worker → GET de resultado, 401 sin autenticación y preferencia PUT/GET. Respuesta sintética sin identificadores ni tokens en `clinical-api-synthetic.json`; el frontend la consume en una regresión de contrato. No se obtuvo verificación visual en el navegador remoto porque no alcanza el servidor local; no se presenta como UAT.
