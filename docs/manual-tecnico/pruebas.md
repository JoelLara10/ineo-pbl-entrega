# Manual técnico — Estrategia de pruebas

**Sistema:** INEO — React y API Hospital  
**Sprint:** 5 — Calidad, Seguridad y Spark  
**Responsable:** Jesús  
**Fecha de revisión:** 14 de agosto de 2026

## 1. Objetivo

Definir una estrategia reproducible para verificar la API Flask, el frontend React, la autenticación, los permisos, los módulos clínicos y la integración analítica sin utilizar datos reales de pacientes.

## 2. Alcance comprobado

La revisión cubre los repositorios `api_hospital` y `clinica-web-react`. En el estado analizado no existen directorios de pruebas automatizadas ni flujos CI incorporados. Por ello, este documento distingue entre verificaciones estáticas ejecutadas y pruebas funcionales que deben realizarse cuando estén disponibles MongoDB, la API y el frontend.

## 3. Pirámide de pruebas propuesta

| Nivel | Objetivo | Herramientas sugeridas |
|---|---|---|
| Unitarias | Validadores, servicios, serialización y cálculos | `pytest`, mocks de MongoDB |
| Integración API | Rutas, JWT, roles, códigos HTTP y persistencia | Cliente de pruebas de Flask |
| Componentes web | Formularios, estados vacíos y permisos | Vitest y Testing Library |
| Extremo a extremo | Flujos completos por rol | Playwright o Cypress |
| Seguridad | Autorización, entradas y archivos | Casos negativos automatizados |

Las herramientas listadas constituyen una recomendación de implementación; no deben reportarse como instaladas o ejecutadas hasta que sus archivos formen parte del repositorio.

## 4. Preparación del entorno

1. Crear una base MongoDB exclusiva para pruebas.
2. Definir `SECRET_KEY`, `JWT_SECRET_KEY`, URI de MongoDB y orígenes CORS mediante variables de entorno.
3. Usar usuarios ficticios para los roles `admin`, `administrativo`, `medico`, `enfermero` y `estudios`.
4. No copiar respaldos, resultados médicos ni credenciales de producción.
5. Iniciar la API y verificar `GET /health`.
6. Iniciar React y confirmar la URL configurada en `VITE_API_URL`.

## 5. Casos mínimos para la API

| ID | Caso | Resultado esperado |
|---|---|---|
| API-001 | `GET /health` | 200 con estado `ok` |
| API-002 | Inicio de sesión válido | 200, token y usuario sin contraseña |
| API-003 | Inicio de sesión incompleto | 400 |
| API-004 | Ruta protegida sin token | 401 |
| API-005 | Token inválido o expirado | 401 |
| API-006 | Rol no autorizado | 403 |
| API-007 | Recurso inexistente | 404 en JSON |
| API-008 | Alta de paciente sin campos requeridos | 400 |
| API-009 | Consulta de atención válida | 200 y expediente correspondiente |
| API-010 | Error interno controlado | 500 sin traza sensible |

## 6. Casos por módulo

### Administración

- Crear, consultar y editar un paciente ficticio.
- Abrir y cerrar una atención.
- Registrar cargos y pagos válidos.
- Rechazar importes negativos o datos incompletos.
- Verificar que solo los roles autorizados modifiquen cuentas.

### Médico y Enfermería

- Seleccionar una atención abierta.
- Guardar signos vitales y consultar historial.
- Registrar nota médica SOAP y nota de Enfermería.
- Registrar diagnóstico, receta, valoración, cuidados y balance hídrico.
- Confirmar que los registros queden ligados al `id_atencion` correcto.

### Estudios

- Solicitar examen como médico.
- Consultar pendientes como personal de Estudios.
- Cargar, visualizar, editar y eliminar un resultado ficticio.
- Rechazar archivos o identificadores inválidos.

### Configuración y respaldos

- Probar CRUD de camas, usuarios, diagnósticos y servicios.
- Crear respaldos JSON, CSV/ZIP, XLSX y PDF.
- Restaurar únicamente formatos compatibles.
- Confirmar que un usuario sin rol `admin` reciba 403.

## 7. Pruebas del frontend

Ejecutar, cuando las dependencias estén instaladas:

```powershell
npm run lint
npm run build
```

El `package.json` actual no contiene un script `test`. Para validar manualmente:

1. Recorrer cada ruta protegida con un rol permitido y otro denegado.
2. Probar carga, error, vacío y datos disponibles.
3. Confirmar limpieza de sesión después de una respuesta 401.
4. Cambiar entre español e inglés.
5. Revisar formularios en escritorio y pantalla móvil.

## 8. Datos y evidencias

Cada ejecución debe registrar fecha, versión o commit, entorno, caso, resultado esperado, resultado obtenido, estado y evidencia. Las capturas deben ocultar nombres, expedientes, tokens y contraseñas.

Formato recomendado:

| Caso | Commit | Resultado | Estado | Evidencia |
|---|---|---|---|---|
| API-004 | `<hash>` | 401 sin token | Aprobado | `evidence/...` |

## 9. Criterio de salida

El Sprint puede considerarse validado cuando las pruebas críticas de autenticación, autorización y persistencia pasan; no existen defectos bloqueantes; el frontend compila; y cualquier función incompleta, incluida Spark, está marcada expresamente como pendiente.

