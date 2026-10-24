# Pruebas web QA - OftalCore

Fecha: 24 de octubre de 2026. URL: https://ineo-web-qa.vercel.app/.
Alcance: acceso, módulos principales, formularios, manejo de errores, sesión y presentación. Cuenta sintética de QA; no se registran datos reales.

## Hallazgos

### ISSUE-001: La web sigue presentando el nombre anterior INEO

Severidad: baja. Categoría: contenido. Repro Video: N/A (visible al cargar).

La página de acceso y el título del navegador presentan INEO, aunque el nombre confirmado por el equipo es OftalCore. Evidencia: `screenshots/01-login-marca-anterior.png`.

Pasos: abrir la URL QA sin sesión y observar el encabezado, pie de página y título del navegador. Se espera OftalCore.

## Pruebas realizadas

- Inicio de exploración; resultados se incorporan durante la ejecución.

### ISSUE-002: El formulario web no permite registrar servicios válidos

Severidad: alta. Categoría: funcional/contrato API. La regresión se reprodujo con costo 0 y costo 500, clave y descripción completas. El formulario envía serv_costo2..serv_costo8 vacíos y la validación reciente del servidor los rechaza como inválidos.

Pasos: Configuración > Catálogo de Servicios; completar clave WEBQA-2410-TEST, descripción ficticia y precio; pulsar Guardar servicio. Resultado: mensaje «Costo, IVA o tipo de servicio inválido» y formulario sin guardar.

Evidencias: screenshots/03-servicio-valido-rechazado-cero.png y screenshots/04-servicio-valido-rechazado.png. Video no disponible: la herramienta de grabación no encontró ffmpeg; se conservaron capturas de las dos reproducciones.

La navegación se confirmó en un segundo navegador: no se considera fallo de la aplicación la lectura obsoleta observada inicialmente en la herramienta CLI.

### ISSUE-003: El alta ignora el estado Inactivo seleccionado

Severidad: media. Categoría: funcional/persistencia.

Se creó el servicio ficticio WEBQA-2410-INACTIVO con Estado Inactivo y precios opcionales en cero para aislar el otro fallo. El POST fue exitoso, pero la consulta posterior mostró ACTIVO (id_serv 5). Evidencia: screenshots/05-inactivo-guardado-como-activo.png. El servicio de backend fijaba serv_activo a SI.

## Cobertura funcional observada

Acceso y dashboard con datos; navegación a configuración, médico, enfermería, estudios, administración/pacientes, monitoreo y panel de análisis. Los paneles cargaron. Se probaron consulta y búsqueda del catálogo y el alta de un servicio ficticio. Los formularios clínicos, los dispositivos físicos, las restauraciones y las operaciones financieras no se ejecutaron sobre registros existentes.
