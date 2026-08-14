from utils.database import get_collection, serialize_doc, get_next_sequence
from datetime import datetime
from bson import ObjectId
import os
from werkzeug.utils import secure_filename

class ExamService:

    # ================================================================
    #  NUEVOS MÉTODOS (iguales a la lógica de estudios.py)
    # ================================================================

    @staticmethod
    def _get_catalog_ids_by_type(tipo):
        """Devuelve lista de id_catalogo cuyo tipo coincida (insensible a mayúsc/minúsc)."""
        collection = get_collection('catalogo_examenes')
        docs = collection.find({"tipo": {"$regex": f"^{tipo}$", "$options": "i"}}, {"id_catalogo": 1})
        return [doc['id_catalogo'] for doc in docs]

    # En ExamService, reemplaza los métodos get_pending_exams y get_completed_exams
# o agrega los parámetros.

    @staticmethod
    def get_pending_exams(exam_type=None, page=1, limit=5):
        db = get_collection('examenes_det').database
        skip = (page - 1) * limit

        if exam_type:
            tipo_upper = exam_type.upper()
            if tipo_upper not in ('LABORATORIO', 'GABINETE'):
                return []
            ids_catalogo = ExamService._get_catalog_ids_by_type(tipo_upper)
        else:
            ids_catalogo = None

        pipeline = [
            {"$lookup": {"from": "atencion", "localField": "id_atencion", "foreignField": "id_atencion", "as": "atencion"}},
            {"$unwind": {"path": "$atencion", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "pacientes", "localField": "atencion.Id_exp", "foreignField": "Id_exp", "as": "paciente"}},
            {"$unwind": {"path": "$paciente", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "camas", "localField": "atencion.id_cama", "foreignField": "id_cama", "as": "cama"}},
            {"$unwind": {"path": "$cama", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "users", "localField": "id_medico", "foreignField": "_id", "as": "user"}},
            {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "examenes_det", "localField": "id_examen", "foreignField": "id_examen", "as": "det"}},
            {"$unwind": {"path": "$det", "preserveNullAndEmptyArrays": False}},
            {"$match": {"det.estado": {"$regex": "^PENDIENTE$", "$options": "i"}}},
            {"$lookup": {"from": "catalogo_examenes", "localField": "det.id_catalogo", "foreignField": "id_catalogo", "as": "cat"}},
            {"$unwind": {"path": "$cat", "preserveNullAndEmptyArrays": True}},
        ]

        if ids_catalogo is not None:
            pipeline.append({"$match": {"det.id_catalogo": {"$in": ids_catalogo}}})

        pipeline.extend([
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
                        "in": {"$concat": ["$$value", {"$cond": [{"$eq": ["$$value", ""]}, "", ", "]}, "$$this"]}
                    }
                }
            }},
            {"$sort": {"fecha": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ])

        results = list(db['examenes'].aggregate(pipeline))
        return [serialize_doc(r) for r in results]


    @staticmethod
    def get_completed_exams(exam_type=None, page=1, limit=5):
        db = get_collection('examenes_det').database
        skip = (page - 1) * limit

        if exam_type:
            tipo_upper = exam_type.upper()
            if tipo_upper not in ('LABORATORIO', 'GABINETE'):
                return []
            ids_catalogo = ExamService._get_catalog_ids_by_type(tipo_upper)
        else:
            ids_catalogo = None

        pipeline = [
            {"$lookup": {"from": "atencion", "localField": "id_atencion", "foreignField": "id_atencion", "as": "atencion"}},
            {"$unwind": {"path": "$atencion", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "pacientes", "localField": "atencion.Id_exp", "foreignField": "Id_exp", "as": "paciente"}},
            {"$unwind": {"path": "$paciente", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "camas", "localField": "atencion.id_cama", "foreignField": "id_cama", "as": "cama"}},
            {"$unwind": {"path": "$cama", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "users", "localField": "id_medico", "foreignField": "_id", "as": "user"}},
            {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "examenes_det", "localField": "id_examen", "foreignField": "id_examen", "as": "det"}},
            {"$unwind": {"path": "$det", "preserveNullAndEmptyArrays": False}},
            {"$match": {"det.estado": {"$regex": "^REALIZADO$", "$options": "i"}}},
            {"$lookup": {"from": "catalogo_examenes", "localField": "det.id_catalogo", "foreignField": "id_catalogo", "as": "cat"}},
            {"$unwind": {"path": "$cat", "preserveNullAndEmptyArrays": True}},
        ]

        if ids_catalogo is not None:
            pipeline.append({"$match": {"det.id_catalogo": {"$in": ids_catalogo}}})

        pipeline.extend([
            {"$group": {
                "_id": "$id_examen",
                "fecha": {"$first": "$fecha"},          # fecha de solicitud
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
                "fecha": 1,                      # ← SOLO fecha de solicitud
                "fecha_realizado": 1,
                "paciente": 1,
                "medico": 1,
                "habitacion": 1,
                "estudios": {
                    "$reduce": {
                        "input": "$estudios",
                        "initialValue": "",
                        "in": {"$concat": ["$$value", {"$cond": [{"$eq": ["$$value", ""]}, "", ", "]}, "$$this"]}
                    }
                }
            }},
            {"$sort": {"fecha": -1}},              # ordenar por fecha de solicitud
            {"$skip": skip},
            {"$limit": limit}
        ])

        results = list(db['examenes'].aggregate(pipeline))
        return [serialize_doc(r) for r in results]

    @staticmethod
    def get_counts():
        """
        Retorna conteo de solicitudes PENDIENTES (id_examen únicos) por tipo.
        """
        db = get_collection('examenes_det').database

        lab_ids = ExamService._get_catalog_ids_by_type("LABORATORIO")
        gab_ids = ExamService._get_catalog_ids_by_type("GABINETE")

        def count_pending_by_ids(ids):
            if not ids:
                return 0
            pipeline = [
                {"$match": {"id_catalogo": {"$in": ids}, "estado": {"$regex": "^PENDIENTE$", "$options": "i"}}},
                {"$group": {"_id": "$id_examen"}},
                {"$count": "count"}
            ]
            res = list(db['examenes_det'].aggregate(pipeline))
            return res[0]['count'] if res else 0

        lab_pend = count_pending_by_ids(lab_ids)
        gab_pend = count_pending_by_ids(gab_ids)

        return {
            'laboratorio': lab_pend,
            'gabinete': gab_pend,
            'total': lab_pend + gab_pend
        }

    # ================================================================
    #  MÉTODOS EXISTENTES (sin cambios)
    # ================================================================

    @staticmethod
    def get_exam_catalog(exam_type=None):
        collection = get_collection('catalogo_examenes')
        query = {}
        if exam_type:
            query['tipo'] = exam_type
        exams = list(collection.find(query, {
            'id_catalogo': 1,
            'nombre': 1,
            'tipo': 1,
            'precio': 1
        }).sort('nombre', 1))
        return [serialize_doc(e) for e in exams]

    @staticmethod
    def request_exams(id_atencion, exam_ids, id_medico, observations=''):
        db = get_collection('examenes').database
        atencion = db['atencion'].find_one({'id_atencion': id_atencion})
        if not atencion:
            return None, 'Atención no encontrada'

        id_examen = get_next_sequence('examenes_id_examen')
        examen_header = {
            'id_examen': id_examen,
            'id_atencion': id_atencion,
            'id_medico': ObjectId(id_medico),
            'observaciones': observations,
            'fecha': datetime.now()
        }
        db['examenes'].insert_one(examen_header)

        subtotal_total = 0
        catalogo = db['catalogo_examenes']
        for id_catalogo in exam_ids:
            exam = catalogo.find_one({'id_catalogo': int(id_catalogo)})
            if exam:
                nombre = exam.get('nombre', '')
                precio = exam.get('precio', 0)
                cantidad = 1
                subtotal = precio * cantidad
                subtotal_total += subtotal
                db['examenes_det'].insert_one({
                    'id_examen': id_examen,
                    'id_catalogo': int(id_catalogo),
                    'nombre_examen': nombre,
                    'precio': precio,
                    'cantidad': cantidad,
                    'subtotal': subtotal,
                    'estado': 'PENDIENTE',
                    'fecha': datetime.now()
                })
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

        db['examenes'].update_one(
            {'id_examen': id_examen},
            {'$set': {'subtotal_total': subtotal_total}}
        )
        return serialize_doc(examen_header), None

    @staticmethod
    def update_exam_results(id_examen, results):
        db = get_collection('examenes_det').database
        examen = db['examenes'].find_one({'id_examen': id_examen})
        if not examen:
            return False
        for result in results:
            db['examenes_det'].update_one(
                {
                    'id_examen': id_examen,
                    'id_catalogo': result.get('id_catalogo')
                },
                {
                    '$set': {
                        'resultado': result.get('resultado'),
                        'estado': 'REALIZADO',
                        'fecha_realizado': datetime.now()
                    }
                }
            )
        return True

    @staticmethod
    def get_patient_exams(id_atencion):
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
            }}
        ]
        exams = list(db['examenes'].aggregate(pipeline))
        return [serialize_doc(e) for e in exams]

    @staticmethod
    def upload_exam_file(id_examen, file):
        upload_dir = 'uploads/exams'
        os.makedirs(upload_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"exam_{id_examen}_{timestamp}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        db = get_collection('examenes_det').database
        db['examenes_det'].update_one(
            {'id_examen': id_examen},
            {'$set': {
                'archivo_resultado': filepath,
                'estado': 'REALIZADO',
                'fecha_realizado': datetime.now()
            }}
        )
        return filepath
    



    @staticmethod
    def upload_exam_results(id_examen, exam_type, files, observaciones=''):
        db = get_collection('examenes_det').database
        ids_catalogo = ExamService._get_catalog_ids_by_type(exam_type)
        if not ids_catalogo:
            return False

        exam = db['examenes'].find_one({'id_examen': id_examen})
        if not exam:
            return False

        if exam_type.upper() == 'LABORATORIO':
            upload_folder = 'static/resultados/laboratorio'
        else:
            upload_folder = 'static/resultados/gabinete'

        os.makedirs(upload_folder, exist_ok=True)

        nombres_guardados = []
        for file in files:
            if not file or not file.filename:
                continue

            # Validar extensión
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if ext not in {'pdf', 'png', 'jpg', 'jpeg'}:
                print(f"Extensión no permitida: {ext} en {file.filename}")
                continue

            filename_secure = secure_filename(file.filename)
            ts = datetime.now().strftime('%Y%m%d%H%M%S%f')
            nombre_guardado = f"{id_examen}_{ts}_{filename_secure}"
            filepath = os.path.join(upload_folder, nombre_guardado)
            file.save(filepath)
            nombres_guardados.append(nombre_guardado)
            print(f"Archivo guardado: {filepath}")

        if not nombres_guardados:
            print("No se guardó ningún archivo válido.")
            return False

        archivos_db = ','.join(nombres_guardados)

        result = db['examenes_det'].update_many(
            {
                'id_examen': id_examen,
                'id_catalogo': {'$in': ids_catalogo},
                'estado': {'$regex': '^PENDIENTE$', '$options': 'i'}
            },
            {'$set': {
                'archivo_resultado': archivos_db,
                'observaciones': observaciones,
                'fecha_realizado': datetime.now(),
                'estado': 'REALIZADO'
            }}
        )
        print(f"Documentos actualizados: {result.modified_count}")
        return True
    


    @staticmethod
    def get_edit_info(id_examen, tipo):
        db = get_collection('examenes_det').database
        ids_catalogo = ExamService._get_catalog_ids_by_type(tipo)
        if not ids_catalogo:
            return None

        pipeline = [
            {"$match": {"id_examen": id_examen}},
            {"$lookup": {"from": "atencion", "localField": "id_atencion", "foreignField": "id_atencion", "as": "atencion"}},
            {"$unwind": "$atencion"},
            {"$lookup": {"from": "pacientes", "localField": "atencion.Id_exp", "foreignField": "Id_exp", "as": "paciente"}},
            {"$unwind": "$paciente"},
            {"$lookup": {"from": "camas", "localField": "atencion.id_cama", "foreignField": "id_cama", "as": "cama"}},
            {"$unwind": {"path": "$cama", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "examenes_det", "localField": "id_examen", "foreignField": "id_examen", "as": "dets"}},
            {"$unwind": {"path": "$dets", "preserveNullAndEmptyArrays": True}},
            {"$match": {"dets.id_catalogo": {"$in": ids_catalogo}}},
            {"$group": {
                "_id": "$id_examen",
                "paciente": {"$first": {"$concat": [
                    {"$ifNull": ["$paciente.nom_pac", ""]}, " ",
                    {"$ifNull": ["$paciente.papell", ""]}, " ",
                    {"$ifNull": ["$paciente.sapell", ""]}
                ]}},
                "habitacion": {"$first": "$cama.numero"},
                "archivos_raw": {"$addToSet": "$dets.archivo_resultado"},
                "observaciones": {"$first": "$dets.observaciones"}
            }},
            {"$project": {
                "id_examen": "$_id",
                "paciente": 1,
                "habitacion": 1,
                "archivos": {
                    "$reduce": {
                        "input": "$archivos_raw",
                        "initialValue": [],
                        "in": {
                            "$concatArrays": [
                                "$$value",
                                {
                                    "$cond": {
                                        "if": {"$eq": [{"$type": "$$this"}, "string"]},
                                        "then": {
                                            "$cond": {
                                                "if": {"$eq": ["$$this", ""]},
                                                "then": [],
                                                "else": {"$split": ["$$this", ","]}
                                            }
                                        },
                                        "else": []
                                    }
                                }
                            ]
                        }
                    }
                },
                "observaciones": {"$ifNull": ["$observaciones", ""]}
            }}
        ]
        result = list(db['examenes'].aggregate(pipeline))
        if not result:
            return None
        info = result[0]
        # Limpiar y eliminar duplicados de la lista de archivos
        archivos = [a.strip() for a in info.get('archivos', []) if a and a.strip()]
        archivos = list(dict.fromkeys(archivos))
        info['archivos'] = archivos
        # Asegurar que observaciones sea string
        info['observaciones'] = info.get('observaciones', '') or ''
        return info
    

    @staticmethod
    def update_edit(id_examen, exam_type, new_files, delete_files, observaciones):
        db = get_collection('examenes_det').database
        ids_catalogo = ExamService._get_catalog_ids_by_type(exam_type)
        if not ids_catalogo:
            return False

        # Obtener archivos actuales
        doc = db['examenes_det'].find_one(
            {'id_examen': id_examen, 'id_catalogo': {'$in': ids_catalogo}}
        )
        if not doc:
            return False

        archivo_str = doc.get('archivo_resultado', '')
        archivos_actuales = [a.strip() for a in archivo_str.split(',') if a.strip()]
        archivos_actuales = list(dict.fromkeys(archivos_actuales))

        # Eliminar archivos marcados
        upload_folder = 'static/resultados/laboratorio' if exam_type.upper() == 'LABORATORIO' else 'static/resultados/gabinete'
        if delete_files:
            for nombre in delete_files:
                if nombre in archivos_actuales:
                    archivos_actuales.remove(nombre)
                ruta = os.path.join(upload_folder, nombre)
                if os.path.exists(ruta):
                    try:
                        os.remove(ruta)
                    except:
                        pass

        # Guardar nuevos archivos
        os.makedirs(upload_folder, exist_ok=True)
        nuevos_guardados = []
        for file in new_files:
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if ext not in {'pdf', 'png', 'jpg', 'jpeg'}:
                    continue
                filename_secure = secure_filename(file.filename)
                ts = datetime.now().strftime('%Y%m%d%H%M%S%f')
                nombre_guardado = f"{id_examen}_{ts}_{filename_secure}"
                filepath = os.path.join(upload_folder, nombre_guardado)
                file.save(filepath)
                nuevos_guardados.append(nombre_guardado)

        archivos_finales = archivos_actuales + nuevos_guardados
        archivos_finales = list(dict.fromkeys(archivos_finales))
        archivos_db = ','.join(archivos_finales)

        result = db['examenes_det'].update_many(
            {'id_examen': id_examen, 'id_catalogo': {'$in': ids_catalogo}},
            {'$set': {
                'archivo_resultado': archivos_db,
                'observaciones': observaciones,
                'fecha_realizado': datetime.now(),
                'estado': 'REALIZADO'
            }}
        )
        return result.modified_count > 0
    

    

    @staticmethod
    def get_files(id_examen, tipo):
        db = get_collection('examenes_det').database
        ids_catalogo = ExamService._get_catalog_ids_by_type(tipo)
        if not ids_catalogo:
            return []

        dets = db['examenes_det'].find({
            "id_examen": id_examen,
            "id_catalogo": {"$in": ids_catalogo},
            "estado": {"$regex": "^REALIZADO$", "$options": "i"}
        }, {"archivo_resultado": 1})

        folder = 'laboratorio' if tipo == 'LABORATORIO' else 'gabinete'
        archivos_dict = {}
        for d in dets:
            ar = d.get('archivo_resultado')
            if ar:
                for nombre in ar.split(','):
                    nombre = nombre.strip()
                    if nombre and nombre not in archivos_dict:
                        archivos_dict[nombre] = {
                            'nombre': nombre,
                            'tipo': nombre.split('.')[-1].lower(),
                            'url': f'/static/resultados/{folder}/{nombre}'
                        }
        return list(archivos_dict.values())
    


    @staticmethod
    def delete_exam_results(id_examen, exam_type):
        """
        Elimina los archivos físicos y los registros de detalles de un examen.
        Si no quedan detalles, elimina también el encabezado del examen.
        """
        db = get_collection('examenes_det').database

        # Obtener los id_catalogo según el tipo
        ids_catalogo = ExamService._get_catalog_ids_by_type(exam_type)
        if not ids_catalogo:
            return False

        # 1. Obtener los archivos asociados a ese examen y tipo
        rows = list(db['examenes_det'].find(
            {"id_examen": id_examen, "id_catalogo": {"$in": ids_catalogo}},
            {"archivo_resultado": 1}
        ))

        # 2. Eliminar archivos físicos
        upload_folder = 'static/resultados/laboratorio' if exam_type.upper() == 'LABORATORIO' else 'static/resultados/gabinete'
        for row in rows:
            archivo = row.get('archivo_resultado')
            if archivo:
                for nombre in archivo.split(','):
                    nombre = nombre.strip()
                    if nombre:
                        ruta = os.path.join(upload_folder, nombre)
                        if os.path.exists(ruta):
                            try:
                                os.remove(ruta)
                                print(f"Archivo eliminado: {ruta}")
                            except Exception as e:
                                print(f"Error al eliminar {ruta}: {e}")

        # 3. Eliminar los detalles del examen para ese tipo
        result_det = db['examenes_det'].delete_many(
            {"id_examen": id_examen, "id_catalogo": {"$in": ids_catalogo}}
        )

        # 4. Verificar si quedan otros detalles (de otro tipo)
        restantes = db['examenes_det'].count_documents({"id_examen": id_examen})
        if restantes == 0:
            # Si no quedan detalles, eliminar el encabezado del examen
            db['examenes'].delete_one({"id_examen": id_examen})
            print(f"Encabezado del examen {id_examen} eliminado (sin detalles restantes)")
        else:
            print(f"Quedan {restantes} detalles para el examen {id_examen}, no se elimina el encabezado")

        return result_det.deleted_count > 0