# Ambiente reproducible — Sprint 7 de Zahid

## Suite aislada, sin Mongo ni expedientes reales

Desde `backend/api_hospital`, Python 3.12:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-test.txt
python -m pytest -q
```

Las fixtures fuerzan configuración de prueba antes de importar la app, sustituyen
la conexión Mongo por mongomock, desactivan el scheduler y restablecen los datos
antes de cada prueba. No necesitan `.env` ni acceso a Atlas. Se conservan también
las fixtures anteriores de Joel para evitar romper su trabajo.

Para incluir motor real, instalar Java 17 y comprobar `java -version`:

```bash
pip install -r requirements-spark.txt
# Linux/macOS:
RUN_SPARK_TESTS=1 python -m pytest -q
# PowerShell: $env:RUN_SPARK_TESTS='1'; python -m pytest -q
```

PySpark 3.5.7 requiere setuptools para su importación de distutils en Python 3.12;
esa dependencia está fijada. Los tests del motor están omitidos explícitamente
en la suite ligera y son obligatorios en el job CI `spark-runtime`.

## Aplicación completa con Mongo de prueba

Desde la raíz del repositorio, Docker y Docker Compose:

```bash
docker compose -f compose.test.yml up --build -d
docker compose -f compose.test.yml logs api-test
```

API: `http://localhost:5002/api/v1`; salud: `http://localhost:5002/health`.
Mongo de prueba: `mongodb://127.0.0.1:27018/`, base `ineo_test_sprint7`.
El contenedor incluye Python, Java y PySpark, usa un worker Gunicorn y cuatro hilos.
El seed termina antes de iniciar la API. Los puertos sólo se publican en localhost.
Para conectar React local, configura `VITE_API_URL=http://localhost:5002/api/v1`
en su `.env` y ejecuta `npm ci` seguido de `npm run dev`.

| Rol | Usuario sintético | Contraseña exclusiva de pruebas |
|---|---|---|
| admin | admin.test | Prueba-Sprint7! |
| medico | medico.test | Prueba-Sprint7! |
| enfermeria | enfermeria.test | Prueba-Sprint7! |
| estudios | estudios.test | Prueba-Sprint7! |

Son datos inventados: ocho pacientes, ocho atenciones, ocho signos, un estudio y
una cama. Los IDs y fechas son estables; las contraseñas se almacenan con bcrypt
(coste reducido sólo para pruebas). No utilizar estos usuarios en producción.

Restablecer: detener primero la API y ejecutar la semilla explícitamente:

```bash
docker compose -f compose.test.yml stop api-test
docker compose -f compose.test.yml run --rm seed
docker compose -f compose.test.yml up -d api-test
```

Eliminar exclusivamente este ambiente y sus datos sintéticos:

```bash
docker compose -f compose.test.yml down -v
```

La semilla rechaza bases que no comiencen con `ineo_test_`, servidores no locales
y ejecución sin `INEO_TEST_RESET=YES`. Nunca se ejecuta automáticamente al iniciar
la aplicación normal. El scheduler normal conserva su comportamiento; sólo el
ambiente sintético usa `ENABLE_SCHEDULER=false`.

## Operación de Spark

La aplicación habitual sigue instalándose con requirements.txt. Para ejecutar
Spark necesita adicionalmente requirements-spark.txt y Java 17. Sin ese runtime,
los endpoints siguen respondiendo pero la ejecución informa un fallo controlado.
El Dockerfile de pruebas proporciona ambos. No se ha modificado Render ni publicado
una versión de producción como parte de este sprint.

Los trabajos viven en `spark_jobs`, con un documento por tipo; cada proceso API
dispone de una cola local de un trabajador y ejecuta una JVM por análisis. Un análisis
tiene un máximo de 180 segundos; una cola perdida caduca en 840 segundos. La siguiente
consulta marca el trabajo vencido como fallido y permite volver a ejecutarlo.
No hay recuperación automática tras un reinicio. En Linux se termina todo el grupo
del subproceso al agotar el tiempo. Un resultado anterior correcto se conserva.
Para este prototipo se recomienda un solo worker API; otros workers comparten el
bloqueo por tipo de Mongo pero disponen de sus propias colas y consumen más memoria.
Reservar memoria para JVM y API; esta entrega no certifica capacidad del plan de Render.

## Comprobación manual disponible

1. Iniciar sesión con admin.test y abrir `/admin/spark`.
2. Abrir cada módulo, ejecutar y esperar a que termine; verificar total 8.
3. En general deben aparecer cuatro atenciones abiertas y cuatro cerradas.
4. En clínico, media de frecuencia cardíaca = 82.5 lat/min.
5. En no supervisado, la suma de tamaños de grupos debe ser 8.
6. Cambiar español/inglés; verificar etiquetas, medidas y estados.
7. Consultar los endpoints con token de enfermería: deben devolver 403.

Estos pasos son un guion; no se presentan como UAT firmada ni prueba visual realizada.
