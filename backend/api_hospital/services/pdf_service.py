from utils.database import get_collection, serialize_doc
from datetime import datetime
from fpdf import FPDF
import tempfile
import os
from services.study_service import StudyService

class PDFService:
    
    @staticmethod
    def _get_patient_data(id_exp, id_atencion):
        """Obtiene datos de paciente y atención"""
        db = get_collection('atencion').database
        
        atencion = db['atencion'].find_one({"id_atencion": id_atencion}) or {}
        paciente = db['pacientes'].find_one({"Id_exp": id_exp}) or {}
        
        # Obtener médico
        medicos_asignados = list(db['atencion_medicos'].find({"id_atencion": id_atencion}))
        medico = {}
        if medicos_asignados:
            id_medico = medicos_asignados[0].get('id_medico')
            if id_medico:
                medico = db['users'].find_one({"id": int(id_medico)}) or {}
        
        return {
            'atencion': atencion,
            'paciente': paciente,
            'medico': medico
        }
    
    @staticmethod
    def generate_initial_sheet(id_exp, id_atencion):
        """Genera hoja inicial"""
        data = PDFService._get_patient_data(id_exp, id_atencion)
        atencion = data['atencion']
        paciente = data['paciente']
        medico = data['medico']
        
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 25)
        pdf.add_page()
        
        # Título
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'HOJA INICIAL', ln=True, align='C')
        
        # Fecha
        pdf.set_font('Arial', '', 10)
        fecha = atencion.get('fecha_ing')
        if fecha:
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha.split('T')[0], '%Y-%m-%d')
                except:
                    fecha = datetime.now()
            fecha_str = fecha.strftime('%d/%m/%Y %H:%M')
        else:
            fecha_str = ''
        pdf.cell(0, 6, f'Fecha de ingreso: {fecha_str}', ln=True, align='R')
        pdf.ln(4)
        
        # Datos del Paciente
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Datos del Paciente', ln=True)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, f"Paciente: {paciente.get('papell', '')} {paciente.get('sapell', '')} {paciente.get('nom_pac', '')}", ln=True)
        pdf.cell(0, 7, f"Teléfono: {paciente.get('tel', 'No especificado')}", ln=True)
        
        # Datos de Atención
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Datos de Atención', ln=True)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, f"Área: {atencion.get('area', '')}", ln=True)
        pdf.multi_cell(0, 7, f"Motivo de atención:\n{atencion.get('motivo', '')}")
        pdf.multi_cell(0, 7, f"Alergias:\n{atencion.get('alergias', 'No especificado')}")
        
        # Médico
        pdf.ln(20)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, f"Médico: {medico.get('papell', '')} ({medico.get('username', '')})", ln=True, align='C')
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def generate_front_sheet(id_exp, id_atencion):
        """Genera hoja frontal"""
        data = PDFService._get_patient_data(id_exp, id_atencion)
        atencion = data['atencion']
        paciente = data['paciente']
        medico = data['medico']
        
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 25)
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'HOJA FRONTAL', ln=True, align='C')
        
        pdf.set_font('Arial', '', 10)
        fecha = atencion.get('fecha_ing')
        if fecha:
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha.split('T')[0], '%Y-%m-%d')
                except:
                    fecha = datetime.now()
            fecha_str = fecha.strftime('%d/%m/%Y %H:%M')
        else:
            fecha_str = ''
        pdf.cell(0, 6, f'Fecha de ingreso: {fecha_str}', ln=True, align='R')
        pdf.ln(4)
        
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Datos del Paciente', ln=True)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, f"Paciente: {id_exp} - {paciente.get('papell', '')} {paciente.get('sapell', '')} {paciente.get('nom_pac', '')}", ln=True)
        pdf.cell(0, 7, f"Teléfono: {paciente.get('tel', 'No especificado')}", ln=True)
        
        # Edad
        fecnac = paciente.get('fecnac')
        if fecnac:
            if isinstance(fecnac, str):
                try:
                    fecnac = datetime.strptime(fecnac.split('T')[0], '%Y-%m-%d')
                except:
                    fecnac = None
            if fecnac:
                edad = datetime.now().year - fecnac.year
                pdf.cell(0, 7, f"Edad: {edad} años", ln=True)
        
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Datos de Atención', ln=True)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, f"Área: {atencion.get('area', '')}", ln=True)
        pdf.cell(0, 7, f"Especialidad: {atencion.get('especialidad', 'No especificada')}", ln=True)
        pdf.multi_cell(0, 7, f"Motivo de atención:\n{atencion.get('motivo', '')}")
        pdf.multi_cell(0, 7, f"Alergias:\n{atencion.get('alergias', 'No especificado')}")
        
        pdf.ln(15)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, f"Médico tratante: {medico.get('papell', '')} ({medico.get('username', '')})", ln=True, align='C')
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def generate_contract(id_exp, id_atencion):
        """Genera contrato de servicios"""
        data = PDFService._get_patient_data(id_exp, id_atencion)
        atencion = data['atencion']
        paciente = data['paciente']
        medico = data['medico']
        
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 30)
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'CONTRATO DE PRESTACIÓN DE SERVICIOS HOSPITALARIOS', ln=True, align='C')
        
        pdf.set_font('Arial', '', 10)
        fecha = atencion.get('fecha_ing')
        if fecha:
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha.split('T')[0], '%Y-%m-%d')
                except:
                    fecha = datetime.now()
            fecha_str = fecha.strftime('%d/%m/%Y %H:%M')
        else:
            fecha_str = ''
        pdf.cell(0, 6, f'Fecha: {fecha_str}', ln=True, align='R')
        pdf.ln(4)
        
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Datos del Paciente', ln=True)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, f"Paciente: {id_exp} - {paciente.get('papell', '')} {paciente.get('sapell', '')} {paciente.get('nom_pac', '')}", ln=True)
        pdf.cell(0, 7, f"Teléfono: {paciente.get('tel', 'No especificado')}", ln=True)
        
        pdf.ln(4)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'CLÁUSULAS', ln=True, align='C')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 9)
        
        clausulas = [
            "PRIMERA.- El INSTITUTO DE ENFERMEDADES OCULARES se obliga, a solicitud del PACIENTE, a proporcionarle los servicios hospitalarios necesarios conforme a indicaciones médicas.",
            "SEGUNDA.- El PACIENTE se obliga a cubrir el importe total de los servicios médicos, hospitalarios, medicamentos, estudios y cualquier otro cargo derivado de su atención.",
            "TERCERA.- El PACIENTE acepta que los pagos deberán cubrirse conforme se generen los cargos, liquidando el total al momento del alta médica.",
            "CUARTA.- El PACIENTE se compromete a respetar el reglamento interno del Instituto, liberándolo de cualquier responsabilidad ajena al acto médico.",
            f"QUINTA.- El PACIENTE autoriza al Médico tratante {medico.get('papell', '')} para llevar a cabo los procedimientos médicos y/o quirúrgicos que considere necesarios.",
            "SEXTA.- En caso de que el PACIENTE no pueda firmar el presente contrato, podrá hacerlo la persona responsable que lo acompañe."
        ]
        
        for clausula in clausulas:
            pdf.multi_cell(0, 6, clausula)
            pdf.ln(2)
        
        pdf.ln(10)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f'Metepec, México a {datetime.now().strftime("%d/%m/%Y")}', ln=True, align='C')
        pdf.ln(8)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(95, 6, 'PACIENTE', 0, 0, 'C')
        pdf.cell(95, 6, 'INSTITUTO', 0, 1, 'C')
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(95, 6, f"{paciente.get('papell', '')} {paciente.get('sapell', '')} {paciente.get('nom_pac', '')}", 0, 0, 'C')
        pdf.cell(95, 6, 'INSTITUTO DE ENFERMEDADES OCULARES', 0, 1, 'C')
        
        pdf.ln(4)
        pdf.cell(95, 6, '_____________________________', 0, 0, 'C')
        pdf.cell(95, 6, '_____________________________', 0, 1, 'C')
        pdf.cell(95, 6, 'NOMBRE Y FIRMA', 0, 0, 'C')
        pdf.cell(95, 6, 'NOMBRE Y FIRMA', 0, 1, 'C')
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def generate_consent(id_exp, id_atencion):
        """Genera consentimiento de datos personales"""
        data = PDFService._get_patient_data(id_exp, id_atencion)
        paciente = data['paciente']
        
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(True, 30)
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, 'CARTA DE CONSENTIMIENTO PARA TRATAMIENTO DE DATOS PERSONALES', ln=True, align='C')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.set_fill_color(230, 240, 255)
        pdf.cell(0, 8, 'Datos del Paciente:', ln=True, fill=True)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, f"Paciente: {paciente.get('papell', '')} {paciente.get('sapell', '')} {paciente.get('nom_pac', '')}", ln=True)
        pdf.cell(0, 7, f"Teléfono: {paciente.get('tel', 'No especificado')}", ln=True)
        pdf.ln(4)
        
        pdf.set_font('Arial', 'B', 13)
        pdf.set_fill_color(220, 230, 250)
        pdf.cell(0, 8, 'CARTA DE CONSENTIMIENTO', ln=True, align='C', fill=True)
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 9)
        
        texto = """El (la) que suscribe otorga su consentimiento expreso para que el 
INSTITUTO DE ENFERMEDADES OCULARES recabe, almacene, proteja y trate 
sus datos personales, necesarios para brindarle atención médica.

Manifiesto que tengo pleno conocimiento del Aviso de Privacidad Integral 
relativo al tratamiento de mis datos personales, así como de los 
mecanismos para ejercer mis derechos ARCO. Asimismo, autorizo que la 
información médica generada sea resguardada en mi Expediente Clínico 
durante el tiempo que la ley establece."""
        
        pdf.multi_cell(0, 6, texto, align='J')
        
        pdf.ln(10)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Metepec, México a {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
        pdf.ln(8)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(95, 6, 'PACIENTE', 0, 0, 'C')
        pdf.cell(95, 6, 'INSTITUTO', 0, 1, 'C')
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(95, 6, f"{paciente.get('papell', '')} {paciente.get('sapell', '')} {paciente.get('nom_pac', '')}", 0, 0, 'C')
        pdf.cell(95, 6, 'INSTITUTO DE ENFERMEDADES OCULARES', 0, 1, 'C')
        
        pdf.ln(4)
        pdf.cell(95, 6, '_____________________________', 0, 0, 'C')
        pdf.cell(95, 6, '_____________________________', 0, 1, 'C')
        pdf.cell(95, 6, 'NOMBRE Y FIRMA', 0, 0, 'C')
        pdf.cell(95, 6, 'NOMBRE Y FIRMA', 0, 1, 'C')
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name

    @staticmethod
    def generate_identification_sheet(id_exp, id_atencion):
        """Genera la ficha de identificación con el formato del proyecto Mongo."""
        data = PDFService._get_patient_data(id_exp, id_atencion)
        atencion = data['atencion']
        paciente = data['paciente']
        medico = data['medico']

        pdf = FPDF('L', 'mm', (210, 135))
        pdf.set_margins(15, 12, 15)
        pdf.set_auto_page_break(True, 15)
        pdf.add_page()

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'TARJETA DE IDENTIFICACIÓN', ln=True, align='C')

        fecha = atencion.get('fecha_ing')
        if fecha:
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha.split('T')[0], '%Y-%m-%d')
                except (TypeError, ValueError):
                    fecha = datetime.now()
            fecha_str = fecha.strftime('%d/%m/%Y %H:%M')
        else:
            fecha_str = ''

        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 5, f'Fecha: {fecha_str}', ln=True, align='R')
        pdf.ln(2)

        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 6, 'Datos del Paciente', ln=True)
        pdf.set_font('Arial', '', 8)

        nombre = (
            f"{paciente.get('papell', '')} "
            f"{paciente.get('sapell', '')} "
            f"{paciente.get('nom_pac', '')}"
        ).strip()

        pdf.cell(12, 5, 'Paciente:', 0, 0)
        pdf.cell(60, 5, f'{id_exp} - {nombre}', 0, 0)
        pdf.cell(18, 5, 'Nacimiento:', 0, 0)

        fecnac = paciente.get('fecnac')
        if isinstance(fecnac, str):
            try:
                fecnac = datetime.strptime(fecnac.split('T')[0], '%Y-%m-%d')
            except (TypeError, ValueError):
                fecnac = None
        nacimiento = fecnac.strftime('%d/%m/%Y') if fecnac else 'No especificado'
        pdf.cell(40, 5, nacimiento, 0, 1)

        pdf.cell(28, 5, 'CURP:', 0, 0)
        pdf.cell(40, 5, str(paciente.get('curp') or 'No especificado'), 0, 0)
        pdf.cell(18, 5, 'Tel:', 0, 0)
        pdf.cell(0, 5, str(paciente.get('tel') or 'No especificado'), 0, 1)

        medico_nombre = (
            f"{medico.get('papell', '')} "
            f"{medico.get('sapell', '')} "
            f"{medico.get('nombre', medico.get('username', ''))}"
        ).strip() or 'No especificado'

        pdf.cell(15, 5, 'Ingreso:', 0, 0)
        pdf.cell(45, 5, fecha_str, 0, 0)
        pdf.cell(15, 5, 'Médico:', 0, 0)
        pdf.cell(0, 5, medico_nombre, 0, 1)

        pdf.cell(25, 5, 'Servicio:', 0, 0)
        pdf.cell(40, 5, str(atencion.get('area') or 'No especificado'), 0, 1)

        pdf.cell(12, 5, 'DX:', 0, 0)
        pdf.multi_cell(0, 5, str(atencion.get('motivo') or 'No especificado'))

        pdf.cell(18, 5, 'Alergias:', 0, 0)
        pdf.multi_cell(0, 5, str(atencion.get('alergias') or 'No especificado'))

        pdf.ln(2)
        pdf.cell(
            0,
            5,
            'Riesgo de Caídas: _______________    Riesgo de UPP: _______________',
            0,
            1,
        )

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()

        return temp_file.name
    
    @staticmethod
    def generate_vital_signs_pdf(id_signos):
        """Genera PDF de signos vitales"""
        db = get_collection('signos_vitales').database
        
        pipeline = [
            {"$match": {"id_signos": id_signos}},
            {"$lookup": {
                "from": "atencion",
                "localField": "id_atencion",
                "foreignField": "id_atencion",
                "as": "atencion"
            }},
            {"$unwind": "$atencion"},
            {"$lookup": {
                "from": "pacientes",
                "localField": "atencion.Id_exp",
                "foreignField": "Id_exp",
                "as": "paciente"
            }},
            {"$unwind": "$paciente"}
        ]
        
        datos = list(db['signos_vitales'].aggregate(pipeline))
        if not datos:
            return None
        
        datos = datos[0]
        
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'SIGNOS VITALES', ln=True, align='C')
        
        pdf.ln(5)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, f"Paciente: {datos['paciente']['papell']} {datos['paciente']['sapell']} {datos['paciente']['nom_pac']}", ln=True)
        
        fecha = datos['fecha_registro'].strftime('%d/%m/%Y %H:%M')
        pdf.cell(0, 7, f"Fecha: {fecha}", ln=True)
        
        pdf.ln(4)
        pdf.set_font('Arial', 'B', 10)
        
        signos = [
            ('TA', datos.get('ta', '')),
            ('FC', datos.get('fc', '')),
            ('FR', datos.get('fr', '')),
            ('Temperatura', datos.get('temp', '')),
            ('SpO2', datos.get('spo2', '')),
            ('Peso', datos.get('peso', '')),
            ('Talla', datos.get('talla', ''))
        ]
        
        for label, value in signos:
            pdf.cell(60, 7, label, border=1)
            pdf.cell(0, 7, str(value), border=1, ln=True)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def generate_medical_note_pdf(id_nota):
        """Genera PDF de nota médica"""
        db = get_collection('notas_medicas').database
        
        pipeline = [
            {"$match": {"id_nota": id_nota}},
            {"$lookup": {
                "from": "atencion",
                "localField": "id_atencion",
                "foreignField": "id_atencion",
                "as": "atencion"
            }},
            {"$unwind": "$atencion"},
            {"$lookup": {
                "from": "pacientes",
                "localField": "atencion.Id_exp",
                "foreignField": "Id_exp",
                "as": "paciente"
            }},
            {"$unwind": "$paciente"}
        ]
        
        datos = list(db['notas_medicas'].aggregate(pipeline))
        if not datos:
            return None
        
        datos = datos[0]
        
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'NOTA MÉDICA (SOAP)', ln=True, align='C')
        
        pdf.ln(5)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, f"Paciente: {datos['paciente']['papell']} {datos['paciente']['sapell']} {datos['paciente']['nom_pac']}", ln=True)
        
        fecha = datos['fecha_registro'].strftime('%d/%m/%Y %H:%M')
        pdf.cell(0, 7, f"Fecha: {fecha}", ln=True)
        
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Subjetivo:', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 7, datos.get('subjetivo') or 'No especificado')
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Objetivo:', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 7, datos.get('objetivo') or 'No especificado')
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Análisis:', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 7, datos.get('analisis') or 'No especificado')
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Plan:', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 7, datos.get('plan') or 'No especificado')
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def generate_diagnosis_pdf(id_diagnostico):
        """Genera PDF de diagnóstico"""
        db = get_collection('diagnosticos').database
        
        pipeline = [
            {"$match": {"id_diagnostico": id_diagnostico}},
            {"$lookup": {
                "from": "atencion",
                "localField": "id_atencion",
                "foreignField": "id_atencion",
                "as": "atencion"
            }},
            {"$unwind": "$atencion"},
            {"$lookup": {
                "from": "pacientes",
                "localField": "atencion.Id_exp",
                "foreignField": "Id_exp",
                "as": "paciente"
            }},
            {"$unwind": "$paciente"}
        ]
        
        datos = list(db['diagnosticos'].aggregate(pipeline))
        if not datos:
            return None
        
        datos = datos[0]
        
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'DIAGNÓSTICO MÉDICO', ln=True, align='C')
        
        pdf.ln(5)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 7, f"Paciente: {datos['paciente']['papell']} {datos['paciente']['sapell']} {datos['paciente']['nom_pac']}", ln=True)
        
        fecha = datos['fecha_registro'].strftime('%d/%m/%Y %H:%M')
        pdf.cell(0, 7, f"Fecha: {fecha}", ln=True)
        
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Diagnóstico principal:', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 7, datos.get('diagnostico_principal') or 'No especificado')
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Diagnósticos secundarios:', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 7, datos.get('diagnosticos_secundarios') or 'No especificado')
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Observaciones:', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 7, datos.get('observaciones') or 'No especificado')
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def generate_prescription_pdf(id_receta):
        """Genera PDF de receta médica"""
        db = get_collection('recetas').database
        
        pipeline = [
            {"$match": {"id_receta": id_receta}},
            {"$lookup": {
                "from": "atencion",
                "localField": "id_atencion",
                "foreignField": "id_atencion",
                "as": "atencion"
            }},
            {"$unwind": "$atencion"},
            {"$lookup": {
                "from": "pacientes",
                "localField": "atencion.Id_exp",
                "foreignField": "Id_exp",
                "as": "paciente"
            }},
            {"$unwind": "$paciente"}
        ]
        
        datos = list(db['recetas'].aggregate(pipeline))
        if not datos:
            return None
        
        datos = datos[0]
        
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'RECETA MÉDICA', ln=True, align='C')
        
        pdf.ln(10)
        pdf.set_font('Arial', '', 11)
        
        pdf.cell(0, 7, f"Paciente: {datos['paciente']['papell']} {datos['paciente']['sapell']} {datos['paciente']['nom_pac']}", ln=True)
        pdf.cell(0, 7, f"Fecha: {datos['fecha_registro'].strftime('%d/%m/%Y %H:%M')}", ln=True)
        
        pdf.ln(10)
        pdf.cell(0, 0, '', 'T', ln=True)
        pdf.ln(5)
        
        for i, med in enumerate(datos.get('medicamentos', []), 1):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, f"{i}. {med.get('medicamento', '')}", ln=True)
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f"   Dosis: {med.get('dosis', '')}", ln=True)
            pdf.cell(0, 6, f"   Frecuencia: {med.get('frecuencia', '')}", ln=True)
            pdf.cell(0, 6, f"   Duración: {med.get('duracion', '')}", ln=True)
            
            if med.get('indicaciones'):
                pdf.multi_cell(0, 6, f"   Indicaciones: {med.get('indicaciones', '')}")
            
            pdf.ln(5)
        
        pdf.ln(20)
        pdf.cell(0, 7, "__________________________________", ln=True, align='R')
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, "Firma del Médico", ln=True, align='R')
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def generate_lab_pdf(id_examen):
        """Genera PDF de resultados de laboratorio"""
        study = StudyService.get_study_details(id_examen)
        
        if not study or not study.get('detalles'):
            return None
        
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'RESULTADOS DE LABORATORIO', ln=True, align='C')
        
        pdf.ln(5)
        pdf.set_font('Arial', '', 11)
        
        paciente = study.get('paciente', {})
        pdf.cell(0, 7, f"Paciente: {paciente.get('nombre', '')}", ln=True)
        pdf.cell(0, 7, f"Fecha de solicitud: {study.get('fecha', '')}", ln=True)
        
        if study.get('observaciones'):
            pdf.ln(3)
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 7, 'Observaciones:', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, study['observaciones'])
        
        pdf.ln(5)
        pdf.cell(0, 0, '', 'T', ln=True)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Exámenes realizados:', ln=True)
        pdf.ln(3)
        
        pdf.set_font('Arial', '', 10)
        for i, det in enumerate(study['detalles'], 1):
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, f"{i}. {det.get('nombre', '')}", ln=True)
            pdf.set_font('Arial', '', 10)
            
            if det.get('resultado'):
                pdf.multi_cell(0, 5, f"   Resultado: {det['resultado']}")
            
            if det.get('observaciones'):
                pdf.multi_cell(0, 5, f"   Observaciones: {det['observaciones']}")
            
            pdf.ln(3)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def generate_imaging_pdf(id_examen):
        """Genera PDF de resultados de gabinete"""
        study = StudyService.get_study_details(id_examen)
        
        if not study or not study.get('detalles'):
            return None
        
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(True, 20)
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'RESULTADOS DE GABINETE', ln=True, align='C')
        
        pdf.ln(5)
        pdf.set_font('Arial', '', 11)
        
        paciente = study.get('paciente', {})
        pdf.cell(0, 7, f"Paciente: {paciente.get('nombre', '')}", ln=True)
        pdf.cell(0, 7, f"Fecha de solicitud: {study.get('fecha', '')}", ln=True)
        
        if study.get('observaciones'):
            pdf.ln(3)
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 7, 'Observaciones:', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, study['observaciones'])
        
        pdf.ln(5)
        pdf.cell(0, 0, '', 'T', ln=True)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Estudios realizados:', ln=True)
        pdf.ln(3)
        
        pdf.set_font('Arial', '', 10)
        for i, det in enumerate(study['detalles'], 1):
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, f"{i}. {det.get('nombre', '')}", ln=True)
            pdf.set_font('Arial', '', 10)
            
            if det.get('archivo_resultado'):
                pdf.cell(0, 5, f"   Archivo: Disponible", ln=True)
            
            if det.get('observaciones'):
                pdf.multi_cell(0, 5, f"   Observaciones: {det['observaciones']}")
            
            pdf.ln(3)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
