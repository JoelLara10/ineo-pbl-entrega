# Manual técnico — Respaldos y restauración

**Sistema:** INEO — Flask, MongoDB y React  
**Sprint:** 4 — Médico, Estudios y Configuración  
**Responsable:** Jesús

## 1. Objetivo y componentes

Documentar la API, persistencia de archivos, formatos, automatización y controles de seguridad del subsistema de respaldos.

| Capa | Archivo principal |
|---|---|
| UI | `src/pages/config/BackupConfigScreen.jsx` |
| Automatización UI | `src/pages/config/AutomationConfigScreen.jsx` |
| Cliente HTTP | `src/services/backupService.js` |
| Blueprint Flask | `routes/backup.py` |
| Lógica de respaldo | `utils/backups.py` |
| Programación | `scheduler/jobs.py` |
| Almacenamiento | `backups/` |

El prefijo efectivo es `/api/v1/backup`. Todas las operaciones administrativas exigen token; salvo `health`, también requieren rol `admin`.

## 2. Endpoints

| Método | Ruta | Función |
|---|---|---|
| GET | `/backup` | Listar respaldos |
| GET | `/backup/collections` | Listar colecciones MongoDB |
| POST | `/backup/create` | Crear un respaldo |
| POST | `/backup/restore` | Restaurar un archivo existente |
| GET | `/backup/download/{filename}` | Descargar |
| DELETE | `/backup/{filename}` | Eliminar |
| POST | `/backup/clean` | Conservar los últimos N |
| GET/PUT | `/backup/automation` | Leer o actualizar automatización |
| GET | `/backup/health` | Comprobar MongoDB |

Encabezado requerido:

```http
Authorization: Bearer <token>
Content-Type: application/json
```

## 3. Crear un respaldo

```json
{
  "tipo": "completa",
  "formato": "json",
  "colecciones": ["pacientes", "atencion", "users"]
}
```

Tipos válidos: `completa`, `incremental`, `diferencial`. Formatos válidos: `json`, `csv`, `xlsx`, `pdf`; `excel` se normaliza a `xlsx`.

- Completa: incluye todos los documentos seleccionados.
- Incremental: consulta cambios posteriores a la última copia.
- Diferencial: consulta cambios posteriores a la última copia completa.

La detección de cambios usa `updated_at`, `fecha_modificacion` o la fecha implícita del `_id`. Si las colecciones no mantienen estos campos de forma consistente, un respaldo incremental o diferencial puede omitir modificaciones; la completa es la referencia más segura.

## 4. Formatos

| Formato | Archivo | Restaurable | Detalle |
|---|---|---:|---|
| JSON | `.json` | Sí | BSON serializado con metadatos y datos |
| CSV | `.zip` | Sí | Un CSV por colección y `metadata.json` |
| Excel | `.xlsx` | Sí | Hoja por colección y metadatos ocultos |
| PDF | `.pdf` | No | Reporte de consulta; limita filas y columnas visibles |

Los archivos incluyen versión, base de datos, fecha, tipo, formato, origen automático, colecciones y conteos.

## 5. Restauración

```json
{ "filename": "backup_manual_completa_2026-08-12_20-00-00.json" }
```

La utilidad valida el nombre, extensión y existencia. Rechaza rutas con directorios y rutas internas peligrosas dentro de ZIP. PDF no puede restaurarse. Si algunas colecciones fallan, la API responde `409` e informa `collections` restauradas y `failed_collections`; por ello una restauración parcial requiere revisión manual inmediata.

Antes de restaurar:

1. Crear una copia completa actual.
2. Confirmar base de datos y archivo.
3. Restringir operaciones concurrentes.
4. Verificar espacio disponible.

Después, validar conteos, usuarios, pacientes, atenciones y catálogos.

## 6. Automatización

```json
{
  "activo": true,
  "tipo": "completa",
  "formato": "json",
  "intervalo": 1440,
  "colecciones": ["pacientes", "atencion"],
  "max_backups": 4
}
```

El intervalo acepta 5–525600 minutos y `max_backups` se limita a 1–50. La configuración se guarda en `backups/automation.json` y `configure_backup_job` actualiza la tarea. `control.json` conserva las fechas base de copias completas e incrementales.

## 7. Códigos de respuesta

| Código | Significado |
|---:|---|
| 200 | Consulta, eliminación, restauración o sin cambios nuevos |
| 201 | Respaldo creado |
| 400 | Parámetros, formato o archivo inválido |
| 401/403 | Sesión o rol no autorizado |
| 404 | Respaldo no encontrado |
| 409 | Restauración parcial |

## 8. Seguridad y operación

- El backend aplica `os.path.basename` y comparación del nombre para evitar traversal.
- No deben versionarse `.env`, respaldos reales ni datos de pacientes.
- El directorio `backups/` necesita permisos de lectura y escritura únicamente para el servicio.
- Los archivos deben cifrarse o trasladarse a almacenamiento protegido según la política institucional.
- La limpieza automática no sustituye una política externa de retención.
- Deben probarse restauraciones periódicamente en una base aislada.

## 9. Pruebas mínimas

1. Crear cada formato y verificar listado/descarga.
2. Restaurar JSON, ZIP y XLSX en una base de prueba.
3. Confirmar que PDF tenga restauración deshabilitada.
4. Probar usuario sin rol administrador.
5. Probar filename con `../` y extensiones no válidas.
6. Simular una colección fallida y comprobar respuesta 409.
7. Verificar tarea automática, intervalo y retención.

## 10. Criterio de aceptación

El módulo crea y lista respaldos, protege las rutas administrativas, diferencia formatos restaurables, reporta restauraciones parciales y conserva una automatización válida sin incluir datos clínicos en Git.
