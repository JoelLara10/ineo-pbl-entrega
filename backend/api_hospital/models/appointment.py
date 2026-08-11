from utils.database import get_collection, serialize_doc, get_next_sequence
from datetime import datetime
from bson import ObjectId

class AppointmentModel:
    @staticmethod
    def create(data):
        """Crea una nueva atención"""
        db = get_collection('atencion').database
        
        # Verificar si el paciente ya tiene atención activa
        existing = db['atencion'].find_one({
            'Id_exp': data['Id_exp'],
            'status': 'ABIERTA'
        })
        
        if existing:
            return None, 'El paciente ya tiene una atención activa'
        
        id_atencion = get_next_sequence('atencion_id_atencion')
        
        appointment = {
            'id_atencion': id_atencion,
            'Id_exp': data['Id_exp'],
            'area': data.get('area'),
            'id_cama': data.get('id_cama'),
            'motivo': data.get('motivo', ''),
            'especialidad': data.get('especialidad', ''),
            'alergias': data.get('alergias', ''),
            'fecha_ing': datetime.now(),
            'status': 'ABIERTA'
        }
        
        db['atencion'].insert_one(appointment)
        
        # Asignar médicos si se proporcionan
        if data.get('medicos'):
            for id_medico in data['medicos']:
                db['atencion_medicos'].insert_one({
                    'id_atencion': id_atencion,
                    'id_medico': int(id_medico)
                })
        
        # Marcar cama como ocupada
        if data.get('id_cama'):
            db['camas'].update_one(
                {'id_cama': data['id_cama']},
                {'$set': {'ocupada': 1}}
            )
        
        return serialize_doc(appointment), None
    
    @staticmethod
    def find_by_id(id_atencion):
        """Busca atención por ID"""
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
                'Id_exp': 1,
                'area': 1,
                'motivo': 1,
                'especialidad': 1,
                'alergias': 1,
                'fecha_ing': 1,
                'status': 1,
                'id_cama': 1,
                'num_cama': '$cama.numero',
                'paciente': {
                    'Id_exp': '$paciente.Id_exp',
                    'nombre': {'$concat': ['$paciente.papell', ' ', '$paciente.sapell', ' ', '$paciente.nom_pac']},
                    'curp': '$paciente.curp',
                    'fecnac': '$paciente.fecnac',
                    'tel': '$paciente.tel'
                },
                'medicos': {
                    '$map': {
                        'input': '$doctores',
                        'as': 'doc',
                        'in': {
                            'id': '$$doc.id',
                            'nombre': {'$concat': ['$$doc.nombre', ' ', '$$doc.papell']},
                            'username': '$$doc.username'
                        }
                    }
                }
            }}
        ]
        
        result = list(db['atencion'].aggregate(pipeline))
        return serialize_doc(result[0]) if result else None
    
    @staticmethod
    def find_by_patient(id_exp, status=None):
        """Busca atenciones de un paciente"""
        db = get_collection('atencion').database
        
        query = {'Id_exp': id_exp}
        if status:
            query['status'] = status
        
        appointments = list(db['atencion'].find(query).sort('fecha_ing', -1))
        return [serialize_doc(a) for a in appointments]
    
    @staticmethod
    def get_active_by_area(area=None):
        """Obtiene atenciones activas por área"""
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
                'area': 1,
                'fecha_ing': 1,
                'motivo': 1,
                'status': 1,
                'num_cama': '$cama.numero',
                'paciente': {
                    'Id_exp': '$paciente.Id_exp',
                    'nombre': {'$concat': ['$paciente.papell', ' ', '$paciente.sapell', ' ', '$paciente.nom_pac']},
                    'edad': {
                        '$let': {
                            'vars': {
                                'birthDate': '$paciente.fecnac',
                                'today': datetime.now()
                            },
                            'in': {
                                '$cond': [
                                    {'$ifNull': ['$$birthDate', False]},
                                    {
                                        '$subtract': [
                                            {'$year': '$$today'},
                                            {'$year': '$$birthDate'},
                                            {
                                                '$cond': [
                                                    {
                                                        '$lt': [
                                                            {'$concat': [{'$toString': {'$month': '$$today'}}, '-', {'$toString': {'$dayOfMonth': '$$today'}}]},
                                                            {'$concat': [{'$toString': {'$month': '$$birthDate'}}, '-', {'$toString': {'$dayOfMonth': '$$birthDate'}}]}
                                                        ]
                                                    },
                                                    1,
                                                    0
                                                ]
                                            }
                                        ]
                                    },
                                    0
                                ]
                            }
                        }
                    }
                }
            }}
        ]
        
        appointments = list(db['atencion'].aggregate(pipeline))
        return [serialize_doc(a) for a in appointments]
    
    @staticmethod
    def update(id_atencion, data):
        """Actualiza una atención"""
        db = get_collection('atencion').database
        
        update_data = {}
        allowed_fields = ['area', 'motivo', 'especialidad', 'alergias']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Manejar cambio de cama
        old_appointment = db['atencion'].find_one({'id_atencion': id_atencion})
        
        if 'id_cama' in data and data['id_cama'] != old_appointment.get('id_cama'):
            # Liberar cama anterior
            if old_appointment.get('id_cama'):
                db['camas'].update_one(
                    {'id_cama': old_appointment['id_cama']},
                    {'$set': {'ocupada': 0}}
                )
            
            # Ocupar nueva cama
            if data['id_cama']:
                db['camas'].update_one(
                    {'id_cama': data['id_cama']},
                    {'$set': {'ocupada': 1}}
                )
            
            update_data['id_cama'] = data['id_cama']
        
        if update_data:
            db['atencion'].update_one(
                {'id_atencion': id_atencion},
                {'$set': update_data}
            )
        
        # Actualizar médicos si se proporcionan
        if data.get('medicos'):
            db['atencion_medicos'].delete_many({'id_atencion': id_atencion})
            for id_medico in data['medicos']:
                db['atencion_medicos'].insert_one({
                    'id_atencion': id_atencion,
                    'id_medico': int(id_medico)
                })
        
        return AppointmentModel.find_by_id(id_atencion)
    
    @staticmethod
    def close(id_atencion, user_id):
        """Cierra una atención (alta)"""
        db = get_collection('atencion').database
        
        appointment = db['atencion'].find_one({'id_atencion': id_atencion})
        
        if not appointment or appointment.get('status') != 'ABIERTA':
            return False, 'Atención no encontrada o ya está cerrada'
        
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
            'total_cuenta': float(total_amount)
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
        
        return True, None
    
    @staticmethod
    def get_billing(id_atencion):
        """Obtiene la cuenta de una atención"""
        db = get_collection('cuenta_paciente').database
        
        items = list(db['cuenta_paciente'].find(
            {'id_atencion': id_atencion}
        ).sort('fecha', 1))
        
        subtotal = sum(item.get('subtotal', 0) for item in items)
        iva = subtotal * 0.16
        total = subtotal + iva
        
        # Obtener pagos
        payments = list(db['depositos_pserv'].find(
            {'id_atencion': id_atencion}
        ))
        
        total_paid = sum(payment.get('deposito', 0) for payment in payments)
        
        return {
            'items': [serialize_doc(item) for item in items],
            'subtotal': float(subtotal),
            'iva': float(iva),
            'total': float(total),
            'total_paid': float(total_paid),
            'balance': float(total - total_paid),
            'payments': [serialize_doc(p) for p in payments]
        }