# PBL-33 — UAT con usuarios representativos (Sprint 3 / Azure 9)

## Resultado actualizado del 22 de octubre de 2026

Los Word originales registran la sesión de Jaime del 21/10: CP-UAT-001 aprobado y CP-UAT-002 condicionado. Se conservan como evidencia histórica.

Por petición explícita de Joel se ejecutó una revalidación **simulada por Codex**, usando Enfermería y Administración con datos sintéticos en MongoDB local aislado. Se corrigieron la valoración vacía, los formatos inválidos, la identificación de unidades y la densidad de texto de las gráficas. Los dos escenarios simulados pasaron. Esto no crea una nueva firma ni aprobación humana.

Informe vigente con capturas: [Corrección y UAT simulada](./Correccion-UAT-Simulada-Sprint9.pdf). Resultados y pasos reproducibles: `evidence/sprint-9-jaime-fix/`. El informe `Revision-Jaime-UAT-Sprint9.pdf` corresponde al diagnóstico previo a la corrección.

**Historia de usuario:** Como Product Owner, quiero realizar UAT con usuarios representativos para aceptar únicamente funciones comprensibles y útiles.

**Trabajo técnico:** Plan de pruebas — documentar guiones UAT del incremento disponible, comprobar la integración de sus flujos, aplicar pruebas con usuarios representativos, registrar defectos y emitir acta en Sprint 3.

**Tipo:** Usuario  
**Trazabilidad Excel:** REQ-17, REQ-22  
**Casos de prueba:** CP-UAT-001, CP-UAT-002  
**Fechas planificadas Gantt:** 2026-10-15 → 2026-10-22  

---

## Documentos de la historia (5 tareas)

| Tarea | Archivo | Fechas planificadas | Descripción |
|-------|---------|---------------------|-------------|
| T1 | [PBL-33-T1-plan-uat.md](./PBL-33-T1-plan-uat.md) | 15–16 oct | Diseñar y documentar plan UAT (alcance, roles, criterios) |
| T2 | [PBL-33-T2-guiones-registro-uat.md](./PBL-33-T2-guiones-registro-uat.md) | 17–18 oct | Guiones ejecutables y formato de registro |
| T3 | [PBL-33-T3-preparacion-ambiente-uat.md](./PBL-33-T3-preparacion-ambiente-uat.md) | 19 oct | Datos sintéticos, precondiciones y GO/NO-GO |
| T4 | [PBL-33-T4-ejecucion-uat.md](./PBL-33-T4-ejecucion-uat.md) | 20–22 oct | Ejecución con usuarios representativos |
| T5 | [PBL-33-T5-acta-uat.md](./PBL-33-T5-acta-uat.md) | 22–23 oct | Informe, defectos y acta de aceptación |

## Definición de terminado (historia)

- Participan usuarios representativos de los roles acordados.
- Cada escenario queda aprobado, rechazado o condicionado con evidencia.
- Guiones documentados y pruebas realmente aplicadas.
- Resultado esperado/obtenido, fecha, versión, defectos y acta de aceptación registrados.

Tras la sesión real con usuarios, completar las tablas de resultados en T4 y la firma del acta en T5.

## Responsable

Jaime (casos CP-UAT-001 y CP-UAT-002; facilitación UAT).
