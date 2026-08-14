from flask import Blueprint, request, jsonify
from middleware.auth_middleware import token_required, role_required
from services.bed_service import BedService

beds_bp = Blueprint('beds', __name__)

@beds_bp.route('/beds', methods=['OPTIONS'])
def beds_options():
    return '', 204

@beds_bp.route('/beds', methods=['GET'])
@token_required
def get_beds():
    area = request.args.get('area')
    status = request.args.get('status')
    
    beds = BedService.get_all_beds(area, status)
    return jsonify(beds), 200

@beds_bp.route('/beds', methods=['POST'])
@token_required
@role_required('admin')
def create_bed():
    data = request.get_json()
    
    required_fields = ['numero', 'area']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    result, error = BedService.create_bed(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(result), 201

@beds_bp.route('/beds/<int:id_cama>', methods=['PUT'])
@token_required
@role_required('admin')
def update_bed(id_cama):
    data = request.get_json()
    
    result = BedService.update_bed(id_cama, data)
    
    if not result:
        return jsonify({'error': 'Cama no encontrada'}), 404
    
    return jsonify(result), 200

@beds_bp.route('/beds/<int:id_cama>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_bed(id_cama):
    result, error = BedService.delete_bed(id_cama)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Cama eliminada correctamente'}), 200

@beds_bp.route('/beds/occupancy', methods=['GET'])
@token_required
def get_occupancy():
    occupancy = BedService.get_occupancy_report()
    return jsonify(occupancy), 200