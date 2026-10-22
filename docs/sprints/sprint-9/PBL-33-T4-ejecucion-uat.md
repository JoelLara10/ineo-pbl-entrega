# PBL-33-T4 — Aplicar UAT con usuarios representativos

**Historia:** PBL-33 — UAT con usuarios representativos  
**Sprint:** 3 (Azure Sprint 9)  
**Dependencia:** PBL-33-T3 (GO de precondiciones)  
**Responsable:** Jaime   
**Fechas planificadas:** 2026-10-20 → 2026-10-22  
**Estado:** Sesión original en Word; revalidación simulada completada el 22/10/2026.

Los registros vacíos de abajo se conservan como plantilla. Los resultados reales de Jaime están en `PBL-33-Plantillas-Registro-UAT.docx`. La revalidación solicitada por Joel fue ejecutada por Codex simulando los roles, sin participantes humanos nuevos.

| Caso | Resultado de la revalidación simulada | Evidencia |
|---|---|---|
| CP-UAT-001 | Aprobado en simulación: login, paciente sintético, campos obligatorios, rechazo de dolor 11, guardado con dolor 2 y consulta persistente | `Correccion-UAT-Simulada-Sprint9.pdf`; `evidence/sprint-9-jaime-fix/simulation.json` |
| CP-UAT-002 | Aprobado en simulación: unidades explícitas, explicación desplegable, cuatro vistas, periodo de seis días y comparación de 4 contra 4 atenciones | Mismo informe y capturas nuevas |

La interpretación simulada identifica 0 % de cambio en el conteo y propone revisar distribución por fecha y área antes de concluir que la carga fue igual. La calificación de claridad del agente no reemplaza una opinión humana representativa.

---

## 1. Objetivo

Ejecutar los guiones CP-UAT-001 y CP-UAT-002 con usuarios representativos; registrar resultados, capturas y defectos; corregir y reejecutar escenarios fallidos cuando proceda.

## 2. Condiciones de la sesión

| Campo | Valor |
|-------|--------|
| Fecha(s) de sesión | (rellenar) |
| Ambiente | UAT — versión del incremento Sprint 3 / Azure 9 |
| Facilitador | Jaime |
| Usuarios representativos | (nombre / rol) |


## 3. Ejecución CP-UAT-001 — Enfermería

**Usuario representativo:** ________________ (rol Enfermería)  
**Fecha/hora inicio:** ________  
**Versión / commit:** ________

| Paso | Acción | Resultado obtenido | Evidencia | Observación |
|------|--------|--------------------|-----------|-------------|
| 1 | Login rol Enfermería | | | |
| 2 | Abrir módulo Enfermería / valoración | | | |
| 3 | Seleccionar paciente sintético | | | |
| 4 | Completar campos obligatorios | | | |
| 5 | Guardar registro | | | |
| 6 | Verificar historial / consulta | | | |
| 7 | Calificación de textos y diseño | | | |

**¿Completó el escenario sin ayuda técnica sustancial?** ☐ Sí  ☐ No  

**Calificación de comprensibilidad / utilidad (usuario):**  
☐ Comprensible y útil  ☐ Parcialmente comprensible  ☐ No comprensible / no útil  

**Observaciones del usuario:**  
_______________________________________________  

**Defectos detectados:**  
| ID | Descripción | Severidad | Acción |
|----|-------------|-----------|--------|
| | | | |

**Decisión del escenario:** ☐ Aprobado  ☐ Condicionado  ☐ Rechazado  

**Firma usuario:** ________________  **Fecha:** ________  
**Firma facilitador:** ________________  **Fecha:** ________

---

## 4. Ejecución CP-UAT-002 — Analytics (Administración)

**Usuario representativo:** ________________ (rol Administración)  
**Fecha/hora inicio:** ________  
**Versión / commit:** ________

| Paso | Acción | Resultado obtenido | Evidencia | Observación |
|------|--------|--------------------|-----------|-------------|
| 1 | Login rol Administración | | | |
| 2 | Abrir Analytics | | | |
| 3 | Identificar periodo | | | |
| 4 | Identificar unidad | | | |
| 5 | Explicar gráfica / indicador | | | |
| 6 | Formular conclusión / decisión | | | |
| 7 | Calificación de claridad | | | |

**¿Explicó correctamente gráfica, periodo, unidad y conclusión?** ☐ Sí  ☐ No  

**Calificación de comprensibilidad / utilidad (usuario):**  
☐ Comprensible y útil  ☐ Parcialmente comprensible  ☐ No comprensible / no útil  

**Observaciones del usuario:**  
_______________________________________________  

**Defectos detectados:**  
| ID | Descripción | Severidad | Acción |
|----|-------------|-----------|--------|
| | | | |

**Decisión del escenario:** ☐ Aprobado  ☐ Condicionado  ☐ Rechazado  

**Firma usuario:** ________________  **Fecha:** ________  
**Firma facilitador:** ________________  **Fecha:** ________

---

## 5. Reejecuciones (si hubo rechazo o condición que requiera corrección)

| Caso | Iteración | Fecha | Resultado | Observación |
|------|-----------|-------|-----------|-------------|
| CP-UAT-001 | 2 | | | |
| CP-UAT-002 | 2 | | | |

## 6. Resumen de defectos de la sesión

| ID defecto | Caso | Severidad | Estado al cierre de sesión | Evidencia |
|------------|------|-----------|----------------------------|-----------|
| | | | | |

## 7. Definición de terminado (T4)

- Guiones ejecutados con usuarios representativos de los roles acordados.
- Resultados, capturas y defectos registrados.
- Escenarios fallidos corregidos y reejecutados cuando procedió.
- Listo para consolidar informe y acta (T5).

---

**Documento generado para PBL-33-T4.**  
**Siguiente tarea:** PBL-33-T5 — Documentar resultados y acta UAT.
