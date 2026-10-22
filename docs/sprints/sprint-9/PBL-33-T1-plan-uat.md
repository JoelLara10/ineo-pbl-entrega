# PBL-33-T1 — Diseñar y documentar plan UAT

**Historia:** PBL-33 — UAT con usuarios representativos  
**Sprint:** 3 (Azure Sprint 9)  
**Tipo:** Usuario  
**Requisitos vinculados:** REQ-17, REQ-22  
**Responsable de documentación:** Jaime  
**Fechas planificadas:** 2026-10-15 → 2026-10-16  
**Estado:** Completado (documentación)

---

## 1. Objetivo

Definir el alcance, roles, ambiente, criterios de aceptación y escenarios del UAT del incremento disponible en Sprint 3 (Azure 9), de modo que solo se acepten funciones comprensibles y útiles según usuarios representativos.

## 2. Alcance del UAT

### Incluido (incremento disponible e integrado)

| Flujo | Módulo | Descripción |
|-------|--------|-------------|
| Acceso por rol | Autenticación / autorización | Login, redirección según rol, bloqueo de rutas no autorizadas |
| Registro de turno / valoración de Enfermería | Enfermería | Registro completo de turno/valoración sin ayuda técnica |
| Consulta e interpretación de Analytics | Administración | Visualización de indicadores, gráficas, periodo, unidad y toma de decisión |

### Excluido

- Funciones futuras no integradas en el incremento de Sprint 3.
- Módulos Médico, Estudios, Configuración avanzada y respaldos (fuera del alcance de este UAT).
- Pruebas de carga, seguridad profunda o automatización completa (solo UAT de usabilidad y comprensión).

## 3. Versión e identificación del incremento

| Campo | Valor |
|-------|--------|
| Rama de trabajo | `feature/sprint9` (sincronizada con `develop`) |
| Ambiente UAT | Ambiente de pruebas integrado (API + Web + MongoDB sintético) |
| Versión del incremento | Sprint 3 / Azure 9 — flujos de acceso, Enfermería y Analytics |
| Contrato API | `contracts/v1` (PBL-13) |
| Endpoints relevantes | Autenticación, Enfermería, Analytics (PBL-43) |
| Precondición de ambiente | PBL-26 (ambiente disponible) y comprobación integrada aprobada |

## 4. Roles y usuarios representativos

| Rol | Perfil representativo | Escenarios que ejecuta |
|-----|----------------------|------------------------|
| Enfermería | Usuario clínico con experiencia operativa | CP-UAT-001 (registro de turno) |
| Administración | Usuario de gestión / toma de decisiones | CP-UAT-002 (interpretación de Analytics) |
| Product Owner | Aceptación formal | Revisión de resultados y firma de acta |

Los usuarios representativos son personas distintas del equipo de desarrollo técnico que implementó las funciones bajo prueba.

## 5. Criterios de aceptación del UAT

1. Participan usuarios representativos de los roles acordados.
2. Cada escenario queda **aprobado**, **rechazado** o **condicionado** con evidencia.
3. Guiones documentados y pruebas realmente aplicadas.
4. Se registra: resultado esperado / obtenido, fecha, versión, defectos y acta de aceptación.
5. Solo se aceptan funciones que los usuarios califiquen como **comprensibles** y **útiles**.

## 6. Casos de prueba del catálogo (diseñados)

| ID | Tipo | Historia | Módulo | Escenario | Responsable | Estado |
|----|------|----------|--------|-----------|-------------|--------|
| CP-UAT-001 | UAT | PBL-33 | Enfermería | Registrar turno completo sin ayuda técnica | Jaime | Diseñado |
| CP-UAT-002 | UAT | PBL-33 | Administración | Interpretar Analytics y tomar una decisión | Jaime | Diseñado |

### CP-UAT-001 — Detalle

- **Precondición:** Sprint 3 (Azure 9); incremento identificado, integración verificada y ambiente UAT disponible.
- **Datos:** Caso clínico sintético.
- **Resultado esperado:** Usuario completa el escenario y califica textos/diseño como comprensibles.
- **Automatizable:** Parcial.
- **Evidencia esperada:** Guion firmado y observaciones.

### CP-UAT-002 — Detalle

- **Precondición:** Ambiente UAT.
- **Datos:** Indicadores conocidos.
- **Resultado esperado:** Usuario explica correctamente gráfica, periodo, unidad y conclusión.
- **Automatizable:** Parcial.
- **Evidencia esperada:** Acta y observaciones.

## 7. Criterios de decisión por escenario

| Decisión | Condición |
|----------|-----------|
| Aprobado | El usuario completa el flujo sin ayuda técnica sustancial y declara textos/diseño comprensibles y útiles. |
| Condicionado | El flujo se completa pero existen observaciones menores de usabilidad o claridad que no impiden el uso. |
| Rechazado | El usuario no puede completar el flujo o declara que la función no es comprensible/útil. |

## 8. Trazabilidad

| Elemento | Vinculación |
|----------|-------------|
| REQ-17 | UAT con usuarios representativos y registro de aceptación |
| REQ-22 | Trazabilidad requisito → caso de prueba → resultado → defecto → evidencia |
| PBL-33 | Historia de usuario principal |
| CP-UAT-001 / CP-UAT-002 | Casos de prueba del catálogo |
| PBL-33-T1 … T5 | Tareas de la historia |

## 9. Dependencias

- Historia y criterios de aceptación aprobados.
- Incremento integrado (acceso por rol, Enfermería, Analytics).
- Ambiente UAT disponible (PBL-26).
- Contratos y endpoints verificados (PBL-13, PBL-43).

## 10. Definición de terminado (T1)

- Alcance UAT documentado (incluido / excluido).
- Versión, roles, ambiente y criterios registrados.
- Casos de prueba del catálogo referenciados.
- Plan listo para elaborar guiones ejecutables (T2).

## 11. Riesgos

| Riesgo | Mitigación |
|--------|------------|
| Ambiente UAT inestable | Comprobación previa de precondiciones (T3) y bloqueo de sesión si falla. |
| Usuarios no disponibles | Agenda anticipada; roles representativos definidos. |
| Alcance difuso | Exclusión explícita de funciones futuras. |

---