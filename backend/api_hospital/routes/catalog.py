from flask import Blueprint, request, jsonify, g
import math
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
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Solicitud de servicio inválida'}), 400
    for field, limit in [('serv_cve', 40), ('serv_desc', 250)]:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
            return jsonify({'error': f'Campo inválido: {field}'}), 400
        data[field] = value.strip()
    data['serv_cve'] = data['serv_cve'].upper()
    try:
        for field in ['serv_costo', 'iva'] + [f'serv_costo{i}' for i in range(2, 9)]:
            value = data.get(field, 16 if field == 'iva' else 0)
            if field == 'serv_costo' and field not in data:
                raise ValueError()
            if value is None or isinstance(value, bool) or str(value).strip() == '':
                raise ValueError()
            number = float(value)
            if not math.isfinite(number) or number < 0 or (field == 'iva' and number > 100):
                raise ValueError()
            data[field] = number
        tipo = data.get('tipo')
        if isinstance(tipo, bool) or str(tipo) not in ('1', '2', '3', '4', '5'):
            raise ValueError()
        data['tipo'] = int(tipo)
    except (TypeError, ValueError, OverflowError):
        return jsonify({'error': 'Costo, IVA o tipo de servicio inválido'}), 400

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