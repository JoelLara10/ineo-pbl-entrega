# Sprint 11: controles de artefacto y paquete de evidencia

## Hash del artefacto

Después de `npm run build`, Jenkins genera `artifact-manifest.json` con la ruta,
el tamaño y SHA-256 de cada archivo de `frontend/clinica-web-react/dist`. Copia
el resultado a `qa-promotion-simulation` y compara cada archivo contra el
manifiesto. Esto demuestra integridad de la copia local; no publica a Vercel ni
acredita despliegue a QA. El SHA de commit se conserva aparte en
`source-sha.txt`.

## Validador de evidencia CP-S11-CI-05

El validador exige estas carpetas por caso: `CP-S11-CI-01`, `CP-S11-CI-02`,
`CP-S11-CI-03`, `CP-S11-CI-04`, `CP-S11-SIT-01`, `CP-S11-OAT-03`,
`CP-S11-OAT-04` y `CP-S11-CI-05`. Cada carpeta requiere un `.docx` válido
(contenedor Word con `word/document.xml`), una captura PNG válida, un resultado
XML bien formado o JSON y un `result.txt` con el resultado observado.

En **Build with Parameters**, `EVIDENCE_PACKAGE_DIR` puede apuntar a la carpeta
raíz del paquete. Vacío omite esta etapa; lleno ejecuta el validador y bloquea
el build si falta un caso o archivo. El script solo valida presencia e
integridad estructural; no interpreta si las conclusiones del Word son ciertas
ni reemplaza la revisión de Jaime o las pruebas del profesor.

## Reproducción local

Desde la raíz del repositorio, usando Python 3:

```powershell
python -m unittest discover -s ci -p "test_sprint11_helpers.py" -v
python ci/sprint11_artifact.py manifest frontend/clinica-web-react/dist reports/artifact-manifest.json
python ci/sprint11_artifact.py copy-verify frontend/clinica-web-react/dist reports/qa-promotion-simulation reports/artifact-manifest.json
python ci/validate_sprint11_evidence.py evidence/sprint-11/package --json reports/evidence-validation.json
```

La última instrucción falla hasta que exista un paquete real completo; no se
deben llenar los registros con capturas de ejemplo ni resultados simulados.
