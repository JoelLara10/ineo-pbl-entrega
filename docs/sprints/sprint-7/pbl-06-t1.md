# PBL-06-T1 — Persistencia del idioma y formato regional

Complemento del Sprint 7 (Sprint 1 del Excel). Responsable: Zahid.
Este cambio completa la tarea faltante y conserva la entrega anterior.

## Comportamiento

- La aplicación restaura `@ineo_lang` antes del primer render; español es el valor
  predeterminado. `en-US`/`es-MX` guardados se normalizan a `en`/`es`.
- Cualquier cambio de i18next persiste la elección, sin depender del formulario
  de login. El cierre de sesión elimina la autenticación, pero conserva el idioma.
- Los botones ES/EN actualizan textos y formatos en el componente ya montado,
  sin recargar la página. El atributo HTML `lang` también se actualiza.
- Si el navegador bloquea almacenamiento, la aplicación sigue funcionando con
  la selección durante esa sesión; no se promete persistencia cuando no se puede guardar.
- Se usa `es-MX` para español y `en-US` para inglés. Fechas en español:
  `24/09/2026`; en inglés: `09/24/2026`. Fechas largas y horas usan el mismo locale,
  sin insertar conectores españoles en el texto inglés.
- Cantidades numéricas: ambos locales usan `1,234.50`. Esto es correcto para México
  y Estados Unidos; no se fuerza el formato de España. Moneda MXN: `$1,234.50` en
  es-MX y `MX$1,234.50` en en-US. La moneda de negocio sigue siendo MXN.
- Fechas de calendario `YYYY-MM-DD` no se desplazan un día por interpretarlas como UTC.

## Cambios acotados

Inicialización/persistencia en `src/i18n/setup.js`; utilidades puras en
`src/i18n/regional.js`. Las pantallas que tenían formatos Moment fijos utilizan
esas utilidades (dashboard, médico y enfermería); Spark localiza sus fechas MET
y cantidades. Administración aplica los mismos locales a fechas y moneda.
No se modifican API, contratos backend, algoritmos Spark, base de datos ni Render.
Las pantallas de estudios/configuración que ya usan explícitamente es-MX/en-US
conservan su implementación.

## Evidencia automatizada

Archivo: `src/tests/pbl06-language.test.jsx`, 14 casos con Vitest y jsdom.
Se montan LoginScreen, AuthProvider y la visualización real de datos Spark;
no se sustituye i18next por un mock ni se comprueba únicamente el texto del código.

| Criterio | Prueba |
|---|---|
| Restauración entre sesiones | Cambiar a EN, cerrar sesión real, desmontar y montar con una instancia nueva; el botón EN, texto y fecha se restauran |
| Cambio sin recargar | Pulsar ES/EN reales; verificar textos, fecha y moneda, conservando los mismos nodos del login e input |
| Formato regional | Fecha corta/larga, fecha y hora, cantidades y MXN para es-MX/en-US |
| Casos límite | Preferencia inválida/regional, almacenamiento bloqueado, fechas inválidas, nulos y números no finitos |

Ejecutado en zona `America/Mexico_City` para cubrir el riesgo de desplazamiento de
fechas. Resultado: **35 pruebas frontend aprobadas** (21 anteriores + 14 nuevas).
Lint y compilación de producción aprobados. No se repite la suite backend porque
este cambio no modifica archivos de la API.

Desde `frontend/clinica-web-react`:

```bash
npm ci
npm run lint
npm test
npm run build
# Evidencia reproducible en Linux/macOS:
TZ=America/Mexico_City npm test -- --reporter=default --reporter=junit --outputFile=../../evidence/zahid/pbl06-frontend.xml
```

[Reporte JUnit](../../../evidence/zahid/pbl06-frontend.xml).
La prueba DOM automatizada no se presenta como UAT firmada por un usuario.
