# routes/exams.py
from flask import Blueprint, request, jsonify, g, send_from_directory, abort
from middleware.auth_middleware import token_required, role_required
from utils.database import get_db, serialize_doc, get_next_sequence
from datetime import datetime
from bson import ObjectId
from services.exam_service import ExamService
from werkzeug.utils import secure_filename
import os

exams_bp = Blueprint('exams', __name__, url_prefix='/exams')

# ---------- CATÁLOGO ----------
@exams_bp.route('/catalog', methods=['GET'])
@token_required
def get_exam_catalog():
    try:
        db = get_db()
        exam_type = request.args.get('type')
        query = {}
        if exam_type:
            query['tipo'] = exam_type.upper()
        catalog = list(db['catalogo_examenes'].find(
            query,
            {'id_catalogo': 1, 'nombre': 1, 'tipo': 1, 'precio': 1}
        ).sort('nombre', 1))
        return jsonify([serialize_doc(c) for c in catalog]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------- SOLICITAR EXÁMENES ----------
@exams_bp.route('/request', methods=['POST'])
@token_required
@role_required('admin', 'medico')
def request_exams():
    try:
        db = get_db()
        data = request.get_json()
        id_atencion = data.get('id_atencion')
        exam_ids = data.get('exams', [])
        observations = data.get('observations', '')
        exam_type = data.get('type', 'LABORATORIO')
        
        atencion = db['atencion'].find_one({'id_atencion': id_atencion})
        if not atencion:
            return jsonify({'error': 'Atención no encontrada'}), 404
        
        if 'examenes' not in db.list_collection_names():
            db.create_collection('examenes')
        
        id_examen = get_next_sequence('examenes_id_examen')
        examen_solicitud = {
            'id_examen': id_examen,
            'id_atencion': id_atencion,
            'id_medico': ObjectId(g.user['user_id']),
            'observaciones': observations,
            'fecha': datetime.now(),
            'tipo': exam_type,
            'estado': 'PENDIENTE'
        }
        db['examenes'].insert_one(examen_solicitud)
        
        if 'examenes_det' not in db.list_collection_names():
            db.create_collection('examenes_det')
        
        catalogo = db['catalogo_examenes']
        for id_catalogo in exam_ids:
            examen = catalogo.find_one({'id_catalogo': int(id_catalogo)})
            if examen:
                db['examenes_det'].insert_one({
                    'id_examen': id_examen,
                    'id_catalogo': int(id_catalogo),
                    'nombre_examen': examen['nombre'],
                    'tipo': examen['tipo'],
                    'precio': examen.get('precio', 0),
                    'cantidad': 1,
                    'subtotal': examen.get('precio', 0),
                    'estado': 'PENDIENTE',
                    'fecha': datetime.now()
                })
        return jsonify({'message': 'Exámenes solicitados correctamente', 'id_examen': id_examen}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------- CONSULTAR SOLICITUDES POR ATENCIÓN ----------
@exams_bp.route('/requested/<int:id_atencion>', methods=['GET'])
@token_required
def get_requested_exams(id_atencion):
    try:
        db = get_db()
        exam_type = request.args.get('type')
        pipeline = [
            {'$match': {'id_atencion': id_atencion}},
            {'$lookup': {
                'from': 'examenes_det',
                'localField': 'id_examen',
                'foreignField': 'id_examen',
                'as': 'detalles'
            }},
            {'$lookup': {
                'from': 'users',
                'localField': 'id_medico',
                'foreignField': '_id',
                'as': 'medico'
            }},
            {'$unwind': {'path': '$medico', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'id_examen': 1,
                'fecha': 1,
                'fecha_solicitud': '$fecha',
                'observaciones': 1,
                'estado': 1,
                'tipo': 1,
                'medico': {'$concat': [
                    {'$ifNull': ['$medico.nombre', '']}, ' ', 
                    {'$ifNull': ['$medico.papell', '']}
                ]},
                'examenes': '$detalles.nombre_examen'
            }},
            {'$sort': {'fecha': -1}}
        ]
        if exam_type:
            pipeline.insert(1, {'$match': {'tipo': exam_type.upper()}})
        results = list(db['examenes'].aggregate(pipeline))
        serialized = []
        for r in results:
            if '_id' in r:
                r['_id'] = str(r['_id'])
            if 'fecha' in r and r['fecha'] and hasattr(r['fecha'], 'isoformat'):
                r['fecha'] = r['fecha'].isoformat()
            serialized.append(r)
        return jsonify(serialized), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------- TEST ----------
@exams_bp.route('/test', methods=['GET'])
@token_required
def test_exams():
    return jsonify({'message': 'Exams blueprint funcionando correctamente'}), 200

# ===================================================================
#  NUEVOS ENDPOINTS PARA ESTUDIOS (coinciden con la lógica web)
# ===================================================================
@exams_bp.route('/pending', methods=['GET'])
@token_required
@role_required('admin', 'estudios')
def get_pending_exams():
    exam_type = request.args.get('type')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 5))
    exams = ExamService.get_pending_exams(exam_type, page, limit)
    return jsonify(exams), 200


@exams_bp.route('/completed', methods=['GET'])
@token_required
@role_required('admin', 'estudios')
def get_completed_exams():
    exam_type = request.args.get('type')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 5))
    exams = ExamService.get_completed_exams(exam_type, page, limit)
    return jsonify(exams), 200

@exams_bp.route('/counts', methods=['GET'])
@token_required
def get_study_counts():
    """Conteo de solicitudes pendientes por tipo (Laboratorio / Gabinete)"""
    counts = ExamService.get_counts()
    return jsonify(counts), 200

# ===================================================================
#  ENDPOINTS ADICIONALES (resultados, archivos, etc.)
# ===================================================================
@exams_bp.route('/<int:id_examen>/results', methods=['PUT'])
@token_required
@role_required('admin', 'estudios')
def update_exam_results(id_examen):
    data = request.get_json()
    if 'results' not in data:
        return jsonify({'error': 'Se requieren los resultados'}), 400
    result = ExamService.update_exam_results(id_examen, data['results'])
    if not result:
        return jsonify({'error': 'Examen no encontrado'}), 404
    return jsonify({'message': 'Resultados actualizados correctamente'}), 200

@exams_bp.route('/patient/<int:id_atencion>', methods=['GET'])
@token_required
def get_patient_exams(id_atencion):
    try:
        db = get_db()
        exam_type = request.args.get('type')
        pipeline = [
            {'$match': {'id_atencion': id_atencion}},
            {'$lookup': {
                'from': 'examenes_det',
                'localField': 'id_examen',
                'foreignField': 'id_examen',
                'as': 'detalles'
            }},
            {'$lookup': {
                'from': 'users',
                'localField': 'id_medico',
                'foreignField': '_id',
                'as': 'medico'
            }},
            {'$unwind': {'path': '$medico', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'id_examen': 1,
                'fecha': 1,
                'observaciones': 1,
                'tipo': 1,
                'medico': {'$concat': ['$medico.nombre', ' ', '$medico.papell']},
                'detalles': {
                    '$map': {
                        'input': '$detalles',
                        'as': 'det',
                        'in': {
                            'nombre': '$$det.nombre_examen',
                            'estado': '$$det.estado',
                            'resultado': '$$det.resultado',
                            'archivo_resultado': '$$det.archivo_resultado'
                        }
                    }
                }
            }},
            {'$sort': {'fecha': -1}}
        ]
        if exam_type:
            pipeline.insert(1, {'$match': {'tipo': exam_type.upper()}})
        results = list(db['examenes'].aggregate(pipeline))
        return jsonify([serialize_doc(r) for r in results]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exams_bp.route('/<int:id_examen>/results/file', methods=['POST'])
@token_required
@role_required('admin', 'estudios')
def upload_exam_file(id_examen):
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400
    result = ExamService.upload_exam_file(id_examen, file)
    if not result:
        return jsonify({'error': 'Error al subir archivo'}), 500
    return jsonify({'message': 'Archivo subido correctamente', 'file_url': result}), 200



@exams_bp.route('/<int:id_examen>/results/upload', methods=['POST'])
@token_required
@role_required('admin', 'estudios')
def upload_exam_results_multiple(id_examen):
    try:
        print("=== Inicio de upload_exam_results_multiple ===")
        print(f"id_examen: {id_examen}")

        exam_type = request.form.get('type')
        print(f"type: {exam_type}")

        if not exam_type or exam_type.upper() not in ('LABORATORIO', 'GABINETE'):
            return jsonify({'error': 'Tipo de examen no válido'}), 400

        files = request.files.getlist('archivos')
        print(f"Cantidad de archivos recibidos: {len(files)}")
        for f in files:
            print(f"Archivo: {f.filename}, tamaño: {f.content_length}, tipo: {f.content_type}")

        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'Debe seleccionar al menos un archivo'}), 400

        observaciones = request.form.get('observaciones', '')

        result = ExamService.upload_exam_results(
            id_examen, exam_type, files, observaciones
        )

        if not result:
            return jsonify({'error': 'No se pudo subir. Verifique que el examen exista y tenga detalles pendientes.'}), 400

        print("=== Subida exitosa ===")
        return jsonify({'message': 'Resultados subidos correctamente'}), 200

    except Exception as e:
        print(f"Error en upload_exam_results: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    


@exams_bp.route('/<int:id_examen>/info', methods=['GET'])
@token_required
def get_exam_info(id_examen):
    try:
        db = get_db()
        pipeline = [
            {"$match": {"id_examen": id_examen}},
            {"$lookup": {"from": "atencion", "localField": "id_atencion", "foreignField": "id_atencion", "as": "atencion"}},
            {"$unwind": "$atencion"},
            {"$lookup": {"from": "pacientes", "localField": "atencion.Id_exp", "foreignField": "Id_exp", "as": "paciente"}},
            {"$unwind": "$paciente"},
            {"$lookup": {"from": "camas", "localField": "atencion.id_cama", "foreignField": "id_cama", "as": "cama"}},
            {"$unwind": {"path": "$cama", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {"from": "examenes_det", "localField": "id_examen", "foreignField": "id_examen", "as": "det"}},
            {"$unwind": "$det"},
            {"$lookup": {"from": "catalogo_examenes", "localField": "det.id_catalogo", "foreignField": "id_catalogo", "as": "cat"}},
            {"$unwind": "$cat"},
            {"$group": {
                "_id": "$id_examen",
                "paciente": {"$first": {"$concat": ["$paciente.nom_pac", " ", "$paciente.papell", " ", "$paciente.sapell"]}},
                "habitacion": {"$first": "$cama.numero"},
                "estudios": {"$push": "$cat.nombre"}
            }},
            {"$project": {
                "id_examen": "$_id",
                "paciente": 1,
                "habitacion": 1,
                "estudios": {
                    "$reduce": {
                        "input": "$estudios",
                        "initialValue": "",
                        "in": {"$concat": ["$$value", {"$cond": [{"$eq": ["$$value", ""]}, "", ", "]}, "$$this"]}
                    }
                }
            }}
        ]
        results = list(db['examenes'].aggregate(pipeline))
        if not results:
            return jsonify({'error': 'Solicitud no encontrada'}), 404
        return jsonify(results[0]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# ===================================================================
#  EDITAR RESULTADOS (móvil)
# ===================================================================
@exams_bp.route('/<int:id_examen>/edit-info', methods=['GET'])
@token_required
@role_required('admin', 'estudios')
def get_exam_edit_info(id_examen):
    try:
        tipo = request.args.get('type')
        if not tipo or tipo.upper() not in ('LABORATORIO', 'GABINETE'):
            return jsonify({'error': 'Tipo de examen no válido'}), 400
        info = ExamService.get_edit_info(id_examen, tipo.upper())
        if not info:
            return jsonify({'error': 'Examen no encontrado'}), 404
        return jsonify(info), 200
    except Exception as e:
        print(f"Error en get_exam_edit_info: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@exams_bp.route('/<int:id_examen>/edit', methods=['PUT'])
@token_required
@role_required('admin', 'estudios')
def update_exam_results_edit(id_examen):
    try:
        exam_type = request.form.get('type')
        if not exam_type or exam_type.upper() not in ('LABORATORIO', 'GABINETE'):
            return jsonify({'error': 'Tipo de examen no válido'}), 400

        files = request.files.getlist('archivos')
        eliminar = request.form.getlist('eliminar_archivos')
        observaciones = request.form.get('observaciones', '')

        result = ExamService.update_edit(id_examen, exam_type, files, eliminar, observaciones)
        if not result:
            return jsonify({'error': 'Error al actualizar'}), 400
        return jsonify({'message': 'Actualizado correctamente'}), 200
    except Exception as e:
        print(f"Error en update_exam_results_edit: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    

@exams_bp.route('/<int:id_examen>/files', methods=['GET'])
@token_required
@role_required('admin', 'estudios')
def get_exam_files(id_examen):
    try:
        tipo = request.args.get('type')
        if not tipo or tipo.upper() not in ('LABORATORIO', 'GABINETE'):
            return jsonify({'error': 'Tipo de examen no válido'}), 400
        files = ExamService.get_files(id_examen, tipo.upper())
        return jsonify(files), 200
    except Exception as e:
        print(f"Error en get_exam_files: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    

# ===================================================================
#  ELIMINAR RESULTADOS (LABORATORIO / GABINETE)
# ===================================================================
@exams_bp.route('/<int:id_examen>/results', methods=['DELETE'])
@token_required
@role_required('admin', 'estudios')
def delete_exam_results(id_examen):
    """
    Elimina los resultados (archivos y registros) de un examen completo.
    Se espera el tipo ('LABORATORIO' o 'GABINETE') en los query params.
    """
    try:
        exam_type = request.args.get('type', '').upper()
        if exam_type not in ('LABORATORIO', 'GABINETE'):
            return jsonify({'error': 'Tipo de examen no válido'}), 400

        result = ExamService.delete_exam_results(id_examen, exam_type)
        if not result:
            return jsonify({'error': 'No se encontraron resultados para eliminar'}), 404

        return jsonify({'message': f'Resultados de {exam_type.lower()} eliminados correctamente'}), 200
    except Exception as e:
        print(f"Error en delete_exam_results: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------


@exams_bp.route('/download/<filename>', methods=['GET'])
@token_required
@role_required('admin', 'estudios')
def download_exam_file(filename):
    """
    Descarga un archivo de resultados.
    Se espera el parámetro 'tipo' en la query string: LABORATORIO o GABINETE.
    """
    tipo = request.args.get('tipo', '').upper()
    if tipo not in ('LABORATORIO', 'GABINETE'):
        abort(400, 'Tipo de examen no válido')

    # Carpeta base donde se guardan los archivos
    base_dir = os.path.join('static', 'resultados', tipo.lower())
    if not os.path.exists(base_dir):
        abort(404, 'Carpeta no encontrada')

    # Verificar que el archivo existe y está dentro de la carpeta permitida
    safe_path = os.path.join(base_dir, filename)
    if not os.path.isfile(safe_path):
        abort(404, 'Archivo no encontrado')

    # Servir el archivo con send_from_directory (evita path traversal)
    return send_from_directory(base_dir, filename, as_attachment=True)