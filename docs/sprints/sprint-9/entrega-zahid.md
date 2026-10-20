# Sprint 9 — Entrega de Zahid

Base: `develop`. Rama: `sprint-9-zahid`. Alcance verificado en Azure DevOps el 20/10/2026: PBL-11 (#290), PBL-25 (#312), PBL-38 (#441). PBL-06 ya estaba cerrada. No se modifica el estado de historias ni se sustituye la revisión del equipo.

## PBL-11 / T1 #355 — Implementación y verificación

Se agregaron `metadata.generated_at`, `last_updated_at`, `period.start/end`, `undated_rows` y `timezone` al resultado Spark. La generación corresponde al resultado terminado, no a cada consulta. La última actualización es la fecha más reciente registrada en la fuente (`atencion.fecha_ing` o `signos_vitales.fecha_registro`); no equivale a la hora de lectura ni a un historial de modificaciones inexistente. El periodo cubre las fechas conocidas del conjunto proyectado analizado, incluidas filas posteriormente excluidas por calidad; `undated_rows` identifica cobertura temporal incompleta. No se inventan fechas para fuentes sin fecha ni para resultados históricos. Un reintento fallido conserva el resultado y sus metadatos anteriores.

La pantalla común de las cuatro clases de análisis muestra generación, actualización y periodo en español o inglés, incluidos los componentes especializados. Las fechas calendario se conservan en UTC y las horas se presentan en la zona del navegador. El contrato se amplió de forma compatible con resultados anteriores.

## PBL-25 — Análisis T1 #410

Se identificó persistencia de expedientes, listas de pacientes, notas, signos, recetas, resultados e historial de impresión en `localStorage`. Esos datos no son aptos para operación offline sin un mecanismo clínico autorizado. Se sustituyó la caché clínica persistente por memoria con TTL, que se vacía al desconectar, cerrar sesión o cambiar de cuenta. La selección de paciente y el historial de impresión permanecen sólo durante la sesión en memoria. Se purgan las claves heredadas al iniciar.

Archivos afectados: servicios de API/caché/cola, contexto de autenticación y paciente, pantallas médicas y de enfermería, configuración de caché, contenedor offline, arranque, recursos PWA y configuración de compilación. No se modifica el contrato de las escrituras clínicas.

Casos límite: almacenamiento bloqueado o corrupto; cola caducada; cambio de usuario; 401/403; caída del servidor con navegador online; modificación del idioma durante una sincronización; repetición de solicitudes; filas analíticas sin fechas; reintento analítico fallido.

## PBL-25 — Diseño T2 #411

Política de permiso por omisión: sólo se admite guardar el idioma `es/en`. No se ofrece captura clínica offline. Sin conexión, un contenedor desmonta las pantallas clínicas y muestra las acciones seguras. El interceptor rechaza solicitudes de API cuando el navegador está offline. Aunque el indicador de red diga online, el servidor vuelve a comprobar token y cuenta activa para sincronizar.

La cola en `sessionStorage` contiene exclusivamente propietario de sesión, idioma y fecha local de creación; no contiene URL, token ni datos clínicos. Sólo conserva la selección más reciente, expira en ocho horas, se elimina al cerrar sesión y no puede enviarse desde otra cuenta. Si el almacenamiento está deshabilitado, funciona sólo en memoria. `PUT /api/v1/auth/preferences` recibe únicamente `{language: 'es'|'en'}` y usa la identidad autenticada; repetir el mismo PUT es idempotente. Entre dispositivos, prevalece el último PUT recibido por el servidor. Los fallos de red/5xx conservan la cola para reintento; 400/401/403 la descartan. El estado de error y el botón de reintento son visibles.

## PBL-25 — Desarrollo T3 #412

Se incorporaron contenedor offline, selector de idioma, estado de sincronización y endpoint autenticado de preferencia. El Service Worker precarga sólo el HTML estático y los recursos de compilación enumerados. No intercepta API, mutaciones, recursos externos ni URLs con query. No almacena respuestas obtenidas al navegar ni añade cachés dinámicas. Se agregó manifest e icono para instalación en navegadores compatibles. Requiere HTTPS (o localhost), compilación de producción y una primera visita online para instalar el contenedor. Si el navegador bloquea Service Workers, la aplicación online continúa disponible.

## PBL-25 — Integración T4 #413

La política se aplica a todas las pantallas mediante el contenedor común. El modo offline desmonta también el contexto de paciente y borra la caché transitoria. Al reconectar, la aplicación vuelve a consultar la API. El cierre de sesión online conserva la revocación existente; offline cierra la sesión local y descarta la cola. La invalidación 401 vacía credenciales y contexto de usuario. El endpoint utiliza el middleware actual, incluyendo revocación y cuenta activa. Las etiquetas de los nuevos estados existen en ambos idiomas.

## PBL-25 — Validación T5 #414

Las suites `test_sprint9_zahid.py`, `sprint9-zahid.test.jsx`, `sprint9-worker.test.js` y `sprint9-network.test.js` verifican metadatos, traducción, cola y aislamiento, permisos, privacidad y contenedor estático. Los resultados reales de ejecución y las regresiones se incluyen en `evidence/sprint-9-zahid/`. La revisión de código por otro integrante y la prueba en QA/UAT deben registrarse con sus resultados reales antes de aceptar las historias.

## PBL-38 / T1 #500 — Diseño y reporte

Se versionó la relación requisito → historia → tareas → casos en `traceability.json`. El generador `scripts/traceability.py` lee JUnit real, conserva el resultado más reciente por caso, distingue fallo/omitido/no ejecutado y genera JSON y HTML consultables sin servicios adicionales. Cada evidencia XML lleva SHA-256. El reporte incluye defectos declarados y aprobación con referencia a un archivo real dentro del repositorio. No ejecuta cambios en Azure DevOps.

Una historia queda pendiente si falta algún caso, hay pruebas omitidas/fallidas (también en regresión), defectos abiertos o aprobación documentada. La opción `--strict` devuelve código 1 mientras no se cumpla la puerta. Que no haya defectos registrados no acredita ausencia de defectos. Los campos de aprobación se dejan vacíos hasta que el responsable revise la evidencia; la existencia de un archivo no reemplaza la verificación humana de su autoría. El manifiesto cubre exclusivamente las tres historias de Zahid, no certifica las historias del resto del equipo.

## Reproducir la evidencia

Desde la raíz, con dependencias instaladas:

```bash
cd frontend/clinica-web-react
npm run check:i18n
npm run lint
npm test -- --reporter=default --reporter=junit --outputFile=../../evidence/sprint-9-zahid/frontend.xml
npm run build
cd ../../backend/api_hospital
python -m pytest -q --junitxml=../../evidence/sprint-9-zahid/backend.xml
cd ../..
python scripts/traceability.py --junit evidence/sprint-9-zahid/frontend.xml evidence/sprint-9-zahid/backend.xml
```

Para comprobar la puerta de aceptación, agregar `--strict`. Es esperable un resultado pendiente mientras no se adjunten revisión y aprobación reales. La automatización del sprint reproduce pruebas y publica el reporte como artefacto en cada push a `sprint-9-zahid` o PR a `develop`.

## Revisión en QA antes del cierre

1. Abrir cada tipo de análisis con datos sintéticos; comprobar fechas y cambiar español/inglés. Probar fuente sin fechas y un análisis que falle después de otro exitoso.
2. Instalar la aplicación desde la compilación de producción. Tras una visita online, desconectar y recargar una ruta: debe aparecer únicamente el modo limitado.
3. Cambiar idioma offline, reconectar y comprobar el idioma en `GET /api/v1/auth/preferences`; repetir con API no disponible y reintento. Verificar que cambiar de cuenta no transfiere la cola.
4. Inspeccionar almacenamiento: sin datos clínicos persistentes ni respuestas de API en Cache Storage. Probar cierre de sesión, expiración y desactivación de cuenta.
5. Incorporar las evidencias QA/UAT y defectos reales en el manifiesto; registrar aprobación correspondiente. Regenerar y verificar con `--strict` antes de solicitar cierre en Azure.

## Ejecución local de referencia

Frontend: 104 pruebas aprobadas; compilación, traducciones y lint completados (una advertencia heredada en UsuariosConfigScreen). API: 226 pruebas aprobadas y siete de Spark omitidas en la suite normal. Se ejecutaron de nuevo 87 pruebas del sprint y del contrato Spark tras incorporar compatibilidad con resultados históricos: todas aprobadas. La unión de la regresión y esta ejecución cubre 227 pruebas API aprobadas.

La compilación se abrió en el navegador y volvió a cargar la pantalla de acceso después de detener el servidor local: el contenedor estático quedó disponible desde el Service Worker. El estado de conexión del navegador no detecta por sí solo una caída exclusiva del servidor; ese caso conserva los errores y reintentos de la API.

La integración real de Spark en Windows/Python 3.13 presentó primero una instalación global distinta (`SPARK_HOME`) y después errores WinError 10038 en los workers. Se conserva el entorno del sistema y se verifica esa integración en el flujo del sprint con Linux, Python 3.12 y Java 17, conforme a la configuración del proyecto. No se registra esa ejecución local como aprobada.
