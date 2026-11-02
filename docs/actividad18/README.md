# Actividad 18 API y compatibilidad web

Se conserva GET y POST /api/v1/appointments/{id_atencion}/nursing-notes y sus respuestas existentes. POST ahora rechaza JSON inválido, nota vacía, tipos distintos de cadena y más de 5000 caracteres con HTTP 400, antes de crear el registro. Se conservan JWT, autorización por rol y HTTP 404 para atención inexistente.

Pruebas: tests/test_activity18_sync.py verifica consulta-creación-consulta, persistencia por atención, límites, ausencia de sesión, rol incorrecto y HTTP 500 seguro. frontend/clinica-web-react/src/tests/activity18-notes.test.jsx verifica que la web mantiene el contrato, consulta tras guardar, bloquea datos vacíos y conserva borradores ante errores.

Validación local: 59 pruebas API aprobadas, 1 omitida en Windows; 187 pruebas web aprobadas y vite build correcto. Ver docs/actividad18 del repositorio móvil para registros de ejecución y alcance de demostración.

Demostración aislada: python ci/demo_api.py --ready-file ready.json --port 5001 --activity18. Usa MongoMock y cuentas sintéticas de testing/seed.py, sin conexión a MongoDB externo. Las notas y el login se procesan en las rutas reales de Flask. Los datos de la demostración desaparecen al apagar el proceso. Este comando es de prueba y no configura la nube QA.

Destino de revisión: qa. Publicar la rama no despliega automáticamente este cambio.
