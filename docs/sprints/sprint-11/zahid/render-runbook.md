# Despliegue reproducible de API en Render

Se versionó render.yaml para describir el servicio Docker y su readiness.
La API existente proporcionada para verificación es
https://api-clinica-jx4m.onrender.com. Las comprobaciones remotas se conservaron
en evidence/sprint-11/zahid/render-smoke.json. No se afirma que ese servicio
se haya recreado ni que ejecute el SHA de esta rama.

## Configuración y despliegue

1. Seleccionar el servicio de QA autorizado y registrar su ID, rama, SHA,
   versión anterior y configuración de recursos. Importar o reconciliar el
   blueprint; no crear un duplicado del servicio existente sin revisión.
2. Revisar dockerContext backend/api_hospital y dockerfilePath
   backend/api_hospital/Dockerfile, ambos relativos a la raíz del repositorio.
   El comando de inicio
   existente usa gunicorn, un worker, veinte hilos, timeout 240 y PORT de Render.
   Docker expone 10000 y Render termina HTTPS. El health check /ready comprueba
   MongoDB; /health identifica liveness. No intercambiar ambos criterios.
3. Configurar MONGO_URI, MONGO_DB, SECRET_KEY y CORS_ORIGINS en Render.
   Usar secretos reales mediante el almacén del proveedor; no copiarlos a Git,
   documentos ni capturas. El blueprint requiere entrada manual para estos valores.
   SECRET_KEY debe cumplir la validación de la aplicación de al menos 32 caracteres.
4. Mantener ENABLE_SCHEDULER=false y revisar ANALYSIS_ENGINE=auto, recursos y
   dependencias Java/Spark del Dockerfile. Validar compatibilidad entre API/web.
5. Ejecutar despliegue manual del SHA revisado. Registrar ID, inicio/fin reales,
   resultado y logs sin secretos. El blueprint mantiene autoDeployTrigger off.
6. Ejecutar render_smoke.py, login sintético en QA, permisos negativos y lecturas
   representativas. Vincular las evidencias al mismo SHA y despliegue.

## Recuperación

Registrar primero el último deployment estable. Si falla readiness, compatibilidad
o un caso crítico, detener la promoción y volver a ese deployment desde Render.
Repetir salud, readiness, login, permisos y consulta; registrar ID y hora reales.
Restaurar datos requiere un procedimiento específico si fuera necesario; una
reversión del contenedor no demuestra una restauración de base de datos.

## Pendiente de comprobación remota

Sin acceso al panel o API de gestión de Render no se pudieron observar la rama,
SHA, variables, recursos ni historial del servicio. Por ello T1 se entregó como
inventario de configuración esperada y verificada desde el repositorio, T2 como
configuración lista para ejecutar y T3 como smoke remoto con límites explícitos.
La reproducibilidad y reversión remotas deben demostrarse antes del cierre de
PBL-39. La prueba local Terraform no sustituye este requisito.

Referencia técnica comprobada: [Render Blueprint YAML Reference](https://render.com/docs/blueprint-spec).
