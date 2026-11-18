# Sprint 11 — verificación local de controles CI y evidencia

Fecha: 18/11/2026 (America/Mexico_City)  
Rama: `codex/sprint-11-joel`  
Alcance: CP-S11-CI-02 y CP-S11-CI-05 (controles locales); no equivale a despliegue QA ni aprobación de revisor.

## Ejecuciones observadas

| Control | Evidencia | Resultado |
|---|---|---|
| Helpers del manifiesto y validador | `python -m unittest discover -s ci -p test_sprint11_helpers.py -v` | 4 pruebas aprobadas. Incluye copia íntegra, detección de alteración, paquete completo de fixture y rechazo de paquete incompleto. |
| UT frontend PBL-12 | Vitest: `analysis-dashboard.test.jsx`, `analysis-tools.test.jsx` | 14 pruebas aprobadas en dos archivos. |
| OAT API | Pytest: `test_oat_joel.py`, `test_oat_http_joel.py` | 10 pruebas aprobadas; API/DB sintéticas, no QA real ni Mongo persistente. |
| Build web | `npm run build` | Vite compiló 220 módulos. |
| Integridad de copia | `ci/sprint11_artifact.py manifest` + `copy-verify` sobre `frontend/clinica-web-react/dist` | Manifiesto SHA-256 de 86 archivos; la copia local simulada coincidió. |

## Cambios incorporados

- `ci/sprint11_artifact.py`: crea y verifica manifiesto SHA-256, con copia local para simular promoción.
- `ci/validate_sprint11_evidence.py`: exige ocho carpetas de caso, un Word DOCX estructuralmente válido, PNG válido, resultado XML/JSON y `result.txt` por caso.
- `ci/test_sprint11_helpers.py`: pruebas para el hash y el validador.
- `ci/Jenkinsfile-sprint11`: agrega la copia local verificada y una etapa opcional para validar un paquete real cuando se indique `EVIDENCE_PACKAGE_DIR`.

## Límites de esta evidencia

Las fixtures de las pruebas del validador son archivos sintéticos usados solo para comprobar el comportamiento del script; no son actas, capturas ni resultados de ejecución de los casos del Sprint 11. La etapa del nuevo Jenkinsfile aún debe ejecutarse en el job para acreditar el cambio dentro de Jenkins. La copia `qa-promotion-simulation` es local y no publica a Vercel. No se ejecutó SIT autenticada contra QA, OAT con Mongo real, rollback, interrupción de la base de QA, JMeter, SonarQube ni UAT humana. Los casos que dependen de esos entornos/personas no deben cerrarse con esta evidencia.
