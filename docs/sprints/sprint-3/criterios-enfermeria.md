# Criterios de aceptación — Módulo de Enfermería

**Proyecto:** Sistema de Gestión Clínica INEO  
**Sprint:** 3 — Enfermería  
**Responsable:** Jesús  
**Historias:** ENF-001 a ENF-009

## 1. Objetivo del Sprint

Integrar un módulo de Enfermería que permita localizar pacientes con atenciones activas, consultar su información e incorporar registros clínicos trazables desde una interfaz protegida por roles.

## 2. Definición de terminado general

Una historia se considera terminada cuando:

- El frontend tiene una ruta funcional y accesible para el rol autorizado.
- La API valida token, rol, atención y cuerpo recibido.
- Los datos se almacenan en MongoDB con atención, expediente, responsable y fecha.
- El historial recupera solamente los datos de la atención solicitada.
- La interfaz muestra estados de carga, éxito, error y ausencia de datos.
- No se incluyen secretos, datos reales ni archivos generados en Git.
- La operación se prueba con información ficticia.

## 3. Matriz de historias

| Historia | Funcionalidad | Evidencia principal |
|---|---|---|
| ENF-001 | Acceso y panel de Enfermería | Pacientes agrupados por área |
| ENF-002 | Selección y detalle del paciente | Expediente, atención, cama y alertas |
| ENF-003 | Signos vitales | Captura e historial |
| ENF-004 | Notas de Enfermería | Nota asociada al profesional |
| ENF-005 | Medicamentos | Lista de administraciones |
| ENF-006 | Valoración | Estado, dolor, movilidad y riesgos |
| ENF-007 | Balance hídrico | Ingresos, egresos y balance calculado |
| ENF-008 | Cuidados de Enfermería | Diagnóstico, plan, evaluación y estado |
| ENF-009 | Historial, seguridad y trazabilidad | Registros aislados por atención |

## 4. ENF-001 — Panel de Enfermería

**Como** personal de Enfermería, **quiero** visualizar pacientes por área **para** identificar las atenciones que debo atender.

### Criterios

- Dado un usuario autenticado con rol permitido, cuando abre `/enfermeria`, entonces puede ver el panel.
- El panel consulta `GET /api/v1/medico`.
- La respuesta se organiza en Consulta, Urgencias y Hospitalizados.
- Cada lugar indica si está libre u ocupado.
- Los pacientes ocupados muestran expediente y atención suficientes para continuar.
- Una cama libre no abre un detalle inexistente.
- El usuario puede actualizar la información.
- Si la API falla, se muestra un error sin cerrar inesperadamente la aplicación.
- La paginación no pierde ni duplica pacientes.

## 5. ENF-002 — Detalle del paciente

**Como** personal de Enfermería, **quiero** confirmar la identidad y atención del paciente **para** registrar información en el expediente correcto.

### Criterios

- El detalle recibe `id_atencion` e `Id_exp`.
- Consulta `GET /api/v1/paciente/{id_atencion}/{Id_exp}`.
- Muestra nombre, expediente, atención, área, cama, motivo y alergias.
- Presenta familiar y médicos cuando existan.
- Conserva el paciente seleccionado en el contexto mientras se navega por sus registros.
- Una combinación inexistente devuelve 404 y presenta un mensaje claro.
- Todas las acciones posteriores conservan el mismo número de atención.

## 6. ENF-003 — Signos vitales

**Como** personal de Enfermería, **quiero** registrar signos vitales **para** dar seguimiento al estado del paciente.

### Criterios

- Se capturan `ta`, `fc`, `fr`, `temp`, `spo2`, `peso` y `talla`.
- El formulario exige al menos un campo con información.
- La petición usa la atención seleccionada.
- Un registro válido responde 201.
- El historial se actualiza después de guardar.
- Los registros muestran fecha y responsable cuando estén disponibles.
- La API rechaza una atención inexistente sin crear datos huérfanos.
- Se deben validar formato, rango y unidad antes de considerar la historia plenamente robusta.

## 7. ENF-004 — Nota de Enfermería

**Como** personal de Enfermería, **quiero** guardar observaciones **para** mantener continuidad durante la atención.

### Criterios

- La nota no puede enviarse vacía desde la interfaz.
- La API guarda el texto en `nursing_notes`.
- El registro contiene `id_nota`, atención, expediente, enfermero y fecha.
- Una creación válida responde 201.
- El historial aparece ordenado de más reciente a más antiguo.
- El historial muestra el nombre del profesional cuando puede resolverse.
- El contenido de una atención no aparece en otra.

## 8. ENF-005 — Medicamentos

**Como** personal de Enfermería, **quiero** registrar medicamentos administrados **para** conservar evidencia del tratamiento aplicado.

### Criterios

- La interfaz permite agregar y quitar filas antes de guardar.
- Cada elemento puede incluir nombre, dosis, frecuencia, vía y fecha.
- Solo se envían elementos con nombre.
- El cuerpo utiliza la propiedad `medicamentos` como arreglo.
- La API asocia el registro con atención, expediente y enfermero.
- Una creación válida responde 201 con `id_registro`.
- El historial muestra todos los medicamentos de cada administración.
- No deben aceptarse registros sin ningún medicamento válido.

## 9. ENF-006 — Valoración de Enfermería

**Como** personal de Enfermería, **quiero** documentar la valoración inicial o de seguimiento **para** identificar necesidades y riesgos.

### Criterios

- Se incluyen estado general, dolor, movilidad, riesgo de caídas, riesgo UPP y observaciones.
- La valoración queda anidada en `valoracion` dentro del documento persistido.
- La API genera `id_valoracion`.
- Una creación válida responde 201.
- Después de guardar, el formulario se limpia y el historial se actualiza.
- El historial conserva profesional y fecha.
- Los riesgos deben usar una escala o vocabulario definido por el proyecto.

## 10. ENF-007 — Balance hídrico

**Como** personal de Enfermería, **quiero** registrar ingresos y egresos **para** conocer el balance neto del paciente.

### Criterios

- Se capturan ingresos orales, ingresos IV, orina y drenajes.
- Los valores vacíos se interpretan como cero.
- Los valores aceptados son numéricos y no negativos.
- El servidor calcula total de ingresos, total de egresos y balance neto.
- El cliente no envía totales como valores confiables.
- Una creación válida responde 201 con `id_balance`.
- El historial muestra entradas, totales, balance, observaciones, fecha y responsable.
- Un valor inválido debe devolver 400 y no 500.

## 11. ENF-008 — Cuidados de Enfermería

**Como** personal de Enfermería, **quiero** documentar el plan de cuidados **para** dar seguimiento a objetivos e intervenciones.

### Criterios

- Se capturan diagnóstico, objetivos, intervenciones, evaluación y observaciones.
- El estado solo admite `EN_PROCESO`, `PENDIENTE` o `COMPLETADO`.
- Si no se envía estado, se utiliza `EN_PROCESO`.
- La API genera `id_cuidado`.
- Una creación válida responde 201.
- El historial se ordena por fecha descendente.
- Cada registro conserva atención, expediente, profesional y fecha.
- Después de guardar, el formulario se reinicia.

## 12. ENF-009 — Historial, seguridad y trazabilidad

**Como** responsable clínico, **quiero** consultar registros trazables y protegidos **para** conocer quién realizó cada intervención.

### Criterios

- Todas las consultas requieren token.
- Todas las escrituras permiten únicamente roles definidos.
- El backend obtiene el usuario del token, no del cuerpo enviado por el cliente.
- La fecha de registro se genera en el servidor.
- Cada consulta filtra por `id_atencion`.
- Los resultados se ordenan de más reciente a más antiguo.
- La caché no sustituye la base y puede actualizarse manualmente.
- Un token inválido produce 401.
- Un rol no autorizado produce 403.
- Una atención inexistente produce 404.
- Los errores no exponen secretos ni información interna innecesaria.

## 13. Casos de prueba integrales

| ID | Caso | Resultado esperado |
|---|---|---|
| CP-ENF-01 | Enfermero abre el panel | Visualiza áreas y pacientes |
| CP-ENF-02 | Usuario ajeno intenta escribir | 403 |
| CP-ENF-03 | Se abre paciente válido | Detalle correcto |
| CP-ENF-04 | Se registra un signo | 201 e historial actualizado |
| CP-ENF-05 | Nota vacía | No se envía |
| CP-ENF-06 | Lista de medicamentos válida | 201 y registro completo |
| CP-ENF-07 | Se registra valoración | Campos visibles en historial |
| CP-ENF-08 | Balance 800 + 500 − 900 − 100 | Balance neto igual a 300 |
| CP-ENF-09 | Cuidado sin estado | Estado `EN_PROCESO` |
| CP-ENF-10 | Atención inexistente | 404 sin inserción |
| CP-ENF-11 | Se consulta otra atención | No hay fuga de registros |
| CP-ENF-12 | Se actualiza historial | Se muestra la última información de MongoDB |

## 14. Evidencias esperadas

- Captura del panel de Enfermería.
- Captura del detalle con datos ficticios.
- Captura de signos vitales e historial.
- Captura de valoración.
- Captura de balance hídrico con cálculo comprobable.
- Captura de cuidados y estados.
- Pruebas de API con códigos 201, 401, 403 y 404.
- Registro en MongoDB sin información real de pacientes.

## 15. Riesgos detectados

| Riesgo | Acción requerida |
|---|---|
| Diferencia entre roles `enfermeria` y `enfermero` | Normalizar el valor en frontend, API y base |
| Validaciones clínicas insuficientes | Añadir esquemas y rangos |
| Conversión numérica produce 500 | Responder 400 ante datos inválidos |
| Caché presenta información anterior | Mostrar fecha y permitir actualización |
| Escrituras implementadas directamente en rutas | Centralizar en servicio y probar |
| Historial depende de tipos de identificador | Homologar `_id`, `id` y ObjectId de usuarios |

## 16. Aprobación del Sprint

El Sprint 3 puede aprobarse cuando ENF-001 a ENF-009 cuentan con evidencia funcional, las pruebas integrales pasan con datos ficticios, la autorización se comporta correctamente y los registros permanecen aislados por atención.
