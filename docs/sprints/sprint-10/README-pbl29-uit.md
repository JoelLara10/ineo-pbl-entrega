# Sprint Azure 10 / PBL-29 — UIT y campaña UAT

**Historia:** Como usuario clínico, quiero que formularios y tableros sean probados en su interacción para capturar e interpretar información sin errores.

**Trabajo técnico:** Crear UIT para Enfermería, Estudios y Analytics (validación, teclado, gráficas y mensajes).

**Responsable principal:** Jaime Díaz  
**Revisor cruzado nominado:** Zahid  
**Rama de trabajo:** `feature/sprint-10-jaime` (partir de `develop`)

## Requisitos y casos

| ID | Módulo | Escenario | Herramienta | Automatizable |
|----|--------|-----------|-------------|---------------|
| CP-UIT-001 | Valoración de Enfermería | Completar y validar formulario | Vitest + RTL | Sí |
| CP-UIT-002 | Balance hídrico | Entradas/salidas y totales | Vitest + RTL | Sí |
| CP-UIT-003 | Cuidados de Enfermería | Crear / mensajes consistentes | Vitest + RTL | Sí |
| CP-UIT-004 | Analytics | Gráfica + tabla equivalente | Vitest + RTL | Sí |
| CP-S10-UAT-01 | Valoración comprensible | Localizar, registrar, consultar | Guion + Selenium | Sí (simulada) |
| CP-S10-UAT-02 | Lectura de Analytics | Interpretar unidad/periodo/total | Guion + Selenium | Sí (simulada) |
| CP-S10-UAT-03 | Recuperación de error | Fallo de red + reintento | Guion + Selenium | Sí (simulada) |
| CP-S10-UAT-04 | Aceptación del incremento | Acta PO / usuario real | Guion + Selenium | **Humana** |
| CP-S10-UI-05 | Contraste tema oscuro | Formularios claro/oscuro | Selenium + Chrome | Sí |

## Archivos de esta entrega

```
frontend/clinica-web-react/src/tests/pbl29-uit-enfermeria-analytics.test.jsx
qa/sprint-10/selenium/test_pbl29_uat.py
evidence/sprint-10/uit/
evidence/sprint-10/uat/
docs/sprints/sprint-10/README-pbl29-uit.md
```

## Comandos

```bash
# Dependencias (una vez)
cd frontend/clinica-web-react
npm ci

# Suite UIT (Vitest + React Testing Library)
npm test -- src/tests/pbl29-uit-enfermeria-analytics.test.jsx

# Cobertura opcional
npm run test:coverage -- src/tests/pbl29-uit-enfermeria-analytics.test.jsx
```

## Selenium / UAT

Las credenciales QA no están versionadas ni tienen valores predeterminados. Proporciónalas al proceso desde un gestor de secretos o variables locales del entorno; no las escribas en el repositorio, capturas, comandos registrados ni reportes. `INEO_USER` e `INEO_PASSWORD` son obligatorias. `INEO_ADMIN_USER` e `INEO_ADMIN_PASSWORD` son opcionales y solo se usan juntas para Analytics.

PowerShell:

```powershell
$env:INEO_BASE_URL = "http://127.0.0.1:5173"
$env:INEO_USER = Read-Host "Usuario de QA"
$securePassword = Read-Host "Contraseña de QA" -AsSecureString
$env:INEO_PASSWORD = [System.Net.NetworkCredential]::new("", $securePassword).Password
pytest qa/sprint-10/selenium/test_pbl29_uat.py -v --tb=short
Remove-Item Env:INEO_USER, Env:INEO_PASSWORD
Remove-Variable securePassword
```

El caso UI-05 emula la preferencia oscura de Chrome y comprueba que los controles visibles mantengan contraste WCAG AA (4.5:1) con el esquema claro forzado por la aplicación.

```bash
export INEO_BASE_URL=http://127.0.0.1:5173
export INEO_SCREENSHOT_DIR=evidence/sprint-10/uat/screenshots
read -r -p 'Usuario QA: ' INEO_USER
export INEO_USER
read -r -s -p 'Contraseña QA: ' INEO_PASSWORD
export INEO_PASSWORD
printf '\n'
pytest qa/sprint-10/selenium/test_pbl29_uat.py -v --tb=short
unset INEO_USER INEO_PASSWORD
```

## Datos sintéticos

- Atención: `AT-S10-001`
- Expediente: `EXP-S10-001`
- Usuario enfermería de demo: `enfermeria.test`
- Base de datos: **no** usar producción; preferir `ineo_test_s10` o instancia disposable.

## Evidencia obligatoria (estándar Azure #604)

Por cada caso:

1. Completar `Plantilla_Registro_Prueba_OftalCore.docx`
2. Capturas reales con pie explicativo
3. Reporte/log original sanitizado
4. SHA/build, ambiente, fecha (America/Mexico_City), ejecutor y revisor distinto
5. Estado real: Pendiente / En ejecución / Aprobado / Fallido / Bloqueado

Ruta sugerida:

```
evidence/sprint-10/CP-<ID>/ejecucion-YYYYMMDD-<build>/
```

## Notas de cierre

- UAT de agente se declara **simulada**; no sustituye aceptación humana del PO/usuario representativo (CP-S10-UAT-04).
- SIT con mocks no acredita integración real.
- No cerrar la historia sin Word por caso, capturas y revisión cruzada.
- Bloqueado ≠ Aprobado.
- Conservar defectos y repruebas sin borrar el fallo original.

## Tareas hijas

- **PBL-29-T6 (#585)** — Ampliar automatización y escenarios negativos (SAST + UAT-01)
- **PBL-29-T7 (#586)** — Ejecutar campaña y documentar aceptación (UAT-02/03/04 + UI-05)
