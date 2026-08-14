# Resultados de pruebas — Sprint 5

**Sistema:** INEO — React y API Hospital  
**Sprint:** 5 — Calidad, Seguridad y Spark  
**Responsable:** Jesús  
**Fecha:** 14 de agosto de 2026

## 1. Resumen ejecutivo

Se realizó una revisión estática del código disponible. La sintaxis Python y los recursos de internacionalización superaron las verificaciones ejecutadas. No se encontraron suites de pruebas automatizadas en ninguno de los dos repositorios. La integración Spark no está completa porque el frontend existe, pero faltan las rutas y el servicio en la API.

## 2. Entorno revisado

| Componente | Repositorio |
|---|---|
| Backend Flask | `api_hospital` |
| Frontend React/Vite | `clinica-web-react` |
| Persistencia esperada | MongoDB |
| API | Prefijo `/api/v1` |

La revisión no utilizó datos clínicos reales ni secretos de producción.

## 3. Resultados ejecutados

| ID | Verificación | Resultado obtenido | Estado |
|---|---|---|---|
| EST-001 | Análisis sintáctico de archivos Python | 50 archivos analizados, 0 errores | Aprobado |
| EST-002 | Lectura de `es.json` | JSON válido | Aprobado |
| EST-003 | Lectura de `en.json` | JSON válido | Aprobado |
| EST-004 | Paridad de traducciones | 956 claves ES y 956 EN; 0 faltantes | Aprobado |
| EST-005 | Búsqueda de pruebas automatizadas | No se encontraron archivos de prueba | Pendiente |
| EST-006 | Búsqueda de backend Spark | No existen archivos Spark en la API revisada | Bloqueado |
| EST-007 | Revisión de registro de blueprints | No se registra `/api/v1/spark` | Bloqueado |

## 4. Verificaciones no ejecutadas

| ID | Verificación | Motivo | Estado |
|---|---|---|---|
| FUN-001 | Inicio de sesión contra MongoDB | Requiere servicios y datos de prueba activos | No ejecutada |
| FUN-002 | CRUD de pacientes y atenciones | Requiere entorno integrado | No ejecutada |
| FUN-003 | Flujos Médico, Enfermería y Estudios | Requiere API, frontend y base activa | No ejecutada |
| FUN-004 | Respaldo y restauración | Requiere base aislada y permisos de escritura | No ejecutada |
| WEB-001 | `npm run lint` | Dependencias no verificadas en esta revisión | No ejecutada |
| WEB-002 | `npm run build` | Dependencias no verificadas en esta revisión | No ejecutada |
| SPK-001 | Ejecución analítica Spark | Backend y endpoints ausentes | Bloqueada |

Una prueba no ejecutada no debe reportarse como aprobada.

## 5. Hallazgos de seguridad

| Severidad | Hallazgo | Recomendación |
|---|---|---|
| Alta | Secretos con valores predeterminados | Exigir variables de entorno seguras |
| Alta | Depuración activa por defecto | Usar `DEBUG=False` en producción |
| Alta | Token almacenado en `localStorage` | Reforzar XSS o migrar a cookie segura según arquitectura |
| Alta | Algunas descargas PDF reciben token por URL | Usar encabezado Bearer y descarga blob |
| Media | Sin rate limiting visible en login | Limitar intentos y auditar |
| Media | Mensajes distinguen usuario y contraseña incorrectos | Unificar respuesta de credenciales |
| Media | No hay matriz automatizada de permisos | Crear pruebas negativas por ruta y rol |

## 6. Evaluación por área

| Área | Evaluación |
|---|---|
| Sintaxis backend | Aprobada en revisión estática |
| Internacionalización | Aprobada en estructura y paridad de claves |
| Pruebas automáticas | Pendientes de implementación |
| Seguridad | Controles básicos presentes; riesgos altos pendientes |
| Spark frontend | Componentes y cliente HTTP presentes |
| Spark backend | Ausente en la versión revisada |
| Spark extremo a extremo | No funcional |

## 7. Acciones prioritarias

1. Añadir pruebas de autenticación y autorización antes de ampliar funcionalidad.
2. Eliminar secretos predeterminados y desactivar depuración.
3. Incorporar CI para análisis, pruebas y compilación.
4. Implementar y registrar el backend Spark antes de mostrar el módulo como disponible.
5. Ejecutar pruebas funcionales con una base exclusiva y conservar evidencia sin datos personales.

## 8. Conclusión

El código Python y los archivos de idioma no presentan errores en las verificaciones estáticas realizadas. Sin embargo, el Sprint 5 no debe considerarse completamente aprobado: faltan pruebas automatizadas y la integración Spark del backend. Los resultados pendientes y bloqueados quedan registrados para evitar afirmar funcionalidades no comprobadas.

