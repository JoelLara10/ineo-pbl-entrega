# Proceso de verificación de la API desplegada en Render

Se verificó la API existente https://api-clinica-jx4m.onrender.com mediante
nueve comprobaciones GET. Todas obtuvieron el código y contrato esperados.
Se conservó el despliegue actual durante la verificación.

## Proceso realizado

1. Se tomó como destino la URL de la API desplegada proporcionada por Zahid.
2. Se consultó `/health` para comprobar la respuesta de salud del servicio.
3. Se consultó `/ready` para verificar disponibilidad y conexión con MongoDB.
4. Se consultó la raíz `/` y se contrastó su respuesta HTTP.
5. Se consultaron cinco rutas protegidas sin credenciales para comprobar
   el rechazo de solicitudes no autenticadas.
6. Se consultó pacientes con un token inválido sintético para comprobar
   que el servicio rechazara esa credencial.
7. Se registraron los resultados originales en
   `evidence/sprint-11/zahid/revalidation/existing-api.json` y se incorporó
   la captura `screenshots/existing-api-validation.png` al informe.

## Resultados obtenidos

| Comprobación | Esperado | Obtenido |
|---|---|---|
| `/health` | 200 y estado correcto | Cumple |
| `/ready` | 200 y base de datos disponible | Cumple |
| `/` | 200 | Cumple |
| `/api/v1/patients` sin credenciales | 401 | 401 |
| `/api/v1/auth/me` sin credenciales | 401 | 401 |
| `/api/v1/medico` sin credenciales | 401 | 401 |
| `/api/v1/appointments/1/fluid-balance` sin credenciales | 401 | 401 |
| `/api/v1/analytics/dashboard` sin credenciales | 401 | 401 |
| `/api/v1/patients` con token inválido | 401 | 401 |

Resultado: nueve de nueve comprobaciones aprobadas. Estas verificaciones
acreditan salud, disponibilidad y protección de las rutas consultadas en
el momento de ejecución. Las pruebas funcionales autenticadas, de carga y
persistencia se ejecutaron en QA local y tienen evidencias independientes.

## Configuración versionada y revisión

Se revisaron `render.yaml`, el contexto `backend/api_hospital`, su Dockerfile,
el inicio con gunicorn y PORT, readiness y las variables declaradas sin exponer
secretos. El blueprint mantiene `autoDeployTrigger: off`. La configuración
local no identifica por sí sola el SHA interno del servicio remoto.

Jesús revisa la configuración, el proceso y sus resultados.
