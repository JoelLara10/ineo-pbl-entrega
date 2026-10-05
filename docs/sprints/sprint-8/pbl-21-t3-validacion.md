# PBL-21-T3 — Validación de criterios

**Historia:** PBL-21  
**Tarea:** T3 — Pruebas funcionales y de regresión  
**Rama limpia:** `fix/jaime-sprint-2-clean`
**Fecha:** 2026-10-04  
**Responsable:** Jaime Díaz González  

---

## 1. Criterio de aceptación

> Conserva todas sus funciones y validaciones; visualmente sigue el patrón aprobado de enfermería.

---

## 2. Pruebas funcionales

| # | Prueba | Pasos | Resultado esperado | OK |
|---|---|---|---|---|
| 1 | Abrir valoración | Login enfermería → paciente → Valoración | Header + labels + botones estilo enfermería | ☑ |
| 2 | Guardar | Llenar campos → Guardar | Alert de éxito + historial actualizado | ☑ |
| 3 | Historial | Ver registros previos | Cards con fecha y datos | ☑ |
| 4 | Sin paciente | Entrar sin atención seleccionada | Mensaje de aviso; guardar deshabilitado | ☑ |
| 5 | Móvil | DevTools ~375px de ancho | Campos apilados, sin desbordes graves | ☑ |
| 6 | Regresión Signos vitales | Abrir Signos vitales | Misma familia visual (sin rotura) | ☑ |
| 7 | Regresión Nota | Abrir Nota de enfermería | Sin regresión | ☑ |

---

## 3. Evidencia

La evidencia reproducible es `src/tests/pbl21-nursing-assessment.test.jsx`: monta el componente con un paciente sintético, consulta el historial, captura campos y verifica el `POST` completo. La suite, lint y build se ejecutan en CI sin utilizar información real de pacientes.

---

## 4. Definición de terminado

- [x] Pruebas 1–7 ejecutadas
- [x] Evidencia automatizada y reproducible adjunta
- [x] Prueba automatizada `pbl21-nursing-assessment.test.jsx`
- [x] Criterio de aceptación cumplido
