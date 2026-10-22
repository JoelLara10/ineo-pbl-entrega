# PBL-33-T3 — Preparar datos y ambiente UAT

## Ambiente de la revalidación simulada del 22 de octubre

La simulación autorizada por Joel usó frontend `127.0.0.1:5189`, Flask `127.0.0.1:5019` y una instancia MongoDB 8.2 exclusiva en `127.0.0.1:27029`, base `ineo_test_uat_simulation`. Los datos fueron creados por `testing.uat_server` y no proceden del sistema clínico real. Se usó el motor ligero real para verificar las vistas de análisis. El Word de preparación original se conserva como evidencia de la sesión histórica de Jaime y no describe este ambiente nuevo.

**Historia:** PBL-33 — UAT con usuarios representativos  
**Sprint:** 3 (Azure Sprint 9)  
**Dependencias:** PBL-33-T2; ambiente PBL-26; contratos PBL-13; endpoints PBL-43  
**Responsable:** Jaime  
**Fechas planificadas:** 2026-10-19 → 2026-10-19  
**Estado:** Completado (checklist y evidencia de precondiciones)

---

## 1. Objetivo

Preparar usuarios y datos sintéticos; comprobar manualmente la comunicación web-API, login, permisos y persistencia de los flujos del incremento **antes** de convocar a los usuarios representativos. Registrar evidencia y bloquear la sesión UAT si falla alguna precondición.

## 2. Ambiente UAT

| Elemento | Valor / ubicación |
|----------|-------------------|
| API | Ambiente de pruebas (local o staging; puerto documentado en README / compose.test.yml) |
| Frontend | Aplicación React (Vite) apuntando a `VITE_API_URL` del ambiente UAT |
| Base de datos | MongoDB con datos sintéticos (sin datos clínicos reales) |
| Contrato | `contracts/v1/api.schema.json` |
| Versión del incremento | feature/sprint9 sincronizada con develop (Sprint 3 / Azure 9) |

**Regla de bloqueo:** Si cualquier precondición crítica falla, no se convoca a usuarios y se registra el bloqueo.

## 3. Usuarios sintéticos de prueba

| Usuario | Rol | Uso en UAT |
|-------------------|-----|------------|
| enfermera.uat@ineo.test | Enfermería | CP-UAT-001 |
| admin.uat@ineo.test | Administración | CP-UAT-002 |
| po.uat@ineo.test | Product Owner / observador | Firma de acta |

## 4. Datos sintéticos

### Para CP-UAT-001 (Enfermería)

- Paciente sintético.
- Datos demográficos y clínicos mínimos no reales.
- Caso clínico sintético suficiente para completar un turno/valoración completa.

### Para CP-UAT-002 (Analytics)

- Indicadores conocidos (periodo, unidad, valores de referencia).
- Datos que permitan visualizar al menos una gráfica o KPI interpretable.
- Evitar conjuntos vacíos o estados de error no controlados durante la sesión UAT.

## 5. Checklist de precondiciones (comprobación manual)

| # | Precondición | Resultado | Fecha | Evidencia | Responsable |
|---|--------------|-----------|-------|-----------|-------------|
| 1 | API responde en `/health` (o equivalente) | ☐ OK / ☐ Falla | | | |
| 2 | Frontend carga y se conecta a la API UAT | ☐ OK / ☐ Falla | | | |
| 3 | Login con rol Enfermería funciona | ☐ OK / ☐ Falla | | | |
| 4 | Login con rol Administración funciona | ☐ OK / ☐ Falla | | | |
| 5 | Permisos: Enfermería no accede a funciones de Administración no autorizadas | ☐ OK / ☐ Falla | | | |
| 6 | Permisos: Administración ve Analytics | ☐ OK / ☐ Falla | | | |
| 7 | Persistencia: registro de Enfermería se guarda y se consulta | ☐ OK / ☐ Falla | | | |
| 8 | Analytics muestra indicadores / gráficas con datos sintéticos | ☐ OK / ☐ Falla | | | |
| 9 | Datos sintéticos cargados y no reales | ☐ OK / ☐ Falla | | | |
| 10 | Versión del incremento identificada y documentada | ☐ OK / ☐ Falla | | | |

**Decisión de go / no-go:**

- **GO:** Todas las precondiciones críticas (1–10) en OK → se convoca a usuarios.
- **NO-GO:** Cualquier falla crítica → se bloquea la sesión UAT, se registra el defecto y se corrige antes de reintentar.

## 6. Evidencia de preparación

Registrar en este documento o en anexos:

- Capturas de `/health` y de las pantallas de login.
- Resultado de un registro de prueba de Enfermería (ID o referencia).
- Captura de la vista Analytics con indicadores visibles.
- Nota de la versión/commit o etiqueta del incremento bajo prueba.

## 7. Registro de bloqueo (si aplica)

| Fecha | Motivo del bloqueo | Precondición fallida | Acción correctiva | Responsable | Fecha de desbloqueo |
|-------|--------------------|----------------------|-------------------|-------------|---------------------|
| | | | | | |

## 8. Definición de terminado (T3)

- Usuarios y datos sintéticos preparados.
- Comunicación web-API, login, permisos y persistencia comprobados.
- Evidencia registrada.
- Decisión GO/NO-GO documentada.
- Listo para aplicar UAT con usuarios (T4) solo si hay GO.

---

**Documento generado para PBL-33-T3.**  
**Siguiente tarea:** PBL-33-T4 — Aplicar UAT con usuarios representativos.
