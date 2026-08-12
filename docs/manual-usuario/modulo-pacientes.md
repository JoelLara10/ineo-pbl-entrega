# Manual de usuario — Módulo de pacientes

**Sistema:** INEO — Gestión Clínica  
**Sprint:** 2 — Pacientes y Administrativo  
**Dirigido a:** Administradores y personal administrativo  
**Responsable del documento:** Jesús

## 1. Introducción

El módulo de pacientes permite registrar expedientes, consultar pacientes, actualizar información, revisar el censo hospitalario, administrar cuentas y consultar el corte de caja. Este manual explica el uso de las pantallas incluidas en el Sprint 2.

## 2. Requisitos de acceso

Antes de comenzar, verifique que:

- La aplicación web y la API estén funcionando.
- MongoDB esté disponible.
- Su usuario tenga rol **Administrador** o **Administrativo**.
- El navegador tenga conexión con la dirección configurada para la API.
- Haya iniciado sesión correctamente.

## 3. Menú administrativo

El módulo incluye las siguientes opciones principales:

| Opción | Uso |
|---|---|
| Gestión de pacientes | Consultar, buscar, registrar y editar pacientes |
| Nuevo paciente | Crear el expediente y la atención inicial |
| Cuenta del paciente | Consultar cargos, saldo, documentos y cierre de cuenta |
| Censo | Revisar pacientes activos por área o sección |
| Corte de caja | Consultar ingresos, movimientos y cuentas activas |

## 4. Consultar pacientes

1. Inicie sesión.
2. Seleccione **Gestión de pacientes**.
3. Espere a que se carguen las tablas.
4. Revise los indicadores superiores:
   - Activos.
   - Expedientes.
   - Altas.
5. Escriba en el campo de búsqueda para filtrar resultados.
6. Utilice los botones **‹** y **›** para cambiar de página.
7. Presione **Ver** para abrir la cuenta o **Editar** para modificar el expediente.

Cada registro muestra expediente, nombre, edad, teléfono, área y cama. Si la información no aparece, utilice la opción de actualizar de la pantalla.

## 5. Registrar un paciente

### Paso 1. Abrir el formulario

En **Gestión de pacientes**, presione **Nuevo paciente**.

### Paso 2. Datos personales

Capture:

- CURP — obligatorio.
- Primer apellido — obligatorio.
- Segundo apellido — opcional.
- Nombre o nombres — obligatorio.
- Fecha de nacimiento — obligatoria.
- Teléfono.

Revise la CURP antes de guardar; este dato ayuda a evitar expedientes duplicados.

### Paso 3. Datos de atención

Seleccione:

- Área.
- Cama, si aplica.
- Motivo de atención.
- Especialidad.
- Alergias conocidas.

Las opciones disponibles son proporcionadas por el sistema. Si una cama no aparece, puede estar ocupada o deshabilitada.

### Paso 4. Médicos asignados

Marque los médicos responsables. La interfaz permite seleccionar como máximo cinco. Desmarque un médico si necesita sustituirlo.

### Paso 5. Familiar responsable

Capture nombre, parentesco y teléfono. Esta información facilita el contacto durante la atención.

### Paso 6. Guardar

1. Revise todos los campos.
2. Presione **Guardar** una sola vez.
3. Espere a que termine el proceso.
4. El sistema regresará al listado cuando el registro sea correcto.

Si aparece un mensaje de error, corrija el dato indicado y vuelva a intentarlo. No recargue la página mientras se está guardando.

## 6. Editar un paciente

1. Localice al paciente en **Gestión de pacientes**.
2. Presione **Editar**.
3. Espere a que se cargue el expediente.
4. Modifique únicamente los datos necesarios.
5. Revise área, cama, médicos y familiar responsable.
6. Presione **Guardar**.

La edición actualiza el expediente existente; no crea uno nuevo. Use **Cancelar** o regrese a la pantalla anterior si no desea conservar los cambios.

## 7. Consultar el censo

1. Abra la opción **Censo**.
2. Revise los indicadores de activos, áreas y avisos.
3. Use el buscador para localizar a un paciente.
4. Consulte número de atención, expediente, área, médico, motivo y aviso.
5. Cambie de página dentro de cada sección cuando sea necesario.

El censo debe utilizarse para conocer la situación administrativa actual. Si un movimiento reciente no aparece, actualice la pantalla.

## 8. Consultar una cuenta

Puede abrir una cuenta desde el listado de pacientes o desde **Corte de caja**.

1. Seleccione la cuenta deseada.
2. Revise el resumen:
   - Subtotal.
   - Impuestos.
   - Total.
   - Saldo.
3. Confirme que el nombre y número de atención correspondan al paciente correcto antes de realizar movimientos.

## 9. Agregar un cargo

1. Abra la cuenta del paciente.
2. En **Agregar cargo**, seleccione el tipo:
   - Servicio.
   - Medicamento.
3. Seleccione el concepto disponible.
4. Capture la cantidad.
5. Presione **Agregar**.
6. Verifique que aparezca en la tabla y que el total se actualice.

No repita el movimiento si el botón tarda en responder. Primero actualice la cuenta y confirme si el cargo ya fue registrado.

## 10. Eliminar un cargo

1. Localice el cargo en la tabla.
2. Presione el botón con el icono de papelera.
3. Revise la descripción del movimiento.
4. Confirme la eliminación.
5. Verifique el nuevo total.

Esta acción debe utilizarse solo para corregir cargos incorrectos y de acuerdo con las políticas del hospital.

## 11. Registrar un pago

Cuando la opción se encuentre habilitada en la cuenta:

1. Confirme el paciente y el saldo.
2. Capture el importe.
3. Seleccione el método de pago disponible.
4. Registre el pago.
5. Compruebe que el saldo haya disminuido.

Si el sistema informa un error, no vuelva a registrar el pago hasta verificar los movimientos del corte de caja.

## 12. Descargar documentos

En la sección **Documentos** pueden aparecer:

- Hoja inicial.
- Carátula.
- Contrato.
- Consentimiento.
- Hoja de identificación.

Para descargar:

1. Confirme que la cuenta esté abierta.
2. Presione el nombre del documento.
3. Espere a que el navegador genere la descarga.
4. Abra el PDF y revise paciente, expediente y atención.

No comparta documentos clínicos por medios no autorizados.

## 13. Cerrar una cuenta

Antes de cerrar:

- Verifique todos los cargos.
- Confirme pagos y saldo.
- Revise que sea la atención correcta.
- Genere los documentos necesarios.

Después:

1. Presione **Cerrar cuenta**.
2. Lea la confirmación.
3. Acepte únicamente si la información es correcta.
4. Espere el mensaje de cierre exitoso.

No cierre una cuenta si existen movimientos pendientes de registrar.

## 14. Consultar el corte de caja

1. Abra **Corte de caja**.
2. Revise las tarjetas de ingresos, movimientos y cuentas activas.
3. Use el buscador para filtrar por paciente, concepto u otro dato visible.
4. En **Movimientos**, revise hora, paciente, concepto, método e importe.
5. En **Cuentas activas**, revise total y saldo.
6. Presione **Ver** para abrir una cuenta.

El corte de caja sirve como consulta operativa. Las exportaciones o reportes formales deben generarse mediante las opciones autorizadas.

## 15. Mensajes frecuentes

| Mensaje o situación | Qué hacer |
|---|---|
| Cargando | Espere; no presione varias veces el botón |
| Sesión vencida | Inicie sesión nuevamente |
| Acceso no autorizado | Verifique que su usuario tenga el rol correcto |
| Paciente no encontrado | Revise el expediente o vuelva al listado |
| Cama no disponible | Seleccione otra cama o confirme su estado |
| Error de API | Compruebe que Flask y MongoDB estén funcionando |
| No hay pacientes | Quite el filtro o actualice la pantalla |
| Documento no disponible | Confirme que exista una atención válida |
| Cuenta no puede cerrarse | Revise saldo y movimientos pendientes |

## 16. Buenas prácticas

- Confirme la identidad del paciente antes de modificar información.
- No comparta su usuario, contraseña o token.
- Evite crear un expediente si el paciente ya existe.
- No registre pagos o cargos dos veces.
- Revise los documentos antes de imprimirlos.
- Cierre la sesión al terminar.
- No use datos reales en ambientes de prueba.

## 17. Lista de verificación

Antes de finalizar una atención administrativa confirme:

- [ ] Los datos personales son correctos.
- [ ] La atención tiene área y motivo válidos.
- [ ] La cama y los médicos corresponden al paciente.
- [ ] Los cargos fueron revisados.
- [ ] Los pagos aparecen en el sistema.
- [ ] El saldo coincide con los movimientos.
- [ ] Los documentos necesarios fueron generados.
- [ ] La cuenta se cerró solamente cuando correspondía.
