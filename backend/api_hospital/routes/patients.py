from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import token_required, role_required
from models.patient import PatientModel
from services.patient_service import PatientService
from utils.database import serialize_doc

patients_bp = Blueprint('patients', __name__, url_prefix='/patients')

@patients_bp.route('', methods=['GET'])
@token_required
def get_patients():
    """Obtiene lista de pacientes paginada"""
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', 20)), 100)
    search = request.args.get('search', '')
    
    if search:
        result = PatientModel.search(search, page, page_size)
    else:
        result = PatientModel.get_all_active(page, page_size)
    
    return jsonify(result), 200

@patients_bp.route('/<int:id_exp>', methods=['GET'])
@token_required
def get_patient(id_exp):
    """Obtiene un paciente por ID"""
    patient = PatientModel.get_with_active_appointment(id_exp)
    
    if not patient:
        return jsonify({'error': 'Paciente no encontrado'}), 404
    
    return jsonify(patient), 200

@patients_bp.route('', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def create_patient():
    """Crea un nuevo paciente"""
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['curp', 'papell', 'nom_pac', 'fecnac']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    try:
        patient = PatientModel.create(data)
        return jsonify(patient), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:id_exp>', methods=['PUT'])
@token_required
@role_required('admin', 'administrativo', 'medico')
def update_patient(id_exp):
    """Actualiza un paciente"""
    data = request.get_json()
    
    patient = PatientModel.find_by_id(id_exp)
    if not patient:
        return jsonify({'error': 'Paciente no encontrado'}), 404
    
    try:
        updated = PatientModel.update(id_exp, data)
        return jsonify(updated), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:id_exp>/appointments', methods=['GET'])
@token_required
def get_patient_appointments(id_exp):
    """Obtiene todas las atenciones de un paciente"""
    from services.medical_service import MedicalService
    
    appointments = MedicalService.get_patient_appointments(id_exp)
    return jsonify(appointments), 200

@patients_bp.route('/<int:id_exp>/current-appointment', methods=['GET'])
@token_required
def get_current_appointment(id_exp):
    """Obtiene la atención activa del paciente"""
    from services.medical_service import MedicalService
    
    appointment = MedicalService.get_active_appointment(id_exp)
    return jsonify(appointment or {}), 200