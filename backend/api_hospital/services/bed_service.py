from utils.database import get_collection, serialize_doc, get_next_sequence

class BedService:
    @staticmethod
    def get_all_beds(area=None, status=None):
        """Obtiene todas las camas con filtros"""
        collection = get_collection('camas')
        
        query = {}
        if area:
            query['area'] = area
        if status == 'libre':
            query['ocupada'] = 0
        elif status == 'ocupada':
            query['ocupada'] = 1
        
        beds = list(collection.find(query).sort('numero', 1))
        
        # Enriquecer con información de ocupación
        db = collection.database
        for bed in beds:
            if bed.get('ocupada', 0) == 1:
                # Buscar atención activa en esta cama
                atencion = db['atencion'].find_one({
                    'id_cama': bed['id_cama'],
                    'status': 'ABIERTA'
                })
                
                if atencion:
                    paciente = db['pacientes'].find_one({'Id_exp': atencion['Id_exp']})
                    if paciente:
                        bed['current_patient'] = {
                            'Id_exp': paciente['Id_exp'],
                            'nombre': f"{paciente.get('papell', '')} {paciente.get('nom_pac', '')}",
                            'id_atencion': atencion['id_atencion']
                        }
        
        return [serialize_doc(b) for b in beds]
    
    @staticmethod
    def create_bed(data):
        """Crea una nueva cama"""
        collection = get_collection('camas')
        
        # Verificar si ya existe una cama con ese número
        existing = collection.find_one({'numero': data['numero']})
        if existing:
            return None, 'Ya existe una cama con ese número'
        
        id_cama = get_next_sequence('camas_id_cama')
        
        bed = {
            'id_cama': id_cama,
            'numero': data['numero'],
            'area': data['area'],
            'tipo_habitacion': data.get('tipo_habitacion'),
            'piso': data.get('piso'),
            'seccion': data.get('seccion'),
            'ocupada': int(data.get('ocupada', 0))
        }
        
        collection.insert_one(bed)
        return serialize_doc(bed), None
    
    @staticmethod
    def update_bed(id_cama, data):
        """Actualiza una cama"""
        collection = get_collection('camas')
        
        update_data = {}
        allowed_fields = ['numero', 'area', 'tipo_habitacion', 'piso', 'seccion', 'ocupada']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = int(data[field]) if field == 'ocupada' else data[field]
        
        if not update_data:
            return None
        
        result = collection.update_one(
            {'id_cama': id_cama},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return BedService.get_all_beds()  # Retornar lista actualizada
    
    @staticmethod
    def delete_bed(id_cama):
        """Elimina una cama si no está ocupada"""
        collection = get_collection('camas')
        
        # Verificar si está ocupada
        bed = collection.find_one({'id_cama': id_cama})
        if not bed:
            return False, 'Cama no encontrada'
        
        if bed.get('ocupada', 0) == 1:
            return False, 'No se puede eliminar una cama ocupada'
        
        result = collection.delete_one({'id_cama': id_cama})
        
        if result.deleted_count == 0:
            return False, 'Error al eliminar'
        
        return True, None
    
    @staticmethod
    def get_occupancy_report():
        """Genera reporte de ocupación"""
        collection = get_collection('camas')
        
        # Estadísticas por área
        pipeline = [
            {'$group': {
                '_id': '$area',
                'total': {'$sum': 1},
                'occupied': {'$sum': {'$cond': ['$ocupada', 1, 0]}}
            }}
        ]
        
        stats = list(collection.aggregate(pipeline))
        
        report = []
        for stat in stats:
            report.append({
                'area': stat['_id'],
                'total_beds': stat['total'],
                'occupied_beds': stat['occupied'],
                'available_beds': stat['total'] - stat['occupied'],
                'occupancy_percentage': (stat['occupied'] / stat['total'] * 100) if stat['total'] > 0 else 0
            })
        
        return report
