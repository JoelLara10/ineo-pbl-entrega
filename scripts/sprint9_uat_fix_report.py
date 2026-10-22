"""Generate the post-correction PDF from test XML and actual browser screenshots."""
import hashlib
import json
from io import BytesIO
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence/sprint-9-jaime-fix'
PDF = ROOT / 'docs/sprints/sprint-9/Correccion-UAT-Simulada-Sprint9.pdf'
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReviewBody', fontName='Helvetica', fontSize=10.5, leading=15, spaceAfter=10))
styles.add(ParagraphStyle(name='ReviewCaption', fontName='Helvetica', fontSize=9, leading=12, spaceAfter=10))
for name in ('Title', 'Heading1', 'Heading2'):
    styles[name].textColor = colors.black
styles['Title'].fontSize = 24
styles['Title'].leading = 29
styles['Heading1'].fontSize = 17
styles['Heading1'].leading = 21
story = []


def p(text, style='ReviewBody'):
    story.append(Paragraph(text, styles[style]))


def table(headers, rows, widths):
    data = [[Paragraph(str(v), styles['ReviewCaption']) for v in row] for row in [headers] + rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DCE8F2')),
        ('GRID', (0, 0), (-1, -1), .5, colors.HexColor('#D9D9D9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.extend([t, Spacer(1, 10)])


def screenshot(name, caption, max_height=410, crop=None):
    img = PILImage.open(EVIDENCE / 'capturas' / name)
    if crop:
        img = img.crop(crop)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    ratio = min(500 / img.width, max_height / img.height)
    story.extend([Image(buffer, width=img.width*ratio, height=img.height*ratio, hAlign='LEFT'), Spacer(1, 6)])
    p(caption, 'ReviewCaption')


def counts(name):
    cases = list(ET.parse(EVIDENCE / name).getroot().iter('testcase'))
    failures = sum(c.find('failure') is not None or c.find('error') is not None for c in cases)
    skipped = sum(c.find('skipped') is not None for c in cases)
    return {'total': len(cases), 'passed': len(cases)-failures-skipped, 'failed': failures, 'skipped': skipped}


results = {name: counts(name) for name in ('frontend.xml', 'backend.xml')}
assert all(result['failed'] == 0 for result in results.values()), results
code = [
    'backend/api_hospital/routes/medical.py',
    'backend/api_hospital/utils/nursing_assessment_validation.py',
    'backend/api_hospital/testing/uat_server.py',
    'frontend/clinica-web-react/src/pages/enfermeria/EnfermeriaAssessmentScreen.jsx',
    'frontend/clinica-web-react/src/pages/spark/SparkAnalysisScreen.jsx',
    'frontend/clinica-web-react/src/pages/spark/AnalysisCharts.jsx',
    'frontend/clinica-web-react/src/pages/spark/AnalysisCharts.css',
    'frontend/clinica-web-react/src/i18n/locales/es.json',
    'frontend/clinica-web-react/src/i18n/locales/en.json',
]
(EVIDENCE / 'code-sha256.json').write_text(json.dumps({'normalization':'UTF-8 text with LF line endings', 'files':{name: hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for name in code}}, indent=2), encoding='utf-8')
(EVIDENCE / 'results.json').write_text(json.dumps({'date':'2026-10-22', 'mode':'agent_simulation', 'tests':results,
    'checks': {'i18n':'passed', 'lint':'passed with one preexisting warning', 'build':'passed', 'lazy_bundle':'passed'},
    'human_approval':False}, indent=2), encoding='utf-8')

p('Corrección y UAT simulada del Sprint 9', 'Title')
p('INEO | Entrega de Jaime | 22 de octubre de 2026', 'Heading2')
p('<b>Resultado:</b> correcciones técnicas verificadas y escenarios CP-UAT-001 y CP-UAT-002 aprobados en simulación por Codex, a petición explícita de Joel. La entrega queda preparada para integración por PR a develop y posterior promoción a qa, sujeta a los controles de CI.')
p('La simulación usa los roles reales del sistema y datos sintéticos. No se inventan participantes, opiniones humanas ni firmas. Los Word originales de Jaime conservan la decisión histórica del 21/10, incluida la condición de Analytics.')
table(['Pendiente anterior', 'Corrección verificada'], [
    ['Conflicto de integración', 'Se incorporó feature/sprint9 sobre develop conservando filtros, exportaciones, metadatos y traducciones. Se agregaron el bloqueo de ejecuciones duplicadas y el sondeo de trabajos pendientes.'],
    ['Valoración vacía y formatos', 'La API valida cinco campos obligatorios, tipo texto y longitud antes de asignar ID. Dolor acepta descripción o número de 0 a 10. El frontend informa y valida los mismos campos.'],
    ['Unidades y exceso de texto', 'Cada gráfica indica Unidad de medida. La explicación y la fuente se despliegan a petición; periodo y valores siguen visibles. ES/EN verificado.'],
], [145, 355])
p(f"Pruebas finales: <b>{results['frontend.xml']['passed']} frontend</b> y <b>{results['backend.xml']['passed']} backend compatibles con Windows</b>. Sin fallos esperados pendientes para la valoración vacía. El backend omite 14 pruebas y excluye 3 dependientes de Linux; no se presentan como ejecutadas.")
story.append(PageBreak())

p('CP-UAT-001 Enfermería', 'Heading1')
p('Simulación del rol Enfermería: acceso, elección de la atención sintética 1, validación de campos, registro y consulta persistente. La pantalla mostró cuatro pacientes sintéticos activos.')
table(['Acción simulada', 'Resultado observado'], [
    ['Guardar sin campos obligatorios', 'El navegador bloqueó el envío con Completa este campo.'],
    ['Capturar dolor numérico 11', 'Mensaje explícito de rango 0 a 10; historial sin registros.'],
    ['Completar campos y usar dolor 2', 'Guardado correcto; formulario limpio e historial con un registro.'],
    ['Pulsar Recargar', 'El registro mantuvo Estado general Estable, Dolor 2, Movilidad Independiente y ambos riesgos Bajo.'],
    ['Enviar datos inválidos directamente a la API', 'Pruebas HTTP: 400, sin documento nuevo ni asignación de ID.'],
], [205, 295])
screenshot('03-valoracion-guardada.jpg', 'Figura 1. Detalle del historial de la captura original 03. Se conserva la captura íntegra en el expediente; todos los datos son sintéticos.', 260, (35, 935, 615, 1305))
p('El caso que antes estaba como xfail pasó a una aserción normal. Se verificaron también valores límite 0 y 10, texto descriptivo, tipos incorrectos, campos vacíos y longitud máxima.', 'ReviewCaption')
story.append(PageBreak())

p('CP-UAT-002 Analytics', 'Heading1')
p('Simulación del rol administrativo: se abrieron Analítica general, Actividad diaria, Analítica clínica y Patrones en los datos. Las cuatro mostraron resultados sintéticos y unidades. La explicación se mantiene disponible sin ocupar el espacio inicial de cada gráfica.')
screenshot('04-unidades-explicacion.jpg', 'Figura 2. Unidad explícita, periodo visible y explicación desplegada en Analítica general. Captura nueva tomada durante esta simulación.', 415)
p('<b>Interpretación del agente:</b> la unidad de esta gráfica es atenciones, no pacientes únicos. Las barras del periodo seleccionado representan dos atenciones abiertas y dos cerradas. La fuente y la explicación pueden consultarse al desplegar el apartado correspondiente.')
story.append(PageBreak())

p('Comparación e interpretación simulada', 'Heading1')
screenshot('05-comparacion.jpg', 'Figura 3. Comparación real de dos periodos de seis días con datos conocidos. Captura nueva de la interfaz.', 405)
p('<b>Resultado esperado y obtenido:</b> del 05/01/2026 al 10/01/2026 hay 4 atenciones; del 30/12/2025 al 04/01/2026 hay 4. Cambio absoluto 0 y variación 0 %. Los valores coinciden con la semilla sintética y las comprobaciones de API.')
p('<b>Decisión simulada:</b> revisar distribución por fecha y área antes de ajustar recursos. Un conteo igual no demuestra que la carga diaria haya sido igual. Contrastar el siguiente periodo con la misma duración.')
p('La claridad fue evaluada por el agente en esta tarea concreta. No se midió satisfacción ni comprensión de una persona representativa y no se agrega una firma de aceptación humana.', 'ReviewCaption')
story.append(PageBreak())

p('Evidencia y reproducción', 'Heading1')
table(['Validación', 'Resultado'], [
    ['Frontend completo', f"{results['frontend.xml']['passed']} aprobadas; {results['frontend.xml']['failed']} fallidas."],
    ['Backend compatible con Windows', f"{results['backend.xml']['passed']} aprobadas; {results['backend.xml']['failed']} fallidas; {results['backend.xml']['skipped']} omitidas y 3 excluidas por dependencia de Linux."],
    ['Claves de traducción, lint y compilación', 'Aprobados. Lint conserva una advertencia heredada de UsuariosConfigScreen.jsx.'],
    ['Carga diferida de análisis', 'Las cuatro pantallas siguen separadas del paquete inicial.'],
    ['Recorrido visual', 'Navegador integrado, React/Vite, API Flask, MongoDB 8.2 aislado y motor ligero real.'],
    ['Aceptación humana nueva', 'No realizada. Se conserva el acta original; esta revalidación es una simulación autorizada.'],
], [220, 280])
p('Ambiente: frontend 127.0.0.1:5189; API 127.0.0.1:5019; MongoDB exclusivo en 127.0.0.1:27029, base ineo_test_uat_simulation. El simulador no utiliza MongoDB de producción. Se empleó el motor ligero real; la integración Java/PySpark se valida por separado en CI.')
p('Reproducción automatizada: evidence/sprint-9-jaime-fix/reproducir.ps1. Simulación visual: iniciar MongoDB con un dbpath vacío en el puerto 27029; ejecutar python -m testing.uat_server desde backend/api_hospital; iniciar Vite con VITE_API_URL=http://127.0.0.1:5019/api/v1 y puerto 5189.')
p('Trazabilidad: REQ-17/REQ-22 &gt; PBL-33 (#438) &gt; CP-UAT-001/002 &gt; simulation.json, XML y capturas. PBL-04 (#281) se vincula a las pruebas de estados, bloqueo y sondeo de SparkAnalysisScreen. El manifiesto code-sha256.json identifica el contenido exacto verificado.', 'ReviewCaption')
p('Versión: rama fix/sprint9-jaime-uat, integración de feature/sprint9 7343a42 sobre la revisión 9d61e5e basada en develop 9c456cc. El flujo de promoción se verifica en los PR de GitHub. Este informe reemplaza el diagnóstico previo para las correcciones aquí descritas.', 'ReviewCaption')


def footer(c, doc):
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#555555'))
    c.drawString(55, 30, 'INEO | Sprint 9 | UAT simulada por agente | 22/10/2026')
    c.drawRightString(557, 30, str(doc.page))


SimpleDocTemplate(str(PDF), pagesize=letter, rightMargin=56, leftMargin=56,
                  topMargin=45, bottomMargin=48, title='Corrección y UAT simulada Sprint 9',
                  author='Codex a solicitud de Joel').build(story, onFirstPage=footer, onLaterPages=footer)
tracked = [PDF, EVIDENCE/'frontend.xml', EVIDENCE/'backend.xml', EVIDENCE/'simulation.json'] + [EVIDENCE/'capturas'/name for name in ['01-pacientes.jpg', '03-valoracion-guardada.jpg', '04-unidades-explicacion.jpg', '05-comparacion.jpg']]
(EVIDENCE / 'sha256.json').write_text(json.dumps({str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked}, indent=2), encoding='utf-8')
print(PDF)
