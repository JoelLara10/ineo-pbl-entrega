# Manual de usuario — Módulo Médico

**Sistema:** INEO — React y API Hospital  
**Sprint:** 4 — Médico, Estudios y Configuración  
**Responsable del documento:** Jesús

## 1. Objetivo

Explicar el uso del módulo Médico para localizar pacientes con atención abierta, consultar su expediente y registrar información clínica durante la atención.

## 2. Acceso

1. Inicie sesión con una cuenta autorizada.
2. Seleccione **Médico** en el menú lateral.
3. El panel organiza a los pacientes en **Consulta externa**, **Urgencias** y **Hospitalizados**.
4. Seleccione una tarjeta ocupada para abrir el detalle. Las camas libres no contienen expediente clínico.

El sistema requiere conexión con la API y un token vigente. Si la consulta falla, puede mostrar datos guardados previamente junto con un aviso de funcionamiento sin conexión.

## 3. Panel médico

Cada tarjeta ocupada muestra el nombre del paciente, expediente, número de cama o consulta y estado. Al seleccionar al paciente, INEO conserva `id_atencion` e `Id_exp`; estos identificadores permiten que los formularios registren información en la atención correcta.

## 4. Funciones disponibles

| Función | Uso principal |
|---|---|
| Historia clínica | Registrar antecedentes, padecimiento y exploración clínica |
| Signos vitales | Capturar TA, FC, FR, temperatura, SpO2, peso y talla |
| Historial de signos | Consultar mediciones anteriores |
| Nota médica SOAP | Registrar información subjetiva, objetiva, análisis y plan |
| Diagnóstico | Seleccionar diagnósticos del catálogo y revisar historial |
| Receta | Indicar medicamentos, dosis, vía y frecuencia |
| Laboratorio | Solicitar exámenes de laboratorio |
| Gabinete | Solicitar estudios de imagen o gabinete |
| Resultados | Consultar resultados disponibles |
| Imprimir documentos | Preparar documentos clínicos para impresión |

## 5. Historia clínica

Abra **Historia clínica**, complete los datos solicitados y seleccione **Guardar**. Si existe una historia previa, la pantalla la consulta para evitar perder información. Revise el expediente y la atención mostrados antes de confirmar.

## 6. Nota médica SOAP

Complete las cuatro secciones:

- **S — Subjetivo:** síntomas y comentarios del paciente.
- **O — Objetivo:** hallazgos de la valoración.
- **A — Análisis:** interpretación médica.
- **P — Plan:** tratamiento, estudios y seguimiento.

Seleccione **Guardar nota**. El historial se relaciona con la atención activa y conserva la fecha y el médico responsable.

## 7. Diagnóstico y receta

En **Diagnóstico**, busque o seleccione una opción del catálogo, añada observaciones y guarde. En **Receta**, capture únicamente indicaciones clínicas verificadas. Antes de confirmar, revise nombre, dosis, frecuencia, vía y duración de cada medicamento.

## 8. Solicitud de estudios

1. Abra **Laboratorio** o **Gabinete**.
2. Seleccione uno o varios estudios del catálogo.
3. Agregue indicaciones u observaciones cuando corresponda.
4. Confirme la solicitud.
5. Use **Ver resultados** para consultar el seguimiento.

El personal de Estudios cargará el resultado; el médico no debe crear solicitudes duplicadas para sustituir una ya registrada.

## 9. Impresión

La pantalla **Imprimir documentos** permite elegir signos vitales, nota médica, diagnóstico, receta y solicitudes de estudios. Verifique que el navegador permita abrir o descargar archivos y que la información pertenezca al paciente seleccionado.

## 10. Recomendaciones y errores comunes

- Seleccione primero un paciente; de lo contrario, las pantallas clínicas no tendrán una atención válida.
- No use el botón Atrás del navegador durante un guardado en curso.
- Si aparece **No autorizado**, cierre sesión e ingrese con el rol correcto.
- Si no aparecen pacientes, actualice el panel y confirme que existan atenciones con estado `ABIERTA`.
- Si un resultado no aparece, verifique su estado en el módulo Estudios.
- No comparta capturas, impresiones ni datos clínicos fuera de los canales autorizados.

## 11. Resultado esperado

El usuario médico puede completar el flujo clínico de una atención, solicitar estudios, consultar resultados e imprimir documentos sin cambiar manualmente los identificadores del paciente.
