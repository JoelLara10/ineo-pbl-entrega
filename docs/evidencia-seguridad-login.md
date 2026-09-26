# Evidencia: seguridad del inicio de sesión

## 1. Flujo de información seleccionado

```text
Aplicación móvil (Expo/React Native)
        │  POST /api/v1/auth/login por HTTPS
        │  { username, password }
        ▼
API Flask desplegada en Render
        │  consulta de usuario y verificación bcrypt
        ▼
MongoDB Atlas
        │
        └── La API responde con JWT y datos mínimos del usuario
```

### Información involucrada

| Elemento | Detalle |
|---|---|
| Sale del dispositivo | Nombre de usuario y contraseña. |
| Recibe el dispositivo | JWT y datos mínimos de sesión: id, usuario, rol y nombre. |
| Información sensible | Contraseña, JWT e identidad/rol del usuario. |
| Persistencia | La contraseña se conserva como hash bcrypt en MongoDB; la app guarda la sesión local para mantener el acceso. |
| Posibles vulnerabilidades | JSON inválido, campos vacíos o sobredimensionados, enumeración de usuarios, mensajes internos expuestos y respuestas de API malformadas. |

No se deben usar pacientes ni credenciales reales para las pruebas.

## 2. Mecanismos seleccionados y justificación

### Validación de entradas

La app valida campos vacíos y límites antes de realizar la petición. La API repite la validación porque el cliente no es una frontera de confianza: rechaza cuerpos que no sean JSON, tipos incorrectos, usuarios mayores de 80 caracteres y contraseñas mayores de 72 bytes.

Esto reduce errores inesperados, entradas abusivas y problemas asociados con el límite de bcrypt.

### Manejo seguro de errores y respuestas

La API devuelve el mismo mensaje, `Credenciales inválidas`, cuando el usuario no existe o la contraseña es incorrecta. Así evita confirmar qué cuentas existen. También se eliminaron registros que incluían el nombre de usuario durante fallos.

La app no presenta directamente errores enviados por el servidor. Distingue solamente entre falta de conexión y fallo de autenticación, y valida que la respuesta exitosa tenga un token y un usuario con la estructura esperada antes de almacenarlos.

### Controles ya existentes que complementan la implementación

- Comunicación con la API pública mediante HTTPS.
- Contraseñas verificadas con bcrypt.
- Autenticación JWT con vencimiento.
- Middleware de autorización por rol.
- Exclusión de contraseñas en respuestas de consulta de usuarios.

## 3. Archivos modificados

### Aplicación móvil

- `src/screens/auth/LoginScreen.js`: validación antes del envío y mensajes seguros.
- `src/context/AuthContext.js`: validación de la respuesta y clasificación segura de errores.

### API

- `backend/api_hospital/routes/auth.py`: validación estricta del cuerpo y error genérico.
- `backend/api_hospital/services/auth_service.py`: prevención de enumeración y eliminación de logs sensibles.
- `backend/api_hospital/tests/test_auth.py`: pruebas automatizadas del mecanismo.

## 4. Pruebas

| ID | Entrada o condición | Resultado esperado | Tipo |
|---|---|---|---|
| PS-01 | Cuerpo JSON malformado en `POST /api/v1/auth/login` | HTTP 400 con mensaje controlado; la API no genera error 500. | Automatizada |
| PS-02 | Contraseña de 73 caracteres | HTTP 400 y `AuthService.login` no se ejecuta. | Automatizada |
| PS-03 | Usuario inexistente | HTTP 401 con `Credenciales inválidas`; no revela si el usuario existe. | Automatizada |
| PS-04 | Usuario con espacios al inicio y al final | La API normaliza el usuario antes de autenticar. | Automatizada |
| PM-01 | Campos vacíos o fuera de límite en la pantalla móvil | La app bloquea el envío y muestra una alerta. | Manual |
| PM-02 | Respuesta exitosa sin token o usuario válido | La app no guarda la sesión y muestra un mensaje genérico. | Manual |

Las pruebas automatizadas se ejecutan con:

```bash
cd backend/api_hospital
python -m pytest tests/test_auth.py -v
```

GitHub Actions también ejecuta la suite completa de la API en cada pull request hacia `main`.

## 5. Criterio de aceptación

La implementación se considera aprobada cuando la suite de GitHub Actions termina correctamente y las dos pruebas manuales de la aplicación producen los resultados esperados sin mostrar contraseñas, tokens ni detalles internos.
