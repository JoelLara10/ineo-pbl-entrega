from utils.database import get_collection, serialize_doc
from datetime import date, datetime, timedelta
from decimal import Decimal
import pandas as pd
from fpdf import FPDF
import tempfile
import os

class ReportService:
    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return None
            try:
                parsed = datetime.fromisoformat(raw.replace('Z', '+00:00'))
                return parsed.replace(tzinfo=None)
            except ValueError:
                pass

            candidates = [raw]
            if 'T' in raw:
                candidates.append(raw.split('T')[0].strip())
            if ' ' in raw:
                candidates.append(raw.split(' ')[0].strip())

            for candidate in dict.fromkeys(candidates):
                for fmt in (
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%d/%m/%Y %H:%M:%S',
                    '%d/%m/%Y %H:%M',
                    '%Y-%m-%d',
                    '%d/%m/%Y',
                ):
                    try:
                        return datetime.strptime(candidate, fmt)
                    except ValueError:
                        continue
        return None

    @staticmethod
    def get_census(area=None):
        """Obtiene censo de pacientes"""
        db = get_collection('atencion').database
        
        query = {'status': 'ABIERTA'}
        if area:
            query['area'] = area
        
        pipeline = [
            {'$match': query},
            {'$lookup': {
                'from': 'pacientes',
                'localField': 'Id_exp',
                'foreignField': 'Id_exp',
                'as': 'paciente'
            }},
            {'$unwind': '$paciente'},
            {'$lookup': {
                'from': 'camas',
                'localField': 'id_cama',
                'foreignField': 'id_cama',
                'as': 'cama'
            }},
            {'$unwind': {'path': '$cama', 'preserveNullAndEmptyArrays': True}},
            {'$lookup': {
                'from': 'atencion_medicos',
                'localField': 'id_atencion',
                'foreignField': 'id_atencion',
                'as': 'medicos'
            }},
            {'$lookup': {
                'from': 'users',
                'localField': 'medicos.id_medico',
                'foreignField': 'id',
                'as': 'doctores'
            }},
            {'$project': {
                'id_atencion': 1,
                'area': 1,
                'fecha_ing': 1,
                'motivo': 1,
                'num_cama': '$cama.numero',
                'Id_exp': '$paciente.Id_exp',
                'paciente_nombre': {
                    '$concat': ['$paciente.papell', ' ', '$paciente.sapell', ' ', '$paciente.nom_pac']
                },
                'fecnac': '$paciente.fecnac',
                'medico': {'$arrayElemAt': ['$doctores.username', 0]}
            }}
        ]
        
        patients = list(db['atencion'].aggregate(pipeline))
        
        # Calcular edad
        for p in patients:
            birth_date = ReportService._parse_date(p.get('fecnac'))
            if birth_date:
                edad = datetime.now().year - birth_date.year
                if (datetime.now().month, datetime.now().day) < (birth_date.month, birth_date.day):
                    edad -= 1
                p['edad'] = edad
            else:
                p['edad'] = 0
        
        return [serialize_doc(p) for p in patients]
    
    @staticmethod
    def export_census_pdf(area=None):
        """Exporta censo a PDF"""
        census = ReportService.get_census(area)
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'CENSO DE PACIENTES', 0, 1, 'C')
                self.set_font('Arial', '', 9)
                self.cell(0, 6, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'R')
                self.ln(5)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        
        pdf = PDF('L', 'mm', 'Legal')
        pdf.add_page()
        
        # Encabezados de tabla
        pdf.set_font('Arial', 'B', 8)
        headers = ['Cama', 'Paciente', 'Edad', 'Ingreso', 'Área', 'Médico', 'Motivo']
        widths = [20, 80, 15, 25, 25, 40, 100]
        
        for header, width in zip(headers, widths):
            pdf.cell(width, 8, header, 1)
        pdf.ln()
        
        # Datos
        pdf.set_font('Arial', '', 8)
        for p in census:
            pdf.cell(20, 7, str(p.get('num_cama', '')), 1)
            pdf.cell(80, 7, p.get('paciente_nombre', '')[:35], 1)
            pdf.cell(15, 7, str(p.get('edad', '')), 1)
            
            fecha_ing = p.get('fecha_ing')
            if fecha_ing:
                fecha_str = fecha_ing.strftime('%d/%m/%Y') if hasattr(fecha_ing, 'strftime') else str(fecha_ing)[:10]
            else:
                fecha_str = ''
            pdf.cell(25, 7, fecha_str, 1)
            
            pdf.cell(25, 7, p.get('area', ''), 1)
            pdf.cell(40, 7, p.get('medico', '')[:20], 1)
            pdf.cell(100, 7, p.get('motivo', '')[:50], 1)
            pdf.ln()
        
        # Guardar temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def export_census_excel(area=None):
        """Exporta censo a Excel"""
        census = ReportService.get_census(area)
        
        # Preparar datos para DataFrame
        data = []
        for p in census:
            data.append({
                'Cama': p.get('num_cama', ''),
                'Paciente': p.get('paciente_nombre', ''),
                'Edad': p.get('edad', ''),
                'Expediente': p.get('Id_exp', ''),
                'Atención': p.get('id_atencion', ''),
                'Área': p.get('area', ''),
                'Fecha Ingreso': p.get('fecha_ing'),
                'Médico': p.get('medico', ''),
                'Motivo': p.get('motivo', '')
            })
        
        df = pd.DataFrame(data)
        
        # Guardar temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df.to_excel(temp_file.name, index=False)
        temp_file.close()
        
        return temp_file.name
    
    @staticmethod
    def get_cash_drawer_report(start_date, end_date):
        """Genera reporte de corte de caja"""
        db = get_collection('depositos_pserv').database
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Obtener pagos
        pipeline = [
            {'$match': {
                'fecha': {'$gte': start, '$lt': end}
            }},
            {'$lookup': {
                'from': 'atencion',
                'localField': 'id_atencion',
                'foreignField': 'id_atencion',
                'as': 'atencion'
            }},
            {'$unwind': {'path': '$atencion', 'preserveNullAndEmptyArrays': True}},
            {'$lookup': {
                'from': 'pacientes',
                'localField': 'atencion.Id_exp',
                'foreignField': 'Id_exp',
                'as': 'paciente'
            }},
            {'$unwind': {'path': '$paciente', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'fecha': 1,
                'paciente': {'$concat': ['$paciente.papell', ' ', '$paciente.nom_pac']},
                'monto': '$deposito',
                'tipo_pago': 1,
                'id_atencion': 1
            }},
            {'$sort': {'fecha': 1}}
        ]
        
        payments = list(db['depositos_pserv'].aggregate(pipeline))
        
        # Calcular totales por método de pago
        totals_by_method = {}
        for p in payments:
            method = p.get('tipo_pago', 'OTRO')
            totals_by_method[method] = totals_by_method.get(method, 0) + float(p['monto'])
        
        total_general = sum(totals_by_method.values())
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'payments': [serialize_doc(p) for p in payments],
            'totals_by_method': totals_by_method,
            'total_general': total_general,
            'payment_count': len(payments)
        }
    
    @staticmethod
    def export_cash_drawer_pdf(start_date, end_date):
        """Exporta corte de caja a PDF"""
        report = ReportService.get_cash_drawer_report(start_date, end_date)
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 14)
                self.cell(0, 10, 'CORTE DE CAJA', 0, 1, 'C')
                self.set_font('Arial', '', 10)
                self.cell(0, 6, f'Periodo: {start_date} al {end_date}', 0, 1, 'C')
                self.cell(0, 6, f'Fecha de generación: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
                self.ln(5)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        
        pdf = PDF()
        pdf.add_page()
        
        # Tabla de pagos
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(35, 8, 'Fecha', 1)
        pdf.cell(80, 8, 'Paciente', 1)
        pdf.cell(35, 8, 'Monto', 1, align='C')
        pdf.cell(40, 8, 'Método de Pago', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 9)
        total = 0
        for payment in report['payments']:
            fecha = payment['fecha'].strftime('%d/%m/%Y %H:%M') if hasattr(payment['fecha'], 'strftime') else str(payment['fecha'])[:16]
            pdf.cell(35, 7, fecha, 1)
            pdf.cell(80, 7, payment.get('paciente', '')[:35], 1)
            pdf.cell(35, 7, f"${payment['monto']:.2f}", 1, align='R')
            pdf.cell(40, 7, payment.get('tipo_pago', ''), 1)
            pdf.ln()
            total += payment['monto']
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(150, 8, 'TOTAL GENERAL:', 0)
        pdf.cell(40, 8, f"${total:.2f}", 1, align='R')
        
        # Resumen por método de pago
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, 'RESUMEN POR MÉTODO DE PAGO', 0, 1)
        
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(80, 8, 'Método', 1)
        pdf.cell(40, 8, 'Total', 1, align='C')
        pdf.ln()
        
        pdf.set_font('Arial', '', 9)
        for method, amount in report['totals_by_method'].items():
            pdf.cell(80, 7, method, 1)
            pdf.cell(40, 7, f"${amount:.2f}", 1, align='R')
            pdf.ln()
        
        # Guardar
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return temp_file.name
