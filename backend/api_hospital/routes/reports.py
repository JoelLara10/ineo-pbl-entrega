from flask import Blueprint, request, jsonify, send_file, g
from middleware.auth_middleware import token_required, role_required
from services.report_service import ReportService
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/census', methods=['GET'])
@token_required
def get_census():
    """Obtiene censo de pacientes"""
    area = request.args.get('area')
    
    census = ReportService.get_census(area)
    return jsonify(census), 200

@reports_bp.route('/census/pdf', methods=['GET'])
@token_required
def export_census_pdf():
    """Exporta censo a PDF"""
    area = request.args.get('area')
    
    pdf_file = ReportService.export_census_pdf(area)
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'censo_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

@reports_bp.route('/census/excel', methods=['GET'])
@token_required
def export_census_excel():
    """Exporta censo a Excel"""
    area = request.args.get('area')
    
    excel_file = ReportService.export_census_excel(area)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'censo_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@reports_bp.route('/cash-drawer', methods=['POST'])
@token_required
@role_required('admin')
def cash_drawer_report():
    """Genera reporte de corte de caja"""
    data = request.get_json()
    
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Fechas de inicio y fin son requeridas'}), 400
    
    report = ReportService.get_cash_drawer_report(start_date, end_date)
    return jsonify(report), 200

@reports_bp.route('/cash-drawer/pdf', methods=['POST'])
@token_required
@role_required('admin')
def export_cash_drawer_pdf():
    """Exporta corte de caja a PDF"""
    data = request.get_json()
    
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Fechas de inicio y fin son requeridas'}), 400
    
    pdf_file = ReportService.export_cash_drawer_pdf(start_date, end_date)
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'corte_caja_{start_date}_a_{end_date}.pdf'
    )