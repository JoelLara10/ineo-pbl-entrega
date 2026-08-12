# Estrategia de migración e integración Flask–React

**Sprint:** 1 — Arquitectura y bases  
**Responsable:** Jesús  
**Historia principal:** MIG-002

## 1. Objetivo

Integrar los repositorios existentes de Flask y React en la estructura del PBL sin alterar su historial original ni incorporar archivos sensibles. La migración es una reorganización controlada del sistema existente, no una afirmación de que el código fue creado nuevamente durante estos sprints.

## 2. Origen y destino

| Origen | Destino |
|---|---|
| `jaimediaz25/api_hospital` | `backend/api_hospital/` |
| `JoelLara10/clinica-web-react` | `frontend/clinica-web-react/` |
| Documentación dispersa o nueva | `docs/` |
| Mockups y criterios visuales | `design/` |
| Evidencias por integrante | `evidence/<integrante>/` |

## 3. Principios de migración

- Integrar únicamente los archivos asignados a cada sprint.
- Mantener el historial original en los dos repositorios fuente.
- Usar commits actuales con mensajes de integración o documentación.
- No modificar fechas ni simular un historial anterior.
- Excluir secretos, dependencias instaladas, respaldos y datos clínicos.
- Validar que cada lote integrado pueda identificarse con su historia y responsable.

## 4. Preparación

Antes de copiar código:

1. Crear y fusionar la rama de estructura inicial.
2. Confirmar las carpetas `frontend/`, `backend/`, `docs/`, `design/`, `evidence/` y `PBL/`.
3. Aplicar el `.gitignore` general.
4. Verificar que los repositorios fuente estén actualizados.
5. Revisar manualmente los archivos por copiar para evitar secretos o datos reales.

## 5. Migración técnica por etapas

### Etapa 1. Base documental y arquitectura

Jesús incorpora el inventario, la arquitectura objetivo, esta estrategia y el diagrama. Esta etapa establece las reglas utilizadas por los siguientes integrantes.

### Etapa 2. Base de la API Flask

Se integran configuración, autenticación, middleware, modelos, acceso a MongoDB y dependencias. La API debe iniciar y responder en `/health` antes de incorporar dominios adicionales.

### Etapa 3. Base React

Se integran Vite, punto de entrada, router, contexto de autenticación, servicios de API, login y layout. El frontend debe compilar y mostrar el acceso sin errores.

### Etapa 4. Módulos por sprint

Pacientes, administrativo, enfermería, médico, estudios, analítica y configuración se incorporan en los sprints correspondientes. Cada módulo debe incluir frontend, endpoints, servicios, diseño y documentación según la planificación.

### Etapa 5. Estabilización

Se revisan rutas, variables, CORS, permisos, respuestas de error, compilación, pruebas integrales y documentación de operación.

## 6. Variables de entorno

### Backend (`.env.example`)

```dotenv
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=hospital_db
SECRET_KEY=cambiar-en-entorno-local
JWT_SECRET_KEY=cambiar-en-entorno-local
DEBUG=True
PORT=5001
```

El archivo real `.env` nunca debe agregarse a Git.

### Frontend (`.env.example`)

```dotenv
VITE_API_URL=http://localhost:5001/api/v1
```

En una prueba desde otro dispositivo debe sustituirse `localhost` por la IP accesible del equipo que ejecuta Flask y agregarse el origen del frontend a CORS.

## 7. Contrato de comunicación

- Las rutas de negocio se publican bajo `/api/v1`.
- Las solicitudes y respuestas utilizan JSON, excepto cargas o descargas documentales.
- Axios usa un tiempo de espera común y el encabezado `Content-Type`.
- Las rutas privadas reciben un token Bearer.
- Los errores deben conservar códigos HTTP coherentes: 400, 401, 403, 404 y 500.
- Los cambios incompatibles futuros requieren una nueva versión de API.

## 8. Procedimiento de validación

### Backend

```powershell
cd backend\api_hospital
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Comprobar `http://localhost:5001/health` y una operación de autenticación con datos de prueba.

### Frontend

```powershell
cd frontend\clinica-web-react
npm install
npm run dev
```

Comprobar `http://localhost:5173`, el inicio de sesión, la navegación protegida y la comunicación con la API.

### Integración

1. Iniciar MongoDB.
2. Iniciar Flask en el puerto configurado.
3. Iniciar Vite.
4. Abrir las herramientas de red del navegador.
5. Confirmar que las peticiones usan `/api/v1` y reciben respuestas válidas.
6. Probar cierre de sesión, token inválido y acceso por rol.

## 9. Estrategia Git para Jesús en Sprint 1

```powershell
git checkout main
git pull origin main
git checkout -b sprint-1/jesus-documentacion

git add docs/sprints/sprint-1/inventario-sistema-anterior.md
git add docs/arquitectura/arquitectura-general.md
git add docs/arquitectura/migracion-flask-react.md
git add docs/arquitectura/diagrama-arquitectura.png

git commit -m "docs(sprint-1): add system inventory and target architecture"
git push -u origin sprint-1/jesus-documentacion
```

Después debe abrirse un Pull Request hacia `main`. Antes de fusionar, se revisan las rutas, el contenido y la ausencia de datos sensibles.

## 10. Plan de reversión

Si el lote provoca conflictos o contiene archivos incorrectos:

1. No fusionar el Pull Request.
2. Corregir el contenido en la misma rama.
3. Volver a validar el alcance del sprint.
4. Si ya fue fusionado, crear un commit de reversión documentado; no reescribir el historial compartido.

## 11. Criterios de aceptación de MIG-002

- La arquitectura objetivo está documentada y acompañada por un diagrama legible.
- Se conocen las rutas de origen y destino de cada aplicación.
- La configuración sensible se maneja mediante variables de entorno.
- Existe un procedimiento reproducible para ejecutar y validar ambas aplicaciones.
- La migración conserva la trazabilidad de los repositorios originales.
- El commit contiene exclusivamente los cuatro archivos asignados a Jesús en el Sprint 1.
