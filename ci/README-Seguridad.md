# Revisión automática de código y seguridad

`ci/security_review.py` ejecuta siete controles independientes: Bandit (API),
pip-audit (dependencias Python y su resolución), npm audit (web), detect-secrets
(archivos versionados), oxlint (web), pruebas de sesión React y pruebas de
seguridad Flask. Un error de herramienta, timeout o reporte inválido falla el
control; se ejecutan los restantes para conservar un diagnóstico completo.

El gate de dependencias web bloquea severidad alta/crítica y conserva el resto
en el reporte. pip-audit bloquea cualquier vulnerabilidad detectada. Bandit
bloquea hallazgos de severidad media/alta. Los siete controles deben aprobar.
Los informes JUnit de controles, pruebas, JSON y logs se archivan incluso si falla.
`source.json` identifica SHA, fecha UTC y cambios locales versionados.

## Jenkins

El proyecto `OftalCore-Seguridad-Codigo` utiliza `ci/Jenkinsfile.security` y consulta
cambios SCM cada cinco minutos mientras Jenkins está encendido. La definición
y rama efectivamente configuradas se ven en Configure del job. Usa un workspace
independiente; conserva los últimos 30 builds y no modifica los jobs de UAT.

Preparar Python 3.12 con `ci/requirements-security.txt`, otro Python con los
requirements de API/tests y Node 22. Parámetros SECURITY_PYTHON y TEST_PYTHON
identifican esos ejecutables. CA_BUNDLE es opcional para equipos que usan el
almacén corporativo de confianza; no se deshabilita la verificación TLS.

```text
python ci/security_review.py --out reports/security/manual --test-python RUTA_PYTHON_API
python -m pytest ci/test_security_gate.py
```

Jenkins es local: apagado el equipo no ejecuta el polling. GitHub Actions también
ejecuta estos controles en cada PR/push hacia develop, qa y main. Los workflows
existentes de API, web y seguridad se conservan. Un gate fallido se reporta como
check fallido; el bloqueo obligatorio de merge depende de las reglas de rama.
CodeQL añade análisis de seguridad de Python y JavaScript en GitHub y publica los
hallazgos en Security and quality del repositorio.

## Secretos y excepciones

El scanner no verifica credenciales contra proveedores (`--no-verify`). Nunca
publica su valor: solo archivo/tipo/línea. Las excepciones exactas en
`security-reviewed-fixtures.json` corresponden a contraseñas sintéticas de tests,
textos traducidos y SHA/checksums de evidencias revisados. Coinciden por ruta,
tipo y hash, no por directorio completo. Una credencial nueva o un valor cambiado
falla. No actualizar automáticamente las excepciones para obtener un build verde.
El propio catálogo se excluye de la detección, pero se valida su esquema: solo
rutas existentes, tipos permitidos, hashes SHA1 y motivos revisados. No admite
valores de credenciales. Los literales falsos de las pruebas del gate se anotan
únicamente en sus cuatro líneas con `pragma: allowlist secret`.
El análisis no reemplaza rotar una credencial real si se descubre una filtración
ni incluye el historial completo de Git.

## Correcciones y flujo

Dependabot propone actualizaciones semanales mediante PR hacia develop para npm,
pip y Actions; su configuración se activa al llegar a la rama predeterminada de
GitHub. No se fusionan automáticamente ni corrigen arbitrariamente lógica clínica.
El análisis funciona sin una suscripción o clave de un modelo de IA. Esto es
análisis automatizado de código, no un agente de IA que cambia código sin revisión.
Revisar el informe, corregir en rama, ejecutar regresión y seguir develop → qa →
main con la aceptación correspondiente. No es aceptación UAT ni despliegue.
