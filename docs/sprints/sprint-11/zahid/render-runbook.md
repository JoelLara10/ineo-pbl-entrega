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

## Alcance vigente de esta entrega

El solicitante indicó reutilizar la API existente y no realizar un nuevo
despliegue. Se ejecutaron nueve comprobaciones GET reales; sus resultados
están en revalidation/existing-api.json. Se validó la configuración versionada
y se documentó el ensayo en deployment-dry-run.json. Los pasos de publicación,
selección de versión y rollback de este runbook son instrucciones y simulación,
no acciones remotas realizadas. El SHA interno del servicio no fue observado.
No se considera pendiente un nuevo despliegue dentro del alcance ajustado.
Jesús revisa el procedimiento, la configuración y las evidencias.

Referencia: [Render Blueprint YAML Reference](https://render.com/docs/blueprint-spec).
