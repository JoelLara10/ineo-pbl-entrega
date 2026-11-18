"""Populate Sprint 11 test records from the instructor's Word template."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "evidence" / "sprint-11" / "package"
TEMPLATE = Path(r"C:\Users\JOEL LARA\Downloads\Documento de Caso de Prueba.docx")
DATE = "18/11/2026"


def set_cell(table, row: int, column: int, value: str) -> None:
    cell = table.cell(row, column)
    cell.text = value
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(8)


def make_case(case_id: str, title: str, classification: str, description: str,
              objective: str, preconditions: str, test_data: str,
              steps: list[tuple[str, str, str, str]], final: str,
              evidence: str, observations: str, annexes: list[tuple[Path, str]]) -> None:
    case_dir = PACKAGE / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    output = case_dir / f"{case_id}.docx"
    shutil.copy2(TEMPLATE, output)
    doc = Document(output)
    doc.paragraphs[0].text = f"Caso de prueba — {case_id}"
    doc.paragraphs[1].text = f"Sprint 11 · {DATE} · {title} · Evidencia: Joel Lara"

    t = doc.tables
    fields = {
        (1, 1): case_id, (1, 3): DATE,
        (2, 1): title, (2, 3): "Joel Lara (evidencia compartida; firma pendiente)",
        (3, 1): "OftalCore", (3, 3): "QA / Jenkins local 8081 según aplique",
        (4, 1): "Aplicación web / API / entrega CI según caso",
        (4, 3): "☐ Desarrollo ☒ QA ☐ Producción",
        (5, 1): "Sprint 11 / PBL-41-T5 (#590)",
        (5, 3): "☐ Alta ☒ Media ☐ Baja",
    }
    for (r, c), value in fields.items():
        set_cell(t[0], r, c, value)
    level = "☐ Unitaria ☐ Integración ☒ Sistema ☐ Aceptación" if case_id.startswith("CP-S11-OAT-") else "☐ Unitaria ☒ Integración ☐ Sistema ☐ Aceptación"
    test_type = "☐ Funcional ☒ No funcional ☐ Regresión ☐ Rendimiento ☐ Seguridad ☐ Usabilidad ☐ Otro" if case_id.startswith("CP-S11-OAT-") else "☒ Funcional ☐ No funcional ☐ Regresión ☐ Rendimiento ☐ Seguridad ☐ Usabilidad ☐ Otro"
    set_cell(t[1], 1, 0, level)
    set_cell(t[1], 1, 1, test_type)
    set_cell(t[1], 2, 0, "Técnica: ☒ Caja negra ☒ Caja blanca")
    set_cell(t[1], 2, 1, "Ejecución: ☒ Mixta (manual/automatizada)")
    for r, value in enumerate((f"{description}\n\nClasificación: {classification}", objective, preconditions, test_data), start=1):
        set_cell(t[2], r, 1, value)
    for idx, step in enumerate(steps, start=1):
        if idx > 5:
            break
        action, expected, observed, mark = step
        for col, value in enumerate((str(idx), action, expected, observed, mark)):
            set_cell(t[3], idx, col, value)
    set_cell(t[4], 1, 1, final)
    set_cell(t[4], 2, 1, evidence)
    set_cell(t[4], 3, 1, "No reportado")
    set_cell(t[4], 4, 1, "No aplica / sin defecto reportado")
    set_cell(t[4], 5, 1, observations)
    set_cell(t[5], 1, 0, "Joel Lara — firma pendiente")
    set_cell(t[5], 1, 1, "Revisado por: pendiente de revisión — sin firma")

    for path, caption in annexes:
        if not path.is_file():
            continue
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(caption).bold = True
        pic = doc.add_paragraph()
        pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pic.add_run().add_picture(str(path), width=Inches(6.1))
    doc.save(output)


sit = PACKAGE / "CP-S11-SIT-01"
make_case(
    "CP-S11-SIT-01", "Comprobar web de QA y persistencia de una nota mediante API",
    "Nivel: integración (SIT) · Tipo: funcional · Técnica: caja negra y revisión de datos · Ejecución: manual",
    "Validar el recorrido web de enfermería en QA y que una nota guardada aparezca después en el historial y en el registro persistido.",
    "Comprobar integración de la interfaz con el servicio de notas en el entorno QA.",
    "Acceso autenticado de pruebas en QA; paciente/atención sintéticos disponibles; DevTools abierto.",
    "Nota sintética: ‘prueba qa nota enfermeria’; registro mostrado con id_nota 8 e id_atencion 1. No usar datos clínicos reales.",
    [
        ("Abrir https://ineo-web-qa.vercel.app y comprobar el tablero.", "El tablero carga y muestra módulos.", "Se observa el tablero QA de Alex en vista móvil.", "✓"),
        ("Abrir Enfermería > Nota y escribir la nota sintética.", "El formulario acepta el texto.", "El texto aparece en el formulario antes del guardado.", "✓"),
        ("Guardar la nota.", "La aplicación registra la nota y actualiza el historial.", "La nota aparece en Historial de Notas.", "✓"),
        ("Verificar Network y el historial de la aplicación.", "La integración completa sin error visible.", "La captura del historial muestra la nota; el filtro de Network usado no lista la solicitud de guardado.", "✓*"),
        ("Verificar el registro persistido disponible para QA.", "El registro contiene la nota y sus referencias.", "La evidencia de datos muestra id_nota 8, atención 1 y el texto guardado.", "✓"),
    ],
    "☒ Aprobada según el recorrido y persistencia observados; observación de trazabilidad de red registrada.",
    "Anexos 01–05: tablero, formulario, historial, panel Network y registro persistido.",
    "La captura Network tiene filtro `is:service-worker-intercepted` y no permite identificar el POST ni su código HTTP. La persistencia se respalda por el historial y la vista del registro. La marca ✓* refiere solo a revisión complementaria, no a una respuesta HTTP observada.",
    [(sit / "screenshots" / f"{i:02d}-{name}.png", caption) for i, (name, caption) in enumerate([
        ("dashboard-qa", "Evidencia 01 — tablero QA en vista móvil."),
        ("formulario-nota", "Evidencia 02 — nota sintética escrita antes de guardar."),
        ("historial-nota", "Evidencia 03 — nota visible en historial después del guardado."),
        ("red-estatica", "Evidencia 04 — recursos web 200; el filtro activo no muestra el POST de guardado."),
        ("registro-persistido", "Evidencia 05 — registro QA con texto y referencias de atención."),
    ], start=1)],
)

oat03 = PACKAGE / "CP-S11-OAT-03"
oat03_json = json.loads((oat03 / "result.json").read_text(encoding="utf-8"))
make_case(
    "CP-S11-OAT-03", "Rollback y recuperación de versión estable (ensayo local aislado)",
    "Nivel: operación · Tipo: resiliencia/recuperación · Técnica: caja negra · Ejecución: automatizada local",
    "Ensayar la detección de una versión estática inválida, recuperar la versión estable y medir el tiempo del rollback con un servidor HTTP local temporal.",
    "Verificar que el smoke detecte el candidato defectuoso y que la restauración recupere contenido y hash del artefacto estable.",
    "Build web local existente; runner Python; servidor ligado únicamente a 127.0.0.1 y directorios temporales.",
    "Artefacto Vite actual; candidato inválido sintético; sin credenciales ni datos clínicos.",
    [
        ("Publicar la copia estable en servidor local temporal y ejecutar smoke.", "HTTP 200 y contenido estable.", f"HTTP {oat03_json['initial_stable_smoke']['http_status']}; smoke aprobó.", "✓"),
        ("Sustituir por candidato inválido sintético y ejecutar smoke.", "Smoke rechaza el contenido inválido.", "HTTP 200 pero el contenido no cumple; la validación lo detecta como candidato inválido.", "✓"),
        ("Restaurar la copia estable desde el respaldo temporal.", "Los hashes de index.html coinciden.", f"SHA-256 estable/restaurado coincide: {oat03_json['rollback']['sha256_matches_stable']}.", "✓"),
        ("Medir tiempo y repetir smoke tras rollback.", "El servicio vuelve a responder con versión estable.", f"HTTP {oat03_json['recovery_smoke']['http_status']}; RTO observado {oat03_json['rollback']['rto_seconds']} s.", "✓"),
        ("Confirmar alcance del ensayo.", "No se alteran QA/producción ni Mongo.", "Ensayo aislado local; QA/producción y base de datos no fueron tocados.", "✓"),
    ],
    "☒ Aprobada solo como ensayo local aislado; rollback real de QA pendiente.",
    "result.json, script reproducible rollback_static_simulation.py y resumen visual del ensayo.",
    "No acredita rollback en Vercel/QA, recuperación de MongoDB, alertas ni tráfico real. Mantener el criterio de aceptación operativa pendiente hasta ejecutar el rollback controlado en QA y conservar su registro.",
    [(oat03 / "rollback-summary.png", "Salida generada del ensayo local — no es captura de un despliegue QA.")],
)

oat04 = PACKAGE / "CP-S11-OAT-04"
make_case(
    "CP-S11-OAT-04", "Alerta de dependencia: evidencia offline de frontend (parcial)",
    "Nivel: operación · Tipo: disponibilidad/recuperación · Técnica: caja negra · Ejecución: manual/automatizada",
    "Documentar las nuevas capturas del módulo Enfermería mostrando estado sin conexión, datos guardados visibles y recursos servidos por el service worker; contrastarlo con el criterio Azure de caída DB y alerta.",
    "Comprobar la respuesta offline visible del frontend y dejar explícito si esa evidencia prueba o no la interrupción de MongoDB/API definida por CP-S11-OAT-04.",
    "Entorno QA; endpoint de readiness de API y Mongo de prueba con método controlado para interrumpir/restaurar.",
    "Módulo QA /enfermeria; banner ‘Sin conexión. Se muestran los datos guardados previamente’; lista visible de cama/paciente; Network con filtro is:service-worker-intercepted.",
    [
        ("Abrir QA en /enfermeria y registrar el banner de conectividad.", "La aplicación hace visible la pérdida de conexión.", "La captura muestra ‘Sin conexión. Se muestran los datos guardados previamente.’", "✓"),
        ("Revisar contenido que permanece visible sin conexión.", "Datos previamente guardados se muestran sin simular registros nuevos.", "La captura muestra la lista previamente disponible, pacientes/camas y contadores.", "✓"),
        ("Revisar Network con filtro de solicitudes interceptadas.", "Recursos offline quedan servidos desde el service worker.", "La segunda captura muestra recursos estáticos y /ready con status 200 desde service worker.", "✓"),
        ("Determinar si esto comprueba caída de Mongo/API y alerta de dependencia.", "Debe identificarse health/log/alerta de la API al interrumpir Mongo de prueba.", "No: evidencia es del frontend/service worker; no muestra interrupción Mongo ni logs/alerta del API.", "✗"),
        ("Registrar estado OAT del criterio original.", "Fallo/recuperación DB documentados antes, durante y después.", "No ejecutado; subprueba offline del frontend observada, alerta de dependencia queda pendiente.", "—"),
    ],
    "☒ Parcial / bloqueada para el criterio original: offline de frontend observado; alerta de DB/API pendiente.",
    "Anexos 01–03: /ready web servido desde service worker; estado sin conexión con datos guardados; recursos estáticos interceptados.",
    "Las capturas nuevas prueban el fallback offline del frontend y disponibilidad de recursos cacheados. No prueban que Mongo de QA se haya detenido, que la API haya emitido alerta/log de dependencia ni recuperación DB. Para cerrar CP-S11-OAT-04, ejecutar con Mongo aislada y permiso operativo, guardar health/log antes-durante-después y restauración. No interrumpir la base compartida sin ventana y respaldo aprobados.",
    [(oat04 / "screenshots" / "01-ready-web-200.png", "Evidencia 01 — /ready del host web responde 200 desde service worker; no es readiness de API/Mongo."),
     (oat04 / "screenshots" / "02-offline-banner-and-cached-data.png", "Evidencia 02 — la interfaz anuncia modo sin conexión y conserva datos previamente guardados."),
     (oat04 / "screenshots" / "03-service-worker-assets.png", "Evidencia 03 — recursos web y /ready figuran 200 desde service worker; no se ven logs/alertas del API." )],
)

ci05 = PACKAGE / "CP-S11-CI-05"
ci_json = {
    "case": "CP-S11-CI-05",
    "local_validator_unit_tests": {"command": "python -m unittest discover -s ci -p test_sprint11_helpers.py -v", "passed": 4, "failed": 0, "scope": "synthetic fixtures for validator and SHA-256 helper"},
    "jenkins_job": "OftalCore-Joel-Sprint11",
    "jenkins_build": 6,
    "jenkins_result": "SUCCESS as shown by user-provided Stage View screenshot",
    "jenkins_build_reports": ["analysis-ut.xml: 14 tests", "oat-synthetic.xml: 10 tests", "selenium.xml: 20 tests"],
    "jenkins_limit": "Screenshot stage list has no evidence-validator stage; this build does not prove CP-S11-CI-05 ran inside Jenkins.",
    "aggregate_evidence_validation": "Expected to fail until CI-01..CI-04 and complete OAT-04 are added; do not call the whole package complete.",
}
(ci05 / "result.json").write_text(json.dumps(ci_json, indent=2) + "\n", encoding="utf-8")
make_case(
    "CP-S11-CI-05", "Validar estructura e integridad del paquete de evidencia y ejecución Jenkins",
    "Nivel: integración CI · Tipo: automatizada/funcional · Técnica: caja blanca · Ejecución: automatizada",
    "Comprobar el validador de expedientes y revisar el resultado Jenkins build #6 aportado para el job Sprint 11.",
    "Detectar paquetes de evidencia completos/incompletos y conservar los reportes de las etapas ejecutadas en Jenkins.",
    "Repositorio Sprint 11; Python; suite test_sprint11_helpers.py; job local Jenkins 8081 autenticado.",
    "Fixtures temporales completas/incompletas para el validador; reportes Jenkins build #6 de UT, OAT sintética y Selenium.",
    [
        ("Ejecutar la suite de helpers del validador y manifiesto.", "Pruebas de paquete completo/incompleto y hashes pasan.", "4 pruebas unitarias locales aprobadas; consola guardada en validator-unittest.txt.", "✓"),
        ("Revisar Stage View de Jenkins build #6.", "Las etapas ejecutadas finalizan correctamente.", "La captura final muestra etapas verdes y último resultado sin fallas.", "✓"),
        ("Revisar resultados JUnit archivados.", "Reportes UT, OAT sintética y Selenium disponibles.", "14 UT, 10 OAT sintéticas y 20 casos Selenium reportados en build-6.", "✓"),
        ("Verificar si Jenkins ejecutó la validación integral de la carpeta de evidencia.", "La etapa CI-05 aparece y valida el paquete real.", "La lista visible de etapas no muestra el validador de evidencias.", "✗"),
        ("Determinar estado de aceptación global.", "Paquete completo válido y expedientes requeridos presentes.", "La suite de helper pasó; paquete global aún incompleto por casos faltantes y OAT-04.", "✗"),
    ],
    "☒ Parcial: helpers y build #6 aprobados; ejecución integral CI-05 dentro de Jenkins y paquete completo pendientes.",
    "Capturas Jenkins #6 en ejecución y SUCCESS; XML/JSON de resultados; consola de cuatro unit tests.",
    "Build #6 acredita su pipeline mostrado (14 UT, 10 OAT sintéticas, 20 Selenium, build/smoke); no incluye etapa explícita de validación integral de evidencias. Las pruebas del validador fueron ejecutadas localmente con fixtures sintéticas. La validación real del paquete debe fallar hasta incluir CI-01..CI-04 y evidencia OAT-04 suficiente.",
    [(ci05 / "screenshots" / "01-jenkins-build-6-en-ejecucion.png", "Evidencia 01 — Jenkins 8081 build #6 con etapas todavía ejecutándose."),
     (ci05 / "screenshots" / "02-jenkins-build-6-exitoso.png", "Evidencia 02 — Jenkins 8081 build #6 finalizado en verde." )],
)

print("Generated four separate Word records from the instructor template.")
