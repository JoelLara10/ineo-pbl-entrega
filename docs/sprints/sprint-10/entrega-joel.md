# Sprint académico 4 de Joel

Periodo planificado: 24 octubre a 6 noviembre 2026. Azure: Sprint 10.
Historias: PBL-37 (#440), PBL-47 (#532), 5 puntos cada una, total 10.
Este expediente cubre el trabajo técnico de Joel; no acredita trabajo ni aceptación de otros integrantes.

## Diseño y trazabilidad

PBL-37-T1 #497: diseño de puertas, datos sintéticos, riesgos y criterios en este documento.
PBL-37-T2 #498: `ci/Jenkinsfile.sprint10` y `ci/sprint10_run.py` implementan checkout, lint, traducciones, UT/contratos, cobertura, compilación, OAT y publicación de reportes.
PBL-37-T3 #499: positivos, autorización negativa, caída de dependencia, correlación sanitizada y ensayos negativos; datos aislados en `ineo_test_s10`.
PBL-37-T4 #581: CP-S10-CI-01 a 04, conservando el alcance OAT previo.
PBL-37-T5 #582: CP-S10-OAT-01 a 04 y expediente Word con anexos originales.
PBL-47-T1 #533: conexión acordada GitHub SCM → Jenkins; trazabilidad hacia Azure mediante IDs en build y expediente adjunto a historias/tareas. Azure es el gestor del trabajo; el código permanece en GitHub. No existe repositorio Azure Repos ni se declara uno configurado.
PBL-47-T2 #534: job dedicado `OftalCore-Joel-Sprint4`, agente local y checkout público sin credenciales SCM. La cuenta de administración local se usa fuera del repositorio; ningún secreto se publica. No necesita PAT de Azure para la vinculación documental.
PBL-47-T3 #535: polling SCM cada dos minutos mientras Jenkins está encendido; archivo de resultados JUnit/cobertura/logs también en fallos.
PBL-47-T4 #536: `source.json` identifica SHA, historias, tareas, build, fecha UTC y causa del disparo.

## Ejecución desde checkout limpio

Requisitos: Python 3.12, Node 22, Docker con motor activo, Jenkins con Git/Pipeline/JUnit y acceso a Internet. El agente debe tener acceso al motor Docker. Instalar dependencias API y test desde sus archivos fijados; instalar también `ci/requirements-security.txt` para el job de seguridad existente. `npm ci` instala el lock web.

Desde la raíz del repositorio:

```powershell
python -m venv .sprint10-api
.sprint10-api/Scripts/python -m pip install -r backend/api_hospital/requirements.txt -r backend/api_hospital/requirements-test.txt
$env:S10_TERRAFORM_DOCKER='1'
# Solo si la red requiere la CA de confianza del equipo:
$env:CA_BUNDLE='RUTA_ABSOLUTA_AL_PEM_DE_CONFIANZA'
.sprint10-api/Scripts/python qa/sprint-10/oat/run_oat.py --out reports/sprint10/local-oat
```

No poner claves reales en los comandos ni desactivar TLS. Terraform 1.13.5 se ejecuta en la imagen oficial `hashicorp/terraform:1.13.5`; proveedor Docker 4.2.0 fijado en lock. Mongo 7.0.16 se publica en un puerto aleatorio de 127.0.0.1. Flask usa el código real por HTTP local con el entorno sobrescrito antes de importar dotenv. No usa mocks de Mongo. Spark no forma parte de estos cuatro OAT.

En Jenkins crear Pipeline con el contenido de `ci/Jenkinsfile.sprint10`, fijar TEST_PYTHON al intérprete instalado y CA_BUNDLE solo si aplica. SOURCE_BRANCH selecciona la rama remota; el SHA resuelto queda en source.json. SCENARIO normal ejecuta el flujo completo; ut-failure ejecuta una aserción fallida real en la rama de ensayo y debe impedir el candidato. agent-unavailable solicita durante 20 segundos la etiqueta exclusiva `ineo-sprint10-disposable-offline-agent`, que no debe asignarse a un agente real. Su timeout debe abortar y omitir etapas posteriores; no se desconecta el agente compartido ni se interrumpen otros trabajos.

## Criterios y evidencia

CI-01: causa SCM y SHA coincidentes. CI-02: resultado FAILURE, aserción UT visible y candidato ausente. CI-03: JUnit, logs y cobertura no vacíos y accesibles. CI-04: espera de agente no disponible termina por timeout y no produce candidato.
OAT-01: /ready 200 con Mongo real, 503 sin Mongo, /health 200, recuperación 200. OAT-02: request ID generado presente en log; token/cabecera/ruta sintéticos ausentes. OAT-03: proceso API nuevo, mismo puerto, salud 200 y petición sin sesión 401; objetivo técnico de ensayo 45 segundos, sujeto a revisión operativa. OAT-04: Terraform destruye únicamente el estado privado de esta ejecución; cero contenedores con su etiqueta y contenedores ajenos siguen activos.

La API registra el identificador X-Request-ID que genera para cada petición. Mantiene los datos del cliente fuera de ese mensaje. El servidor de ensayo desactiva el access log de Werkzeug, que de otro modo imprimiría la URL sin sanitizar. En despliegues, revisar que proxy y servidor tampoco registren cuerpos o URLs sensibles.

Reportes por build en `reports/sprint10/build-N/`. No versionar entornos, caché del proveedor ni estado Terraform. Guardar los JSON/XML/logs sanitizados originales y los Word por caso, informe y anexos. La cobertura obtenida se reporta como medición, no se presenta como cumplimiento del Quality Gate Sonar del equipo. El job de seguridad separado conserva sus controles y reportes; no se sustituye Sonar/JMeter de otros responsables.

## Administración y recuperación

El pipeline no fusiona ni despliega. Solo emite un candidato técnico después de todas sus etapas. La protección de main y los checks obligatorios se deben verificar en GitHub; un Jenkins local sin callback de estado no equivale a un check obligatorio del PR. La revisión de Jaime, capacitación/UAT de usuarios y decisión operativa se registran únicamente cuando ocurran. Mantener las historias activas si faltan esos requisitos.

Para recuperar un ensayo, detener solo el proceso API identificado por el runner. La limpieza automática usa Terraform destroy sobre el directorio de estado de ese reporte y su run_id. Si hubo interrupción, revisar primero `oat.json`, `tf-*.log`, contenedor con etiqueta `ineo.qa.run` y el estado privado correspondiente; repetir destroy solo con ese run_id y ese estado. No ejecutar docker prune ni tocar volúmenes de otros proyectos. Un fallo de limpieza se conserva como fallo y requiere seguimiento.

## Glosario

CI: integración continua. OAT: aceptación operativa. SCM: control de código fuente. SHA: identificador del commit. JUnit: formato XML de resultados. IaC: infraestructura como código. Readiness: capacidad de atender con dependencias disponibles. UAT: aceptación funcional por usuario real.

