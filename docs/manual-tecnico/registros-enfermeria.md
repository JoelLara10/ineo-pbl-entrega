# Manual técnico — Registros de Enfermería

**Sistema:** INEO — React y API Hospital  
**Sprint:** 3 — Enfermería  
**Responsable:** Jesús  
**Historias:** ENF-001 a ENF-009

## 1. Objetivo

Documentar la implementación técnica del módulo de Enfermería: navegación, selección del paciente, endpoints, cuerpos JSON, colecciones MongoDB, historiales, autorización y comportamiento de caché.

## 2. Arquitectura del módulo

| Capa | Componentes |
|---|---|
| Presentación | `src/pages/enfermeria/` |
| Estado compartido | `PatientContext.jsx` |
| Comunicación | Instancia Axios de `src/services/api.js` |
| Caché | `localStorage` y `cacheService.js` |
| API | `routes/medical.py` |
| Negocio | `services/medical_service.py` y lógica de rutas de Enfermería |
| Validación | `schemas/schemas.py` y validaciones explícitas |
| Persistencia | MongoDB mediante `utils/database.py` |

La API utiliza el prefijo global `/api/v1`. Aunque el blueprint declara `url_prefix='/medical'`, se registra directamente con el prefijo global, por lo que las rutas efectivas observadas por React son `/api/v1/medico`, `/api/v1/paciente/...` y `/api/v1/appointments/...`.

## 3. Autenticación y roles

Todas las rutas requieren `token_required`. Las operaciones de escritura de Enfermería utilizan:

```python
@role_required('admin', 'medico', 'enfermero')
```

El router React permite las pantallas a `admin`, `enfermero` y `enfermeria`. Para evitar un acceso visible en React pero rechazado por Flask, se recomienda normalizar el rol almacenado a `enfermero` o ampliar conscientemente la política del backend.

Encabezado:

```http
Authorization: Bearer <token>
Content-Type: application/json
```

## 4. Rutas del frontend

| Ruta React | Pantalla |
|---|---|
| `/enfermeria` | Panel por áreas |
| `/enfermeria/paciente/:id` | Detalle compatible |
| `/enfermeria/paciente/:idAtencion/:idExp` | Detalle de paciente |
| `/enfermeria/signos-vitales` | Captura e historial de signos |
| `/enfermeria/nota` | Nota de Enfermería |
| `/enfermeria/medicamentos` | Administración de medicamentos |
| `/enfermeria/valoracion` | Valoración de Enfermería |
| `/enfermeria/cuidados` | Plan y cuidados |
| `/enfermeria/balance-hidrico` | Ingresos, egresos y balance |

Las pantallas obtienen `id_atencion` e `Id_exp` desde `PatientContext` o `location.state`.

## 5. Panel y selección del paciente

### GET `/api/v1/medico`

Devuelve tres grupos utilizados tanto por Médico como por Enfermería:

```json
{
  "beds_consulta": [],
  "beds_preparacion": [],
  "beds_recuperacion": []
}
```

Correspondencia en Enfermería:

| Respuesta | Área mostrada |
|---|---|
| `beds_consulta` | Consulta |
| `beds_preparacion` | Urgencias |
| `beds_recuperacion` | Hospitalizados |

La API consulta atenciones con estado `ABIERTA`, une pacientes y camas y marca los lugares como `OCUPADA` o `LIBRE`.

### GET `/api/v1/paciente/{id_atencion}/{Id_exp}`

Obtiene:

```json
{
  "paciente": {},
  "familiar": {},
  "medicos": [],
  "cama": {}
}
```

Responde 404 cuando no encuentra la combinación expediente–atención.

## 6. Signos vitales

### POST `/api/v1/appointments/{id_atencion}/vital-signs`

Cuerpo:

```json
{
  "ta": "120/80",
  "fc": "72",
  "fr": "18",
  "temp": "36.5",
  "spo2": "98",
  "peso": "70",
  "talla": "1.70"
}
```

La ruta añade el identificador del usuario autenticado y delega en `MedicalService.add_vital_signs`. Respuesta correcta: 201.

### GET `/api/v1/appointments/{id_atencion}/vital-signs`

Devuelve el historial de la atención. Requiere token; actualmente no aplica un decorador explícito de rol.

La estructura se corresponde con `VitalSignsSchema`, cuyos campos son opcionales. El frontend exige que al menos uno tenga contenido.

## 7. Notas de Enfermería

### POST `/api/v1/appointments/{id_atencion}/nursing-notes`

```json
{
  "nota_enfermeria": "Paciente consciente y orientado; se realizan cuidados indicados."
}
```

La API comprueba la atención y crea:

| Campo | Tipo lógico | Origen |
|---|---|---|
| `id_nota` | integer | Secuencia `nursing_notes_id` |
| `id_atencion` | integer | URL |
| `Id_exp` | integer | Atención encontrada |
| `nota` | string | `nota_enfermeria` |
| `id_enfermero` | ObjectId | Usuario autenticado |
| `fecha_registro` | datetime | Servidor |

Colección: `nursing_notes`. Respuesta: 201 con `id_nota`.

### GET `/api/v1/appointments/{id_atencion}/nursing-notes`

Realiza `$lookup` con `users`, proyecta `enfermero_nombre` y ordena por `fecha_registro` descendente.

## 8. Administración de medicamentos

### POST `/api/v1/appointments/{id_atencion}/medications`

```json
{
  "medicamentos": [
    {
      "nombre": "Medicamento de prueba",
      "dosis": "500 mg",
      "frecuencia": "Cada 8 horas",
      "via": "Oral",
      "fecha": "12/08/2026"
    }
  ]
}
```

La API almacena el arreglo completo en la colección `medications` con `id_registro`, atención, expediente, enfermero y fecha de servidor. Respuesta: 201.

### GET `/api/v1/appointments/{id_atencion}/medications`

Devuelve registros con medicamentos, fecha y nombre del profesional, ordenados del más reciente al más antiguo.

El backend acepta una lista vacía, pero el frontend descarta filas sin nombre. Se recomienda validar en la API que exista al menos un medicamento válido.

## 9. Valoración de Enfermería

### POST `/api/v1/appointments/{id_atencion}/nursing-assessment`

```json
{
  "estado_general": "Estable",
  "dolor": "2/10",
  "movilidad": "Con apoyo",
  "riesgo_caidas": "Medio",
  "riesgo_upp": "Bajo",
  "observaciones": "Se mantienen medidas preventivas."
}
```

Colección: `nursing_assessment`. Los campos clínicos se agrupan dentro de `valoracion`. El sistema genera `id_valoracion` y responde 201.

### GET `/api/v1/appointments/{id_atencion}/nursing-assessment`

Devuelve `id_valoracion`, `valoracion`, fecha y `enfermero_nombre`.

## 10. Balance hídrico

### POST `/api/v1/appointments/{id_atencion}/fluid-balance`

```json
{
  "ingresos_orales": 800,
  "ingresos_iv": 500,
  "egresos_orina": 900,
  "egresos_drenajes": 100,
  "observaciones": "Turno matutino"
}
```

La ruta convierte entradas a `float` y calcula:

```text
total_ingresos = ingresos_orales + ingresos_iv
total_egresos = egresos_orina + egresos_drenajes
balance_neto = total_ingresos - total_egresos
```

Colección: `fluid_balance`. Identificador: `id_balance`. Respuesta: 201.

### GET `/api/v1/appointments/{id_atencion}/fluid-balance`

Devuelve valores originales, totales, balance neto, observaciones, fecha y profesional.

Una cadena no numérica genera actualmente una excepción y puede producir 500; se recomienda validación previa con respuesta 400.

## 11. Cuidados de Enfermería

### POST `/api/v1/appointments/{id_atencion}/nursing-care`

```json
{
  "diagnostico_enfermeria": "Riesgo de caída",
  "objetivos": "Mantener al paciente sin caídas",
  "intervenciones": "Barandales elevados y acompañamiento",
  "evaluacion": "Sin incidentes durante el turno",
  "estado": "EN_PROCESO",
  "observaciones": "Continuar vigilancia"
}
```

Estados utilizados por React: `EN_PROCESO`, `PENDIENTE`, `COMPLETADO`.

Colección: `nursing_care`. Identificador: `id_cuidado`. La ruta utiliza `EN_PROCESO` como valor predeterminado.

### GET `/api/v1/appointments/{id_atencion}/nursing-care`

Devuelve diagnóstico, objetivos, intervenciones, evaluación, estado, observaciones, fecha y enfermero.

## 12. Respuestas y errores

| Código | Situación |
|---|---|
| 200 | Historial o detalle recuperado |
| 201 | Registro creado |
| 400 | Debería usarse para datos inválidos |
| 401 | Token ausente o inválido |
| 403 | Rol no autorizado |
| 404 | Atención o paciente no encontrado |
| 500 | Error de persistencia, conversión o excepción no controlada |

Formato común:

```json
{
  "error": "Atención no encontrada"
}
```

## 13. Caché del frontend

| Información | Prefijo aproximado | Vigencia |
|---|---|---|
| Panel de áreas | `ineo_web_cache_` | 5 minutos |
| Detalle del paciente | `ineo_web_cache_patient_detail_` | 2 minutos |
| Signos vitales | `ineo_web_cache_enfermeria_vital_signs_` | 2 minutos |
| Notas | `ineo_web_cache_enfermeria_notes_` | 2 minutos |
| Medicamentos | `ineo_web_cache_enfermeria_medications_` | 2 minutos |

La caché es una ayuda de lectura y no sustituye la persistencia en MongoDB. Tras una escritura, la pantalla debe volver a consultar el historial.

## 14. Trazabilidad y persistencia

Los registros creados directamente por las rutas de Enfermería incluyen:

- Identificador secuencial.
- `id_atencion`.
- `Id_exp`.
- `id_enfermero` obtenido del token.
- `fecha_registro` generada por el servidor.

Los historiales unen `id_enfermero` con `_id` de `users`. Debe comprobarse que el esquema de usuarios y el tipo almacenado sean compatibles.

## 15. Archivos relacionados

### Frontend

- `src/pages/enfermeria/EnfermeriaScreen.jsx`
- `src/pages/enfermeria/PatientDetailScreen.jsx`
- `src/pages/enfermeria/EnfermeriaVitalSignsScreen.jsx`
- `src/pages/enfermeria/EnfermeriaNoteScreen.jsx`
- `src/pages/enfermeria/EnfermeriaMedicationsScreen.jsx`
- `src/pages/enfermeria/EnfermeriaAssessmentScreen.jsx`
- `src/pages/enfermeria/EnfermeriaFluidBalanceScreen.jsx`
- `src/pages/enfermeria/EnfermeriaCareScreen.jsx`
- `src/context/PatientContext.jsx`
- `src/services/api.js`
- `src/services/cacheService.js`

### Backend

- `routes/medical.py`
- `services/medical_service.py`
- `schemas/schemas.py`
- `middleware/auth_middleware.py`
- `utils/database.py`
- `utils/sequences.py`

## 16. Pruebas mínimas

| Prueba | Resultado esperado |
|---|---|
| Panel con token válido | 200 y tres grupos |
| Detalle válido | 200 y datos de paciente |
| Atención inexistente | 404 |
| Escritura sin token | 401 |
| Escritura con rol ajeno | 403 |
| Registro válido | 201 e identificador |
| Consulta posterior | Registro visible al inicio del historial |
| Balance válido | Totales y balance correctos |
| Historial de otra atención | No incluye datos de la atención actual |

## 17. Mejoras técnicas recomendadas

- Crear esquemas Pydantic específicos para todos los registros de Enfermería.
- Validar rangos y unidades de signos vitales.
- Rechazar listas vacías de medicamentos.
- Rechazar volúmenes negativos y valores no numéricos con 400.
- Validar los estados de cuidados mediante enumeración.
- Unificar el nombre del rol entre React y Flask.
- Mover la lógica de persistencia restante desde las rutas a `MedicalService`.
- Implementar pruebas automatizadas de autorización y aislamiento por atención.
