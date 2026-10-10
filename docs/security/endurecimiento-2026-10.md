# Endurecimiento de seguridad — octubre de 2026

## Controles incorporados

- Límite de cinco intentos de inicio por usuario e IP durante quince minutos.
- Respuestas genéricas para evitar enumeración de usuarios.
- Costo bcrypt también para usuarios inexistentes.
- JWT con `jti`, emisor, audiencia, expiración y fecha de activación obligatorios.
- Revocación del token al cerrar sesión.
- Rol actualizado desde la base en cada petición autenticada.
- Contraseñas nuevas de al menos 12 caracteres, con mayúscula, minúscula y número.
- Impedimento para que un administrador elimine o desactive su propia cuenta.
- CORS definido por variable de entorno y sin credenciales cross-origin.
- Solicitudes limitadas a 1 MiB por defecto.
- Encabezados HTTP defensivos en Flask y Vercel.
- Registro de rutas sin query strings.
- Dependencias web y Python actualizadas a versiones sin avisos conocidos.
- Pipeline para `npm audit`, `pip-audit` y Bandit.

## Variables obligatorias de producción

```dotenv
SECRET_KEY=<valor-aleatorio-de-al-menos-32-caracteres>
CORS_ORIGINS=https://clinica-ocular-ten.vercel.app
DEBUG=False
MAX_CONTENT_LENGTH=1048576
LOGIN_MAX_ATTEMPTS=5
LOGIN_WINDOW_SECONDS=900
```

QA debe usar secretos, URL, API y base de datos diferentes de producción.

## Verificación local

- Backend: 179 pruebas aprobadas; 7 pruebas Spark opcionales omitidas.
- Frontend: 76 pruebas aprobadas; i18n, lint y build aprobados.
- `npm audit`: cero vulnerabilidades conocidas.
- `pip-audit`: cero vulnerabilidades conocidas.
- Bandit: sin hallazgos de severidad media o alta en el código ejecutable analizado.

## Riesgo arquitectónico pendiente

El token permanece en `localStorage`. La CSP y la ausencia de HTML dinámico reducen
el riesgo, pero una migración futura a cookies `HttpOnly`, `Secure` y `SameSite`
ofrecería una defensa más fuerte frente a robo de token por XSS. Este cambio requiere
rediseñar de forma coordinada la autenticación web y móvil, por lo que no debe
aplicarse como una modificación aislada.
