# Manual de usuario — Módulo de Enfermería

**Sistema:** INEO — Gestión Clínica  
**Sprint:** 3 — Enfermería  
**Dirigido a:** Personal de enfermería y administradores  
**Responsable del documento:** Jesús

## 1. Introducción

El módulo de Enfermería permite consultar pacientes con una atención abierta y registrar información clínica relacionada con signos vitales, notas, medicamentos, valoraciones, balance hídrico y cuidados. Cada registro queda asociado al número de atención, expediente, usuario responsable y fecha de captura.

Este manual describe las pantallas incluidas en las historias ENF-001 a ENF-009.

## 2. Requisitos de acceso

Antes de utilizar el módulo verifique que:

- La aplicación web, la API Flask y MongoDB estén funcionando.
- Su cuenta tenga el rol de enfermería autorizado.
- Haya iniciado sesión correctamente.
- El paciente tenga una atención abierta.
- La aplicación tenga comunicación con la API configurada.

En la API el rol utilizado es `enfermero`. El frontend reconoce `enfermero` y `enfermeria`; por ello, la cuenta debe estar configurada de forma compatible con el backend.

## 3. Acceso al panel

1. Inicie sesión en INEO.
2. Abra la opción **Enfermería**.
3. Espere a que cargue el panel de pacientes.
4. Revise las áreas disponibles:
   - Consulta o ambulatorio.
   - Urgencias.
   - Hospitalizados.
5. Utilice los controles de página cuando existan más registros.
6. Presione el paciente o la cama ocupada que desea atender.

El botón de actualización vuelve a consultar la información. Una cama libre no permite abrir un expediente clínico porque no tiene una atención asociada.

## 4. Panel de pacientes

El panel muestra pacientes agrupados por área. Cada tarjeta puede presentar:

- Número de cama o consulta.
- Estado de ocupación.
- Nombre del paciente.
- Número de expediente.
- Número de atención.

Los datos se conservan temporalmente en la caché del navegador para mejorar la respuesta de la pantalla. Use **Actualizar** cuando necesite confirmar información reciente.

## 5. Detalle del paciente

Al seleccionar un paciente se abre su detalle. Antes de registrar información confirme:

- Nombre completo.
- Número de expediente.
- Número de atención.
- Área y cama.
- Motivo de atención.
- Alergias.
- Familiar responsable, cuando exista.
- Médicos asignados.

Desde esta pantalla se accede a las funciones de Enfermería. Si el nombre o la atención no corresponden, regrese al panel y seleccione el registro correcto.

## 6. Registrar signos vitales

1. Desde el detalle presione **Signos vitales**.
2. Confirme el expediente y número de atención mostrados en la parte superior.
3. Capture uno o varios campos:
   - Tensión arterial (`ta`), por ejemplo `120/80`.
   - Frecuencia cardiaca (`fc`) en latidos por minuto.
   - Frecuencia respiratoria (`fr`) en respiraciones por minuto.
   - Temperatura (`temp`) en grados Celsius.
   - Saturación de oxígeno (`spo2`) en porcentaje.
   - Peso en kilogramos.
   - Talla en metros.
4. Revise los valores.
5. Presione **Guardar**.
6. Espere el mensaje de confirmación.
7. Revise el historial actualizado.

El formulario requiere al menos un dato. No escriba unidades dentro de campos numéricos, salvo el formato propio de la tensión arterial.

## 7. Registrar una nota de Enfermería

1. Presione **Nota de Enfermería**.
2. Confirme el paciente seleccionado.
3. Escriba una observación clínica clara, objetiva y completa.
4. Presione **Guardar** una sola vez.
5. Abra o actualice el historial para verificar el registro.

La nota no puede estar vacía. Debe describir hechos observados, acciones realizadas y respuesta del paciente, evitando opiniones personales o abreviaturas ambiguas.

## 8. Registrar medicamentos administrados

1. Abra **Medicamentos**.
2. Capture el nombre del medicamento.
3. Registre la dosis.
4. Indique la frecuencia.
5. Capture la vía de administración.
6. Registre la fecha solicitada por la pantalla.
7. Use **Agregar medicamento** si necesita incluir otro elemento.
8. Elimine una fila únicamente antes de guardar si fue añadida por error.
9. Presione **Guardar**.
10. Revise el historial de administraciones.

Solo se envían filas que tengan nombre de medicamento. Antes de guardar aplique las verificaciones institucionales: paciente, medicamento, dosis, vía, hora y registro correctos.

## 9. Registrar valoración de Enfermería

La valoración incluye:

- Estado general.
- Dolor.
- Movilidad.
- Riesgo de caídas.
- Riesgo de úlceras por presión (`riesgo_upp`).
- Observaciones.

Procedimiento:

1. Abra **Valoración de Enfermería**.
2. Evalúe al paciente conforme al protocolo institucional.
3. Capture los campos con términos claros.
4. Presione **Guardar**.
5. Compruebe que el registro aparezca en el historial.

Los campos de riesgo deben expresar el resultado de la valoración aplicada y no una suposición sin evaluación.

## 10. Registrar balance hídrico

1. Abra **Balance hídrico**.
2. Capture en mililitros:
   - Ingresos orales.
   - Ingresos intravenosos.
   - Egresos por orina.
   - Egresos por drenajes.
3. Agregue observaciones cuando sean necesarias.
4. Presione **Guardar**.
5. Revise en el historial:
   - Total de ingresos.
   - Total de egresos.
   - Balance neto.

El sistema calcula:

```text
Total ingresos = ingresos orales + ingresos IV
Total egresos = orina + drenajes
Balance neto = total ingresos - total egresos
```

Capture `0` cuando se haya comprobado que no existió un movimiento; no use valores negativos.

## 11. Registrar cuidados de Enfermería

1. Abra **Cuidados de Enfermería**.
2. Capture el diagnóstico de Enfermería.
3. Defina los objetivos.
4. Describa las intervenciones.
5. Registre la evaluación.
6. Seleccione el estado:
   - `EN_PROCESO`.
   - `PENDIENTE`.
   - `COMPLETADO`.
7. Agregue observaciones.
8. Presione **Guardar**.
9. Revise el historial.

El estado debe corresponder a la situación real del plan. Un cuidado no debe marcarse como completado si la evaluación o intervención continúa pendiente.

## 12. Consultar historiales

Cada pantalla consulta los registros de la atención actual y los ordena desde el más reciente. El historial puede mostrar:

- Identificador del registro.
- Información capturada.
- Fecha y hora.
- Nombre del profesional responsable.

Algunas pantallas conservan una copia temporal durante dos minutos. Si sospecha que la información cambió, utilice **Actualizar historial**.

Los historiales pertenecen a la atención seleccionada. Confirme siempre el número de atención antes de interpretar registros anteriores.

## 13. Mensajes frecuentes

| Situación | Acción recomendada |
|---|---|
| No hay paciente seleccionado | Regrese al panel y abra una cama ocupada |
| Atención no encontrada | Verifique que la atención siga abierta y actualice el panel |
| Sesión vencida | Inicie sesión nuevamente |
| Acceso no autorizado | Solicite la revisión del rol asignado |
| Error al guardar | Conserve los datos, revise la conexión y evite duplicar el registro |
| Historial vacío | Confirme el número de atención y actualice |
| Datos antiguos | Use el botón de actualización para omitir la caché |
| Paciente no encontrado | Regrese al panel y seleccione nuevamente |

## 14. Recomendaciones de seguridad

- No comparta su cuenta o contraseña.
- Cierre la sesión al finalizar.
- No deje la pantalla abierta sin supervisión.
- Verifique la identidad del paciente antes de cada registro.
- No copie información clínica en aplicaciones no autorizadas.
- No use datos reales en ambientes de prueba.
- Informe inmediatamente cualquier registro realizado en una atención equivocada.

## 15. Buenas prácticas clínicas de captura

- Registre la información inmediatamente después de la intervención.
- Utilice lenguaje objetivo, legible y profesional.
- Evite campos vacíos cuando el dato sea relevante.
- No invente valores para completar el formulario.
- Revise unidades y formato antes de guardar.
- Evite presionar **Guardar** varias veces.
- Compruebe el historial después de cada operación.

## 16. Lista de verificación

Antes de terminar el turno confirme:

- [ ] Revisé pacientes y áreas asignadas.
- [ ] Confirmé expediente y atención antes de registrar.
- [ ] Los signos vitales tienen formato y unidades correctos.
- [ ] Las notas describen hechos y acciones realizadas.
- [ ] Los medicamentos administrados quedaron registrados.
- [ ] La valoración y los riesgos están actualizados.
- [ ] El balance hídrico coincide con ingresos y egresos.
- [ ] Los cuidados tienen estado y evaluación correctos.
- [ ] Revisé los historiales.
- [ ] Cerré mi sesión.
