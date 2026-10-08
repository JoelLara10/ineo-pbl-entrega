# Informe UT PBL-28 — Joel — Azure Sprint 7

Fecha de ejecución: 8 de octubre de 2026. Responsable del PBL: Joel.
Código verificado: `fd8dc6c2ce54a274901a219ae54edcc9684075aa` (main).
Este informe añade configuración de cobertura, dependencia fijada y evidencia a esa versión; no modifica la lógica del producto.
Entorno: Linux, Node 24.19.0, npm 11.9.0, Vitest 4.1.10, React Testing Library y jsdom.

## Objetivo y alcance

Evitar regresiones de componentes React, estados y eventos de hooks, servicios simulados e interfaz ES/EN. La suite completa contiene 74 casos en 14 archivos. Se ejecutó con V8 e inclusión explícita de todo `src/**/*.{js,jsx}` de producción, excluyendo `src/tests/**`. No se ocultan módulos sin pruebas.

## Datos y casos de aceptación

Datos exclusivamente sintéticos; sin API remota ni información de pacientes. El servicio Spark se simula con `vi.mock`, las simulaciones se limpian entre casos y el DOM se desmonta. La navegación usa MemoryRouter y el almacenamiento de idioma es simulado.

| Caso de PBL-28 | Entrada / acción | Resultado esperado y obtenido |
|---|---|---|
| Carga | Promesas de resultados y estado sin resolver | Indicador accesible `status` con traducción de carga; aprobado. |
| Éxito | available=true, total=12, visualizations=[]; estado completed | La interfaz muestra 12; aprobado. |
| Vacío y actualización | available=false; pulsar actualizar | Estado vacío traducido y segunda llamada a getResults; aprobado. |
| Error y reintento | Primer getResults rechaza Error('offline'); segundo devuelve vacío | Alerta accionable traducida y segunda llamada tras reintentar; aprobado. |
| Español | Idioma es, resultado vacío | Encabezado traducido, sin claves técnicas visibles; aprobado. |
| Inglés | Idioma en, resultado vacío | Encabezado traducido, sin claves técnicas visibles; aprobado. |

Los seis casos anteriores están en `src/tests/pbl28-react-testing-library.test.jsx`. La suite también verifica idioma, panel de análisis, navegación y permisos con los casos registrados individualmente en `resultados.json`.

## Ejecución reproducible

Desde `frontend/clinica-web-react`, sobre el commit que incorpora este informe:

```bash
npm ci
npm run test:coverage -- --reporter=json --outputFile=coverage/test-results.json
npm run check:i18n
npm run lint
npm run build
```

`coverage/` se regenera localmente (HTML, JSON y LCOV); los resultados de esta ejecución quedan versionados en esta carpeta. En CI se usa Node 22; esta ejecución local usa Node 24 como se declara arriba.

## Resultados y cobertura

74/74 pruebas aprobadas, 0 fallidas. Validación ES/EN, lint y compilación aprobadas. Archivos de evidencia: `resultados.json`, `cobertura.json`, `ejecucion.txt`, `traducciones.txt`, `lint.txt` y `compilacion.txt`.

| Alcance | Líneas | Sentencias | Funciones | Ramas |
|---|---:|---:|---:|---:|
| total | 10.25% | 10.09% | 9.07% | 6.66% |
| src/i18n/setup.js | 100% | 100% | 100% | 83.33% |
| src/pages/spark/AnalyticsGeneralPanel.jsx | 100% | 100% | 100% | 48.14% |
| src/pages/spark/SparkAnalysisScreen.jsx | 80.82% | 78.43% | 85.18% | 74.5% |
| src/services/sparkService.js | 75% | 75% | 80% | 100% |

## Fallos, correcciones y límites

No hubo fallos de pruebas en esta ejecución. La carencia corregida fue la ausencia de un informe versionado de casos, ejecución y cobertura y de un comando reproducible: se añadió `@vitest/coverage-v8` fijado a 4.1.10, `test:coverage` y configuración de V8.

La cobertura global de producción es baja porque incluye módulos legacy, copias de pantallas y funcionalidades fuera de los casos de este sprint. No equivale a cobertura completa del sistema. Los servicios simulados no verifican conectividad real con la API. La prueba de usabilidad con una persona pertenece a las historias de Jesús del Sprint 8 y sigue pendiente. El PBL no fija un porcentaje mínimo de cobertura para PBL-28.

## Conclusión y trazabilidad

Se satisfacen los casos de aceptación PBL-28 de éxito, carga, vacío, error y ES/EN sin claves visibles. La tarea PBL-28-T5 (Azure 456) dispone de documento versionado, datos, comandos, versión, resultados, cobertura y logs, vinculada a PBL-28 (Azure 429). La evidencia debe integrarse en main antes del cierre formal en Azure.
