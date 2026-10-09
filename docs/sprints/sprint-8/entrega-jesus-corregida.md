# Entrega corregida de Jesús — Sprint 2 / Azure Sprint 8

## Alcance del PBL final

| Historia | Puntos | Resultado |
|---|---:|---|
| PBL-17 | 3 | Microcopias, títulos, ayudas y nombres visibles usan lenguaje cotidiano en español e inglés. |
| PBL-19 | 5 | Instalación, variables, API, pruebas, uso y solución de problemas están documentados desde el README. |

## Trazabilidad de tareas

| Tarea | Evidencia |
|---|---|
| PBL-17-T1 | Inventario de términos y restricciones en esta entrega. |
| PBL-17-T2 | `src/i18n/locales/es.json`, `en.json` y prueba `pbl17-plain-language.test.js`. |
| PBL-17-T3 | Prueba automática de términos visibles, validación de claves, regresión y compilación. |
| PBL-19-T1 | Revisión de requisitos, configuración, documentación previa y rutas de ayuda. |
| PBL-19-T2 | Recorrido único en `README.md`, con variantes Linux/macOS y PowerShell. |
| PBL-19-T3 | README actualizado con instalación, variables, API, pruebas y uso. |
| PBL-19-T4 | Referencias a manuales, contrato, despliegue y reversión existentes. |
| PBL-19-T5 | Comandos reproducibles validados en CI; lista manual para una persona nueva incluida abajo. |

## Decisiones de terminología

| Término técnico anterior | Texto visible aprobado |
|---|---|
| Spark | Análisis de datos |
| Dashboard | Inicio |
| Nota Médica (SOAP) | Nota médica |
| Solicitudes Lab | Solicitudes de laboratorio |
| Backup | Copias de seguridad |
| Métricas de actividad (MET) | Actividad diaria |
| Análisis no supervisado | Patrones en los datos |
| PCA exploratorio | Resumen de variables principales |

Las rutas, claves internas, contratos y nombres técnicos del código no cambian.
Sólo cambia el texto destinado a las personas usuarias.

## Validación manual de aceptación

Una persona que no haya trabajado en la implementación debe marcar esta lista al
probar el commit candidato. No se reporta como ejecutada hasta registrar nombre,
fecha y resultado real.

- [ ] Encuentra **Inicio** sin ayuda.
- [ ] Encuentra **Nota médica** sin conocer la sigla SOAP.
- [ ] Encuentra **Copias de seguridad**.
- [ ] Abre **Análisis de datos** e interpreta **Patrones en los datos**.
- [ ] Clona el repositorio siguiendo únicamente el `README.md`.
- [ ] Inicia o prueba la API y obtiene `status: ok` en `/health`.
- [ ] Ejecuta las pruebas del frontend y la API.
- [ ] Inicia la web y localiza los manuales por rol.

El equipo debe adjuntar el registro firmado o una captura de esta revisión para
cerrar formalmente la evidencia humana solicitada por el PBL. Las verificaciones
automáticas evitan regresiones, pero no sustituyen esa prueba con una persona.

## Revisión de la evidencia recibida el 8 de octubre de 2026

Jesús añadió un registro que declara a una participante como participante el la fecha declarada en el registro original. Los documentos corregidos conservan ese dato como declaración recibida y distinguen las verificaciones automáticas de la aceptación humana. Las capturas originales conservan Dashboard/Backup y muestran un fallo de check:i18n y un rechazo 403; no acreditan todas las actividades como aprobadas.

La ejecución automática actual está en [evidencia-automatica-jesus-20261008.md](evidencia-automatica-jesus-20261008.md): 76 pruebas del frontend aprobadas, idiomas, lint y build aprobados. La aceptación de PBL-17-T3 y PBL-19-T5 permanece pendiente de un registro coherente por actividad y la versión probada. No marcar estas tareas ni el Sprint 8 como cerrado por esta actualización documental.
