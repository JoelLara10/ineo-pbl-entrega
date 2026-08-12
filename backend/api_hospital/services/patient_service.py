from utils.database import get_collection, serialize_doc, get_next_sequence
from datetime import datetime
from bson import ObjectId
from decimal import Decimal

class PatientService:
    @staticmethod
    def get_patient_full_info(id_exp):
        """Obtiene información completa del paciente incluyendo atenciones y familiares"""
        db = get_collection('pacientes').database
        
        # Obtener paciente
        patient = db['pacientes'].find_one({'Id_exp': int(id_exp)})
        if not patient:
            return None
        
        # Obtener familiar
        familiar = db['familiares'].find_one({'Id_exp': int(id_exp)})
        
        # Obtener atenciones
        atenciones = list(db['atencion'].find(
            {'Id_exp': int(id_exp)},
            {'_id': 0, 'id_atencion': 1, 'area': 1, 'fecha_ing': 1, 'status': 1}
        ).sort('fecha_ing', -1))
        
        result = serialize_doc(patient)
        result['familiar'] = serialize_doc(familiar) if familiar else None
        result['atenciones'] = [serialize_doc(a) for a in atenciones]
        
        return result
    
    @staticmethod
    def create_appointment(id_exp, data):
        """Crea una nueva atención para un paciente"""
        db = get_collection('atencion').database
        
        # Verificar si ya tiene atención activa
        existing = db['atencion'].find_one({
            'Id_exp': int(id_exp),
            'status': 'ABIERTA'
        })
        
        if existing:
            return None, 'El paciente ya tiene una atención activa'
        
        # Crear atención
        id_atencion = get_next_sequence('atencion_id_atencion')
        
        appointment = {
            'id_atencion': id_atencion,
            'Id_exp': int(id_exp),
            'area': data.get('area'),
            'id_cama': data.get('id_cama'),
            'motivo': data.get('motivo'),
            'especialidad': data.get('especialidad'),
            'alergias': data.get('alergias', ''),
            'fecha_ing': datetime.now(),
            'status': 'ABIERTA'
        }
        
        db['atencion'].insert_one(appointment)
        
        # Asignar médicos
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
    def update_family(id_exp, data):
        """Actualiza información familiar del paciente"""
        collection = get_collection('familiares')
        
        family_data = {
            'Id_exp': int(id_exp),
            'nombre': data.get('nombre'),
            'parentesco': data.get('parentesco'),
            'telefono': data.get('telefono')
        }
        
        collection.update_one(
            {'Id_exp': int(id_exp)},
            {'$set': family_data},
            upsert=True
        )
        
        return serialize_doc(family_data)
    
    @staticmethod
    def get_patient_billing(id_exp):
        """Obtiene información de facturación del paciente"""
        db = get_collection('cuenta_paciente').database
        
        pipeline = [
            {'$match': {'Id_exp': int(id_exp)}},
            {'$lookup': {
                'from': 'atencion',
                'localField': 'id_atencion',
                'foreignField': 'id_atencion',
                'as': 'atencion'
            }},
            {'$unwind': '$atencion'},
            {'$group': {
                '_id': '$id_atencion',
                'id_atencion': {'$first': '$id_atencion'},
                'area': {'$first': '$atencion.area'},
                'fecha_ing': {'$first': '$atencion.fecha_ing'},
                'total': {'$sum': '$subtotal'},
                'items': {'$push': {
                    'fecha': '$fecha',
                    'descripcion': '$descripcion',
                    'cantidad': '$cantidad',
                    'precio': '$precio',
                    'subtotal': '$subtotal'
                }}
            }},
            {'$sort': {'fecha_ing': -1}}
        ]
        
        billing = list(db['cuenta_paciente'].aggregate(pipeline))
        return [serialize_doc(b) for b in billing]