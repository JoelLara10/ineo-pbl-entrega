# Actividad 15 - OftalCore móvil

Se reutiliza app-movil-clinica (React Native/Expo) y la API Flask/MongoDB del proyecto para consultar y registrar servicios remotos. La implementación móvil está en el repositorio https://github.com/JoelLara10/app-movil-clinica.

## Endpoints de QA

Base: `https://ineo-pbl-entrega.onrender.com/api/v1`.

- `POST /auth/login`: sesión remota.
- `GET /auth/me`: revalidación de sesión.
- `GET /catalog/services`: catálogo; requiere JWT.
- `POST /catalog/services`: registro; requiere JWT y rol admin.
- `POST /auth/logout`: revocación de sesión.

## Cambios de backend

La creación de servicios valida JSON, clave, descripción, costo, IVA y tipo antes de persistir. Rechaza valores negativos, no finitos y campos incompletos con HTTP 400; admite costo cero. Conserva la autenticación y autorización existentes.

## Evidencias

En `evidence/actividad15/` se incluyen resultados sanitizados y capturas de la ejecución web del cliente Expo. El registro de QA A15-EVIDENCIA-2410 fue recuperado mediante una consulta independiente (id_serv 4). No se incluyen credenciales ni JWT.

- 47 pruebas móviles aprobadas al preparar la publicación sobre develop.
- 42 pruebas API aprobadas: actividad 15, autenticación y seguridad.
- Los fallos de red ECONNREFUSED y HTTP 500 se provocaron de forma aislada con Axios real.
- QA respondió 200 para login, sesión y consulta; 400 para formulario incompleto y 401 sin JWT o con credenciales inválidas.
- La exportación Android inicial fue correcta. La ejecución funcional nativa continúa pendiente por fallo en la descarga de Expo Go; las capturas no se presentan como ejecución nativa.

## Flujo de integración

`feature/actividad15-servicios-remotos` → `develop` → `qa`, mediante PR y comprobaciones de CI. No se promueve a main. Se conserva el trabajo existente de QA y no se modifica el frontend web.

## Reproducción

Dentro de backend/api_hospital, con las dependencias de aplicación y prueba instaladas:

```sh
python -m pytest tests/test_activity15_services.py tests/test_auth.py tests/test_security_hardening.py -q
```

Dentro del repositorio móvil: `npm test`. La configuración QA ya utiliza HTTPS. Consultar `docs/actividad15.md` del repositorio móvil para ejecutar el módulo.
