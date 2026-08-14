from utils.database import get_collection, serialize_doc
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import tempfile

class AnalyticsService:
    @staticmethod
    def get_dashboard_stats():
        """Obtiene estadísticas generales del dashboard"""
        db = get_collection('atencion').database
        
        # Pacientes activos por área
        active_by_area = list(db['atencion'].aggregate([
            {'$match': {'status': 'ABIERTA'}},
            {'$group': {
                '_id': '$area',
                'count': {'$sum': 1}
            }}
        ]))
        
        # Total de pacientes atendidos hoy
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_attentions = db['atencion'].count_documents({
            'fecha_ing': {'$gte': today}
        })
        
        # Total de ingresos del día
        today_income = list(db['cuenta_paciente'].aggregate([
            {'$match': {'fecha': {'$gte': today}}},
            {'$group': {
                '_id': None,
                'total': {'$sum': '$subtotal'}
            }}
        ]))
        
        # Ocupación de camas
        total_beds = db['camas'].count_documents({})
        occupied_beds = db['camas'].count_documents({'ocupada': 1})
        
        # Exámenes pendientes
        pending_exams = db['examenes_det'].count_documents({'estado': 'PENDIENTE'})
        
        return {
            'active_patients': {
                'total': sum(item['count'] for item in active_by_area),
                'by_area': {item['_id']: item['count'] for item in active_by_area}
            },
            'today_attentions': today_attentions,
            'today_income': float(today_income[0]['total']) if today_income else 0,
            'bed_occupancy': {
                'total': total_beds,
                'occupied': occupied_beds,
                'available': total_beds - occupied_beds,
                'percentage': (occupied_beds / total_beds * 100) if total_beds > 0 else 0
            },
            'pending_exams': pending_exams
        }
    
    @staticmethod
    def get_revenue_report(start_date, end_date):
        """Genera reporte de ingresos por período"""
        db = get_collection('cuenta_paciente').database
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
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
            {'$unwind': '$atencion'},
            {'$group': {
                '_id': {
                    'area': '$atencion.area',
                    'date': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$fecha'}}
                },
                'total': {'$sum': '$subtotal'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.date': 1}}
        ]
        
        results = list(db['cuenta_paciente'].aggregate(pipeline))
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'data': [{
                'date': item['_id']['date'],
                'area': item['_id']['area'],
                'total': float(item['total']),
                'transactions': item['count']
            } for item in results],
            'total_income': sum(float(item['total']) for item in results)
        }
    
    @staticmethod
    def get_top_services(limit=10):
        """Obtiene los servicios más solicitados"""
        db = get_collection('cuenta_paciente').database
        
        pipeline = [
            {'$group': {
                '_id': '$descripcion',
                'count': {'$sum': 1},
                'total_income': {'$sum': '$subtotal'}
            }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        
        results = list(db['cuenta_paciente'].aggregate(pipeline))
        
        return [{
            'service': item['_id'],
            'times_requested': item['count'],
            'total_income': float(item['total_income'])
        } for item in results]
    
    @staticmethod
    def get_doctor_performance(start_date=None, end_date=None):
        """Evalúa rendimiento de médicos"""
        db = get_collection('atencion_medicos').database
        
        match_stage = {}
        if start_date and end_date:
            match_stage = {
                'fecha_ing': {
                    '$gte': datetime.strptime(start_date, '%Y-%m-%d'),
                    '$lte': datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                }
            }
        
        pipeline = [
            {'$lookup': {
                'from': 'atencion',
                'localField': 'id_atencion',
                'foreignField': 'id_atencion',
                'as': 'atencion'
            }},
            {'$unwind': '$atencion'},
            {'$match': match_stage} if match_stage else {'$match': {}},
            {'$lookup': {
                'from': 'users',
                'localField': 'id_medico',
                'foreignField': 'id',
                'as': 'medico'
            }},
            {'$unwind': '$medico'},
            {'$group': {
                '_id': '$id_medico',
                'doctor_name': {'$first': {'$concat': ['$medico.nombre', ' ', '$medico.papell']}},
                'patients_attended': {'$sum': 1},
                'total_income': {'$sum': {'$ifNull': ['$atencion.cuenta_total', 0]}}
            }},
            {'$sort': {'patients_attended': -1}}
        ]
        
        results = list(db['atencion_medicos'].aggregate(pipeline))
        
        return [{
            'doctor_id': item['_id'],
            'name': item['doctor_name'],
            'patients_attended': item['patients_attended'],
            'total_income': float(item['total_income'])
        } for item in results]
        

    @staticmethod
    def get_patient_flow(period='day'):
        """Obtiene flujo de pacientes"""
        db = get_collection('atencion').database
        
        now = datetime.now()
        
        if period == 'day':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            group_format = '%Y-%m-%d %H:00'
        elif period == 'week':
            start_date = now - timedelta(days=7)
            group_format = '%Y-%m-%d'
        else:  # month
            start_date = now.replace(day=1, hour=0, minute=0, second=0)
            group_format = '%Y-%m-%d'
        
        pipeline = [
            {'$match': {'fecha_ing': {'$gte': start_date}}},
            {'$group': {
                '_id': {'$dateToString': {'format': group_format, 'date': '$fecha_ing'}},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        flow = list(db['atencion'].aggregate(pipeline))
        
        return {
            'period': period,
            'data': [{'date': item['_id'], 'patients': item['count']} for item in flow],
            'total': sum(item['count'] for item in flow)
        }
    
    @staticmethod
    def get_occupancy_trend(days=7):
        """Obtiene tendencia de ocupación"""
        db = get_collection('camas').database
        
        trend = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            
            # Contar camas ocupadas en esa fecha (simplificado)
            total_beds = db['camas'].count_documents({})
            occupied_beds = db['camas'].count_documents({'ocupada': 1})
            
            trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'total_beds': total_beds,
                'occupied_beds': occupied_beds,
                'occupancy_rate': (occupied_beds / total_beds * 100) if total_beds > 0 else 0
            })
        
        return trend[::-1]  # Orden ascendente
    
    @staticmethod
    def get_financial_summary(year):
        """Obtiene resumen financiero por meses"""
        db = get_collection('depositos_pserv').database
        
        monthly_income = []
        
        for month in range(1, 13):
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            total = db['depositos_pserv'].aggregate([
                {'$match': {'fecha': {'$gte': start_date, '$lt': end_date}}},
                {'$group': {'_id': None, 'total': {'$sum': '$deposito'}}}
            ])
            
            total_result = list(total)
            amount = float(total_result[0]['total']) if total_result else 0
            
            monthly_income.append({
                'month': month,
                'month_name': start_date.strftime('%B'),
                'total': amount
            })
        
        # Totales del año
        total_annual = sum(m['total'] for m in monthly_income)
        
        # Promedio mensual
        monthly_average = total_annual / 12 if monthly_income else 0
        
        return {
            'year': year,
            'monthly_income': monthly_income,
            'total_annual': total_annual,
            'monthly_average': monthly_average
        }
    
    @staticmethod
    def export_revenue_excel(start_date, end_date):
        """Exporta reporte de ingresos a Excel"""
        report = AnalyticsService.get_revenue_report(start_date, end_date)
        
        import pandas as pd
        
        # DataFrame con datos diarios
        df = pd.DataFrame(report['data'])
        
        # Crear archivo Excel
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        
        with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ingresos Diarios', index=False)
            
            # Resumen
            summary_data = {
                'Período': [f"{start_date} al {end_date}"],
                'Total Ingresos': [report['total_income']],
                'Transacciones': [sum(d['transactions'] for d in report['data'])]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def get_clinical_analytics():
        """Obtiene análisis clínico"""
        db = get_collection('diagnosticos').database
        
        # Diagnósticos más frecuentes
        top_diagnosis = list(db['diagnosticos'].aggregate([
            {'$group': {
                '_id': '$diagnostico_principal',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]))
        
        # Pacientes por rango de edad
        pipeline_edad = [
            {'$lookup': {
                'from': 'pacientes',
                'localField': 'Id_exp',
                'foreignField': 'Id_exp',
                'as': 'paciente'
            }},
            {'$unwind': '$paciente'},
            {'$project': {
                'edad': {
                    '$let': {
                        'vars': {
                            'birthDate': '$paciente.fecnac',
                            'today': datetime.now()
                        },
                        'in': {
                            '$subtract': [
                                {'$year': '$$today'},
                                {'$year': '$$birthDate'},
                                {'$cond': [
                                    {'$lt': [
                                        {'$concat': [{'$toString': {'$month': '$$today'}}, '-', {'$toString': {'$dayOfMonth': '$$today'}}]},
                                        {'$concat': [{'$toString': {'$month': '$$birthDate'}}, '-', {'$toString': {'$dayOfMonth': '$$birthDate'}}]}
                                    ]},
                                    1,
                                    0
                                ]}
                            ]
                        }
                    }
                }
            }},
            {'$bucket': {
                'groupBy': '$edad',
                'boundaries': [0, 18, 30, 45, 60, 80, 200],
                'default': '80+',
                'output': {'count': {'$sum': 1}}
            }}
        ]
        
        age_distribution = list(db['atencion'].aggregate(pipeline_edad))
        
        # Tiempo promedio de estancia
        estancia = db['expedientes'].aggregate([
            {'$lookup': {
                'from': 'atencion',
                'localField': 'id_atencion',
                'foreignField': 'id_atencion',
                'as': 'atencion'
            }},
            {'$unwind': '$atencion'},
            {'$project': {
                'dias': {
                    '$divide': [
                        {'$subtract': ['$fecha_alta', '$atencion.fecha_ing']},
                        1000 * 60 * 60 * 24
                    ]
                }
            }},
            {'$group': {
                '_id': None,
                'promedio': {'$avg': '$dias'}
            }}
        ])
        
        estancia_result = list(estancia)
        avg_stay = estancia_result[0]['promedio'] if estancia_result else 0
        
        return {
            'top_diagnosis': [{'diagnosis': d['_id'], 'count': d['count']} for d in top_diagnosis],
            'age_distribution': [{'range': str(d['_id']), 'count': d['count']} for d in age_distribution],
            'average_stay_days': round(avg_stay, 2)
        }