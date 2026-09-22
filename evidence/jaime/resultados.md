# Evidencia PBL-03-T4 — Análisis clínico

**Historia:** PBL-03  
**Tarea:** T4 — Conectar permisos, traducciones, estados y manejo de errores  
**Responsable:** Jaime Díaz González  
**Fecha:** 2005-09-22
**Rama:** `feature/pbl-03-analisis-clinico`  


## 1. Objetivo

Demostrar que la interfaz cumple el criterio de aceptación:

> La interfaz cambia entre pendiente, procesando, completado y fallido; al completarse muestra datos reales.

Y que permisos, i18n y errores HTTP están conectados a los módulos relacionados.

## 2. Entorno

| Elemento | Valor |
|---|---|
| API | `http://localhost:5001` |
| Frontend | `http://localhost:5173` |


## 3. Capturas (adjuntar en esta carpeta)

| Archivo | Estado | Cómo obtenerla |
|---|---|---|
| `01-pendiente.png` | Pendiente | Login → `/admin/spark/clinical` sin job previo |
| `02-procesando.png` | Procesando | Clic en **Ejecutar análisis** (capturar antes de que termine) |
| `03-completado.png` | Completado | Tras el polling; debe verse agregados (diagnósticos / edad / estancia) |
| `04-fallido.png` | Fallido | Forzar fallo (p. ej. detener Mongo un momento y ejecutar) o inyectar error en prueba |
| `05-medico-menu.png` | Permiso médico | Login como `medico`; debe verse entrada Spark y solo clínica |
| `06-403-o-idioma.png` | Extra | Opcional: 403 con rol no autorizado, o cambio ES↔EN en estados |

**Regla:** no capturar nombres, expedientes ni estudios de pacientes reales.

## 4. Comandos ejecutados

```bash
cd backend/api_hospital
pytest -v tests/test_spark_clinical.py
# Resultado: _________________ passed

cd frontend/clinica-web-react
npm test
# Resultado: _________________ passed
```

## 5. Checklist de cierre T4

- [ ] Médico entra a `/admin/spark` y `/admin/spark/clinical`
- [ ] Médico **no** ve analytics / met / unsupervised (menú y rutas)
- [ ] Textos **Pendiente / Procesando / Completado / Fallido** visibles en ES
- [ ] Mismas claves en EN (paridad)
- [ ] 403 muestra “Sin permiso”
- [ ] 409 muestra “Análisis en curso” y refresca estado
- [ ] Completado con datos reales de Mongo (no mocks fijos en pantalla)
- [ ] `docs/manual-tecnico/spark.md` actualizado
- [ ] Capturas sin PHI en `evidence/<tu-nombre>/pbl-03/`


