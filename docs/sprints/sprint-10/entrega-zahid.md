# PBL-30 y PBL-45

Responsable: Zahid Galicia. Sprint 4 del PBL; Sprint 10 de Azure según la
corrección del solicitante. Azure no se consultó por falta de conexión;
no se cambiaron work items ni se presume su estado.

## PBL-30 Contratos web API

Se reutiliza `contracts/v1/api.schema.json`, JSON Schema 2020-12. Se añaden
pruebas de esquemas, campos obligatorios, tipos incompatibles, autenticación
inválida y respuestas JSON de pacientes, estudios, Analytics y Spark.
Los cambios incompatibles provocan fallo de pytest y del pipeline. Los tests
de requisitos de Spark ahora seleccionan ese motor explícitamente; su resultado
no depende del modo automático o la memoria del host.

La prueba SIT usa el cliente Axios y `sparkService` reales, HTTP, Flask y MongoDB
local real. El launcher genera su clave en memoria y restablece una base
exclusiva con usuarios y datos sintéticos. La integración comprueba login,
lecturas de cinco módulos y rechazo 401 al eliminar la sesión. El motor de
análisis se configura lightweight; este caso verifica transporte y contratos,
no rendimiento ni ejecución distribuida de Spark.

### Evidencia local

| Verificación | Resultado | Evidencia |
|---|---|---|
| UT del esquema | 6 aprobadas | `evidence/sprint10-ut.xml` |
| Proveedor y regresión de contratos | 156 aprobadas | `evidence/sprint10-contracts.xml` |
| Consumidor Spark aislado | 8 aprobadas | `evidence/sprint10-consumer.xml` |
| SIT cliente real con Flask y MongoDB real | 1 escenario aprobado | `evidence/sprint10-sit.xml` |

El reporte consumidor registra también un caso SIT omitido en la corrida sin
opt-in; su ejecución efectiva y aprobada está en el reporte SIT separado.
Las tres advertencias Python son deprecaciones en dependencias; no son fallos.
El Word utiliza la plantilla de casos aportada y contiene solo documentación
de pruebas UT/SIT. No se documenta OAT porque la aceptación operativa corresponde
a otras historias; Terraform aquí no constituye aceptación operativa.

## PBL-45 Terraform

Se añade un módulo de MongoDB sintético local, variables validadas, health
check, puerto loopback, lockfile, exclusiones de estado/planes y procedimiento
de preparación, provisión y limpieza. Véase `infra/terraform/README.md`.
`fmt`, `validate` y tres planes simulados aprobaron. Se revisó un plan real de
tres altas. El apply falló por Docker/WSL; PBL-45-T4 no se considera terminado.
La integración SIT aprobada con Mongo nativo no sustituye esa prueba.

## Reproducción y CI

En `backend/api_hospital`:

```sh
python -m pytest tests/test_contract_schema_unit.py tests/test_sprint10_contracts.py tests/test_spark_contract.py tests/test_sprint8_zahid.py -q
```

Para SIT seguir el README de Terraform y arrancar `testing.contract_server`.
El workflow `sprint10-zahid.yml` exige contratos, provisión real y SIT y siempre
intenta limpiar los recursos. No se ha creado un pull request ni aprobado la
aceptación del equipo. La rama base es `develop`.
