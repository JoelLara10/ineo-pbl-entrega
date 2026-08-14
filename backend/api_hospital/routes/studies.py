from flask import Blueprint, request, jsonify, g, send_file
from middleware.auth_middleware import token_required, role_required
from services.study_service import StudyService
from werkzeug.utils import secure_filename
from utils.database import get_collection, get_db, serialize_doc
import os

studies_bp = Blueprint('studies', __name__, url_prefix='/studies')

# Configuración de uploads
UPLOAD_FOLDER_GAB = 'uploads/estudios/gabinete'
UPLOAD_FOLDER_LAB = 'uploads/estudios/laboratorio'
os.makedirs(UPLOAD_FOLDER_GAB, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_LAB, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@studies_bp.route('/counts', methods=['GET'])
@token_required
def get_study_counts():
    """Obtiene conteo de estudios pendientes"""
    try:
        db = get_db()
        
        # Obtener IDs de catálogo por tipo
        catalogo = list(db['catalogo_examenes'].find({}, {'id_catalogo': 1, 'tipo': 1}))
        
        lab_ids = [item['id_catalogo'] for item in catalogo if item.get('tipo') == 'LABORATORIO']
        gab_ids = [item['id_catalogo'] for item in catalogo if item.get('tipo') == 'GABINETE']
        
        lab_pending = db['examenes_det'].count_documents({
            'id_catalogo': {'$in': lab_ids},
            'estado': 'PENDIENTE'
        }) if lab_ids else 0
        
        gab_pending = db['examenes_det'].count_documents({
            'id_catalogo': {'$in': gab_ids},
            'estado': 'PENDIENTE'
        }) if gab_ids else 0
        
        return jsonify({
            'laboratorio': lab_pending,
            'gabinete': gab_pending,
            'total': lab_pending + gab_pending
        }), 200
        
    except Exception as e:
        return jsonify({'laboratorio': 0, 'gabinete': 0, 'total': 0}), 200
    
@studies_bp.route('/pending', methods=['GET'])
@token_required
def get_pending_studies():
    """Obtiene estudios pendientes por tipo"""
    study_type = request.args.get('type')  # LABORATORIO or GABINETE
    
    pending = StudyService.get_pending_studies(study_type)
    return jsonify(pending), 200

@studies_bp.route('/completed', methods=['GET'])
@token_required
def get_completed_studies():
    """Obtiene estudios completados por tipo"""
    study_type = request.args.get('type')
    
    completed = StudyService.get_completed_studies(study_type)
    return jsonify(completed), 200

@studies_bp.route('/<int:id_examen>', methods=['GET'])
@token_required
def get_study_details(id_examen):
    """Obtiene detalles de un estudio"""
    study = StudyService.get_study_details(id_examen)
    
    if not study:
        return jsonify({'error': 'Estudio no encontrado'}), 404
    
    return jsonify(study), 200

@studies_bp.route('/<int:id_examen>/upload', methods=['POST'])
@token_required
@role_required('admin', 'estudios')
def upload_results(id_examen):
    """Sube resultados de estudios"""
    if 'files' not in request.files:
        return jsonify({'error': 'No se enviaron archivos'}), 400
    
    files = request.files.getlist('files')
    observaciones = request.form.get('observaciones', '')
    
    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Determinar tipo de estudio
            study = StudyService.get_study_details(id_examen)
            if study and study.get('tipo'):
                folder = UPLOAD_FOLDER_GAB if study['tipo'] == 'GABINETE' else UPLOAD_FOLDER_LAB
                filepath = os.path.join(folder, f"{id_examen}_{filename}")
                file.save(filepath)
                uploaded_files.append(filepath)
    
    if uploaded_files:
        result = StudyService.save_results(id_examen, uploaded_files, observaciones)
        return jsonify({'message': 'Resultados guardados', 'files': uploaded_files}), 200
    
    return jsonify({'error': 'No se guardaron archivos'}), 400

@studies_bp.route('/<int:id_examen>/results', methods=['PUT'])
@token_required
@role_required('admin', 'estudios')
def update_results(id_examen):
    """Actualiza resultados de estudio"""
    data = request.get_json()
    
    result = StudyService.update_results(id_examen, data)
    
    if not result:
        return jsonify({'error': 'Estudio no encontrado'}), 404
    
    return jsonify({'message': 'Resultados actualizados'}), 200

@studies_bp.route('/<int:id_examen>/delete', methods=['DELETE'])
@token_required
@role_required('admin', 'estudios')
def delete_study(id_examen):
    """Elimina un estudio"""
    result = StudyService.delete_study(id_examen)
    
    if not result:
        return jsonify({'error': 'Estudio no encontrado'}), 404
    
    return jsonify({'message': 'Estudio eliminado'}), 200

@studies_bp.route('/file/<path:filename>', methods=['GET'])
@token_required
def get_study_file(filename):
    """Obtiene archivo de resultado"""
    # Buscar en ambas carpetas
    for folder in [UPLOAD_FOLDER_GAB, UPLOAD_FOLDER_LAB]:
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=False)
    
    return jsonify({'error': 'Archivo no encontrado'}), 404

@studies_bp.route('/counts', methods=['GET'])
@token_required
def get_pending_counts():
    """Obtiene conteo de estudios pendientes"""
    counts = StudyService.get_pending_counts()
    return jsonify(counts), 200