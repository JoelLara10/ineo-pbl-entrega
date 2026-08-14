from utils.database import get_collection, serialize_doc, get_next_sequence
from datetime import datetime
from bson import ObjectId
import os

class StudyService:
    
    @staticmethod
    def get_catalog_by_type(study_type):
        """Obtiene IDs de catálogo por tipo"""
        collection = get_collection('catalogo_examenes')
        docs = collection.find(
            {"tipo": {"$regex": f"^{study_type}$", "$options": "i"}},
            {"id_catalogo": 1}
        )
        return [doc['id_catalogo'] for doc in docs]
    
    @staticmethod
    def get_pending_studies(study_type=None):
        """Obtiene estudios pendientes"""
        db = get_collection('examenes').database
        
        type_ids = []
        if study_type:
            type_ids = StudyService.get_catalog_by_type(study_type)
        
        pipeline = [
            {"$lookup": {
                "from": "atencion",
                "localField": "id_atencion",
                "foreignField": "id_atencion",
                "as": "atencion"
            }},
            {"$unwind": {"path": "$atencion", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "pacientes",
                "localField": "atencion.Id_exp",
                "foreignField": "Id_exp",
                "as": "paciente"
            }},
            {"$unwind": {"path": "$paciente", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "camas",
                "localField": "atencion.id_cama",
                "foreignField": "id_cama",
                "as": "cama"
            }},
            {"$unwind": {"path": "$cama", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "users",
                "localField": "id_medico",
                "foreignField": "_id",
                "as": "user"
            }},
            {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "examenes_det",
                "localField": "id_examen",
                "foreignField": "id_examen",
                "as": "det"
            }},
            {"$unwind": {"path": "$det", "preserveNullAndEmptyArrays": False}},
            {"$match": {
                "det.estado": {"$regex": "^PENDIENTE$", "$options": "i"}
            }}
        ]
        
        if type_ids:
            pipeline.append({"$match": {"det.id_catalogo": {"$in": type_ids}}})
        
        pipeline.extend([
            {"$lookup": {
                "from": "catalogo_examenes",
                "localField": "det.id_catalogo",
                "foreignField": "id_catalogo",
                "as": "cat"
            }},
            {"$unwind": {"path": "$cat", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": "$id_examen",
                "fecha": {"$first": "$fecha"},
                "paciente": {
                    "$first": {
                        "$concat": [
                            {"$ifNull": ["$paciente.nom_pac", ""]}, " ",
                            {"$ifNull": ["$paciente.papell", ""]}, " ",
                            {"$ifNull": ["$paciente.sapell", ""]}
                        ]
                    }
                },
                "medico": {"$first": "$user.username"},
                "habitacion": {"$first": "$cama.numero"},
                "estudios": {"$push": "$cat.nombre"}
            }},
            {"$project": {
                "id_examen": "$_id",
                "fecha": 1,
                "paciente": 1,
                "medico": 1,
                "habitacion": 1,
                "estudios": {
                    "$reduce": {
                        "input": "$estudios",
                        "initialValue": "",
                        "in": {
                            "$concat": [
                                "$$value",
                                {"$cond": [{"$eq": ["$$value", ""]}, "", ", "]},
                                "$$this"
                            ]
                        }
                    }
                }
            }},
            {"$sort": {"fecha": -1}}
        ])
        
        results = list(db['examenes'].aggregate(pipeline))
        return [serialize_doc(r) for r in results]
    
    @staticmethod
    def get_completed_studies(study_type=None):
        """Obtiene estudios completados"""
        db = get_collection('examenes').database
        
        type_ids = []
        if study_type:
            type_ids = StudyService.get_catalog_by_type(study_type)
        
        pipeline = [
            {"$lookup": {
                "from": "atencion",
                "localField": "id_atencion",
                "foreignField": "id_atencion",
                "as": "atencion"
            }},
            {"$unwind": {"path": "$atencion", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "pacientes",
                "localField": "atencion.Id_exp",
                "foreignField": "Id_exp",
                "as": "paciente"
            }},
            {"$unwind": {"path": "$paciente", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "camas",
                "localField": "atencion.id_cama",
                "foreignField": "id_cama",
                "as": "cama"
            }},
            {"$unwind": {"path": "$cama", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "users",
                "localField": "id_medico",
                "foreignField": "_id",
                "as": "user"
            }},
            {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "examenes_det",
                "localField": "id_examen",
                "foreignField": "id_examen",
                "as": "det"
            }},
            {"$unwind": {"path": "$det", "preserveNullAndEmptyArrays": False}},
            {"$match": {
                "det.estado": {"$regex": "^REALIZADO$", "$options": "i"}
            }}
        ]
        
        if type_ids:
            pipeline.append({"$match": {"det.id_catalogo": {"$in": type_ids}}})
        
        pipeline.extend([
            {"$lookup": {
                "from": "catalogo_examenes",
                "localField": "det.id_catalogo",
                "foreignField": "id_catalogo",
                "as": "cat"
            }},
            {"$unwind": {"path": "$cat", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": "$id_examen",
                "fecha": {"$first": "$fecha"},
                "fecha_realizado": {"$first": "$det.fecha_realizado"},
                "paciente": {
                    "$first": {
                        "$concat": [
                            {"$ifNull": ["$paciente.nom_pac", ""]}, " ",
                            {"$ifNull": ["$paciente.papell", ""]}, " ",
                            {"$ifNull": ["$paciente.sapell", ""]}
                        ]
                    }
                },
                "medico": {"$first": "$user.username"},
                "habitacion": {"$first": "$cama.numero"},
                "estudios": {"$push": "$cat.nombre"}
            }},
            {"$project": {
                "id_examen": "$_id",
                "fecha": 1,
                "fecha_realizado": 1,
                "paciente": 1,
                "medico": 1,
                "habitacion": 1,
                "estudios": {
                    "$reduce": {
                        "input": "$estudios",
                        "initialValue": "",
                        "in": {
                            "$concat": [
                                "$$value",
                                {"$cond": [{"$eq": ["$$value", ""]}, "", ", "]},
                                "$$this"
                            ]
                        }
                    }
                }
            }},
            {"$sort": {"fecha_realizado": -1}}
        ])
        
        results = list(db['examenes'].aggregate(pipeline))
        return [serialize_doc(r) for r in results]
    
    @staticmethod
    def get_study_details(id_examen):
        """Obtiene detalles de un estudio"""
        db = get_collection('examenes').database
        
        pipeline = [
            {"$match": {"id_examen": id_examen}},
            {"$lookup": {
                "from": "atencion",
                "localField": "id_atencion",
                "foreignField": "id_atencion",
                "as": "atencion"
            }},
            {"$unwind": "$atencion"},
            {"$lookup": {
                "from": "pacientes",
                "localField": "atencion.Id_exp",
                "foreignField": "Id_exp",
                "as": "paciente"
            }},
            {"$unwind": "$paciente"},
            {"$lookup": {
                "from": "camas",
                "localField": "atencion.id_cama",
                "foreignField": "id_cama",
                "as": "cama"
            }},
            {"$unwind": {"path": "$cama", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "examenes_det",
                "localField": "id_examen",
                "foreignField": "id_examen",
                "as": "detalles"
            }},
            {"$lookup": {
                "from": "catalogo_examenes",
                "localField": "detalles.id_catalogo",
                "foreignField": "id_catalogo",
                "as": "catalogo"
            }},
            {"$project": {
                "id_examen": 1,
                "fecha": 1,
                "observaciones": 1,
                "paciente": {
                    "Id_exp": "$paciente.Id_exp",
                    "nombre": {"$concat": ["$paciente.papell", " ", "$paciente.nom_pac"]}
                },
                "habitacion": "$cama.numero",
                "detalles": {
                    "$map": {
                        "input": "$detalles",
                        "as": "det",
                        "in": {
                            "nombre": {
                                "$arrayElemAt": [
                                    "$catalogo.nombre",
                                    {"$indexOfArray": ["$catalogo.id_catalogo", "$$det.id_catalogo"]}
                                ]
                            },
                            "estado": "$$det.estado",
                            "archivo_resultado": "$$det.archivo_resultado",
                            "observaciones": "$$det.observaciones",
                            "fecha_realizado": "$$det.fecha_realizado"
                        }
                    }
                }
            }}
        ]
        
        results = list(db['examenes'].aggregate(pipeline))
        return serialize_doc(results[0]) if results else None
    
    @staticmethod
    def save_results(id_examen, files, observaciones):
        """Guarda resultados de estudios"""
        db = get_collection('examenes_det').database
        
        archivos_db = ','.join(files)
        
        result = db['examenes_det'].update_many(
            {"id_examen": id_examen},
            {"$set": {
                "archivo_resultado": archivos_db,
                "observaciones": observaciones,
                "fecha_realizado": datetime.now(),
                "estado": "REALIZADO"
            }}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def update_results(id_examen, data):
        """Actualiza resultados de estudio"""
        db = get_collection('examenes_det').database
        
        update_data = {}
        if 'resultados' in data:
            update_data['resultado'] = data['resultados']
        if 'observaciones' in data:
            update_data['observaciones'] = data['observaciones']
        if 'estado' in data:
            update_data['estado'] = data['estado']
        
        if not update_data:
            return False
        
        result = db['examenes_det'].update_many(
            {"id_examen": id_examen},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_study(id_examen):
        """Elimina un estudio completo"""
        db = get_collection('examenes').database
        
        # Obtener archivos para eliminar físicamente
        detalles = db['examenes_det'].find(
            {"id_examen": id_examen},
            {"archivo_resultado": 1}
        )
        
        for det in detalles:
            archivo = det.get('archivo_resultado')
            if archivo:
                for nombre in archivo.split(','):
                    nombre = nombre.strip()
                    if nombre:
                        for folder in ['uploads/estudios/gabinete', 'uploads/estudios/laboratorio']:
                            filepath = os.path.join(folder, nombre)
                            if os.path.exists(filepath):
                                try:
                                    os.remove(filepath)
                                except:
                                    pass
        
        # Eliminar detalles
        db['examenes_det'].delete_many({"id_examen": id_examen})
        
        # Eliminar encabezado
        result = db['examenes'].delete_one({"id_examen": id_examen})
        
        return result.deleted_count > 0
    
    @staticmethod
    def get_pending_counts():
        """Obtiene conteo de estudios pendientes"""
        db = get_collection('examenes_det').database
        
        lab_ids = StudyService.get_catalog_by_type("LABORATORIO")
        gab_ids = StudyService.get_catalog_by_type("GABINETE")
        
        lab_pending = db['examenes_det'].count_documents({
            "id_catalogo": {"$in": lab_ids},
            "estado": {"$regex": "^PENDIENTE$", "$options": "i"}
        })
        
        gab_pending = db['examenes_det'].count_documents({
            "id_catalogo": {"$in": gab_ids},
            "estado": {"$regex": "^PENDIENTE$", "$options": "i"}
        })
        
        return {
            'laboratorio': lab_pending,
            'gabinete': gab_pending,
            'total': lab_pending + gab_pending
        }