# Plan de reversión — INEO Web y API

**Sprint:** 6 — Cierre  
**Responsable:** Jesús

## 1. Objetivo

Restablecer una versión estable cuando un despliegue provoque indisponibilidad, pérdida de funcionalidad, incompatibilidad de datos o una vulnerabilidad crítica.

## 2. Activadores

- `/health` no responde o devuelve errores después del despliegue.
- El frontend no compila o no puede comunicarse con la API.
- Fallan login, permisos o flujos clínicos principales.
- Se detecta corrupción o pérdida de datos.
- Se expone un secreto o información clínica.
- La tasa de errores es inaceptable para el equipo.

## 3. Preparación obligatoria

Antes de desplegar, registre:

```text
Versión anterior estable: ____________________
Versión nueva: ______________________________
Respaldo previo: ____________________________
Responsable: ________________________________
Fecha y hora: _______________________________
```

La versión estable debe ser un commit o tag probado. No use `git reset --hard` como procedimiento operativo.

## 4. Reversión de aplicación

1. Detenga el tráfico o habilite mantenimiento.
2. Conserve logs y evidencia del fallo.
3. Cambie a la etiqueta estable:

```powershell
git fetch --tags origin
git checkout TAG_ESTABLE
```

4. Reinstale dependencias si cambiaron.

Backend:

```powershell
cd backend\api_hospital
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Frontend:

```powershell
cd frontend\clinica-web-react
npm ci
npm run build
```

5. Publique el `dist/` generado por la versión estable.
6. Valide `/health`, login y los flujos prioritarios.

## 5. Reversión de base de datos

Solo restaure MongoDB si el despliegue modificó o corrompió datos. Volver el código no siempre exige volver los datos.

1. Bloquee escrituras.
2. Cree una copia del estado fallido para análisis.
3. Seleccione el respaldo anterior al despliegue.
4. Confirme que sea JSON, CSV/ZIP o XLSX restaurable; PDF es solo consulta.
5. Ejecute la restauración con un administrador desde Configuración.
6. Revise colecciones restauradas y fallidas.
7. Valide conteos y relaciones de pacientes, atenciones, usuarios y catálogos.

Una respuesta HTTP 409 indica restauración parcial y exige intervención; no reactive el servicio hasta resolverla.

## 6. Reversión por secreto expuesto

1. Retire acceso al sistema afectado.
2. Rote `SECRET_KEY`, `JWT_SECRET_KEY` y credenciales MongoDB.
3. Invalide sesiones activas.
4. Elimine el secreto del ambiente y revise el historial con el responsable del repositorio.
5. Documente el incidente sin publicar el valor comprometido.

## 7. Validación posterior

```text
[ ] API /health = 200
[ ] MongoDB accesible
[ ] Login válido
[ ] Roles protegidos
[ ] Pacientes y atenciones consultables
[ ] Registros de Enfermería y Médico disponibles
[ ] Estudios y archivos accesibles
[ ] Configuración administrativa restringida
[ ] Sin errores críticos en logs
[ ] Usuarios informados del restablecimiento
```

## 8. Registro de la reversión

| Campo | Valor |
|---|---|
| Incidente |  |
| Versión retirada |  |
| Versión restaurada |  |
| Respaldo utilizado |  |
| Inicio / fin |  |
| Responsable |  |
| Resultado |  |
| Acciones preventivas |  |

## 9. Cierre

Después de estabilizar, abra una corrección en una rama nueva y preserve la evidencia. La reversión no debe ocultar el defecto ni reescribir el historial compartido.
