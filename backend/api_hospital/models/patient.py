from utils.database import get_collection, serialize_doc, get_next_sequence
from datetime import datetime

class PatientModel:
    @staticmethod
    def create(data):
        """Crea un nuevo paciente"""
        collection = get_collection('pacientes')
        
        id_exp = get_next_sequence('pacientes_Id_exp')
        
        patient = {
            'Id_exp': id_exp,
            'curp': data.get('curp'),
            'papell': data.get('papell'),
            'sapell': data.get('sapell'),
            'nom_pac': data.get('nom_pac'),
            'fecnac': datetime.strptime(data.get('fecnac'), '%Y-%m-%d') if data.get('fecnac') else None,
            'tel': data.get('tel', ''),
            'email': data.get('email', ''),
            'created_at': datetime.now()
        }
        
        collection.insert_one(patient)
        return serialize_doc(patient)
    
    @staticmethod
    def find_by_id(id_exp):
        """Busca paciente por ID de expediente"""
        collection = get_collection('pacientes')
        patient = collection.find_one({'Id_exp': int(id_exp)})
        return patient
    
    @staticmethod
    def search(query, page=1, page_size=20):
        """Busca pacientes por nombre o CURP"""
        collection = get_collection('pacientes')
        
        search_filter = {
            '$or': [
                {'nom_pac': {'$regex': query, '$options': 'i'}},
                {'papell': {'$regex': query, '$options': 'i'}},
                {'curp': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        skip = (page - 1) * page_size
        total = collection.count_documents(search_filter)
        patients = list(collection.find(search_filter).skip(skip).limit(page_size))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'data': [serialize_doc(p) for p in patients]
        }
    
    @staticmethod
    def get_all_active(page=1, page_size=20):
        """Obtiene todos los pacientes activos"""
        collection = get_collection('pacientes')
        
        skip = (page - 1) * page_size
        total = collection.count_documents({})
        patients = list(collection.find({}).skip(skip).limit(page_size).sort('Id_exp', -1))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'data': [serialize_doc(p) for p in patients]
        }
    
    @staticmethod
    def update(id_exp, data):
        """Actualiza un paciente"""
        collection = get_collection('pacientes')
        
        update_data = {}
        for field in ['curp', 'papell', 'sapell', 'nom_pac', 'tel', 'email']:
            if field in data:
                update_data[field] = data[field]
        
        if 'fecnac' in data and data['fecnac']:
            update_data['fecnac'] = datetime.strptime(data['fecnac'], '%Y-%m-%d')
        
        if update_data:
            collection.update_one(
                {'Id_exp': int(id_exp)},
                {'$set': update_data}
            )
        
        return PatientModel.find_by_id(id_exp)
    
    @staticmethod
    def get_with_active_appointment(id_exp):
        """Obtiene paciente con su atención activa"""
        db = get_collection('pacientes').database
        patient = PatientModel.find_by_id(id_exp)
        
        if not patient:
            return None
        
        # Buscar atención activa
        appointment = db['atencion'].find_one({
            'Id_exp': int(id_exp),
            'status': 'ABIERTA'
        })
        
        result = serialize_doc(patient)
        result['active_appointment'] = serialize_doc(appointment) if appointment else None
        
        return result