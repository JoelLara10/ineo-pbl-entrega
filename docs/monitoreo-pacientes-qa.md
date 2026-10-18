# Monitoreo de pacientes: integración y prueba en QA

Rama: `feature/monitoreo-pacientes`, creada desde `develop`. API y web están en INEO; el móvil utiliza la misma API mediante sus servicios autenticados.

## Funcionalidad

- Expedientes existentes (`pacientes.Id_exp`), sin duplicar los pacientes de la simulación.
- Roles `admin`, `medico`, `enfermero` y `enfermeria`: lista, detalle, lecturas, historial y reconocimiento de alertas. Solo admin provisiona dispositivos.
- HR, SpO₂, movimiento, posible caída y temperatura del sensor MPU (no temperatura corporal).
- Caídas independientes de los signos vitales, persistencia MongoDB y una alerta pendiente por dispositivo/tipo para evitar duplicados.
- La web y el móvil actualizan cada 10 segundos mientras la pantalla está activa. No hay notificaciones push con la aplicación cerrada.
- Lecturas y conexión se consideran desactualizadas después de 30 segundos. Sin contacto se guardan pulso y SpO₂ como null.

## API

Todas las rutas clínicas usan `Authorization: Bearer <JWT>` y los permisos existentes.

| Método | Ruta relativa a `/api/v1` | Uso |
| --- | --- | --- |
| GET | `/monitoring/patients` | Primeros 100 expedientes, orden descendente |
| GET | `/monitoring/patients/{Id_exp}` | Detalle, alertas pendientes y últimas 50 lecturas |
| POST | `/monitoring/devices` | Admin: `{device_id, patient_id}`; devuelve credencial una sola vez |
| PATCH | `/monitoring/alerts/{id}/acknowledge` | Reconocimiento idempotente con usuario y fecha |
| POST | `/monitoring/data` | Dispositivo: header `X-Device-Token`, JSON con `device_id` y medición |

Provisionar otra vez el mismo dispositivo/paciente rota la credencial y revoca la anterior. No permite reasignarlo a otro paciente ni asociar un segundo dispositivo al mismo expediente. El hash de la credencial no se devuelve en consultas.

Ejemplo de medición: `{ "device_id": "QA-ESP32", "heart_rate": 75, "spo2": 98, "movement": false, "fall": false, "finger_detected": true, "temperature": 28, "acceleration": 1 }`.

Ejemplo de caída sin signos vitales: `{ "device_id": "QA-ESP32", "type": "fall", "event_id": "fall-qa-1" }`. Usar el mismo `event_id` al reintentar la misma caída evita recrearla incluso después de reconocerla.

## Socket.IO del ESP32

Se conserva `/socket.io/` con Engine.IO 4 y los eventos `register_wearable`, `wearable_data`, `wearable_fall_alert`. El registro debe incluir `device_id`, `patient_id` (expediente numérico real) y `device_token`. El servidor confirma el registro con `wearable_registered` y la persistencia mediante `wearable_data_received` o `wearable_fall_alert_received`.

La configuración y firmware de `WearableINEO` NO se modificaron. En una etapa posterior se debe cambiar la URL a QA (WSS/HTTPS fuera de red local), el expediente y agregar la credencial al registro. El firmware actual no envía esa credencial y aún no conserva alertas pendientes durante desconexiones. No afirmar entrega garantizada del hardware hasta implementar cola/reintentos y probarlos físicamente.

## Prueba QA

1. Instalar los requisitos API, configurar MongoDB QA, SECRET_KEY y CORS para la web QA; iniciar con `python app.py` o Gunicorn (un worker con threads, según Procfile/Dockerfile).
2. Configurar la URL de API de la web y del móvil conforme a sus `.env.example`; iniciar sesión con admin, médico o enfermería. Abrir Monitoreo de pacientes.
3. Asociar un dispositivo QA a un expediente existente como admin y guardar la credencial mostrada una sola vez. No usar expedientes o datos reales en la prueba.
4. PowerShell, desde `backend/api_hospital`:

```powershell
$env:MONITORING_DEVICE_TOKEN = '<credencial del dispositivo QA>'
python scripts/simulate_monitoring.py --api-url http://localhost:5001/api/v1 --device-id QA-ESP32 --scenario normal
python scripts/simulate_monitoring.py --api-url http://localhost:5001/api/v1 --device-id QA-ESP32 --scenario fall --event-id fall-qa-1
python scripts/simulate_monitoring.py --api-url http://localhost:5001/api/v1 --device-id QA-ESP32 --scenario low-spo2
python scripts/simulate_monitoring.py --api-url http://localhost:5001/api/v1 --device-id QA-ESP32 --scenario no-contact
```

5. Verificar caída en ambas vistas, repetir el mismo evento (sin duplicado), reconocerlo en una vista y comprobar que desaparece de pendientes en la otra. Esperar 30 segundos sin enviar datos y verificar desactualización.
6. Validar 401 sin sesión/credencial, 403 con rol no clínico y rechazo de datos inválidos. Las pruebas automatizadas usan mongomock y datos sintéticos; no acceden a Atlas.

Los umbrales `MONITORING_HEART_RATE_MIN=50`, `MONITORING_HEART_RATE_MAX=120`, `MONITORING_SPO2_MIN=92` son valores de demostración configurables. Deben acordarse y validarse antes de uso clínico. Los registros automáticos no sustituyen los signos vitales tomados y registrados por personal de enfermería.

## Límites de esta entrega

No despliega ni fusiona develop/main. No configura ni flashea ESP32. No incorpora GPS al firmware, push móvil ni cola offline del dispositivo. La lista se limita a 100 pacientes y el historial a 50 lecturas; añadir paginación antes de ampliar ese volumen.


