# Corrección del runtime Spark

## Problema observado

La interfaz podía permanecer en procesamiento después de que Render reiniciara el
worker o terminara la JVM. El trabajo se consideraba vigente durante 840 segundos.
Además, el subproceso descartaba `stderr`, de modo que PySpark ausente, Java sin
configurar, falta de memoria y timeout producían el mismo mensaje genérico.

## Corrección

- El trabajo interrumpido se recupera en `SPARK_JOB_TTL_SECONDS` (240 segundos por
  defecto), en lugar de permanecer bloqueado hasta 14 minutos.
- El proceso tiene un límite independiente mediante `SPARK_TIMEOUT_SECONDS` (180
  segundos por defecto) y se termina junto con su grupo de procesos.
- La API comprueba PySpark y Java antes de iniciar la JVM.
- Los errores conocidos se convierten en mensajes seguros y accionables. No se
  publican rutas, datos clínicos, variables de entorno ni la salida cruda de Java.
- La pantalla muestra el error seguro informado por el servidor y conserva la
  opción de volver a ejecutar.
- El `Dockerfile` de producción instala Java 17, PySpark y ejecuta un solo worker
  de Gunicorn para que el ejecutor en memoria no se multiplique entre procesos.
- Se fija una versión de `setuptools` compatible con PySpark 3.5 en Python 3.12;
  sin esa capa de compatibilidad el análisis no supervisado falla al cargar ML.

## Ejecución local

```bash
cd backend/api_hospital
python -m pip install -r requirements.txt
java -version
python app.py
```

Java 17 debe estar disponible en `PATH`. En Windows puede ser necesario definir
`JAVA_HOME` y reiniciar la terminal.

## Render

Configurar el servicio como **Docker**, usando
`backend/api_hospital/Dockerfile` y el directorio raíz
`backend/api_hospital`. Mantener las variables existentes de MongoDB, JWT y CORS.

Spark y la JVM requieren más memoria que una API Flask ordinaria. Si el log de
Render informa falta de memoria, el servicio necesita una instancia con memoria
suficiente; aumentar solamente el timeout no corrige ese problema.
