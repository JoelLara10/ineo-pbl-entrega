from flask import Blueprint, request, jsonify, g, send_file
from middleware.auth_middleware import token_required, role_required
from services.analytics_service import AnalyticsService
from datetime import datetime
from utils.database import get_collection, get_db, serialize_doc
import tempfile
import os

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_stats():
    """Obtiene estadísticas del dashboard"""
    try:
        db = get_db()
        
        # Pacientes activos
        active_patients = db['atencion'].count_documents({'status': 'ABIERTA'})
        
        # Pacientes por área
        by_area = list(db['atencion'].aggregate([
            {'$match': {'status': 'ABIERTA'}},
            {'$group': {'_id': '$area', 'count': {'$sum': 1}}}
        ]))
        
        # Ocupación de camas
        total_beds = db['camas'].count_documents({})
        occupied_beds = db['camas'].count_documents({'ocupada': 1})
        
        # Atenciones hoy
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_attentions = db['atencion'].count_documents({'fecha_ing': {'$gte': today_start}})
        
        # Exámenes pendientes
        pending_exams = db['examenes_det'].count_documents({'estado': 'PENDIENTE'})
        
        return jsonify({
            'active_patients': {
                'total': active_patients,
                'by_area': {item['_id']: item['count'] for item in by_area}
            },
            'today_attentions': today_attentions,
            'bed_occupancy': {
                'total': total_beds,
                'occupied': occupied_beds,
                'available': total_beds - occupied_beds,
                'percentage': (occupied_beds / total_beds * 100) if total_beds > 0 else 0
            },
            'pending_exams': pending_exams
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@analytics_bp.route('/revenue', methods=['GET'])
@token_required
@role_required('admin')
def get_revenue_report():
    """Obtiene reporte de ingresos"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Fechas de inicio y fin son requeridas'}), 400
    
    report = AnalyticsService.get_revenue_report(start_date, end_date)
    return jsonify(report), 200

@analytics_bp.route('/top-services', methods=['GET'])
@token_required
def get_top_services():
    """Obtiene los servicios más solicitados"""
    limit = int(request.args.get('limit', 10))
    
    services = AnalyticsService.get_top_services(limit)
    return jsonify(services), 200

@analytics_bp.route('/doctor-performance', methods=['GET'])
@token_required
@role_required('admin')
def get_doctor_performance():
    """Obtiene rendimiento de médicos"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    performance = AnalyticsService.get_doctor_performance(start_date, end_date)
    return jsonify(performance), 200

@analytics_bp.route('/patient-flow', methods=['GET'])
@token_required
def get_patient_flow():
    """Obtiene flujo de pacientes por período"""
    period = request.args.get('period', 'day')  # day, week, month
    
    flow = AnalyticsService.get_patient_flow(period)
    return jsonify(flow), 200

@analytics_bp.route('/occupancy-trend', methods=['GET'])
@token_required
def get_occupancy_trend():
    """Obtiene tendencia de ocupación"""
    days = int(request.args.get('days', 7))
    
    trend = AnalyticsService.get_occupancy_trend(days)
    return jsonify(trend), 200

@analytics_bp.route('/financial-summary', methods=['GET'])
@token_required
@role_required('admin')
def get_financial_summary():
    """Obtiene resumen financiero"""
    year = int(request.args.get('year', datetime.now().year))
    
    summary = AnalyticsService.get_financial_summary(year)
    return jsonify(summary), 200

@analytics_bp.route('/export/revenue-excel', methods=['GET'])
@token_required
@role_required('admin')
def export_revenue_excel():
    """Exporta reporte de ingresos a Excel"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Fechas requeridas'}), 400
    
    excel_file = AnalyticsService.export_revenue_excel(start_date, end_date)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'reporte_ingresos_{start_date}_a_{end_date}.xlsx'
    )

@analytics_bp.route('/clinical', methods=['GET'])
@token_required
@role_required('admin', 'medico')
def get_clinical_analytics():
    """Obtiene análisis clínico"""
    analytics = AnalyticsService.get_clinical_analytics()
    return jsonify(analytics), 200