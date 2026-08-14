# Manual de usuario — Módulo de Estudios

**Sistema:** INEO — React y API Hospital  
**Sprint:** 4 — Médico, Estudios y Configuración  
**Responsable del documento:** Jesús

## 1. Objetivo

Describir el flujo para consultar solicitudes de laboratorio y gabinete, cargar resultados, visualizar archivos, corregir información y eliminar resultados cuando el usuario tenga autorización.

## 2. Acceso y secciones

Después de iniciar sesión, seleccione **Estudios**. El panel contiene cuatro secciones:

| Sección | Contenido |
|---|---|
| Solicitudes de laboratorio | Exámenes de laboratorio pendientes |
| Solicitudes de gabinete | Estudios de gabinete pendientes |
| Resultados de laboratorio | Estudios de laboratorio completados |
| Resultados de gabinete | Estudios de gabinete completados |

Los contadores superiores permiten identificar rápidamente el trabajo pendiente.

## 3. Consultar solicitudes

1. Abra la pestaña correspondiente al tipo de estudio.
2. Localice al paciente por la información mostrada.
3. Revise examen solicitado, médico, fecha e identificador.
4. Seleccione **Subir** para registrar el resultado.

Antes de cargar archivos, confirme que el tipo sea `LABORATORIO` o `GABINETE` y que el identificador coincida con la solicitud.

## 4. Subir un resultado

1. Abra la solicitud pendiente.
2. Adjunte los archivos permitidos por la pantalla.
3. Capture las observaciones clínicas o técnicas necesarias.
4. Revise la selección.
5. Confirme la carga y espere el mensaje de éxito.

No cierre la pestaña mientras se transfieren los archivos. No incluya archivos que correspondan a otro paciente y evite nombres que revelen información innecesaria.

## 5. Consultar resultados

En una sección de resultados, seleccione **Ver**. La pantalla muestra la información del estudio, observaciones y archivos asociados. El navegador puede abrir determinados formatos en una pestaña nueva o descargarlos.

Si un archivo no abre, verifique que aún exista en el servidor y que la sesión siga activa.

## 6. Editar resultados

1. Localice el estudio completado.
2. Seleccione **Editar**.
3. Actualice observaciones, agregue archivos o marque los que deban retirarse.
4. Confirme los cambios.
5. Vuelva a **Ver** para comprobar el resultado final.

La edición no debe usarse para cambiar un resultado a otro paciente. Si el identificador es incorrecto, repórtelo al administrador.

## 7. Eliminar un resultado

Seleccione **Eliminar** y confirme el mensaje del sistema. Esta operación quita los resultados asociados y puede devolver el estudio al flujo correspondiente según la lógica de la API. Úsela únicamente cuando la eliminación esté autorizada y haya verificado el identificador.

## 8. Estados y mensajes

| Mensaje | Acción recomendada |
|---|---|
| No hay solicitudes pendientes | Cambie de sección o actualice el panel |
| No hay resultados registrados | Verifique que la carga haya finalizado |
| Error al cargar estudios | Compruebe conexión, sesión y API |
| Resultado eliminado | Actualice los contadores y la lista |
| Sección inválida | Regrese al panel de Estudios |

## 9. Buenas prácticas

- Trabaje con una sola solicitud a la vez.
- Compruebe paciente, estudio y tipo antes de guardar.
- Use observaciones claras, objetivas y sin abreviaturas ambiguas.
- No cargue ejecutables ni documentos ajenos al expediente.
- No elimine resultados como método de corrección si basta con editarlos.
- Cierre sesión al terminar en equipos compartidos.

## 10. Resultado esperado

Las solicitudes pasan de pendientes a completadas después de una carga válida; el personal autorizado puede visualizar, editar o eliminar los resultados manteniendo la relación con el examen y la atención.
