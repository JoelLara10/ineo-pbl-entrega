from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import token_required, role_required
from services.billing_service import BillingService
from utils.database import serialize_doc
from datetime import datetime

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

@billing_bp.route('/patient/<int:id_atencion>', methods=['GET'])
@token_required
def get_patient_bill(id_atencion):
    """Obtiene la cuenta de un paciente"""
    bill = BillingService.get_patient_bill(id_atencion)
    
    if not bill:
        return jsonify({'error': 'Cuenta no encontrada'}), 404
    
    return jsonify(bill), 200

@billing_bp.route('/patient/<int:id_atencion>/items', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def add_billing_item(id_atencion):
    """Agrega un item a la cuenta del paciente"""
    data = request.get_json()
    
    required_fields = ['descripcion', 'cantidad', 'precio']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    result = BillingService.add_billing_item(id_atencion, data)
    
    if not result:
        return jsonify({'error': 'Error al agregar item'}), 500
    
    return jsonify(result), 201

@billing_bp.route('/patient/<int:id_atencion>/items/<int:item_id>', methods=['DELETE'])
@token_required
@role_required('admin', 'administrativo')
def remove_billing_item(id_atencion, item_id):
    """Elimina un item de la cuenta"""
    result = BillingService.remove_billing_item(id_atencion, item_id)
    
    if not result:
        return jsonify({'error': 'Item no encontrado'}), 404
    
    return jsonify({'message': 'Item eliminado correctamente'}), 200

@billing_bp.route('/payment/<int:id_atencion>', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def register_payment(id_atencion):
    """Registra un pago"""
    data = request.get_json()
    
    if not data.get('amount') or not data.get('payment_method'):
        return jsonify({'error': 'Monto y método de pago son requeridos'}), 400
    
    result = BillingService.register_payment(id_atencion, data, g.user['user_id'])
    
    if not result:
        return jsonify({'error': 'Error al registrar pago'}), 500
    
    return jsonify(result), 201

@billing_bp.route('/payments/<int:id_atencion>', methods=['GET'])
@token_required
def get_payments(id_atencion):
    """Obtiene el historial de pagos"""
    payments = BillingService.get_payments(id_atencion)
    return jsonify(payments), 200

@billing_bp.route('/reports/daily', methods=['GET'])
@token_required
@role_required('admin')
def get_daily_report():
    """Reporte diario de ingresos"""
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    report = BillingService.get_daily_report(date)
    return jsonify(report), 200

@billing_bp.route('/reports/monthly', methods=['GET'])
@token_required
@role_required('admin')
def get_monthly_report():
    """Reporte mensual de ingresos"""
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    
    report = BillingService.get_monthly_report(year, month)
    return jsonify(report), 200

@billing_bp.route('/invoice/<int:id_atencion>/pdf', methods=['GET'])
@token_required
def generate_invoice_pdf(id_atencion):
    """Genera factura en PDF"""
    from fpdf import FPDF
    from io import BytesIO
    
    bill = BillingService.get_patient_bill(id_atencion)
    
    if not bill:
        return jsonify({'error': 'Cuenta no encontrada'}), 404
    
    # Generar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FACTURA", ln=1, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Atención: {bill['id_atencion']}", ln=1)
    pdf.cell(0, 6, f"Paciente: {bill['paciente']}", ln=1)
    pdf.cell(0, 6, f"Fecha: {bill['fecha_ing']}", ln=1)
    pdf.ln(5)
    
    # Tabla de items
    pdf.set_font("Arial", "B", 9)
    pdf.cell(80, 7, "Descripción", 1)
    pdf.cell(30, 7, "Cantidad", 1, align="C")
    pdf.cell(40, 7, "Precio", 1, align="R")
    pdf.cell(40, 7, "Subtotal", 1, align="R")
    pdf.ln()
    
    pdf.set_font("Arial", "", 9)
    for item in bill['items']:
        pdf.cell(80, 7, item['descripcion'][:50], 1)
        pdf.cell(30, 7, str(item['cantidad']), 1, align="C")
        pdf.cell(40, 7, f"${item['precio']:.2f}", 1, align="R")
        pdf.cell(40, 7, f"${item['subtotal']:.2f}", 1, align="R")
        pdf.ln()
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, f"SUBTOTAL: ${bill['subtotal']:.2f}", ln=1, align="R")
    pdf.cell(0, 7, f"IVA (16%): ${bill['iva']:.2f}", ln=1, align="R")
    pdf.cell(0, 7, f"TOTAL: ${bill['total']:.2f}", ln=1, align="R")
    
    # Devolver PDF
    from flask import make_response
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=factura_{id_atencion}.pdf'
    
    return response