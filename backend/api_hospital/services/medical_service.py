from utils.database import get_collection, serialize_doc, get_next_sequence
from datetime import datetime
from bson import ObjectId

class MedicalService:
    @staticmethod
    def get_active_appointments(area=None):
        """Obtiene atenciones activas"""
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
            {'$project': {
                'id_atencion': 1,
                'Id_exp': 1,
                'area': 1,
                'fecha_ing': 1,
                'motivo': 1,
                'status': 1,
                'paciente': {
                    'Id_exp': '$paciente.Id_exp',
                    'nombre_completo': {
                        '$concat': ['$paciente.papell', ' ', '$paciente.sapell', ' ', '$paciente.nom_pac']
                    },
                    'fecnac': '$paciente.fecnac',
                    'tel': '$paciente.tel'
                },
                'cama': {
                    'numero': '$cama.numero',
                    'area': '$cama.area'
                }
            }}
        ]
        
        appointments = list(db['atencion'].aggregate(pipeline))
        return [serialize_doc(a) for a in appointments]
    
    @staticmethod
    def get_appointment_details(id_atencion):
        """Obtiene detalles completos de una atención"""
        db = get_collection('atencion').database
        
        pipeline = [
            {'$match': {'id_atencion': id_atencion}},
            {'$lookup': {
                'from': 'pacientes',
                'localField': 'Id_exp',
                'foreignField': 'Id_exp',
                'as': 'paciente'
            }},
            {'$unwind': '$paciente'},
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
            }}
        ]
        
        result = list(db['atencion'].aggregate(pipeline))
        if not result:
            return None
        
        appointment = serialize_doc(result[0])
        
        # Agregar signos vitales
        appointment['vital_signs'] = MedicalService.get_vital_signs(id_atencion)
        
        # Agregar notas médicas
        appointment['medical_notes'] = MedicalService.get_medical_notes(id_atencion)
        
        # Agregar diagnóstico
        appointment['diagnosis'] = MedicalService.get_current_diagnosis(id_atencion)
        
        return appointment
    
    @staticmethod
    def get_patient_appointments(id_exp):
        """Obtiene todas las atenciones de un paciente"""
        db = get_collection('atencion').database
        
        appointments = list(db['atencion'].find(
            {'Id_exp': id_exp},
            {'_id': 0, 'id_atencion': 1, 'area': 1, 'fecha_ing': 1, 'status': 1}
        ).sort('fecha_ing', -1))
        
        return [serialize_doc(a) for a in appointments]
    
    @staticmethod
    def get_active_appointment(id_exp):
        """Obtiene atención activa de un paciente"""
        db = get_collection('atencion').database
        
        appointment = db['atencion'].find_one({
            'Id_exp': id_exp,
            'status': 'ABIERTA'
        })
        
        return serialize_doc(appointment)
    
    @staticmethod
    def add_vital_signs(id_atencion, data):
        """Agrega signos vitales - CON TIPOS CORRECTOS"""
        collection = get_collection('signos_vitales')
        
        sign = {
            'id_signos': get_next_sequence('signos_vitales_id'),
            'id_atencion': id_atencion,
            'ta': data.get('ta', ''),  # String
            'fecha_registro': datetime.now()
        }
        
        # Agregar solo si tienen valor (como números)
        if data.get('fc') is not None:
            sign['fc'] = int(data['fc']) if isinstance(data['fc'], (int, float)) else int(float(data['fc']))
        if data.get('fr') is not None:
            sign['fr'] = int(data['fr']) if isinstance(data['fr'], (int, float)) else int(float(data['fr']))
        if data.get('temp') is not None:
            sign['temp'] = float(data['temp'])
        if data.get('spo2') is not None:
            sign['spo2'] = int(data['spo2']) if isinstance(data['spo2'], (int, float)) else int(float(data['spo2']))
        if data.get('peso') is not None:
            sign['peso'] = float(data['peso'])
        if data.get('talla') is not None:
            sign['talla'] = float(data['talla'])
        
        collection.insert_one(sign)
        return serialize_doc(sign)
    
    @staticmethod
    def get_vital_signs(id_atencion):
        """Obtiene historial de signos vitales"""
        collection = get_collection('signos_vitales')
        
        signs = list(collection.find(
            {'id_atencion': id_atencion}
        ).sort('fecha_registro', -1))
        
        return [serialize_doc(s) for s in signs]
    
    @staticmethod
    def add_medical_note(id_atencion, data):
        """Agrega nota médica"""
        collection = get_collection('notas_medicas')
        
        note = {
            'id_nota': get_next_sequence('notas_medicas_id'),
            'id_atencion': id_atencion,
            'subjetivo': data.get('subjetivo'),
            'objetivo': data.get('objetivo'),
            'analisis': data.get('analisis'),
            'plan': data.get('plan'),
            'id_medico': ObjectId(data['id_medico']),
            'fecha_registro': datetime.now()
        }
        
        collection.insert_one(note)
        return serialize_doc(note)
    
    @staticmethod
    def get_medical_notes(id_atencion):
        """Obtiene notas médicas"""
        collection = get_collection('notas_medicas')
        
        notes = list(collection.find(
            {'id_atencion': id_atencion}
        ).sort('fecha_registro', -1))
        
        return [serialize_doc(n) for n in notes]
    
    @staticmethod
    def add_diagnosis(id_atencion, data):
        """Agrega o actualiza diagnóstico"""
        collection = get_collection('diagnosticos')
        
        diagnosis = {
            'id_atencion': id_atencion,
            'diagnostico_principal': data.get('diagnostico_principal'),
            'diagnosticos_secundarios': data.get('diagnosticos_secundarios'),
            'observaciones': data.get('observaciones'),
            'fecha_registro': datetime.now()
        }
        
        # Verificar si ya existe
        existing = collection.find_one({'id_atencion': id_atencion})
        
        if existing:
            collection.update_one(
                {'id_atencion': id_atencion},
                {'$set': diagnosis}
            )
            return serialize_doc(diagnosis)
        else:
            diagnosis['id_diagnostico'] = get_next_sequence('diagnosticos_id')
            collection.insert_one(diagnosis)
            return serialize_doc(diagnosis)
    
    @staticmethod
    def get_current_diagnosis(id_atencion):
        """Obtiene diagnóstico actual"""
        collection = get_collection('diagnosticos')
        diagnosis = collection.find_one({'id_atencion': id_atencion})
        return serialize_doc(diagnosis) if diagnosis else None
    
    @staticmethod
    def get_diagnosis_history(id_atencion):
        """Obtiene historial de diagnósticos"""
        db = get_collection('diagnosticos').database
        
        # Obtener historial
        history = list(db['diagnosticos_historial'].find(
            {'id_atencion': id_atencion}
        ).sort('fecha_modificacion', -1))
        
        return [serialize_doc(h) for h in history]

    @staticmethod
    def add_prescription(id_atencion, data):
        """Agrega receta médica"""
        collection = get_collection('recetas')
        
        prescription = {
            'id_receta': get_next_sequence('recetas_id'),
            'id_atencion': id_atencion,
            'medicamentos': data.get('medicamentos', []),
            'id_medico': ObjectId(data['id_medico']),
            'fecha_registro': datetime.now()
        }
        
        collection.insert_one(prescription)
        return serialize_doc(prescription)
    
    @staticmethod
    def get_prescriptions(id_atencion):
        """Obtiene recetas médicas"""
        collection = get_collection('recetas')
        
        prescriptions = list(collection.find(
            {'id_atencion': id_atencion}
        ).sort('fecha_registro', -1))
        
        return [serialize_doc(p) for p in prescriptions]
    
    @staticmethod
    def close_appointment(id_atencion, user_id):
        """Cierra una atención (alta médica)"""
        db = get_collection('atencion').database
        
        # Obtener atención
        appointment = db['atencion'].find_one({'id_atencion': id_atencion})
        if not appointment or appointment.get('status') != 'ABIERTA':
            return False
        
        # Calcular total de cuenta
        total = db['cuenta_paciente'].aggregate([
            {'$match': {'id_atencion': id_atencion}},
            {'$group': {'_id': None, 'total': {'$sum': '$subtotal'}}}
        ])
        total_result = list(total)
        total_amount = total_result[0]['total'] if total_result else 0
        
        # Crear expediente
        db['expedientes'].insert_one({
            'id_exp': appointment['Id_exp'],
            'id_atencion': id_atencion,
            'fecha_alta': datetime.now(),
            'usuario_alta': user_id,
            'total_cuenta': total_amount
        })
        
        # Cerrar atención
        db['atencion'].update_one(
            {'id_atencion': id_atencion},
            {'$set': {'status': 'CERRADA'}}
        )
        
        # Liberar cama
        if appointment.get('id_cama'):
            db['camas'].update_one(
                {'id_cama': appointment['id_cama']},
                {'$set': {'ocupada': 0}}
            )
        
        return True