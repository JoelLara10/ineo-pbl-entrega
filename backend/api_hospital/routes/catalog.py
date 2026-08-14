from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import token_required, role_required
from services.catalog_service import CatalogService

catalog_bp = Blueprint('catalog', __name__, url_prefix='/catalog')

# ==================== SERVICIOS ====================
@catalog_bp.route('/services', methods=['GET'])
@token_required
def get_services():
    """Obtiene catálogo de servicios"""
    servicios = CatalogService.get_services()
    return jsonify(servicios), 200

@catalog_bp.route('/services', methods=['POST'])
@token_required
@role_required('admin')
def create_service():
    """Crea un nuevo servicio"""
    data = request.get_json()
    
    required_fields = ['serv_cve', 'serv_desc', 'serv_costo', 'tipo']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    result, error = CatalogService.create_service(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(result), 201

@catalog_bp.route('/services/<int:id_serv>', methods=['PUT'])
@token_required
@role_required('admin')
def update_service(id_serv):
    """Actualiza un servicio"""
    data = request.get_json()
    
    result = CatalogService.update_service(id_serv, data)
    
    if not result:
        return jsonify({'error': 'Servicio no encontrado'}), 404
    
    return jsonify(result), 200

@catalog_bp.route('/services/<int:id_serv>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_service(id_serv):
    """Elimina un servicio"""
    result = CatalogService.delete_service(id_serv)
    
    if not result:
        return jsonify({'error': 'Servicio no encontrado'}), 404
    
    return jsonify({'message': 'Servicio eliminado correctamente'}), 200

# ==================== DIAGNÓSTICOS ====================
@catalog_bp.route('/diagnostics', methods=['GET'])
@token_required
def get_diagnostics():
    """Obtiene catálogo de diagnósticos"""
    diagnosticos = CatalogService.get_diagnostics()
    return jsonify(diagnosticos), 200

@catalog_bp.route('/diagnostics', methods=['POST'])
@token_required
@role_required('admin', 'medico')
def create_diagnostic():
    """Crea un nuevo diagnóstico"""
    data = request.get_json()
    
    if not data.get('diag') or not data.get('id_cie10'):
        return jsonify({'error': 'Diagnóstico y código CIE-10 son requeridos'}), 400
    
    result, error = CatalogService.create_diagnostic(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(result), 201

@catalog_bp.route('/diagnostics/<int:id_diag>', methods=['PUT'])
@token_required
@role_required('admin', 'medico')
def update_diagnostic(id_diag):
    """Actualiza un diagnóstico"""
    data = request.get_json()
    
    result = CatalogService.update_diagnostic(id_diag, data)
    
    if not result:
        return jsonify({'error': 'Diagnóstico no encontrado'}), 404
    
    return jsonify(result), 200

@catalog_bp.route('/diagnostics/<int:id_diag>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_diagnostic(id_diag):
    """Elimina un diagnóstico"""
    result = CatalogService.delete_diagnostic(id_diag)
    
    if not result:
        return jsonify({'error': 'Diagnóstico no encontrado'}), 404
    
    return jsonify({'message': 'Diagnóstico eliminado correctamente'}), 200