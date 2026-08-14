# Manual de usuario — Módulo de Configuración

**Sistema:** INEO — React y API Hospital  
**Sprint:** 4 — Médico, Estudios y Configuración  
**Responsable del documento:** Jesús

## 1. Objetivo

Explicar las opciones administrativas para camas, usuarios, diagnósticos, servicios, respaldos, automatización, perfil y parámetros generales del sistema.

## 2. Acceso

Seleccione **Configuración** en el menú lateral. Las operaciones administrativas requieren una cuenta con permisos de administrador; el perfil puede consultarse con la sesión autenticada.

## 3. Opciones del panel

| Opción | Función |
|---|---|
| Camas | Alta, edición, eliminación y consulta de disponibilidad |
| Usuarios | Registro, activación, desactivación y eliminación de cuentas |
| Diagnósticos | Administración del catálogo de diagnósticos |
| Servicios | Administración de conceptos, precios y unidades |
| Copias de seguridad | Creación, descarga, restauración y eliminación |
| Automatización | Programación de respaldos automáticos |
| Mi perfil | Consulta de los datos de la cuenta activa |

## 4. Gestión de camas

Abra **Camas**, complete número, área y estado, y guarde. Para modificar una cama, seleccione **Editar**; para eliminarla, confirme que no esté vinculada a una atención activa. Si la API rechaza la operación, conserve el registro y revise su ocupación.

## 5. Usuarios

En **Usuarios**, capture nombre, usuario, contraseña y rol. Verifique el rol antes de guardar porque determina el acceso a datos clínicos y administrativos. Las cuentas pueden activarse o desactivarse sin eliminarlas; esta opción es preferible cuando debe conservarse la trazabilidad histórica.

## 6. Diagnósticos y servicios

En **Diagnósticos**, evite códigos duplicados y use descripciones clínicas claras. En **Servicios**, capture nombre, precio y unidad; revise la moneda y el importe antes de guardar, ya que estos valores pueden afectar las cuentas de pacientes.

## 7. Parámetros generales

La pantalla general conserva localmente el nombre de la clínica, teléfono, dirección, moneda, tema y datos visibles de conexión (`apiHost`, `apiPort`, `apiPath`). Guardar estos valores no reconfigura por sí solo el servidor desplegado ni sustituye las variables de entorno de la aplicación.

## 8. Copias de seguridad

1. Seleccione tipo: completa, incremental o diferencial.
2. Elija formato: JSON, CSV comprimido, Excel o PDF.
3. Marque las colecciones.
4. Seleccione **Crear respaldo**.
5. Espere la confirmación y revise la lista.

JSON, CSV/ZIP y XLSX son restaurables. PDF es únicamente de consulta. Para restaurar, seleccione un respaldo compatible y confirme; la restauración puede reemplazar el contenido de las colecciones incluidas.

## 9. Automatización

Active la automatización, seleccione tipo, formato, intervalo, colecciones y cantidad máxima de respaldos. El intervalo permitido por la API es de 5 a 525600 minutos y la retención se limita de 1 a 50 archivos. Guarde y confirme que la configuración aparezca actualizada.

## 10. Cambio de idioma

INEO incluye español e inglés. Al cambiar el idioma, los textos registrados en los catálogos o expedientes no se traducen; solamente cambian las etiquetas de la interfaz que cuentan con una clave de traducción.

## 11. Seguridad y recomendaciones

- Cree un respaldo antes de eliminar catálogos o ejecutar una restauración.
- No descargue respaldos en equipos públicos.
- No comparta contraseñas ni tokens.
- Desactive usuarios antes de eliminarlos cuando se requiera conservar trazabilidad.
- Compruebe que MongoDB esté disponible antes de respaldar.
- Después de restaurar, valide pacientes, usuarios, catálogos y atenciones.

## 12. Resultado esperado

El administrador mantiene catálogos y cuentas, protege la información con respaldos y puede configurar la interfaz sin exponer funciones administrativas a roles no autorizados.
