# PBL-33-T2 — Preparar guiones y registro UAT

**Historia:** PBL-33 — UAT con usuarios representativos  
**Sprint:** 3 (Azure Sprint 9)  
**Dependencia:** PBL-33-T1  
**Responsable:** Jaime  
**Fechas planificadas:** 2026-10-17 → 2026-10-18  
**Estado:** Completado

---

## 1. Objetivo

Crear guiones ejecutables y el formato de registro de resultados UAT, de forma que cada paso tenga resultado esperado/obtenido, fecha, versión, evidencia, observación y responsable.

## 2. Formato de registro de resultados (plantilla)

Usar una fila por paso o por decisión final del escenario.

| Campo | Descripción |
|-------|-------------|
| ID caso | CP-UAT-001 / CP-UAT-002 |
| Paso | Número de paso del guion |
| Acción del usuario | Qué debe hacer el usuario |
| Resultado esperado | Comportamiento o mensaje esperado |
| Resultado obtenido | Qué ocurrió realmente |
| Fecha / hora | Timestamp de la ejecución |
| Versión / ambiente | Identificador del incremento y ambiente |
| Evidencia | Captura, nota o referencia |
| Observación | Comentario libre del usuario o facilitador |
| Responsable | Quien registra |
| Decisión del escenario | Aprobado / Condicionado / Rechazado |

## 3. Guion CP-UAT-001 — Registrar turno completo (Enfermería)

**Módulo:** Enfermería  
**Escenario:** Registrar turno / valoración completa sin ayuda técnica  
**Precondición:** Usuario de rol Enfermería autenticado; paciente sintético disponible; ambiente UAT operativo.  
**Datos:** Caso clínico sintético (paciente de prueba con datos no reales).

| Paso | Acción del usuario | Resultado esperado |
|------|--------------------|--------------------|
| 1 | Iniciar sesión con credenciales de Enfermería | Acceso concedido; redirección al módulo permitido |
| 2 | Localizar y abrir el módulo de Enfermería / valoración de turno | Pantalla de registro visible y comprensible |
| 3 | Seleccionar o buscar el paciente sintético | Paciente encontrado y seleccionado |
| 4 | Completar los campos obligatorios del turno/valoración | Campos aceptan datos; validaciones claras si faltan datos |
| 5 | Guardar el registro | Confirmación de guardado; datos persistidos |
| 6 | Verificar que el registro aparece en el historial o consulta | Registro visible y coherente |
| 7 | Calificar textos, etiquetas y diseño (comprensibles / útiles) | Usuario emite calificación cualitativa |

**Resultado esperado global:** El usuario completa el escenario sin ayuda técnica sustancial y califica textos/diseño como comprensibles.

**Evidencia esperada:** Guion firmado + capturas + observaciones.

## 4. Guion CP-UAT-002 — Interpretar Analytics (Administración)

**Módulo:** Administración / Analytics  
**Escenario:** Interpretar indicadores y tomar una decisión  
**Precondición:** Usuario de rol Administración autenticado; indicadores conocidos cargados o disponibles.  
**Datos:** Indicadores conocidos (periodo, unidad y valores de referencia).

| Paso | Acción del usuario | Resultado esperado |
|------|--------------------|--------------------|
| 1 | Iniciar sesión con credenciales de Administración | Acceso concedido; módulo Analytics visible |
| 2 | Abrir la vista de Analytics correspondiente | Gráficas / KPIs visibles |
| 3 | Identificar el periodo representado | Usuario indica el periodo correctamente |
| 4 | Identificar la unidad de medida | Usuario indica la unidad correctamente |
| 5 | Explicar el significado de la gráfica / indicador | Explicación coherente con los datos |
| 6 | Formular una conclusión o decisión basada en el indicador | Conclusión lógica y accionable |
| 7 | Calificar claridad de textos, leyendas y diseño | Usuario emite calificación cualitativa |

**Resultado esperado global:** El usuario explica correctamente gráfica, periodo, unidad y conclusión.

**Evidencia esperada:** Acta + observaciones + capturas.

## 5. Plantilla de registro de ejecución (tabla lista para llenar)

### Ejecución CP-UAT-001

| Paso | Resultado obtenido | Fecha/hora | Versión | Evidencia | Observación | Responsable |
|------|--------------------|------------|---------|-----------|-------------|-------------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |

**Decisión del escenario:** ☐ Aprobado  ☐ Condicionado  ☐ Rechazado  
**Firma usuario representativo:** ________________  **Fecha:** ________  
**Firma facilitador / PO:** ________________  **Fecha:** ________

### Ejecución CP-UAT-002

| Paso | Resultado obtenido | Fecha/hora | Versión | Evidencia | Observación | Responsable |
|------|--------------------|------------|---------|-----------|-------------|-------------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |

**Decisión del escenario:** ☐ Aprobado  ☐ Condicionado  ☐ Rechazado  
**Firma usuario representativo:** ________________  **Fecha:** ________  
**Firma facilitador / PO:** ________________  **Fecha:** ________

## 6. Registro de defectos (si aparecen)

| ID defecto | Caso | Paso | Descripción | Severidad | Estado | Evidencia |
|------------|------|------|-------------|-----------|--------|-----------|
| DEF-UAT-xxx | CP-UAT-00x | n | … | Alta/Media/Baja | Abierto/Corregido/Cerrado | |

## 7. Definición de terminado (T2)

- Guiones documentados con pasos, resultados esperados y criterios.
- Formato de registro ejecutable (tablas listas).
- Plantilla de defectos disponible.
- Listo para preparación de datos y ambiente (T3).

---

**Documento generado para PBL-33-T2.**  
**Siguiente tarea:** PBL-33-T3 — Preparar datos y ambiente UAT.
