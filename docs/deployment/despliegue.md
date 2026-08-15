# Guía de despliegue — INEO Web y API

**Sprint:** 6 — Cierre  
**Responsable:** Jesús  
**Componentes:** React/Vite, Flask y MongoDB

## 1. Objetivo

Proporcionar un procedimiento reproducible para instalar y ejecutar la entrega integrada sin copiar secretos ni datos clínicos al repositorio.

## 2. Requisitos

- Git.
- Python compatible con las dependencias del backend.
- Node.js y npm compatibles con Vite 8.
- MongoDB accesible local o remotamente.
- Puertos disponibles: API `5001` y frontend de desarrollo `5173`.

## 3. Obtener la versión

```powershell
git clone https://github.com/JoelLara10/ineo-pbl-entrega.git
cd ineo-pbl-entrega
git checkout main
git pull origin main
```

Para una liberación estable, use una etiqueta aprobada en vez de una rama de trabajo.

## 4. Configurar MongoDB

Confirme que el servicio esté activo y cree una base autorizada. No importe respaldos con pacientes reales en ambientes de prueba. Valores esperados por defecto:

```text
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=hospital_db
```

## 5. Backend Flask

```powershell
cd backend\api_hospital
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Cree `.env` únicamente en el servidor:

```dotenv
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=hospital_db
SECRET_KEY=REEMPLAZAR_CON_VALOR_SEGURO
JWT_SECRET_KEY=REEMPLAZAR_CON_VALOR_SEGURO
DEBUG=False
PORT=5001
```

Inicie la API:

```powershell
python app.py
```

Valide:

```powershell
Invoke-RestMethod http://localhost:5001/health
```

Debe responder `status: ok`. La configuración de CORS debe contener el origen real del frontend.

## 6. Frontend React

En otra terminal:

```powershell
cd frontend\clinica-web-react
npm ci
```

Cree `.env.local`:

```dotenv
VITE_API_URL=http://localhost:5001/api/v1
```

Para desarrollo:

```powershell
npm run dev
```

Para validar y generar la distribución:

```powershell
npm run lint
npm run build
npm run preview
```

El contenido generado en `dist/` no se versiona; debe publicarse en el servidor web configurado para redirigir rutas de SPA a `index.html`.

## 7. Orden de validación

1. MongoDB responde.
2. API `/health` devuelve 200.
3. Login genera una sesión válida.
4. Frontend consume la URL configurada.
5. Se prueban roles `admin`, `administrativo`, `medico`, `enfermero` y `estudios`.
6. Se recorren pacientes, Enfermería, Médico, Estudios y Configuración.
7. Se crea un respaldo de prueba sin datos reales.

## 8. Seguridad

- No use los secretos predeterminados de `config.py` en producción.
- Use HTTPS y una URI MongoDB con autenticación.
- Restrinja CORS al dominio desplegado.
- No exponga el puerto de MongoDB a Internet.
- Limite permisos del directorio `backups/` y de resultados.
- Mantenga `.env`, `venv/`, `node_modules/`, `dist/`, `backups/` y `uploads/` fuera de Git.

## 9. Lista de comprobación

```text
[ ] Versión o tag identificado
[ ] Respaldo previo disponible
[ ] Variables de entorno seguras
[ ] MongoDB disponible
[ ] Dependencias instaladas
[ ] API saludable
[ ] Build web aprobado
[ ] Roles verificados
[ ] Sin datos clínicos reales en el repositorio
[ ] Plan de reversión disponible
```

## 10. Evidencia

Registre fecha, commit/tag, ambiente, comandos, resultados y responsable. Adjunte únicamente capturas sin datos sensibles en las carpetas de evidencia asignadas.
