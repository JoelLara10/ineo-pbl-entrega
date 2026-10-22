"""Build the review PDF from real JUnit results and Jaime's existing screenshots."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/sprint-9-jaime-review'
PDF = ROOT / 'docs/sprints/sprint-9/Revision-Jaime-UAT-Sprint9.pdf'
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyReview', fontName='Helvetica', fontSize=10.5, leading=15, spaceAfter=9))
styles.add(ParagraphStyle(name='CaptionReview', fontName='Helvetica', fontSize=9, leading=12, spaceAfter=10))
for name in ('Title', 'Heading1', 'Heading2'):
    styles[name].textColor = colors.black
styles['Title'].fontSize = 24
styles['Title'].leading = 28
styles['Heading1'].fontSize = 17
styles['Heading1'].leading = 21
story = []


def p(text, style='BodyReview'):
    story.append(Paragraph(text, styles[style]))


def heading(text):
    p(text, 'Heading1')


def table(headers, rows, widths):
    data = [[Paragraph(str(v), styles['CaptionReview']) for v in row] for row in [headers] + rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DCE8F2')),
        ('GRID', (0, 0), (-1, -1), .5, colors.HexColor('#D9D9D9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))


def image(filename, caption, max_height=230):
    path = OUT / 'capturas-originales' / filename
    w, h = ImageReader(str(path)).getSize()
    ratio = min(500 / w, max_height / h)
    story.append(Image(str(path), width=w * ratio, height=h * ratio, hAlign='LEFT'))
    story.append(Spacer(1, 6))
    p(caption, 'CaptionReview')


def junit(name):
    root = ET.parse(OUT / name).getroot()
    cases = list(root.iter('testcase'))
    failed = sum(c.find('failure') is not None or c.find('error') is not None for c in cases)
    skipped = sum(c.find('skipped') is not None for c in cases)
    return {'tests': len(cases), 'passed': len(cases)-failed-skipped, 'failed': failed, 'skipped_or_xfail': skipped}


counts = {name: junit(name) for name in ['frontend-baseline.xml', 'frontend-final.xml', 'jaime-states.xml', 'backend-baseline.xml', 'backend-portable.xml', 'uat-readiness.xml']}
(OUT / 'summary.json').write_text(json.dumps({'date': '2026-10-22', 'develop': '9c456cc', 'jaime': '7343a42',
    'decision': 'NO-GO for promotion of feature/sprint9; human Analytics UAT remains conditional',
    'results': counts}, indent=2), encoding='utf-8')

p('Revisión de Jaime y pruebas UAT', 'Title')
p('Sistema de Gestión Clínica INEO | Sprint 9 de Azure / Sprint 3 del PBL', 'Heading2')
p('22 de octubre de 2026. Revisión técnica realizada por Codex a solicitud de Joel. Fuentes: Azure DevOps, la rama feature/sprint9 y la versión actual de develop.')
heading('Decisión de integración')
p('<b>No promover todavía la rama original de Jaime a develop ni a qa.</b> La integración de prueba produce un conflicto en SparkAnalysisScreen.jsx. La sesión humana documentada aprueba Enfermería, pero condiciona Analytics. Además, se reprodujo que la API guarda una valoración vacía.')
p('La rama de revisión incorpora evidencia y pruebas complementarias sobre develop, sin declarar aceptada la UAT ni modificar los ambientes. El resultado humano se conserva tal como aparece en los Word entregados por Jaime.')
table(['Elemento', 'Resultado verificado'], [
    ['PBL-04 / Azure #281', 'Siete pruebas de estados pasan sobre develop. La implementación original requiere resolver el conflicto sin perder filtros, exportación y metadatos.'],
    ['PBL-33 / Azure #438', 'Guiones y sesión del 21/10 documentados en Word. CP-UAT-001 aprobado; CP-UAT-002 condicionado. Los Markdown T4/T5 siguen vacíos.'],
    ['Flujo de ramas', 'feature/sprint9 7343a42; develop 9c456cc; qa 8e26dae. No se realizó promoción ni publicación en main.'],
], [130, 370])
p('Las capturas de este informe proceden de la entrega original de Jaime. No son capturas de una nueva sesión humana realizada por Codex.', 'CaptionReview')
story.append(PageBreak())

heading('Hallazgos y criterio de salida')
table(['ID', 'Hallazgo', 'Para resolverlo'], [
    ['INT-001', 'Conflicto real al ejecutar la integración de feature/sprint9 sobre develop en SparkAnalysisScreen.jsx.', 'Integrar sobre develop preservando funciones actuales y ejecutar las suites completas antes del PR.'],
    ['DEF-UAT-001', 'POST de nursing-assessment con {} devuelve 201 y persiste una valoración vacía. El caso negativo queda como xfail estricto.', 'Definir campos y formatos requeridos, validar en la API y reejecutar el caso negativo. Un xfail no equivale a un aprobado.'],
    ['DEF-UAT-002', 'El registro humano indica que la persona no identificó la unidad correctamente y requirió ayuda para interpretar Analytics.', 'Confirmar los ajustes visuales con un usuario representativo, registrar el resultado y emitir decisión actualizada.'],
    ['DOC-001', 'Word contiene resultados; Markdown T4/T5 mantiene plantillas y fechas incoherentes. No queda identificado el commit de la sesión.', 'Consolidar versión del incremento, fecha, defecto, resultado y decisión en el expediente de aceptación.'],
    ['ENV-001', 'El Word de preparación usa frontend QA con la API publicada que el README identifica como demostración/producción.', 'Verificar API y base exclusivas de QA y datos sintéticos antes de repetir la UAT. Esta revisión no certifica aislamiento remoto.'],
], [80, 225, 195])
p('Los criterios de Azure permiten registrar escenarios aprobados, rechazados o condicionados con evidencia. Eso acredita el registro de la sesión; no convierte un escenario condicionado en una aprobación sin pendientes.')
story.append(PageBreak())

heading('CP-UAT-001 Enfermería')
p('<b>Registro original:</b> aprobado en el Word de ejecución del 21/10/2026. La persona completó el flujo de acceso, selección, captura, guardado y consulta. También observó falta de validación de formato en algunos campos.')
image('image5.png', 'Figura 1. Confirmación de guardado incluida en el registro original de Jaime. Evidencia histórica; no acredita por sí sola validaciones de datos.', 180)
table(['Verificación adicional', 'Resultado'], [
    ['Login real de rol Enfermería con datos sintéticos', 'Aprobado en Flask test_client.'],
    ['Guardar y consultar una valoración conocida', '201 al guardar; 200 al consultar; contenido recuperado igual al enviado.'],
    ['Restricción de acceso', '401 sin sesión; 403 para usuarios y Analytics desde Enfermería.'],
    ['Atención inexistente', '404, sin persistir la valoración.'],
    ['Valoración vacía', 'Defecto reproducido: guarda con 201. Caso xfail estricto pendiente de corrección.'],
], [280, 220])
p('Estas pruebas ejercitan rutas, autenticación y persistencia con mongomock aislado. No reemplazan una nueva interacción de un usuario humano ni verifican el servidor remoto de QA.')
story.append(PageBreak())

heading('CP-UAT-002 Analytics')
p('<b>Registro original:</b> condicionado. El acta y el guion coinciden en la dificultad para ubicar unidades y la saturación de información. La conclusión se formuló con ayuda del observador; la reejecución humana sigue pendiente.')
image('image10.png', 'Figura 2. KPIs y unidades de la sesión original. La presencia de etiquetas no demuestra que el usuario las comprenda.', 90)
image('image11.png', 'Figura 3. Gráficas de Analytics incluidas por Jaime. La observación de usabilidad queda asociada a estas vistas.', 235)
p('Se añadieron cuatro recorridos técnicos: login de Administración, inicio de análisis, ejecución del motor ligero, lectura autenticada del resultado y comprobación de periodo y unidades para analytics, met, clinical y unsupervised. Se usan signos vitales sintéticos fechados de forma explícita; no se atribuyen opiniones humanas a estas pruebas.')
story.append(PageBreak())

heading('Resultados técnicos y límites')
rows = []
for filename, label in [('frontend-baseline.xml', 'Frontend previo'), ('frontend-final.xml', 'Frontend final'), ('jaime-states.xml', 'Estados PBL-04'), ('backend-baseline.xml', 'Backend completo inicial'), ('backend-portable.xml', 'Backend compatible Windows'), ('uat-readiness.xml', 'Precondiciones UAT nuevas')]:
    c = counts[filename]
    rows.append([label, c['passed'], c['failed'], c['skipped_or_xfail']])
table(['Ejecución', 'Pasan', 'Fallan', 'Omitidas / xfail'], rows, [245, 70, 70, 115])
p('Las siete pruebas PBL-04 y las nueve precondiciones nuevas son subconjuntos de las suites finales; no se suman de nuevo. El caso xfail registra DEF-UAT-001 pendiente de corrección.')
p('La primera ejecución conjunta del frontend tuvo dos fallos temporales en pruebas de rutas/registro bajo carga concurrente. Se repitió la suite con un solo worker y un límite de 15 segundos por prueba; la tabla conserva el resultado final. Esta repetición no implica una corrección de código de producto.', 'CaptionReview')
p('La ejecución inicial del backend tuvo cuatro fallos: tres pruebas dependen de rutas cgroup o killpg de Linux, y una fixture usa codificación local de Windows. La ejecución portable activa PYTHONUTF8=1 y excluye explícitamente las tres pruebas Linux. Las 14 omisiones del motor Spark/memoria no se presentan como pruebas ejecutadas; queda pendiente su verificación en Linux con Java/PySpark.')
p('Traducciones, lint, build y comprobación de carga diferida pasaron. Lint conserva una advertencia heredada en UsuariosConfigScreen.jsx. Los XML conservan los resultados íntegros de cada ejecución.')
p('<b>Reproducción:</b> frontend: npm test; npm run check:i18n; npm run lint; npm run build; npm run check:bundle. Backend: python -m pytest -q. Para el subconjunto UAT: python -m pytest tests/test_sprint9_uat_readiness.py -q -rx. Para Windows, consultar el comando exacto en reproducir.ps1.', 'CaptionReview')
story.append(PageBreak())

heading('Guion de reejecución y trazabilidad')
p('Completar después de corregir los pendientes. Este formato queda preparado; no representa una sesión realizada ni una firma de aceptación.')
table(['Campo de sesión', 'Registro pendiente'], [
    ['Fecha, persona y rol representativo', '__________________________________'],
    ['Commit de qa, frontend, API y base sintética', '__________________________________'],
    ['CP-UAT-001: campos requeridos y formatos', 'Registrar esperado/obtenido, captura y defecto.'],
    ['CP-UAT-001: guardado e historial sin ayuda', 'Aprobado / Condicionado / Rechazado: __________'],
    ['CP-UAT-002: explicar periodo, unidad y gráfica', 'Registrar explicación literal y grado de ayuda.'],
    ['CP-UAT-002: conclusión y claridad de la vista', 'Aprobado / Condicionado / Rechazado: __________'],
    ['Defectos, reejecución y decisión del PO', '__________________________________'],
], [255, 245])
p('<b>REQ-17 y REQ-22 &gt; PBL-33 (#438) &gt; CP-UAT-001/002 &gt; Word original y este informe &gt; DEF-UAT-001/002.</b> PBL-04 (#281) queda vinculada a SparkAnalysisScreen.test.jsx y jaime-states.xml.')
p('Fuentes verificadas: Azure DevOps /utvt1/INEO-Enfermeria/_workitems/edit/438 y /281; GitHub JoelLara10/ineo-pbl-entrega, feature/sprint9 en 7343a42. Documentos originales: PBL-33-Plantillas-Registro-UAT.docx, PBL-33-T3-Preparacion-Ambiente-UAT.docx y PBL-33-T5-Acta-UAT.docx.', 'CaptionReview')
p('El expediente electrónico adjunto incluye XML de pruebas, resumen JSON, instrucciones de reproducción y capturas agregadas extraídas del Word original. No se cambiaron estados de Azure ni se registró una aprobación humana nueva.', 'CaptionReview')


def footer(c, doc):
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#555555'))
    c.drawString(54, 30, 'INEO | Revisión Sprint 9 | 22/10/2026')
    c.drawRightString(558, 30, str(doc.page))


SimpleDocTemplate(str(PDF), pagesize=letter, rightMargin=56, leftMargin=56,
                  topMargin=45, bottomMargin=48, title='Revisión de Jaime y pruebas UAT Sprint 9',
                  author='Revisión técnica solicitada por Joel').build(story, onFirstPage=footer, onLaterPages=footer)
paths = [PDF] + list(OUT.glob('*.xml'))
(OUT / 'sha256.json').write_text(json.dumps({str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, indent=2), encoding='utf-8')
print(PDF)
