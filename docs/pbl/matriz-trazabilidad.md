# Matriz de trazabilidad del PBL INEO

**Sistema:** Sistema de Gestión Clínica INEO  
**Sprint:** 6 — Cierre  
**Responsable:** Jesús  
**Repositorio de integración:** `ineo-pbl-entrega`

## 1. Objetivo

Relacionar los objetivos del PBL con historias, componentes, documentación, evidencia y validación. Esta matriz permite comprobar qué elemento satisface cada requisito sin atribuir al repositorio de integración el historial de desarrollo de los repositorios originales.

## 2. Escala de estado

| Estado | Interpretación |
|---|---|
| Integrado | Código o documento incorporado en la entrega |
| Documentado | Funcionamiento y criterios descritos |
| Validado | Existe evidencia o prueba revisada |
| Pendiente de evidencia | Implementado, pero requiere anexar resultado final |

## 3. Trazabilidad funcional

| ID | Requisito / historia | Sprint | Implementación principal | Documento / evidencia | Criterio verificable | Estado de cierre |
|---|---|---:|---|---|---|---|
| MIG-001 | Inventariar el sistema anterior | 1 | Repositorios originales API y web | `docs/sprints/sprint-1/inventario-sistema-anterior.md` | Componentes, dependencias y riesgos identificados | Documentado |
| MIG-002 | Definir arquitectura objetivo y migración | 1 | React, Flask, MongoDB y API REST | `docs/arquitectura/arquitectura-general.md`, `migracion-flask-react.md` | Capas, responsabilidades y flujo descritos | Documentado |
| ADM-001 | Registrar y consultar pacientes | 2 | `routes/patients.py`, pantallas administrativas | `docs/manual-usuario/modulo-pacientes.md` | Alta, búsqueda, consulta y edición controladas | Integrado |
| ADM-002 | Administrar censo y atención | 2 | `routes/administrative.py`, `CensoScreen.jsx` | `docs/sprints/sprint-2/flujo-pacientes.md` | Atención abierta visible por área y cama | Integrado |
| ADM-003 | Gestionar cuenta, cargos y pagos | 2 | `routes/billing.py`, detalle de paciente | `docs/manual-tecnico/endpoints-administrativos.md` | Saldo y movimientos asociados a la atención | Integrado |
| ENF-001–009 | Registros de Enfermería | 3 | `routes/medical.py`, `pages/enfermeria/` | `docs/sprints/sprint-3/criterios-enfermeria.md` | Signos, notas, medicamentos, valoración, balance y cuidados | Documentado |
| MED-001 | Panel y expediente médico | 4 | `pages/medico/`, `routes/medical.py` | `docs/manual-usuario/modulo-medico.md` | Médico selecciona atención y consulta expediente | Integrado |
| MED-002 | Nota, diagnóstico y receta | 4 | Servicios médicos y catálogos | `docs/manual-usuario/modulo-medico.md` | Registros ligados a `id_atencion` | Integrado |
| EST-001 | Solicitar y procesar estudios | 4 | `routes/exams.py`, `routes/studies.py` | `docs/manual-usuario/modulo-estudios.md` | Solicitud pasa de pendiente a completada | Integrado |
| CFG-001 | Administrar catálogos y usuarios | 4 | `routes/beds.py`, `catalog.py`, `auth.py` | `docs/manual-usuario/modulo-configuracion.md` | CRUD protegido por rol | Integrado |
| CFG-002 | Respaldar y restaurar MongoDB | 4 | `routes/backup.py`, `utils/backups.py` | `docs/manual-tecnico/respaldos.md` | Crea, lista, descarga y restaura formatos compatibles | Documentado |
| I18N-001 | Interfaz español/inglés | 4 | `src/i18n/` y `react-i18next` | `docs/manual-tecnico/internacionalizacion.md` | Claves equivalentes y cambio de idioma | Documentado |
| QA-001 | Pruebas de API y web | 5 | `tests/`, flujos CI cuando estén integrados | `docs/manual-tecnico/pruebas.md`, evidencias Zahid/Joel | Resultados reproducibles sin errores críticos | Pendiente de evidencia final |
| SEC-001 | Autenticación y autorización | 5 | JWT/token, middleware de roles, rutas privadas | `docs/manual-tecnico/seguridad.md` | Accesos no autorizados producen 401/403 | Documentado |
| ANA-001 | Análisis con Spark | 5 | Rutas, servicios y pantallas Spark funcionales | `docs/manual-tecnico/spark.md` | Ejecución y resultados disponibles si el módulo funciona | Pendiente de evidencia final |
| CIE-001 | Despliegue y reversión | 6 | API Flask, frontend Vite y MongoDB | `docs/deployment/despliegue.md`, `reversion.md` | Instalación y retorno a versión estable reproducibles | Documentado |
| CIE-002 | Cierre y trazabilidad | 6 | Documentación y evidencias del equipo | `docs/pbl/acta-cierre.md`, Excel final, `CHANGELOG.md` | Entregables localizables y responsables definidos | Documentado |

## 4. Trazabilidad por sprint y responsable

| Sprint | Alcance | Responsable de integración | Responsable documental / evidencia |
|---:|---|---|---|
| 1 | Arquitectura y bases | Equipo | Jesús; diseño Jaime; API Zahid; web Joel |
| 2 | Pacientes y administración | Zahid / Joel | Jesús; validación Jaime |
| 3 | Enfermería | Zahid / Joel | Jesús; validación Jaime |
| 4 | Médico, estudios y configuración | Zahid / Joel | Jesús; validación Jaime |
| 5 | Calidad, seguridad y Spark | Zahid / Joel | Jesús; accesibilidad Jaime |
| 6 | Cierre | Equipo | Jesús consolida PBL; cada integrante entrega evidencia propia |

## 5. Control de evidencia

| Evidencia | Responsable | Ruta | Validación de cierre |
|---|---|---|---|
| Resultado final API | Zahid | `evidence/zahid/resultados-api.md` | Debe incluir comandos, fecha y resultados |
| Resultado final web | Joel | `evidence/joel/resultados-web.md` | Debe incluir build, lint y flujo funcional |
| Validación visual | Jaime | `design/validacion-final-diseno.md` | Debe cubrir responsive y accesibilidad |
| Documentación y trazabilidad | Jesús | `docs/pbl/`, `docs/deployment/`, `PBL/` | Rutas, versiones y cierre consistentes |

## 6. Reglas para dar un requisito por cerrado

Un requisito solo se marca **Validado** cuando el código está en `main`, el criterio puede reproducirse, no utiliza datos clínicos reales y la evidencia identifica comando, resultado y fecha. La existencia de un archivo planeado no equivale por sí sola a una prueba aprobada.

## 7. Resultado

La matriz cubre los seis sprints y conserva la relación entre requisito, implementación, documentación, responsable y evidencia. Los estados pendientes deben actualizarse en el Excel y en esta matriz después de integrar los Pull Requests finales.
