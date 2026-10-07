# Sistema de Gestión Clínica INEO

Aplicación clínica compuesta por un frontend React/Vite, una API Flask y MongoDB.
Este documento permite que una persona nueva instale, pruebe y use el sistema sin
conocer previamente el repositorio.

## Requisitos

- Git.
- Node.js 20 o superior y npm.
- Python 3.11 o 3.12.
- MongoDB 7 o acceso a una instancia compatible.
- Java 17 únicamente para ejecutar análisis con PySpark.

## 1. Clonar y configurar la API

```bash
git clone https://github.com/JoelLara10/ineo-pbl-entrega.git
cd ineo-pbl-entrega/backend/api_hospital
python -m venv .venv
```

Activa el entorno:

```bash
# Linux/macOS
source .venv/bin/activate

# PowerShell
.venv\Scripts\Activate.ps1
```

Instala las dependencias y crea la configuración local:

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

En PowerShell, sustituye la última orden por `Copy-Item .env.example .env`.
Edita `.env` y reemplaza las claves de ejemplo. `SECRET_KEY` debe tener al menos
32 caracteres. No publiques el archivo `.env`.

Variables principales:

| Variable | Uso | Ejemplo local |
|---|---|---|
| `MONGO_URI` | Conexión a MongoDB | `mongodb://localhost:27017/` |
| `MONGO_DB` | Base de datos | `hospital_db` |
| `SECRET_KEY` | Firma de tokens; mínimo 32 caracteres | valor aleatorio local |
| `JWT_SECRET_KEY` | Compatibilidad de configuración JWT | valor aleatorio local |
| `PORT` | Puerto de Flask | `5001` |
| `DEBUG` | Depuración local | `True` |
| `ENABLE_SCHEDULER` | Tareas programadas | `false` para pruebas |

Inicia MongoDB y después la API:

```bash
python app.py
```

Comprueba `http://localhost:5001/health`. Debe responder con `status: ok`.

## 2. Configurar el frontend

Desde la raíz del repositorio:

```bash
cd frontend/clinica-web-react
npm install
```

Crea `.env.local` con:

```dotenv
VITE_API_URL=http://localhost:5001/api/v1
```

Inicia la web:

```bash
npm run dev
```

Abre `http://localhost:5173`. Para usar los módulos protegidos necesitas un
usuario existente en la base de datos; la aplicación no incluye credenciales de
producción en el repositorio.

## 3. Ejecutar las pruebas

Frontend:

```bash
cd frontend/clinica-web-react
npm run check:i18n
npm test
npm run lint
npm run build
```

API:

```bash
cd backend/api_hospital
python -m pip install -r requirements-test.txt
python -m pytest -q
```

Prueba integrada reproducible con datos sintéticos (requiere Docker):

```bash
docker compose -f compose.test.yml up --build --abort-on-container-exit
```

El entorno integrado utiliza MongoDB en el puerto `27018` y la API en el `5002`.
No utiliza datos clínicos reales.

## 4. API publicada y despliegue

La API de demostración está en
`https://api-clinica-jx4m.onrender.com`. El plan gratuito puede tardar en activar
el servicio después de un periodo sin uso. Comprueba primero `/health`.

El procedimiento de despliegue, variables y reversión está en:

- `docs/deployment/despliegue.md`
- `docs/deployment/reversion.md`

## 5. Uso y documentación

- Manuales por rol: `docs/manual-usuario/`.
- API, seguridad, pruebas, Spark y respaldos: `docs/manual-tecnico/`.
- Arquitectura: `docs/arquitectura/`.
- Contrato versionado: `contracts/v1/api.schema.json`.

Flujo básico: iniciar sesión, elegir el módulo permitido para el rol, seleccionar
un paciente cuando corresponda y realizar la operación. Las rutas protegidas
devuelven `401` sin sesión y `403` cuando el rol no tiene permiso.

## Solución de problemas

| Problema | Revisión |
|---|---|
| La API no inicia por la clave | Usa un `SECRET_KEY` aleatorio de 32 caracteres o más. |
| No conecta a MongoDB | Verifica `MONGO_URI`, que el servicio esté activo y el puerto. |
| La web muestra error de conexión | Verifica `VITE_API_URL` y reinicia Vite. |
| Respuesta `401` o `403` | Inicia sesión o usa un rol autorizado; no es una caída de la API. |
| Spark no inicia | Instala Java 17 y confirma `java -version`. |
| Render tarda en responder | Espera la activación y repite primero la consulta a `/health`. |
