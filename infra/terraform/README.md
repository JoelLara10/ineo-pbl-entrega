# PBL-45 Ambiente de prueba reproducible

Responsable: Zahid. Sprint 4 del PBL / Sprint 10 de Azure, según la corrección
del solicitante. El alcance se obtuvo del PBL; Azure no pudo consultarse.

## Proveedor y alcance

Terraform >=1.7 y <2, proveedor `kreuzwerker/docker` fijado por el lockfile.
El módulo `modules/test_database` administra una imagen MongoDB 7.0.16, un
volumen sintético y un contenedor con health check. El puerto se publica
exclusivamente en 127.0.0.1:27029. No administra Render, DNS, certificados,
cuentas cloud ni datos de producción. La API y sus datos se preparan con el
launcher dedicado de PBL-30; no se confunde esto con un despliegue productivo.

Referencia del proveedor:
https://registry.terraform.io/providers/kreuzwerker/docker/3.9.0/docs/resources/container

## Preparación manual

Instalar Terraform y Docker Engine/Desktop con contenedores Linux, iniciar
Docker y comprobar `docker info`. Disponer de espacio para la imagen y volumen.
Instalar Python y las dependencias de la API, Node y `npm ci` en el frontend.
El nombre debe comenzar con `ineo-test-`; cada ejecución concurrente necesita
nombre y puerto propios. Nunca conecte el seed a una base compartida.

Desde este directorio:

```sh
terraform init -input=false
terraform fmt -check -recursive
terraform validate
terraform test
terraform plan -input=false -out=environment.tfplan
terraform show environment.tfplan
terraform apply -input=false environment.tfplan
```

Revisar que el plan solo crea los tres recursos de prueba. `terraform test`
usa proveedor simulado y no prueba que Docker pueda crear contenedores.
La imagen se fija por versión; para una cadena de suministro con identidad
inmutable, el equipo debe aprobar y fijar su digest antes de promoción.

Desde `backend/api_hospital`, iniciar `python -m testing.contract_server`.
Esto restablece exclusivamente `ineo_test_contract_sprint10` en Mongo local y
expone la API sintética en 127.0.0.1:5029. Desde el frontend:

```sh
# Linux/macOS
RUN_CONTRACT_SIT=1 npx vitest run src/tests/sprint10-contract-sit.test.js
```

PowerShell: `$env:RUN_CONTRACT_SIT='1'`, seguido del comando `npx vitest run`.

## Estado y secretos

El backend local de Terraform se usa solo para este entorno desechable.
El estado no contiene credenciales de producción, pero puede contener metadatos
del host; mantenerlo en un directorio accesible solo al operador. `.gitignore`
excluye estado, copias, planes, `.tfvars` y `.terraform`. El lockfile sí se versiona.
No hay variables secretas en este módulo. La API genera su clave de sesión en
memoria; los usuarios sembrados son sintéticos. No publicar tokens ni logs de login.
Para infraestructura compartida se requiere un backend remoto con cifrado,
control de acceso y bloqueo, aprobado por el equipo; no está configurado aquí.

## Limpieza

Detener primero el servidor de contrato con Ctrl+C. Revisar
`terraform plan -destroy` y ejecutar `terraform destroy` desde este directorio.
Confirmar plan final sin recursos y ausencia del contenedor y volumen con el
nombre de esta ejecución. El destroy elimina los datos sintéticos del volumen;
la imagen permanece en caché por `keep_locally=true`.
No usar limpiezas globales de Docker. En CI, el paso de limpieza usa `always()`.

## Verificación del 4 de noviembre de 2026

`fmt`, `init`, `validate` y los tres planes simulados aprobaron. El plan real
mostró tres altas y ninguna modificación o eliminación. El apply local falló
por el arranque WSL de Docker; no se completó aprovisionamiento ni destroy.
El estado local quedó sin recursos administrados. La prueba SIT se ejecutó
por separado con MongoDB nativo y archivos reducidos debido al espacio local;
ese resultado no demuestra el aprovisionamiento Terraform.
El workflow `sprint10-zahid.yml` reproduce creación, SIT y limpieza en Linux.
PBL-45-T4 permanece pendiente hasta obtener evidencia satisfactoria de ese flujo.
