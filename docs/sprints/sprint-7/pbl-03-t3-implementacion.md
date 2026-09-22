# PBL-03-T3 — Implementación del flujo clínico

**Historia:** PBL-03  
**Tarea:** T3 — Programar ejecución, consulta de estado y carga del resultado clínico  
**Diseño de referencia:** `docs/sprints/sprint-7/pbl-03-t2-diseno-flujo-clinico.md`  
**Fecha:** 22 de septiembre de 2026  
**Responsable:** Jaime Díaz González  
**Rama:** `feature/pbl-03-analisis-clinico`

## Alcance implementado

- Job asíncrono solo para `clinical`.
- Contrato `POST /api/v1/spark/run/clinical`, `GET /status/clinical`, `GET /clinical`, `GET /overview`.
- Estados `pending`, `processing`, `completed`, `failed`.
- Datos reales vía `AnalyticsService.get_clinical_analytics()`.
- Ajuste de UI: `pending` ya no se pinta como procesando.
- Pruebas API CL-01 a CL-12.

## Fuera de esta tarea (T4)

- Ruta `/admin/spark/clinical` para rol `medico` en React.
- Claves i18n `spark.states.pending` y `spark.states.completed`.
- Actualización de `docs/manual-tecnico/spark.md` y evidencias visuales.

## Cómo verificar

```bash
cd backend/api_hospital
pytest -v tests/test_spark_clinical.py tests/test_auth.py tests/test_patients.py

cd ../../frontend/clinica-web-react
npm test
```
