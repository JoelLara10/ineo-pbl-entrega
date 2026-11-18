# Evidencia parcial de Sprint 11 — Joel

Fecha: 18/11/2026 (America/Mexico_City)
Historias: PBL-12 (#291, 5 puntos) y PBL-41 (#512, 4 puntos)
Capacidad de Joel en Sprint Azure 11: 9 puntos. Las tareas hijas no agregan puntos.

## Comprobaciones ejecutadas

| Verificación | Comando/entorno | Resultado observado |
|---|---|---|
| UT de tabla accesible y exportación de análisis | `npm run test -- --reporter=default --run src/tests/analysis-dashboard.test.jsx src/tests/analysis-tools.test.jsx` desde `frontend/clinica-web-react` | Aprobado: 2 archivos, 14 pruebas. |
| Compilación web | `npm run build` desde `frontend/clinica-web-react` | Aprobado: Vite compiló 220 módulos. |
| Pipeline Jenkins parcial | Job `OftalCore-Joel-Sprint11`, build #2 en `http://127.0.0.1:8081/job/OftalCore-Joel-Sprint11/2/` | Aprobado: 14 UT, build web y smoke HTTP de acceso público. El reporte JUnit y JSON del smoke están en `evidence/sprint-11/jenkins/build-2/`. SHA base: `a3cf99adf7c5258277c34f1ac4622fe0586edbc6`; Jenkins registró cambios locales sin commit. |
| OAT sintéticas | `test_oat_joel.py` y `test_oat_http_joel.py` ejecutadas localmente y en Jenkins build #3 | Aprobado: 10 casos. Jenkins build #3 terminó `SUCCESS`: `http://127.0.0.1:8081/job/OftalCore-Joel-Sprint11/3/`. JUnit en `evidence/sprint-11/jenkins/build-3/oat-synthetic.xml`. Incluye API HTTP y dependencia Mongo simulada; no demuestra restauración de Mongo real. |
| Pipeline versionado | Jenkins build #4 sobre commit `2664b3f32b91d55f74fff78e9c037db36b5819f8` | Aprobado: `SUCCESS` con 14 UT, 10 OAT, build web y smoke público QA/producción. Reportes JUnit y demás artefactos en `evidence/sprint-11/jenkins/build-4/`; SHA registrado por Jenkins igual al commit. |
| Selenium remoto | Selenium Grid `4.52.0-20261101` en el contenedor dedicado `oftalcore-selenium-sprint11`, puerto local 4444 | Aprobado: smoke y suite completa de 20 pruebas UI pasaron en Chrome 157. La aplicación y API fueron HTTP locales con datos sintéticos; no se usaron cuentas ni sistemas QA/producción. JUnit y capturas están en `evidence/sprint-11/selenium-local/selenium-remote-final.xml` y los PNG/JSON de cada caso. |
| Smoke público QA y producción | `ci/sprint11_public_smoke.py`, con `REQUESTS_CA_BUNDLE` del equipo | Aprobado: ambas URLs respondieron HTTP 200 y el HTML contiene el título OftalCore. Esto solo comprueba disponibilidad de la pantalla pública. |
| Jenkins previo / Selenium | `OftalCore-Joel-Demo`, build #12 | Fallido: 15 casos fallaron y 20 dieron error; Chrome reportó `tab crashed` / `session not created`. Es un fallo del navegador/agente en esa corrida y requiere reprueba antes de acreditar Selenium. |
| Selenium local de diagnóstico | Chrome/Edge/Firefox instalados en Windows | No utilizables en este equipo: los procesos de pestaña/gráficos se cierran incluso con una página mínima. Se resolvió ejecutando Selenium Chrome en un contenedor independiente, no cambiando los tests de producto. |

## Alcance y estado

Esta evidencia acredita las UT del módulo PBL-12, compilación, 10 OAT con dependencia sintética, Selenium UI (20 casos) en Docker y smoke de acceso público. No acredita SIT autenticada contra la API de QA, OAT con Mongo real, JMeter/Terraform, análisis SonarQube, promoción del artefacto probado ni UAT humana.

No se usaron credenciales ni se escribieron datos en producción o QA. El navegador local de Windows falla, pero el contenedor Selenium remoto permitió ejecutar la suite completa. La campaña aún requiere SIT autenticada web/API, OAT contra Mongo real, Terraform, JMeter, SonarQube, promoción del artefacto probado y UAT con el profesor. Mantener PBL-41-T4 (#589) y PBL-41-T5 (#590) abiertas mientras falte evidencia de sus criterios completos.
