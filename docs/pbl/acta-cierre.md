# Acta de cierre del PBL — Sistema INEO

**Sprint:** 6 — Cierre  
**Responsable de consolidación documental:** Jesús  
**Equipo:** Joel, Jesús, Jaime y Zahid  
**Fecha de elaboración:** 14 de agosto de 2026

## 1. Propósito

Formalizar el cierre de la entrega de integración del Sistema de Gestión Clínica INEO, registrar el alcance consolidado, los entregables, las validaciones requeridas y las condiciones para considerar aceptada la versión final.

## 2. Naturaleza del repositorio

`ineo-pbl-entrega` es el repositorio de integración, documentación y reconstrucción organizada del PBL. Los commits reflejan la incorporación por sprints de trabajo previamente desarrollado; los repositorios originales de la API Flask y la aplicación React conservan el historial de desarrollo anterior.

## 3. Alcance entregado

- Arquitectura React–Flask–MongoDB y estrategia de migración.
- Administración de pacientes, atenciones, censo, cuentas y pagos.
- Registros clínicos de Enfermería.
- Flujo médico, diagnósticos, recetas y documentos.
- Solicitudes y resultados de laboratorio y gabinete.
- Configuración, usuarios, camas, catálogos, respaldos e idiomas.
- Documentación de pruebas, seguridad y analítica/Spark cuando el módulo sea funcional.
- Procedimientos de despliegue y reversión.
- Matriz y libro Excel de trazabilidad final.

## 4. Entregables de cierre

| Entregable | Ruta | Responsable |
|---|---|---|
| Matriz de trazabilidad | `docs/pbl/matriz-trazabilidad.md` | Jesús |
| Acta de cierre | `docs/pbl/acta-cierre.md` | Jesús |
| Guía de despliegue | `docs/deployment/despliegue.md` | Jesús |
| Plan de reversión | `docs/deployment/reversion.md` | Jesús |
| Historial de cambios | `CHANGELOG.md` | Jesús |
| Libro final PBL | `PBL/PBL_FINAL_INEO_WEB_API_Y_COMMITS.xlsx` | Jesús |
| Evidencia API | `evidence/zahid/resultados-api.md` | Zahid |
| Evidencia web | `evidence/joel/resultados-web.md` | Joel |
| Validación final de diseño | `design/validacion-final-diseno.md` | Jaime |

## 5. Criterios de aceptación

1. Los Pull Requests de los seis sprints están integrados en `main`.
2. `git status` está limpio y no existen conflictos sin resolver.
3. La API inicia, `/health` responde 200 y conecta con MongoDB.
4. El frontend compila y se comunica con `/api/v1`.
5. Los roles limitan rutas administrativas, médicas, de Enfermería y Estudios.
6. No se incluyen `.env`, contraseñas, tokens, respaldos, uploads ni datos reales.
7. Las evidencias finales señalan comando, fecha, resultado y responsable.
8. El procedimiento de reversión fue revisado antes de liberar.

## 6. Riesgos y asuntos abiertos

| Riesgo | Tratamiento de cierre |
|---|---|
| Secretos predeterminados en configuración | Sustituir por variables seguras antes de producción |
| Orígenes CORS codificados | Definir orígenes del ambiente de despliegue |
| Datos clínicos en archivos generados | Mantener `backups/`, `uploads/` y resultados reales fuera de Git |
| Spark no funcional en el ambiente final | No declararlo terminado; adjuntar evidencia cuando funcione |
| Dependencia de MongoDB local | Documentar servicio, URI, base y respaldo previo |
| Evidencias de terceros pendientes | No marcar como Validado hasta integrar sus archivos |

## 7. Aprobación técnica previa al cierre

```text
[ ] API validada por Zahid
[ ] Web validada por Joel
[ ] Diseño y accesibilidad validados por Jaime
[ ] Documentación y trazabilidad validadas por Jesús
[ ] Revisión final del equipo
[ ] Integración en main
[ ] Etiqueta de versión creada
```

## 8. Declaración de cierre

La documentación de cierre queda preparada para la entrega. La aceptación definitiva se produce únicamente al completar la lista anterior y anexar las evidencias reales; este documento no sustituye los resultados técnicos de prueba.

## 9. Firmas

| Rol | Nombre | Confirmación / fecha |
|---|---|---|
| Integración web | Joel | ____________________ |
| Documentación | Jesús | ____________________ |
| Diseño y validación | Jaime | ____________________ |
| Integración API | Zahid | ____________________ |
| Docente / revisor |  | ____________________ |
