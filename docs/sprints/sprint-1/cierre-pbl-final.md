# Cierre del Sprint 1 conforme al PBL final

## Resultado por historia

| Historia | Puntos | Responsable | Tareas verificadas | Evidencia |
| --- | ---: | --- | --- | --- |
| PBL-01 | 3 | Joel | T1 análisis, T2 rutas, T3 validación | Cinco rutas directas dentro del bloque exclusivo `isAdmin`; prueba `sprint1-joel.test.js` |
| PBL-05 | 5 | Jesús | T1 análisis, T2 diseño, T3 desarrollo, T4 integración, T5 validación | Diccionarios ES/EN y pruebas dinámicas `sprint7-jesus-screen.test.jsx` |
| PBL-07 | 5 | Jaime | T1 análisis, T2 diseño, T3 desarrollo, T4 integración, T5 validación | `AnalyticsGeneralPanel.jsx` y prueba `pbl07-analytics-general.test.jsx` |
| PBL-15 | 3 | Jesús | T1 análisis, T2 script, T3 caso negativo | `check-i18n-keys.mjs`, comando `npm run check:i18n` y prueba `pbl15-i18n-validator.test.js` |
| PBL-26 | 5 | Zahid | T1 diseño, T2 ambiente, T3 datos, T4 CI, T5 evidencia | Configuración `mongomock`, fixture sintético, restauración por prueba y `test_sprint1_environment.py` |
| PBL-28 | 5 | Joel | T1 diseño, T2 automatización, T3 casos, T4 integración, T5 evidencia | React Testing Library, Vitest y `pbl28-react-testing-library.test.jsx` |
| PBL-43 | 3 | Zahid | T1 inventario, T2 proxy/CORS, T3 pruebas, T4 evidencia | `pbl-43-matriz-proxy-endpoints.md` y `test_sprint1_proxy_endpoints.py` |
| PBL-44 | 3 | Jaime | T1 alcance/riesgos, T2 matriz/datos, T3 defectos/salida, T4 revisión | `pbl-44-plan-qa.md` y resultados de CI del PR de cierre |

## Criterios específicos

### PBL-07

Analytics general utiliza tarjetas para indicadores y una gráfica de barras accesible. La gráfica muestra título, etiquetas por categoría, valores, unidad, periodo, leyenda y una explicación de interpretación. Si la API no entrega una serie no se inventa una gráfica; se mantienen las tarjetas con el resumen real.

### PBL-15

El validador recorre archivos JS/JSX/TS/TSX de producción, extrae claves estáticas utilizadas mediante `t(...)` o `i18n.t(...)` y comprueba su existencia en español e inglés. Una clave faltante termina con código de error e identifica archivo, clave e idioma.

### PBL-28

Las pruebas RTL cubren carga, resultado exitoso, resultado vacío, error recuperable, eventos de botones, servicios simulados y cambio ES/EN sin claves técnicas visibles.

### PBL-43

La matriz registra URL base, prefijo, autenticación, CORS, métodos y permisos. La integración comprueba respuestas 200, 401, 403, 404 y preflight.

## Comandos de aceptación

```bash
cd frontend/clinica-web-react
npm run check:i18n
npm test
npm run lint
npm run build

cd ../../backend/api_hospital
pytest -q
```

El Sprint 1 se considera terminado cuando estas validaciones y la CI del PR están aprobadas y el Product Owner fusiona el cambio.
