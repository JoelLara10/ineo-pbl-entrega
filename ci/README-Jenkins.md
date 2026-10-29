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

## Relación con Azure

- PBL-47: CP-S10-CI-01/02/03 se demuestran parcialmente con ejecución manual,
  fallo controlado y publicación de reportes. No hay webhook SCM instalado:
  **la ejecución automática por commit sigue pendiente**.
- CP-S10-CI-04 (agente no disponible) no se ha ejecutado: el timeout de seguridad
  no sustituye su campaña.
- PBL-37: evidencia parcial para CP-S10-OAT-01/02/03 con la dependencia simulada;
  CP-S10-OAT-04 (limpieza IaC) pendiente.
- Se conservan responsables y estados de Azure; no se cierran historias por esta demo.
