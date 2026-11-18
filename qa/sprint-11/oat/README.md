# PBL-40 / REQ-27 — OAT Sprint Azure 11 (Windows)

Desde la raíz del repositorio, con Docker Desktop activo. Copiar este directorio y `compose.oat-s11.yml` a la raíz. No usar datos reales. El overlay define `ineo_test_s11` sin modificar el Compose del equipo. El proyecto Compose `ineo-oat-s11` separa los volúmenes. Los puertos 27018 y 5002 deben estar libres; no detener otros proyectos sin autorización.

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
docker compose -p ineo-oat-s11 -f compose.test.yml -f compose.oat-s11.yml up -d --build
docker compose -p ineo-oat-s11 -f compose.test.yml -f compose.oat-s11.yml ps -a
docker compose -p ineo-oat-s11 -f compose.test.yml -f compose.oat-s11.yml logs seed
curl.exe -i http://localhost:5002/health
curl.exe -i http://localhost:5002/ready
```

Antes de ejecutar, confirmar que seed terminó exitosamente y ambos endpoints devuelven 200. MongoDB 7 image includes bash and Database Tools; comprobar con `docker compose -p ineo-oat-s11 -f compose.test.yml -f compose.oat-s11.yml exec -T mongo-test mongodump --version` y repetir para mongorestore y mongosh. Si falta herramienta, registrar Bloqueado; no sustituir por mock. No escribir datos desde otras sesiones durante respaldo.

Acordar RPO/RTO con el revisor antes de ejecutar. El ejemplo de 900 s es PROVISIONAL, no un acuerdo. El RPO del script mide la antigüedad del último marcador sintético recuperado respecto al instante de incidente simulado al terminar el dump; no acredita RPO real de producción ni RTO de rollback. No usar duración de dump como RPO.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\qa\sprint-11\oat\run_oat.ps1 -RpoTargetSeconds 900 -Case all
```

Ejecutar casos individualmente con `-Case health`, `-Case backup` o `-Case corrupt`. El runner usa Bash dentro del contenedor MongoDB y `curl.exe` en Windows. No necesita chmod/export ni un Bash en Windows. Preserva reportes y SHA, pero las modificaciones sin commit se registran en metadata; hacer commit antes de campaña definitiva. Los archivos de backup permanecen en `/tmp/oat-*/backups` dentro de contenedor QA, no se publican. El hash compara documentos completos serializados a Extended JSON por colección e ID (fixture estable). La restauración limpia se valida antes de dañar copia. Fallo negativo válido requiere código no cero, diagnóstico de archivo y cero documentos en destino corrupto. No usar estas pruebas como acreditación de alertas, reinicio, rollback, CORS, SAST o UAT.

Evidencias: `evidence/sprint-11/oat-<fecha>/`. Revisar y sanitizar antes de subir; anexar capturas y Word por caso, fecha real, herramientas, SHA, resultado, defectos/reprueba y revisión de Zahid. No marcar aprobación humana por salida técnica. Si faltan requisitos, marcar Bloqueado. Si falla una aserción, Fallido. Los scripts fueron revisados y revisados sintácticamente en Bash, no ejecutados contra Docker real en el entorno de generación; validar en Windows.

Al finalizar, desde raíz, conservar reportes y apagar solo este proyecto:

```powershell
docker compose -p ineo-oat-s11 -f compose.test.yml -f compose.oat-s11.yml down
```

No usar `down -v` salvo que hayas autorizado borrar los volúmenes sintéticos del proyecto y conservado evidencias. No subir archivos de respaldo ni secretos.
