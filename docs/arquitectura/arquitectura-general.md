# Arquitectura general del Sistema de Gestión Clínica INEO

**Sprint:** 1 — Arquitectura y bases  
**Responsable:** Jesús  
**Historias relacionadas:** MIG-001 y MIG-002

## 1. Propósito

Definir la arquitectura objetivo para integrar el frontend React y la API Flask del Sistema INEO, conservando una separación clara entre presentación, comunicación, negocio y persistencia.

## 2. Estilo arquitectónico

La solución adopta una arquitectura cliente-servidor con API REST:

1. El usuario accede a la aplicación web desde un navegador.
2. React presenta las pantallas y administra el estado de sesión.
3. Los servicios del frontend envían solicitudes HTTP/JSON mediante Axios.
4. Flask recibe las solicitudes en blueprints organizados por dominio.
5. El middleware valida el token JWT en rutas protegidas.
6. Los servicios del backend ejecutan reglas de negocio.
7. Las utilidades de acceso a datos consultan o modifican MongoDB.
8. La API devuelve una respuesta JSON para actualizar la interfaz.

## 3. Capas de la solución

| Capa | Componentes | Responsabilidad |
|---|---|---|
| Presentación | React, páginas, componentes, layouts, contextos | Mostrar información, capturar datos y controlar navegación |
| Integración cliente | Servicios Axios e interceptores | Construir peticiones, adjuntar JWT y manejar errores HTTP |
| Exposición API | Flask y blueprints | Publicar endpoints REST bajo `/api/v1` |
| Seguridad | Auth, middleware JWT y CORS | Autenticar, autorizar y controlar orígenes permitidos |
| Negocio | `services/` del backend | Aplicar reglas clínicas, administrativas y de reportes |
| Persistencia | PyMongo, `utils/database.py` y MongoDB | Consultar y almacenar información hospitalaria |
| Soporte | Scheduler, respaldos, PDF y analítica | Automatizar procesos y producir resultados derivados |

## 4. Componentes principales

### Frontend React

- `App.jsx` integra `BrowserRouter`, `AuthProvider` y `PatientProvider`.
- `AppRouter.jsx` concentra las rutas y el acceso por rol.
- `pages/` contiene las pantallas de administración, enfermería, médico, estudios y analítica.
- `services/api.js` define la conexión común a la API.
- Los servicios especializados separan las peticiones por módulo.

### API Flask

- `create_app()` construye la aplicación.
- Los blueprints desacoplan los endpoints por dominio.
- El middleware `token_required` protege recursos privados.
- Los servicios encapsulan la lógica y el acceso a las colecciones.
- `config.py` concentra variables comunes y lee valores del entorno.

### MongoDB

MongoDB almacena los documentos del sistema clínico. La API es la única capa autorizada para acceder a la base; el navegador nunca se conecta directamente a ella.

## 5. Comunicación y seguridad

- Protocolo de aplicación: HTTP/HTTPS.
- Formato principal: JSON.
- URL lógica: `{VITE_API_URL}` o `http://<host>:5001/api/v1`.
- Autorización: encabezado `Authorization: Bearer <token>`.
- CORS: limitado a los orígenes configurados.
- Secretos: solo en variables de entorno del backend.
- Manejo de sesión: el frontend elimina el token local ante una respuesta 401.

En producción deben utilizarse HTTPS, secretos robustos, una lista de CORS restringida y una cuenta de base de datos con permisos mínimos.

## 6. Flujo de autenticación

1. El usuario captura sus credenciales en la pantalla de acceso.
2. React envía la petición al endpoint de autenticación.
3. Flask valida las credenciales mediante el servicio de autenticación.
4. La API devuelve el token y los datos permitidos del usuario.
5. El frontend conserva la sesión y el interceptor adjunta el token.
6. El router habilita las vistas correspondientes al rol.
7. Una respuesta 401 invalida la sesión local y obliga a autenticarse nuevamente.

## 7. Organización en el repositorio de entrega

```text
ineo-pbl-entrega/
├── frontend/clinica-web-react/
├── backend/api_hospital/
├── docs/
├── design/
├── evidence/
└── PBL/
```

Esta organización no mezcla dependencias ni código fuente: cada aplicación conserva su gestor, configuración y ciclo de ejecución.

## 8. Entornos

| Entorno | Frontend | Backend | Base de datos |
|---|---|---|---|
| Desarrollo | Vite en `5173` | Flask en `5001` | MongoDB local o URI de desarrollo |
| Pruebas | Build controlado o Vite | Configuración de prueba | Base aislada sin datos reales |
| Producción | Archivos compilados servidos por HTTPS | Servidor WSGI detrás de proxy | MongoDB protegido y respaldado |

## 9. Decisiones arquitectónicas

- Mantener frontend y backend desacoplados permite desplegarlos y probarlos por separado.
- Utilizar un prefijo versionado (`/api/v1`) reduce el impacto de cambios futuros.
- Separar rutas y servicios evita concentrar reglas de negocio en los controladores HTTP.
- Centralizar Axios permite aplicar de forma uniforme URL, tiempo de espera, token y errores.
- Conservar los repositorios originales mantiene la trazabilidad previa; el nuevo repositorio muestra la integración por sprint.

## 10. Validaciones mínimas de integración

- `GET /health` responde con estado `ok`.
- El frontend puede iniciar sesión contra la API configurada.
- Las rutas privadas rechazan solicitudes sin token.
- El usuario solo visualiza módulos autorizados para su rol.
- Las operaciones de prueba se reflejan en MongoDB sin utilizar información real.
- El repositorio no contiene secretos, respaldos ni resultados clínicos.

## 11. Diagrama

El archivo `diagrama-arquitectura.png`, ubicado en esta misma carpeta, representa la relación entre navegador, aplicación React, API Flask y MongoDB, además de la división interna de responsabilidades.
