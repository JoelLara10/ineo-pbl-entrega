# Demostración de Joel: Jenkins y OAT

Responsable: Joel Alejandro Lara Rodríguez. Sprint académico 4 = Sprint 10 en Azure.
Historias: PBL-47 (pipeline) y PBL-37 (operación). Se reutiliza regresión del
sprint académico 3 / Azure 9; ejecutarla ahora no cambia su sprint de origen.

## Qué puede ejecutar el profesor

1. Abrir Jenkins local, entrar al proyecto **OftalCore-Joel-Demo** y elegir
   **Construir con parámetros / Build with Parameters**.
2. Dejar `FORZAR_FALLO` desmarcado y construir. Revisar las etapas y **Test Result**.
3. Abrir un caso para ver su nombre, duración y resultado; abrir **Console Output**
   para ver los comandos reales. Los XML y el SHA están en **Artifacts**.
4. Repetir marcando `FORZAR_FALLO`. Debe fallar el caso de control y omitirse
   **Promoción de demostración**. No se modifica el sistema para provocar el error.
5. Ejecutar otra vez sin la marca: debe volver a aprobar.

La promoción es un marcador local; no fusiona ramas, no publica servicios ni
constituye aceptación UAT. Cada build usa una carpeta distinta para impedir que
se publiquen reportes antiguos como si fueran nuevos.

## Recorridos Selenium incorporados

La etapa **Selenium recorridos del usuario** ejecuta Chrome contra el React y
la API reales del repositorio, en puertos temporales locales. Mongo sigue siendo
sintético (mongomock). No utiliza cuentas ni datos de producción.

Activar `MOSTRAR_NAVEGADOR` para ver Chrome actuar. `CHROMEDRIVER_EXE` indica el
controlador compatible con Chrome, o queda vacío para usar Selenium Manager.
El Jenkins local ya tiene el controlador configurado.

| Caso | Criterio comprobado en pantalla |
|---|---|
| SEL-01 | Ruta privada sin sesión devuelve al acceso. |
| SEL-02 | Contraseña incorrecta muestra credenciales inválidas. |
| SEL-03 | Acceso de enfermería y navegación a valoración del paciente sintético. |
| SEL-04 | Guardado y consulta del mismo registro tras recargar la página. |
| SEL-05 | Dolor 11 muestra validación y no crea una valoración. |
| SEL-06 | Fallo de conexión a la API muestra error, conserva el formulario y permite reintentar. |
| SEL-07 | Modo offline bloquea el formulario clínico; reconectar vuelve a habilitarlo. |

SEL-06 bloquea la conexión al endpoint de guardado sin desconectar todo Chrome.
SEL-07 comprueba por separado el modo offline limitado, que desmonta el formulario:
no se afirma que conserve borradores. PNG y JSON por caso se guardan en
**Artifacts / screenshots**; `selenium.xml` alimenta **Test Result**.

Las acciones manuales del profesor en otra sesión no se registran automáticamente.
Debe iniciar **Build with Parameters** para generar resultados nuevos. Son
recorridos técnicos: la aceptación humana UAT se registra aparte.

El pipeline ampliado ejecuta **88 comprobaciones**: 63 API + 7 componentes web +
10 OAT + 7 Selenium + 1 control del bloqueo. Las ejecuciones antiguas de 81
conservan su alcance original.

## Etapas y alcance

| Etapa | Evidencia y límites |
|---|---|
| Identificar versión | SHA de Git y diferencias locales archivadas. |
| API sprint 3 / Azure 9 | Valoración, validación, permisos, Analytics y trazabilidad; Flask con Mongo simulado. |
| Web de Joel | Siete verificaciones de presentación clínica, unidades y contexto mediante Vitest/Testing Library; no Selenium. |
| OAT | `/health`, `/ready`, indisponibilidad de DB, recuperación, ausencia del secreto canario en respuestas/logs y lectura sin mutación. |
| OAT por HTTP | Proceso real de API en loopback, caída simulada de DB, reinicio real en el mismo puerto y rechazo sin sesión. |
| Bloqueo | Una aserción optativa falla al activar `FORZAR_FALLO`. |
| Promoción | Solo si pasaron las etapas previas; `promotion.txt` de demostración. |

La base de OAT es **mongomock con datos sintéticos**, incluso en la prueba HTTP.
El reinicio recrea una fixture: no demuestra persistencia de Mongo real ni
restauración de respaldos. Los procesos temporales se cierran al terminar cada
prueba. No se ha implementado ni aprobado aquí Terraform, borrado de recursos
Docker, recuperación de datos reales, carga JMeter ni aceptación humana UAT.
Esto avanza PBL-47/PBL-37; no acredita toda su Definition of Done.

## Reproducir en otro Jenkins de Windows

- Jenkins LTS 2.580.1 con Java 21/25 y plugins Pipeline, JUnit y Stage View.
- Git, Python 3.12 y Node 22 disponibles para el usuario que ejecuta Jenkins.
- Checkout del repositorio. Crear un entorno virtual e instalar
  `ci/requirements-demo-lock.txt`; es el entorno congelado de esta demostración,
  no una sustitución de los requisitos de producción.
- En `frontend/clinica-web-react`, ejecutar `npm ci`.
- Crear un proyecto Pipeline con el contenido de `Jenkinsfile` de esta rama.
  Tras la primera ejecución aparecen los parámetros. Configurar `PROJECT_DIR`
  con la ruta absoluta del checkout y `PYTHON_EXE` con el Python del entorno.
- El pipeline está escrito para agentes **Windows** (`bat`), no Linux.

Comprobación manual equivalente desde `backend/api_hospital`:

```powershell
$env:PYTHONUTF8='1'
python -m pytest tests/test_sprint9_uat_readiness.py tests/test_sprint9_jesus.py tests/test_sprint9_zahid.py -v
python -m pytest tests/test_oat_joel.py tests/test_oat_http_joel.py -v
```

Los ensayos del pipeline tienen timeout de 15 minutos. Si falta una dependencia,
el reporte o el agente, corregir la causa y repetir; no registrar un aprobado.

Para ejecutar solo Selenium desde la raíz del repositorio:

```powershell
$env:PYTHONUTF8='1'
$env:CHROMEDRIVER_EXE='C:/ruta/chromedriver.exe'
$env:INEO_SHOW_BROWSER='true'
New-Item -ItemType Directory -Force reports/selenium-local | Out-Null
python -m pytest ci/selenium -v -p no:cacheprovider --basetemp=reports/selenium-local/tmp --junitxml=reports/selenium-local/selenium.xml
```

Se usan esperas explícitas por elementos y estados, según la documentación de
[Selenium](https://www.selenium.dev/documentation/webdriver/waits/).

## Relación con Azure

- PBL-47: CP-S10-CI-01/02/03 se demuestran parcialmente con ejecución manual,
  fallo controlado y publicación de reportes. No hay webhook SCM instalado:
  **la ejecución automática por commit sigue pendiente**.
- CP-S10-CI-04 (agente no disponible) no se ha ejecutado: el timeout de seguridad
  no sustituye su campaña.
- PBL-37: evidencia parcial para CP-S10-OAT-01/02/03 con la dependencia simulada;
  CP-S10-OAT-04 (limpieza IaC) pendiente.
- Se conservan responsables y estados de Azure; no se cierran historias por esta demo.

## Correcciones UAT del 29 de octubre
Se agregan 13 regresiones visuales y funcionales: los tres formularios en modo
claro y oscuro, botones de Analytics, camas por rol y hora de los tres historiales.
El pipeline actual incorpora además cinco controles de fechas de API y cinco de
formato web. Total actual: 111 comprobaciones (68 API, 12 web, 10 OAT, 20 Selenium
y 1 control). Los builds antiguos de 81 y 88 conservan sus resultados originales.
La interfaz mantiene su diseño claro con color-scheme only light. Las marcas de
registro se guardan en UTC explícito y las horas se presentan en America/Mexico_City.
Administración puede consultar camas; la edición sigue reservada al administrador.
