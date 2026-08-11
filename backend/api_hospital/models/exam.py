from utils.database import get_collection, serialize_doc, get_next_sequence
from datetime import datetime
from bson import ObjectId

class ExamModel:
    @staticmethod
    def get_catalog(exam_type=None):
        """Obtiene catálogo de exámenes"""
        collection = get_collection('catalogo_examenes')
        
        query = {}
        if exam_type:
            query['tipo'] = exam_type
        
        exams = list(collection.find(query, {
            'id_catalogo': 1,
            'nombre': 1,
            'tipo': 1,
            'precio': 1,
            'descripcion': 1
        }).sort('nombre', 1))
        
        return [serialize_doc(e) for e in exams]
    
    @staticmethod
    def create_catalog_item(data):
        """Crea un nuevo examen en el catálogo"""
        collection = get_collection('catalogo_examenes')
        
        # Verificar si ya existe
        existing = collection.find_one({'nombre': data['nombre']})
        if existing:
            return None, 'Ya existe un examen con ese nombre'
        
        # Obtener último ID
        last = collection.find_one(sort=[('id_catalogo', -1)])
        new_id = (last['id_catalogo'] + 1) if last else 1
        
        exam = {
            'id_catalogo': new_id,
            'nombre': data['nombre'],
            'tipo': data['tipo'],
            'precio': float(data.get('precio', 0)),
            'descripcion': data.get('descripcion', ''),
            'activo': True
        }
        
        collection.insert_one(exam)
        return serialize_doc(exam), None
    
    @staticmethod
    def request_exams(id_atencion, exam_ids, id_medico, observations=''):
        """Solicita exámenes para un paciente"""
        db = get_collection('examenes').database
        
        # Verificar atención
        atencion = db['atencion'].find_one({'id_atencion': id_atencion})
        if not atencion:
            return None, 'Atención no encontrada'
        
        # Crear encabezado
        id_examen = get_next_sequence('examenes_id_examen')
        
        examen_header = {
            'id_examen': id_examen,
            'id_atencion': id_atencion,
            'id_medico': ObjectId(id_medico) if isinstance(id_medico, str) else id_medico,
            'observaciones': observations,
            'fecha': datetime.now(),
            'subtotal_total': 0
        }
        
        db['examenes'].insert_one(examen_header)
        
        # Crear detalles
        subtotal_total = 0
        catalogo = db['catalogo_examenes']
        
        for id_catalogo in exam_ids:
            exam = catalogo.find_one({'id_catalogo': int(id_catalogo)})
            
            if exam:
                nombre = exam.get('nombre', '')
                precio = float(exam.get('precio', 0))
                cantidad = 1
                subtotal = precio * cantidad
                subtotal_total += subtotal
                
                # Detalle del examen
                examen_det = {
                    'id_examen': id_examen,
                    'id_catalogo': int(id_catalogo),
                    'nombre_examen': nombre,
                    'precio': precio,
                    'cantidad': cantidad,
                    'subtotal': subtotal,
                    'estado': 'PENDIENTE',
                    'fecha': datetime.now(),
                    'fecha_realizado': None,
                    'resultado': None,
                    'archivo_resultado': None
                }
                
                db['examenes_det'].insert_one(examen_det)
                
                # Agregar a cuenta del paciente
                db['cuenta_paciente'].insert_one({
                    'id_atencion': id_atencion,
                    'Id_exp': atencion['Id_exp'],
                    'fecha': datetime.now(),
                    'descripcion': f"Examen: {nombre}",
                    'cantidad': cantidad,
                    'precio': precio,
                    'subtotal': subtotal,
                    'id_examen': id_examen,
                    'tipo': exam.get('tipo'),
                    'estado': 'PENDIENTE'
                })
        
        # Actualizar subtotal total
        db['examenes'].update_one(
            {'id_examen': id_examen},
            {'$set': {'subtotal_total': subtotal_total}}
        )
        
        return serialize_doc(examen_header), None
    
    @staticmethod
    def get_pending_exams(exam_type=None):
        """Obtiene exámenes pendientes"""
        db = get_collection('examenes_det').database
        
        pipeline = [
            {'$match': {'estado': 'PENDIENTE'}},
            {'$lookup': {
                'from': 'examenes',
                'localField': 'id_examen',
                'foreignField': 'id_examen',
                'as': 'examen'
            }},
            {'$unwind': '$examen'},
            {'$lookup': {
                'from': 'atencion',
                'localField': 'examen.id_atencion',
                'foreignField': 'id_atencion',
                'as': 'atencion'
            }},
            {'$unwind': '$atencion'},
            {'$lookup': {
                'from': 'pacientes',
                'localField': 'atencion.Id_exp',
                'foreignField': 'Id_exp',
                'as': 'paciente'
            }},
            {'$unwind': '$paciente'},
            {'$lookup': {
                'from': 'users',
                'localField': 'examen.id_medico',
                'foreignField': '_id',
                'as': 'medico'
            }},
            {'$unwind': {'path': '$medico', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'id_examen': 1,
                'id_detalle': '$_id',
                'nombre_examen': 1,
                'tipo': 1,
                'precio': 1,
                'fecha_solicitud': '$examen.fecha',
                'observaciones': '$examen.observaciones',
                'paciente': {
                    'Id_exp': '$paciente.Id_exp',
                    'nombre': {'$concat': ['$paciente.papell', ' ', '$paciente.sapell', ' ', '$paciente.nom_pac']}
                },
                'medico': {
                    'nombre': {'$concat': ['$medico.nombre', ' ', '$medico.papell']} if '$medico' else None
                },
                'id_atencion': '$examen.id_atencion'
            }}
        ]
        
        if exam_type:
            pipeline.insert(1, {'$match': {'tipo': exam_type}})
        
        exams = list(db['examenes_det'].aggregate(pipeline))
        return [serialize_doc(e) for e in exams]
    
    @staticmethod
    def get_exams_by_appointment(id_atencion):
        """Obtiene exámenes de una atención"""
        db = get_collection('examenes').database
        
        pipeline = [
            {'$match': {'id_atencion': id_atencion}},
            {'$lookup': {
                'from': 'examenes_det',
                'localField': 'id_examen',
                'foreignField': 'id_examen',
                'as': 'detalles'
            }},
            {'$lookup': {
                'from': 'catalogo_examenes',
                'localField': 'detalles.id_catalogo',
                'foreignField': 'id_catalogo',
                'as': 'catalogo'
            }},
            {'$project': {
                'id_examen': 1,
                'fecha': 1,
                'observaciones': 1,
                'subtotal_total': 1,
                'detalles': {
                    '$map': {
                        'input': '$detalles',
                        'as': 'det',
                        'in': {
                            'nombre_examen': '$$det.nombre_examen',
                            'estado': '$$det.estado',
                            'precio': '$$det.precio',
                            'resultado': '$$det.resultado',
                            'fecha_realizado': '$$det.fecha_realizado',
                            'archivo_resultado': '$$det.archivo_resultado'
                        }
                    }
                }
            }},
            {'$sort': {'fecha': -1}}
        ]
        
        exams = list(db['examenes'].aggregate(pipeline))
        return [serialize_doc(e) for e in exams]
    
    @staticmethod
    def update_results(id_examen, results):
        """Actualiza resultados de exámenes"""
        db = get_collection('examenes_det').database
        
        for result in results:
            update_data = {
                'resultado': result.get('resultado'),
                'estado': 'REALIZADO',
                'fecha_realizado': datetime.now()
            }
            
            if result.get('archivo'):
                update_data['archivo_resultado'] = result['archivo']
            
            db['examenes_det'].update_one(
                {
                    'id_examen': id_examen,
                    'id_catalogo': result.get('id_catalogo')
                },
                {'$set': update_data}
            )
        
        return True
    
    @staticmethod
    def get_exam_details(id_examen):
        """Obtiene detalles completos de un examen"""
        db = get_collection('examenes').database
        
        pipeline = [
            {'$match': {'id_examen': id_examen}},
            {'$lookup': {
                'from': 'examenes_det',
                'localField': 'id_examen',
                'foreignField': 'id_examen',
                'as': 'detalles'
            }},
            {'$lookup': {
                'from': 'atencion',
                'localField': 'id_atencion',
                'foreignField': 'id_atencion',
                'as': 'atencion'
            }},
            {'$unwind': '$atencion'},
            {'$lookup': {
                'from': 'pacientes',
                'localField': 'atencion.Id_exp',
                'foreignField': 'Id_exp',
                'as': 'paciente'
            }},
            {'$unwind': '$paciente'},
            {'$lookup': {
                'from': 'users',
                'localField': 'id_medico',
                'foreignField': '_id',
                'as': 'medico'
            }},
            {'$unwind': {'path': '$medico', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'id_examen': 1,
                'id_atencion': 1,
                'fecha': 1,
                'observaciones': 1,
                'subtotal_total': 1,
                'paciente': {
                    'Id_exp': '$paciente.Id_exp',
                    'nombre': {'$concat': ['$paciente.papell', ' ', '$paciente.sapell', ' ', '$paciente.nom_pac']}
                },
                'medico': {
                    'nombre': {'$concat': ['$medico.nombre', ' ', '$medico.papell']} if '$medico' else None
                },
                'detalles': '$detalles'
            }}
        ]
        
        result = list(db['examenes'].aggregate(pipeline))
        return serialize_doc(result[0]) if result else None