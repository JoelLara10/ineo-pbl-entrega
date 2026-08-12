from flask import Blueprint, request, jsonify, send_file, g, make_response, current_app
from middleware.auth_middleware import token_required
from services.pdf_service import PDFService
from datetime import datetime
from utils.database import get_db, serialize_doc, get_next_sequence
from fpdf import FPDF
from bson import ObjectId
import io
import os
import tempfile
import traceback

from utils.database import serialize_doc

pdf_bp = Blueprint('pdf', __name__, url_prefix='/pdf')


# ==================== FUNCIONES AUXILIARES ====================
def parse_fecha(fecha):
    if fecha is None:
        return datetime.now()
    if isinstance(fecha, datetime):
        return fecha
    if isinstance(fecha, str):
        try:
            return datetime.fromisoformat(fecha.replace('Z', '+00:00'))
        except:
            for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d']:
                try:
                    return datetime.strptime(fecha, fmt)
                except:
                    continue
    return datetime.now()


def formatear_fecha(fecha, formato='%d/%m/%Y %H:%M'):
    if fecha is None:
        return ''
    fecha_dt = parse_fecha(fecha)
    return fecha_dt.strftime(formato)

@pdf_bp.route('/initial-sheet/<int:id_exp>/<int:id_atencion>', methods=['GET'])
@token_required
def get_initial_sheet(id_exp, id_atencion):
    """Genera hoja inicial de paciente"""
    pdf_file = PDFService.generate_initial_sheet(id_exp, id_atencion)
    
    if not pdf_file:
        return jsonify({'error': 'Error generando PDF'}), 500
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'hoja_inicial_{id_atencion}.pdf'
    )

@pdf_bp.route('/front-sheet/<int:id_exp>/<int:id_atencion>', methods=['GET'])
@token_required
def get_front_sheet(id_exp, id_atencion):
    """Genera hoja frontal"""
    pdf_file = PDFService.generate_front_sheet(id_exp, id_atencion)
    
    if not pdf_file:
        return jsonify({'error': 'Error generando PDF'}), 500
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'hoja_frontal_{id_atencion}.pdf'
    )

@pdf_bp.route('/contract/<int:id_exp>/<int:id_atencion>', methods=['GET'])
@token_required
def get_contract(id_exp, id_atencion):
    """Genera contrato de servicios"""
    pdf_file = PDFService.generate_contract(id_exp, id_atencion)
    
    if not pdf_file:
        return jsonify({'error': 'Error generando PDF'}), 500
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'contrato_{id_atencion}.pdf'
    )

@pdf_bp.route('/consent/<int:id_exp>/<int:id_atencion>', methods=['GET'])
@token_required
def get_consent(id_exp, id_atencion):
    """Genera consentimiento de datos personales"""
    pdf_file = PDFService.generate_consent(id_exp, id_atencion)
    
    if not pdf_file:
        return jsonify({'error': 'Error generando PDF'}), 500
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'consentimiento_{id_atencion}.pdf'
    )


@pdf_bp.route('/identification-sheet/<int:id_exp>/<int:id_atencion>', methods=['GET'])
@token_required
def get_identification_sheet(id_exp, id_atencion):
    """Genera la ficha o tarjeta de identificación del paciente."""
    pdf_file = PDFService.generate_identification_sheet(id_exp, id_atencion)

    if not pdf_file:
        return jsonify({'error': 'Error generando PDF'}), 500

    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'ficha_identificacion_{id_atencion}.pdf'
    )


# ==================== PDF DE SIGNOS VITALES ====================
@pdf_bp.route('/vital-signs/<int:id_signos>', methods=['GET'])
def get_vital_signs_pdf(id_signos):
    try:
        token = request.args.get('token')
        id_atencion = request.args.get('id_atencion', type=int)
        if not token or not id_atencion:
            return jsonify({'error': 'Token e id_atencion son requeridos'}), 400
        from middleware.auth_middleware import verify_token
        if not verify_token(token):
            return jsonify({'error': 'Token inválido o expirado'}), 401
        db = get_db()
        datos = db['signos_vitales'].find_one({'id_signos': id_signos, 'id_atencion': id_atencion})
        if not datos:
            return jsonify({'error': 'Signos vitales no encontrados o no pertenecen a esta atención'}), 404
        atencion = db['atencion'].find_one({'id_atencion': id_atencion})
        if not atencion:
            return jsonify({'error': 'Atención no encontrada'}), 404
        paciente = db['pacientes'].find_one({'Id_exp': atencion.get('Id_exp')}) or {}

        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()

        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'SIGNOS VITALES', ln=True, align='C')
        pdf.ln(5)

        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f"Paciente: {paciente.get('papell', '')} {paciente.get('sapell', '')} {paciente.get('nom_pac', '')}", ln=True)
        pdf.cell(0, 7, f"Expediente: {paciente.get('Id_exp', '')}", ln=True)
        pdf.cell(0, 7, f"Fecha: {formatear_fecha(datos.get('fecha_registro'))}", ln=True)
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(60, 10, 'Parametro', border=1, align='C')
        pdf.cell(60, 10, 'Valor', border=1, align='C')
        pdf.cell(60, 10, 'Unidad', border=1, align='C')
        pdf.ln()

        pdf.set_font('Arial', '', 10)
        signos = [
            ('Presion Arterial (TA)', datos.get('ta', ''), 'mmHg'),
            ('Frecuencia Cardiaca (FC)', datos.get('fc', ''), 'lpm'),
            ('Frecuencia Respiratoria (FR)', datos.get('fr', ''), 'rpm'),
            ('Temperatura', datos.get('temp', ''), '°C'),
            ('SpO2', datos.get('spo2', ''), '%'),
            ('Peso', datos.get('peso', ''), 'kg'),
            ('Talla', datos.get('talla', ''), 'm')
        ]

        for label, value, unit in signos:
            pdf.cell(60, 8, label, border=1)
            pdf.cell(60, 8, str(value) if value else '-', border=1, align='C')
            pdf.cell(60, 8, unit, border=1, align='C')
            pdf.ln()

        pdf.ln(15)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, "__________________________________", ln=True, align='C')
        pdf.cell(0, 7, "Firma del Medico", ln=True, align='C')

        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')

        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=signos_vitales_{id_signos}.pdf'
        return response

    except Exception as e:
        print(f"Error generando PDF de signos vitales: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== PDF DE NOTA MÉDICA ====================
@pdf_bp.route('/medical-note/<int:id_nota>', methods=['GET'])

def get_medical_note_pdf(id_nota):
    try:
        token = request.args.get('token')
        id_atencion = request.args.get('id_atencion', type=int)
        
        if not token or not id_atencion:
            return jsonify({'error': 'Token e id_atencion son requeridos'}), 400

        from middleware.auth_middleware import verify_token
        if not verify_token(token):
            return jsonify({'error': 'Token inválido o expirado'}), 401

        db = get_db()

        if not db['notas_medicas'].find_one({'id_nota': id_nota, 'id_atencion': id_atencion}):
            return jsonify({'error': 'Nota médica no encontrada o no pertenece a esta atención'}), 404

        pipeline = [
            {"$match": {"id_nota": id_nota, "id_atencion": id_atencion}},
            {"$lookup": {"from": "atencion", "localField": "id_atencion", "foreignField": "id_atencion", "as": "atencion"}},
            {"$unwind": "$atencion"},
            {"$lookup": {"from": "pacientes", "localField": "atencion.Id_exp", "foreignField": "Id_exp", "as": "paciente"}},
            {"$unwind": "$paciente"},
            {"$lookup": {"from": "users", "localField": "id_medico", "foreignField": "_id", "as": "medico"}},
            {"$unwind": {"path": "$medico", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "subjetivo": 1, "objetivo": 1, "analisis": 1, "plan": 1, "fecha_registro": 1,
                "papell": "$paciente.papell", "sapell": "$paciente.sapell", "nom_pac": "$paciente.nom_pac", 
                "Id_exp": "$paciente.Id_exp",
                "medico_nombre": {"$concat": ["$medico.nombre", " ", "$medico.papell"]}
            }}
        ]

        datos = list(db['notas_medicas'].aggregate(pipeline))[0]

        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()

        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'NOTA MEDICA (SOAP)', ln=True, align='C')
        pdf.ln(5)

        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f"Paciente: {datos['papell']} {datos['sapell']} {datos['nom_pac']}", ln=True)
        pdf.cell(0, 7, f"Expediente: {datos['Id_exp']}", ln=True)
        pdf.cell(0, 7, f"Fecha: {formatear_fecha(datos.get('fecha_registro'))}", ln=True)
        if datos.get('medico_nombre'):
            pdf.cell(0, 7, f"Médico: {datos['medico_nombre']}", ln=True)

        pdf.ln(8)
        for title, content in [
            ('S - Subjetivo', datos.get('subjetivo', 'No especificado')),
            ('O - Objetivo', datos.get('objetivo', 'No especificado')),
            ('A - Análisis', datos.get('analisis', 'No especificado')),
            ('P - Plan', datos.get('plan', 'No especificado'))
        ]:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, title, ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, content)
            pdf.ln(3)

        pdf.ln(10)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, "__________________________________", ln=True, align='C')
        pdf.cell(0, 7, "Firma del Medico", ln=True, align='C')

        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')

        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=nota_medica_{id_nota}.pdf'
        return response

    except Exception as e:
        print(f"Error generando PDF de nota médica: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== PDF DE DIAGNÓSTICO ====================
@pdf_bp.route('/diagnosis/<int:id_diagnostico>', methods=['GET'])
def get_diagnosis_pdf(id_diagnostico):
    try:
        token = request.args.get('token')
        id_atencion = request.args.get('id_atencion', type=int)
        if not token or not id_atencion:
            return jsonify({'error': 'Token e id_atencion son requeridos'}), 400

        from middleware.auth_middleware import verify_token
        if not verify_token(token):
            return jsonify({'error': 'Token inválido o expirado'}), 401

        db = get_db()
        if not db['diagnosticos'].find_one({'id_diagnostico': id_diagnostico, 'id_atencion': id_atencion}):
            return jsonify({'error': 'Diagnóstico no encontrado o no pertenece a esta atención'}), 404

        pipeline = [
            {"$match": {"id_diagnostico": id_diagnostico, "id_atencion": id_atencion}},
            {"$lookup": {"from": "atencion", "localField": "id_atencion", "foreignField": "id_atencion", "as": "atencion"}},
            {"$unwind": "$atencion"},
            {"$lookup": {"from": "pacientes", "localField": "atencion.Id_exp", "foreignField": "Id_exp", "as": "paciente"}},
            {"$unwind": "$paciente"},
            {"$lookup": {"from": "users", "localField": "id_medico", "foreignField": "_id", "as": "medico"}},
            {"$unwind": {"path": "$medico", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "diagnostico_principal": 1, "diagnosticos_secundarios": 1, "observaciones": 1, "fecha_registro": 1,
                "papell": "$paciente.papell", "sapell": "$paciente.sapell", "nom_pac": "$paciente.nom_pac", 
                "Id_exp": "$paciente.Id_exp",
                "medico_nombre": {"$concat": ["$medico.nombre", " ", "$medico.papell"]}
            }}
        ]

        datos = list(db['diagnosticos'].aggregate(pipeline))[0]

        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()

        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'DIAGNOSTICO MEDICO', ln=True, align='C')
        pdf.ln(5)

        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f"Paciente: {datos['papell']} {datos['sapell']} {datos['nom_pac']}", ln=True)
        pdf.cell(0, 7, f"Expediente: {datos['Id_exp']}", ln=True)
        pdf.cell(0, 7, f"Fecha: {formatear_fecha(datos.get('fecha_registro'))}", ln=True)
        if datos.get('medico_nombre'):
            pdf.cell(0, 7, f"Médico: {datos['medico_nombre']}", ln=True)

        pdf.ln(8)
        for title, field in [
            ('Diagnóstico Principal', 'diagnostico_principal'),
            ('Diagnósticos Secundarios', 'diagnosticos_secundarios'),
            ('Observaciones', 'observaciones')
        ]:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, f'{title}:', ln=True)
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 6, datos.get(field) or 'Ninguno')
            pdf.ln(3)

        pdf.ln(10)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, "__________________________________", ln=True, align='C')
        pdf.cell(0, 7, "Firma del Medico", ln=True, align='C')

        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')

        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=diagnostico_{id_diagnostico}.pdf'
        return response

    except Exception as e:
        print(f"Error generando PDF de diagnóstico: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== PDF DE RECETA ====================
@pdf_bp.route('/prescription/<int:id_receta>', methods=['GET'])
def get_prescription_pdf(id_receta):
    try:
        token = request.args.get('token')
        id_atencion = request.args.get('id_atencion', type=int)
        if not token or not id_atencion:
            return jsonify({'error': 'Token e id_atencion son requeridos'}), 400

        from middleware.auth_middleware import verify_token
        if not verify_token(token):
            return jsonify({'error': 'Token inválido o expirado'}), 401

        db = get_db()
        if not db['recetas'].find_one({'id_receta': id_receta, 'id_atencion': id_atencion}):
            return jsonify({'error': 'Receta no encontrada o no pertenece a esta atención'}), 404

        pipeline = [
            {"$match": {"id_receta": id_receta, "id_atencion": id_atencion}},
            {"$lookup": {"from": "atencion", "localField": "id_atencion", "foreignField": "id_atencion", "as": "atencion"}},
            {"$unwind": "$atencion"},
            {"$lookup": {"from": "pacientes", "localField": "atencion.Id_exp", "foreignField": "Id_exp", "as": "paciente"}},
            {"$unwind": "$paciente"},
            {"$lookup": {"from": "users", "localField": "id_medico", "foreignField": "_id", "as": "medico"}},
            {"$unwind": {"path": "$medico", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "medicamentos": 1, "fecha_registro": 1,
                "papell": "$paciente.papell", "sapell": "$paciente.sapell", "nom_pac": "$paciente.nom_pac", 
                "Id_exp": "$paciente.Id_exp",
                "medico_nombre": {"$concat": ["$medico.nombre", " ", "$medico.papell"]}
            }}
        ]

        datos = list(db['recetas'].aggregate(pipeline))[0]

        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()

        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'RECETA MEDICA', ln=True, align='C')
        pdf.ln(5)

        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f"Paciente: {datos['papell']} {datos['sapell']} {datos['nom_pac']}", ln=True)
        pdf.cell(0, 7, f"Expediente: {datos['Id_exp']}", ln=True)
        pdf.cell(0, 7, f"Fecha: {formatear_fecha(datos.get('fecha_registro'))}", ln=True)
        if datos.get('medico_nombre'):
            pdf.cell(0, 7, f"Médico: {datos['medico_nombre']}", ln=True)

        pdf.ln(8)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'MEDICAMENTOS RECETADOS:', ln=True)
        pdf.ln(3)

        for i, med in enumerate(datos.get('medicamentos', []), 1):
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 7, f"{i}. {med.get('medicamento', '')}", ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f"   Dosis: {med.get('dosis', 'No especificada')}", ln=True)
            pdf.cell(0, 6, f"   Frecuencia: {med.get('frecuencia', 'No especificada')}", ln=True)
            pdf.cell(0, 6, f"   Duracion: {med.get('duracion', 'No especificada')}", ln=True)
            if med.get('indicaciones'):
                pdf.multi_cell(0, 6, f"   Indicaciones: {med.get('indicaciones', '')}")
            pdf.ln(3)

        pdf.ln(10)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, "__________________________________", ln=True, align='R')
        pdf.cell(0, 7, "Firma del Medico", ln=True, align='R')

        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')

        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=receta_{id_receta}.pdf'
        return response

    except Exception as e:
        print(f"Error generando PDF de receta: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== PDF DE LABORATORIO ====================
@pdf_bp.route('/lab/<int:id_examen>', methods=['GET'])
def get_lab_pdf(id_examen):
    try:
        token = request.args.get('token')
        id_atencion = request.args.get('id_atencion', type=int)
        if not token or not id_atencion:
            return jsonify({'error': 'Token e id_atencion son requeridos'}), 400

        from middleware.auth_middleware import verify_token
        if not verify_token(token):
            return jsonify({'error': 'Token inválido o expirado'}), 401

        db = get_db()
        if not db['examenes'].find_one({'id_examen': id_examen, 'id_atencion': id_atencion}):
            return jsonify({'error': 'Examen de laboratorio no encontrado o no pertenece a esta atención'}), 404

        

        # Encabezado
        pipeline_enc = [
            {"$match": {"id_examen": id_examen, "id_atencion": id_atencion}},
            {"$lookup": {"from": "atencion", "localField": "id_atencion", "foreignField": "id_atencion", "as": "atencion"}},
            {"$unwind": "$atencion"},
            {"$lookup": {"from": "pacientes", "localField": "atencion.Id_exp", "foreignField": "Id_exp", "as": "paciente"}},
            {"$unwind": "$paciente"},
            {"$lookup": {"from": "users", "localField": "id_medico", "foreignField": "_id", "as": "medico"}},
            {"$unwind": {"path": "$medico", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "fecha": 1, "observaciones": 1,
                "papell": "$paciente.papell", "sapell": "$paciente.sapell", "nom_pac": "$paciente.nom_pac", 
                "Id_exp": "$paciente.Id_exp",
                "medico_nombre": {"$concat": ["$medico.nombre", " ", "$medico.papell"]}
            }}
        ]

        encabezado = list(db['examenes'].aggregate(pipeline_enc))[0]

        # Detalles
        pipeline_det = [
            {"$match": {"id_examen": id_examen}},
            {"$lookup": {"from": "catalogo_examenes", "localField": "id_catalogo", "foreignField": "id_catalogo", "as": "cat"}},
            {"$unwind": "$cat"},
            {"$match": {"cat.tipo": "LABORATORIO"}},
            {"$project": {
                "nombre": "$cat.nombre", "estado": 1, "resultado": 1,
                "fecha_realizado": 1, "observaciones": 1
            }}
        ]

        detalles = list(db['examenes_det'].aggregate(pipeline_det))
        if not detalles:
            detalles = list(db['examenes_det'].find(
                {'id_examen': id_examen, 'tipo': 'LABORATORIO'},
                {'nombre_examen': 1, 'estado': 1, 'resultado': 1, 'fecha_realizado': 1, 'observaciones': 1}
            ))
            detalles = [{
                'nombre': det.get('nombre_examen', 'Examen sin nombre'),
                'estado': det.get('estado'),
                'resultado': det.get('resultado'),
                'fecha_realizado': det.get('fecha_realizado'),
                'observaciones': det.get('observaciones'),
            } for det in detalles]

        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()

        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'EXAMENES DE LABORATORIO', ln=True, align='C')
        pdf.ln(5)

        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f"Paciente: {encabezado['papell']} {encabezado['sapell']} {encabezado['nom_pac']}", ln=True)
        pdf.cell(0, 7, f"Expediente: {encabezado['Id_exp']}", ln=True)
        pdf.cell(0, 7, f"Fecha de solicitud: {formatear_fecha(encabezado.get('fecha'))}", ln=True)
        if encabezado.get('medico_nombre'):
            pdf.cell(0, 7, f"Médico solicitante: {encabezado['medico_nombre']}", ln=True)

        if encabezado.get('observaciones'):
            pdf.ln(3)
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 7, 'Observaciones:', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, encabezado['observaciones'])

        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'EXAMENES SOLICITADOS:', ln=True)
        pdf.ln(3)

        if not detalles:
            pdf.set_font('Arial', '', 11)
            pdf.cell(0, 6, 'Sin detalles de exámenes para esta solicitud.', ln=True)
        else:
            for i, det in enumerate(detalles, 1):
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, f"{i}. {det['nombre']}", ln=True)
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 5, f"   Estado: {det.get('estado', 'PENDIENTE')}", ln=True)
                if det.get('fecha_realizado'):
                    pdf.cell(0, 5, f"   Fecha realizado: {formatear_fecha(det.get('fecha_realizado'), '%d/%m/%Y')}", ln=True)
                if det.get('resultado'):
                    pdf.multi_cell(0, 5, f"   Resultado: {det['resultado']}")
                if det.get('observaciones'):
                    pdf.multi_cell(0, 5, f"   Observaciones: {det['observaciones']}")
                pdf.ln(3)

        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')

        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=laboratorio_{id_examen}.pdf'
        return response

    except Exception as e:
        print(f"Error generando PDF de laboratorio: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== PDF DE GABINETE ====================
@pdf_bp.route('/imaging/<int:id_examen>', methods=['GET'])
def get_imaging_pdf(id_examen):
    try:
        token = request.args.get('token')
        id_atencion = request.args.get('id_atencion', type=int)
        if not token or not id_atencion:
            return jsonify({'error': 'Token e id_atencion son requeridos'}), 400

        from middleware.auth_middleware import verify_token
        if not verify_token(token):
            return jsonify({'error': 'Token inválido o expirado'}), 401

        db = get_db()
        if not db['examenes'].find_one({'id_examen': id_examen, 'id_atencion': id_atencion}):
            return jsonify({'error': 'Examen de gabinete no encontrado o no pertenece a esta atención'}), 404

        # Encabezado
        pipeline_enc = [
            {"$match": {"id_examen": id_examen, "id_atencion": id_atencion}},
            {"$lookup": {"from": "atencion", "localField": "id_atencion", "foreignField": "id_atencion", "as": "atencion"}},
            {"$unwind": "$atencion"},
            {"$lookup": {"from": "pacientes", "localField": "atencion.Id_exp", "foreignField": "Id_exp", "as": "paciente"}},
            {"$unwind": "$paciente"},
            {"$lookup": {"from": "users", "localField": "id_medico", "foreignField": "_id", "as": "medico"}},
            {"$unwind": {"path": "$medico", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "fecha": 1, "observaciones": 1,
                "papell": "$paciente.papell", "sapell": "$paciente.sapell", "nom_pac": "$paciente.nom_pac", 
                "Id_exp": "$paciente.Id_exp",
                "medico_nombre": {"$concat": ["$medico.nombre", " ", "$medico.papell"]}
            }}
        ]

        encabezado = list(db['examenes'].aggregate(pipeline_enc))[0]

        # Detalles
        pipeline_det = [
            {"$match": {"id_examen": id_examen}},
            {"$lookup": {"from": "catalogo_examenes", "localField": "id_catalogo", "foreignField": "id_catalogo", "as": "cat"}},
            {"$unwind": "$cat"},
            {"$match": {"cat.tipo": "GABINETE"}},
            {"$project": {
                "nombre": "$cat.nombre", "estado": 1,
                "fecha_realizado": 1, "observaciones": 1, "archivo_resultado": 1
            }}
        ]

        detalles = list(db['examenes_det'].aggregate(pipeline_det))

        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()

        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'EXAMENES DE GABINETE', ln=True, align='C')
        pdf.ln(5)

        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 7, f"Paciente: {encabezado['papell']} {encabezado['sapell']} {encabezado['nom_pac']}", ln=True)
        pdf.cell(0, 7, f"Expediente: {encabezado['Id_exp']}", ln=True)
        pdf.cell(0, 7, f"Fecha de solicitud: {formatear_fecha(encabezado.get('fecha'))}", ln=True)
        if encabezado.get('medico_nombre'):
            pdf.cell(0, 7, f"Médico solicitante: {encabezado['medico_nombre']}", ln=True)

        if encabezado.get('observaciones'):
            pdf.ln(3)
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 7, 'Observaciones:', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, encabezado['observaciones'])

        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'ESTUDIOS SOLICITADOS:', ln=True)
        pdf.ln(3)

        for i, det in enumerate(detalles, 1):
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, f"{i}. {det['nombre']}", ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f"   Estado: {det.get('estado', 'PENDIENTE')}", ln=True)
            if det.get('fecha_realizado'):
                pdf.cell(0, 5, f"   Fecha realizado: {formatear_fecha(det.get('fecha_realizado'), '%d/%m/%Y')}", ln=True)
            if det.get('archivo_resultado'):
                pdf.cell(0, 5, "   Archivo resultado: Disponible", ln=True)
            if det.get('observaciones'):
                pdf.multi_cell(0, 5, f"   Observaciones: {det['observaciones']}")
            pdf.ln(3)

        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')

        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=gabinete_{id_examen}.pdf'
        return response

    except Exception as e:
        print(f"Error generando PDF de gabinete: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINT DE PRUEBA ====================
@pdf_bp.route('/test', methods=['GET'])
def test_pdf():
    return jsonify({'message': 'PDF blueprint funcionando correctamente'}), 200
