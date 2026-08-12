# Manual técnico — Endpoints administrativos

**Sistema:** INEO — API Hospital  
**Sprint:** 2 — Pacientes y Administrativo  
**Responsable:** Jesús  
**API:** Flask REST — versión 1

## 1. Objetivo

Describir los endpoints utilizados por el frontend React para gestión de pacientes, censo, cuentas, pagos, facturación, reportes y documentos administrativos.

## 2. Configuración común

| Elemento | Valor |
|---|---|
| URL de desarrollo | `http://localhost:5001` |
| Prefijo de API | `/api/v1` |
| Formato principal | `application/json` |
| Autorización | `Authorization: Bearer <token>` |
| Roles administrativos | `admin`, `administrativo` |

Ejemplo de encabezados:

```http
Authorization: Bearer eyJ...
Content-Type: application/json
```

Los endpoints protegidos pueden responder 401 si el token no es válido y 403 si el rol no cuenta con permiso.

## 3. Códigos de respuesta

| Código | Uso |
|---|---|
| 200 | Consulta o actualización realizada correctamente |
| 201 | Recurso creado correctamente |
| 400 | Datos inválidos o regla de negocio incumplida |
| 401 | Token ausente, inválido o vencido |
| 403 | Rol sin autorización |
| 404 | Recurso inexistente |
| 500 | Error interno no controlado |

## 4. Opciones administrativas

### GET `/api/v1/options`

Obtiene catálogos utilizados por el formulario: áreas, motivos, especialidades, camas, médicos, servicios y medicamentos.

Parámetros opcionales:

| Parámetro | Tipo | Descripción |
|---|---|---|
| `current_id_cama` | string/int | Incluye la cama actual durante una edición |
| `all` | boolean | Solicita el conjunto completo de opciones |

Respuesta esperada:

```json
{
  "areas": [],
  "motivos": [],
  "especialidades": [],
  "camas": [],
  "medicos": [],
  "servicios": [],
  "medicamentos": []
}
```

## 5. Gestión de pacientes

### GET `/api/v1/gestion-pacientes`

Devuelve pacientes agrupados y un resumen administrativo. La API también admite los alias `/gestion_pacientes` y `/patients`.

Parámetros comunes:

| Parámetro | Tipo | Descripción |
|---|---|---|
| `search` | string | Texto de búsqueda |
| `page` | integer | Página solicitada |
| `limit` | integer | Registros por página |
| `all` | boolean | Solicita todos los registros para filtrado local |

El frontend espera grupos como `activos`, `expedientes` y `altas`, además de `summary`.

### GET `/api/v1/patients/search`

Búsqueda rápida de pacientes.

```http
GET /api/v1/patients/search?q=Gonzalez&limit=10
```

El límite máximo aplicado por la ruta es 50.

### GET `/api/v1/patients/{id_exp}`

Obtiene el detalle de un expediente, incluyendo información personal, atención activa, médicos y familiar cuando estén disponibles.

### POST `/api/v1/patients`

Crea el paciente y su atención administrativa.

Ejemplo de cuerpo:

```json
{
  "curp": "GODE000101MMCNNNA1",
  "papell": "Gonzalez",
  "sapell": "Diaz",
  "nom_pac": "Ejemplo",
  "fecnac": "2000-01-01",
  "tel": "7220000000",
  "area": "Consulta",
  "cama": "",
  "motivo": "Consulta",
  "especialidad": "Oftalmologia",
  "alergias": "Ninguna conocida",
  "fam_nombre": "Familiar de prueba",
  "fam_parentesco": "Madre",
  "fam_tel": "7220000001",
  "assignedDoctors": [12]
}
```

Campos obligatorios en el frontend: `curp`, `papell`, `nom_pac` y `fecnac`. La API debe realizar su propia validación y no depender únicamente del navegador.

### PUT `/api/v1/patients/{id_exp}`

Actualiza un expediente. Acepta un cuerpo equivalente al registro y conserva el identificador enviado en la URL.

### GET `/api/v1/documents/patients`

Obtiene pacientes o atenciones disponibles para generación de documentos administrativos.

## 6. Censo

### GET `/api/v1/censo`

Alias principal usado por React. También está disponible `/census`.

Parámetros: `search`, `page`, `limit` y `all`.

Respuesta lógica:

```json
{
  "summary": {
    "activos": 0,
    "areas": 0,
    "avisos": 0
  },
  "sections": []
}
```

### GET `/api/v1/census`

El blueprint de reportes también expone una consulta de censo para reportes. Debe distinguirse del alias administrativo por su propósito y formato de respuesta.

### GET `/api/v1/census/pdf`

Exporta el censo en PDF.

### GET `/api/v1/census/excel`

Exporta el censo en Excel.

## 7. Corte de caja y reportes

### GET `/api/v1/corte-caja`

Devuelve el corte operativo utilizado por la pantalla React. También existen los alias `/cash-cut` y `/corte_caja`.

Parámetros opcionales:

- `date`: fecha a consultar.
- `search`: filtro.
- `page` y `limit`: paginación.
- `all`: conjunto completo.

El frontend espera `movements`, `activeAccounts` y `summary` con ingresos, cantidad de movimientos y cuentas activas.

### POST `/api/v1/cash-drawer`

Genera el reporte de corte de caja a partir del cuerpo solicitado por `ReportService`.

### POST `/api/v1/cash-drawer/pdf`

Exporta el corte de caja en PDF.

### GET `/api/v1/reports/daily`

Devuelve el reporte diario de facturación.

### GET `/api/v1/reports/monthly`

Devuelve el reporte mensual de facturación.

## 8. Cuentas administrativas

### GET `/api/v1/cuenta-pacientes`

Lista las cuentas. Alias: `/accounts` y `/cuenta_pacientes`.

Parámetros: `search`, `page`, `limit` y `all`.

### GET `/api/v1/cuenta-pacientes/{id_atencion}`

Obtiene paciente, cargos, pagos, subtotal, impuestos, total, saldo y documentos relacionados con la atención.

### GET `/api/v1/accounts/{id_atencion}/documents`

Obtiene los documentos disponibles para una cuenta.

### POST `/api/v1/accounts/{id_atencion}/charges`

Agrega un cargo.

```json
{
  "type": "service",
  "item_id": 15,
  "quantity": 1
}
```

También puede enviarse `description` cuando el servicio lo permita. Los alias aceptan `charges` o `cargos` bajo `cuenta-pacientes` y `cuenta_pacientes`.

### DELETE `/api/v1/accounts/{id_atencion}/charges/{charge_id}`

Elimina un cargo de la atención.

### POST `/api/v1/accounts/{id_atencion}/payments`

Registra un pago. El cuerpo exacto debe cumplir la validación de `AdministrativeService.register_payment`.

Ejemplo lógico:

```json
{
  "amount": 500.0,
  "method": "Efectivo",
  "concept": "Abono"
}
```

### POST `/api/v1/accounts/{id_atencion}/close`

Cierra la cuenta administrativa.

Respuesta exitosa:

```json
{
  "message": "Cuenta cerrada exitosamente",
  "account": {}
}
```

Alias adicional: `POST /api/v1/cerrar-cuenta/{id_atencion}`.

## 9. Endpoints de facturación

El blueprint `billing` complementa la operación administrativa.

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/patient/{id_atencion}` | Consulta la cuenta de facturación |
| POST | `/api/v1/patient/{id_atencion}/items` | Agrega un concepto |
| DELETE | `/api/v1/patient/{id_atencion}/items/{item_id}` | Elimina un concepto |
| POST | `/api/v1/payment/{id_atencion}` | Registra un pago |
| GET | `/api/v1/payments/{id_atencion}` | Consulta pagos |
| GET | `/api/v1/reports/daily` | Reporte diario |
| GET | `/api/v1/reports/monthly` | Reporte mensual |
| GET | `/api/v1/invoice/{id_atencion}/pdf` | Genera factura o cuenta en PDF |

Todos requieren autenticación y autorización de acuerdo con los decoradores definidos en la ruta.

## 10. Documentos PDF administrativos

El blueprint se registra bajo `/api/v1/pdf`.

| Método | Endpoint | Documento |
|---|---|---|
| GET | `/api/v1/pdf/initial-sheet/{id_exp}/{id_atencion}` | Hoja inicial |
| GET | `/api/v1/pdf/front-sheet/{id_exp}/{id_atencion}` | Carátula |
| GET | `/api/v1/pdf/contract/{id_exp}/{id_atencion}` | Contrato |
| GET | `/api/v1/pdf/consent/{id_exp}/{id_atencion}` | Consentimiento |
| GET | `/api/v1/pdf/identification-sheet/{id_exp}/{id_atencion}` | Hoja de identificación |

La respuesta debe incluir un PDF válido y un encabezado de contenido apropiado. El frontend elimina el prefijo `/api/v1` de endpoints almacenados antes de solicitarlos con la instancia Axios, evitando duplicarlo en la URL base.

## 11. Compatibilidad y alias

`administrative.py` conserva alias con guiones, guiones bajos e inglés. Esto facilita la compatibilidad entre clientes previos, pero la documentación recomienda utilizar una sola ruta canónica en código nuevo:

| Operación | Ruta canónica recomendada |
|---|---|
| Listar pacientes | `/gestion-pacientes` |
| Detalle/registro/edición | `/patients` |
| Censo | `/censo` |
| Corte de caja | `/corte-caja` |
| Cuentas | `/cuenta-pacientes` |
| Movimientos de cuenta | `/accounts/{id_atencion}/...` |

No deben eliminarse alias sin revisar los clientes web o móviles que todavía los consumen.

## 12. Ejemplo con PowerShell

```powershell
$token = "TOKEN_JWT"
$headers = @{ Authorization = "Bearer $token" }

Invoke-RestMethod `
  -Uri "http://localhost:5001/api/v1/gestion-pacientes?all=true" `
  -Method Get `
  -Headers $headers
```

Registro de ejemplo:

```powershell
$body = @{
  curp = "GODE000101MMCNNNA1"
  papell = "Gonzalez"
  nom_pac = "Ejemplo"
  fecnac = "2000-01-01"
  area = "Consulta"
  motivo = "Consulta"
  assignedDoctors = @()
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:5001/api/v1/patients" `
  -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

Use únicamente datos ficticios en las pruebas.

## 13. Pruebas mínimas

| Caso | Resultado esperado |
|---|---|
| Petición sin token | 401 |
| Usuario sin rol permitido | 403 |
| Listado con token administrativo | 200 |
| Alta válida | 201 y nuevo expediente |
| Alta inválida | 400 sin registro parcial |
| Consulta inexistente | 404 |
| Actualización válida | 200 |
| Cargo válido | 200/201 y total actualizado |
| Eliminación de cargo | 200 y saldo recalculado |
| Cierre permitido | 200 y cuenta cerrada |
| Descarga de documento | 200 y archivo PDF válido |

## 14. Archivos relacionados

### Backend

- `routes/administrative.py`
- `routes/patients.py`
- `routes/reports.py`
- `routes/billing.py`
- `routes/pdf.py`
- `services/administrative_service.py`
- `services/patient_service.py`
- `services/billing_service.py`
- `services/report_service.py`
- `services/pdf_service.py`
- `utils/sequences.py`
- `utils/validators.py`

### Frontend

- `src/pages/administrativo/`
- `src/services/adminService.js`
- `src/services/adminCache.js`
- `src/context/PatientContext.jsx`
- `src/components/Pagination.jsx`

## 15. Consideraciones de seguridad

- Nunca registrar tokens, datos clínicos o cuerpos sensibles en Git.
- Validar nuevamente en la API aunque React marque campos obligatorios.
- Restringir CORS a los orígenes necesarios.
- Sanitizar nombres y parámetros utilizados para generar documentos.
- No exponer excepciones internas en respuestas 500.
- Probar con una base separada y datos ficticios.
