from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import token_required, role_required
from models.appointment import AppointmentModel
from services.medical_service import MedicalService

appointment_bp = Blueprint('appointment', __name__, url_prefix='/appointments')

@appointment_bp.route('', methods=['GET'])
@token_required
def get_appointments():
    """Obtiene atenciones activas"""
    area = request.args.get('area')
    
    appointments = AppointmentModel.get_active_by_area(area)
    return jsonify(appointments), 200

@appointment_bp.route('/<int:id_atencion>', methods=['GET'])
@token_required
def get_appointment(id_atencion):
    """Obtiene detalles de una atención"""
    appointment = AppointmentModel.find_by_id(id_atencion)
    
    if not appointment:
        return jsonify({'error': 'Atención no encontrada'}), 404
    
    return jsonify(appointment), 200

@appointment_bp.route('', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def create_appointment():
    """Crea una nueva atención"""
    data = request.get_json()
    
    required_fields = ['Id_exp', 'area']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    appointment, error = AppointmentModel.create(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(appointment), 201

@appointment_bp.route('/<int:id_atencion>', methods=['PUT'])
@token_required
@role_required('admin', 'administrativo', 'medico')
def update_appointment(id_atencion):
    """Actualiza una atención"""
    data = request.get_json()
    
    appointment = AppointmentModel.find_by_id(id_atencion)
    if not appointment:
        return jsonify({'error': 'Atención no encontrada'}), 404
    
    updated = AppointmentModel.update(id_atencion, data)
    return jsonify(updated), 200

@appointment_bp.route('/<int:id_atencion>/close', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def close_appointment(id_atencion):
    """Cierra una atención (alta)"""
    success, error = AppointmentModel.close(id_atencion, g.user['user_id'])
    
    if not success:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Atención cerrada exitosamente'}), 200

@appointment_bp.route('/<int:id_atencion>/billing', methods=['GET'])
@token_required
def get_appointment_billing(id_atencion):
    """Obtiene la cuenta de una atención"""
    billing = AppointmentModel.get_billing(id_atencion)
    return jsonify(billing), 200

@appointment_bp.route('/<int:id_atencion>/vital-signs', methods=['GET'])
@token_required
def get_vital_signs(id_atencion):
    """Obtiene signos vitales de una atención"""
    signs = MedicalService.get_vital_signs(id_atencion)
    return jsonify(signs), 200

@appointment_bp.route('/<int:id_atencion>/vital-signs', methods=['POST'])
@token_required
@role_required('admin', 'medico', 'enfermero')
def add_vital_signs(id_atencion):
    """Agrega signos vitales"""
    data = request.get_json()
    data['id_medico'] = g.user['user_id']
    
    result = MedicalService.add_vital_signs(id_atencion, data)
    
    if not result:
        return jsonify({'error': 'Error al registrar signos vitales'}), 500
    
    return jsonify(result), 201

@appointment_bp.route('/<int:id_atencion>/medical-notes', methods=['GET'])
@token_required
def get_medical_notes(id_atencion):
    """Obtiene notas médicas"""
    notes = MedicalService.get_medical_notes(id_atencion)
    return jsonify(notes), 200

@appointment_bp.route('/<int:id_atencion>/medical-notes', methods=['POST'])
@token_required
@role_required('admin', 'medico')
def add_medical_note(id_atencion):
    """Agrega nota médica"""
    data = request.get_json()
    
    required_fields = ['subjetivo', 'objetivo', 'analisis', 'plan']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    data['id_medico'] = g.user['user_id']
    result = MedicalService.add_medical_note(id_atencion, data)
    
    if not result:
        return jsonify({'error': 'Error al agregar nota médica'}), 500
    
    return jsonify(result), 201

@appointment_bp.route('/<int:id_atencion>/diagnosis', methods=['GET'])
@token_required
def get_diagnosis(id_atencion):
    """Obtiene diagnóstico actual"""
    diagnosis = MedicalService.get_current_diagnosis(id_atencion)
    return jsonify(diagnosis or {}), 200

@appointment_bp.route('/<int:id_atencion>/diagnosis', methods=['POST'])
@token_required
@role_required('admin', 'medico')
def add_diagnosis(id_atencion):
    """Agrega diagnóstico"""
    data = request.get_json()
    
    if not data.get('diagnostico_principal'):
        return jsonify({'error': 'Diagnóstico principal es requerido'}), 400
    
    result = MedicalService.add_diagnosis(id_atencion, data)
    
    if not result:
        return jsonify({'error': 'Error al agregar diagnóstico'}), 500
    
    return jsonify(result), 201

@appointment_bp.route('/<int:id_atencion>/prescriptions', methods=['GET'])
@token_required
def get_prescriptions(id_atencion):
    """Obtiene recetas médicas"""
    prescriptions = MedicalService.get_prescriptions(id_atencion)
    return jsonify(prescriptions), 200

@appointment_bp.route('/<int:id_atencion>/prescriptions', methods=['POST'])
@token_required
@role_required('admin', 'medico')
def add_prescription(id_atencion):
    """Agrega receta médica"""
    data = request.get_json()
    
    if not data.get('medicamentos') or len(data['medicamentos']) == 0:
        return jsonify({'error': 'Se requiere al menos un medicamento'}), 400
    
    data['id_medico'] = g.user['user_id']
    result = MedicalService.add_prescription(id_atencion, data)
    
    if not result:
        return jsonify({'error': 'Error al agregar receta'}), 500
    
    return jsonify(result), 201

@appointment_bp.route('/patient/<int:id_exp>', methods=['GET'])
@token_required
def get_patient_appointments(id_exp):
    """Obtiene todas las atenciones de un paciente"""
    appointments = AppointmentModel.find_by_patient(id_exp)
    return jsonify(appointments), 200

@appointment_bp.route('/patient/<int:id_exp>/active', methods=['GET'])
@token_required
def get_active_appointment(id_exp):
    """Obtiene atención activa de un paciente"""
    appointments = AppointmentModel.find_by_patient(id_exp, status='ABIERTA')
    return jsonify(appointments[0] if appointments else None), 200