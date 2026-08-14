# Manual técnico — Seguridad

**Sistema:** INEO — Flask, MongoDB y React  
**Sprint:** 5 — Calidad, Seguridad y Spark  
**Responsable:** Jesús  
**Fecha de revisión:** 14 de agosto de 2026

## 1. Objetivo

Documentar los controles de seguridad observados, sus límites y las acciones necesarias para proteger información clínica, cuentas y archivos del sistema INEO.

## 2. Controles implementados

| Control | Implementación observada |
|---|---|
| Contraseñas | Hash con `bcrypt` |
| Autenticación | JWT firmado con HS256 |
| Vigencia | Token con expiración de 8 horas |
| Autorización | Decoradores `token_required` y `role_required` |
| Transporte del token | `Authorization: Bearer <token>` |
| CORS | Lista de orígenes desde configuración |
| Respuestas | Errores 401, 403, 404 y 500 en JSON |
| Datos de usuarios | Consultas excluyen el campo `password` |
| Respaldos | Validación de nombres y rutas de archivos |

## 3. Flujo de autenticación

1. React envía usuario y contraseña a `/api/v1/auth/login`.
2. La API localiza la cuenta y verifica el hash con bcrypt.
3. Se genera un JWT con `user_id`, `username`, `role`, `iat` y `exp`.
4. React guarda token y usuario en `localStorage`.
5. El interceptor Axios agrega el encabezado Bearer.
6. Una respuesta 401 elimina la sesión local.

## 4. Roles

El backend debe ser la fuente definitiva de autorización. Ocultar un botón en React no sustituye `role_required`.

| Rol | Alcance general |
|---|---|
| `admin` | Configuración, respaldos y administración global |
| `administrativo` | Pacientes, atenciones, cargos y pagos |
| `medico` | Historia, notas, diagnósticos, recetas y solicitudes |
| `enfermero` | Registros de Enfermería autorizados |
| `estudios` | Carga y edición de resultados |

Debe normalizarse el uso de `enfermero` y `enfermeria`, porque una diferencia entre frontend y API puede causar accesos rechazados o políticas inconsistentes.

## 5. Riesgos identificados

### Críticos o altos

- `SECRET_KEY` y `JWT_SECRET_KEY` contienen valores predeterminados en el código. Producción debe fallar al iniciar si faltan secretos robustos.
- `DEBUG` utiliza `True` como valor predeterminado al ejecutar `app.py`. Debe ser `False` en producción.
- El token permanece en `localStorage`; una vulnerabilidad XSS podría exponerlo.
- Algunas rutas PDF aceptan el token en la cadena de consulta. Los tokens en URL pueden quedar en historial, registros o encabezados de referencia.

### Medios

- No se observa limitación de intentos en el inicio de sesión.
- Los mensajes y `print` de autenticación distinguen usuario inexistente y contraseña incorrecta; esto facilita enumeración y genera registros innecesarios.
- No existe una política de complejidad visible para contraseñas nuevas.
- No se observa una suite automática que recorra todas las rutas y compruebe permisos.
- Debe verificarse que los archivos de Estudios validen extensión, MIME, tamaño y nombre seguro.

## 6. Medidas requeridas antes de producción

1. Eliminar secretos predeterminados y cargar valores aleatorios desde un gestor seguro.
2. Desactivar depuración y usar un servidor WSGI de producción.
3. Restringir CORS a dominios HTTPS exactos.
4. Unificar el mensaje de credenciales inválidas y retirar contraseñas de logs.
5. Implementar limitación de intentos y auditoría de accesos.
6. Evitar tokens en URL; descargar archivos mediante solicitudes autenticadas y blobs.
7. Aplicar validación estricta a cargas y guardarlas fuera de rutas ejecutables.
8. Definir rotación, revocación y renovación de sesiones.
9. Cifrar respaldos y restringir permisos del directorio.
10. Probar autorización negativa para cada endpoint sensible.

## 7. Protección de datos

- No versionar `.env`, bases, respaldos, `uploads/`, resultados ni datos reales.
- Usar información ficticia en desarrollo y evidencias.
- Aplicar mínimo privilegio a cuentas MongoDB y del sistema operativo.
- Mantener bitácoras de acceso, cambio y eliminación sin registrar contenido clínico innecesario.
- Definir retención y eliminación segura conforme a la política institucional aplicable.

## 8. Validación de entradas

La API contiene validaciones para campos requeridos y utilidades de CURP, correo, teléfono, fechas y sanitización de texto. Sin embargo, la validación del frontend solo mejora la experiencia; cada ruta de escritura debe validar tipo, longitud, rango y formato nuevamente en el servidor.

Para MongoDB, no deben aceptarse operadores proporcionados por el cliente dentro de filtros. Los identificadores deben convertirse mediante tipos controlados y las proyecciones deben excluir secretos.

## 9. Lista de comprobación

- [ ] Secretos sin valores predeterminados.
- [ ] `DEBUG=False` en producción.
- [ ] HTTPS activo.
- [ ] CORS limitado.
- [ ] Rate limiting en login.
- [ ] Tokens fuera de URL.
- [ ] Permisos probados por rol.
- [ ] Archivos validados por tipo y tamaño.
- [ ] Respaldos cifrados y restauración probada.
- [ ] Dependencias revisadas y actualizadas.
- [ ] Logs sin credenciales ni expedientes completos.

## 10. Criterio de aceptación

La seguridad se considera aceptable para despliegue únicamente después de corregir los riesgos altos, ejecutar pruebas negativas de todas las rutas sensibles y documentar la configuración real del ambiente. Este documento no certifica el sistema ni reemplaza una auditoría especializada.

