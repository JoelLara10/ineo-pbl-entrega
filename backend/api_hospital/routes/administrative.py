from flask import Blueprint, jsonify, request, g

from middleware.auth_middleware import role_required, token_required
from services.administrative_service import AdministrativeService


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
mobile_admin_bp = Blueprint('mobile_admin', __name__)


def _json_body():
    return request.get_json(silent=True) or {}


def _pagination_params():
    fetch_all = request.args.get('all', default='false').lower() in (
        '1',
        'true',
        'yes',
        'si',
    )

    if fetch_all:
        return 1, None

    page = max(request.args.get('page', default=1, type=int), 1)
    limit = min(max(request.args.get('limit', default=5, type=int), 1), 50)
    return page, limit


def _pagination_meta(total, page, limit):
    if limit is None:
        return {
            'page': 1,
            'limit': total,
            'total': total,
            'total_pages': 1,
            'has_more': False,
            'all': True,
        }

    start = (page - 1) * limit
    end = start + limit

    return {
        'page': page,
        'limit': limit,
        'total': total,
        'total_pages': (total + limit - 1) // limit if limit else 1,
        'has_more': end < total,
    }


def _paginate_list(items, page, limit):
    items = items or []
    total = len(items)

    if limit is None:
        return items, _pagination_meta(total, 1, None)

    start = (page - 1) * limit
    end = start + limit

    return items[start:end], _pagination_meta(total, page, limit)


def _paginate_patient_groups(response, page, limit):
    if not isinstance(response, dict):
        paginated_items, pagination = _paginate_list(response, page, limit)

        return {
            'data': paginated_items,
            'pagination': pagination,
        }

    groups = response.get('groups', []) or []
    paginated_groups = []

    for group in groups:
        patients = group.get('patients', []) or []
        paginated_patients, pagination = _paginate_list(patients, page, limit)

        paginated_groups.append({
            **group,
            'patients': paginated_patients,
            'pagination': pagination,
        })

    return {
        **response,
        'groups': paginated_groups,
        'pagination': {
            'page': page,
            'limit': limit,
        },
    }


def _paginate_census_sections(response, page, limit):
    if not isinstance(response, dict):
        paginated_items, pagination = _paginate_list(response, page, limit)

        return {
            'data': paginated_items,
            'pagination': pagination,
        }

    sections = response.get('sections', []) or []
    paginated_sections = []

    for section in sections:
        patients = section.get('data', []) or []
        paginated_patients, pagination = _paginate_list(patients, page, limit)

        paginated_sections.append({
            **section,
            'data': paginated_patients,
            'pagination': pagination,
        })

    return {
        **response,
        'sections': paginated_sections,
        'pagination': {
            'page': page,
            'limit': limit,
        },
    }


def _paginate_response(response, page, limit, possible_keys=None):
    possible_keys = possible_keys or [
        'data',
        'items',
        'patients',
        'accounts',
        'activeAccounts',
        'census',
        'records',
        'rows',
        'results',
        'movements',
        'charges',
        'payments',
        'cash_cut',
        'corte_caja',
        'beds',
        'camas',
    ]

    if isinstance(response, list):
        paginated_items, pagination = _paginate_list(response, page, limit)

        return {
            'data': paginated_items,
            'pagination': pagination,
        }

    if not isinstance(response, dict):
        return response

    paginated_response = {
        **response,
        'pagination': {
            'page': page,
            'limit': limit,
        },
    }

    found_list = False

    for key in possible_keys:
        if key in response and isinstance(response.get(key), list):
            paginated_items, pagination = _paginate_list(
                response.get(key),
                page,
                limit
            )

            paginated_response[key] = paginated_items
            paginated_response[f'{key}_pagination'] = pagination
            found_list = True

    if not found_list:
        return response

    return paginated_response


def _options_response():
    current_id_cama = request.args.get('current_id_cama', type=int)
    page, limit = _pagination_params()

    response = AdministrativeService.get_options(current_id_cama)

    return jsonify(
        _paginate_response(
            response,
            page,
            limit,
            possible_keys=[
                'beds',
                'camas',
            ],
        )
    ), 200


def _patients_response():
    search = request.args.get('search', '')
    page, limit = _pagination_params()

    response = AdministrativeService.get_patient_groups(search)

    return jsonify(
        _paginate_patient_groups(response, page, limit)
    ), 200


def _patient_detail_response(id_exp):
    patient = AdministrativeService.get_patient_detail(id_exp)

    if not patient:
        return jsonify({'error': 'Paciente no encontrado'}), 404

    return jsonify(patient), 200


def _create_patient_response():
    result, error = AdministrativeService.create_patient(_json_body())

    if error:
        return jsonify({'error': error}), 400

    return jsonify(result), 201


def _update_patient_response(id_exp):
    result, error = AdministrativeService.update_patient(id_exp, _json_body())

    if error:
        return jsonify({'error': error}), 400

    return jsonify(result), 200


def _census_response():
    search = request.args.get('search', '')
    page, limit = _pagination_params()

    response = AdministrativeService.get_census(search)

    return jsonify(
        _paginate_census_sections(response, page, limit)
    ), 200


def _cash_cut_response():
    date_value = request.args.get('date')
    search = request.args.get('search', '')
    page, limit = _pagination_params()

    response = AdministrativeService.get_cash_cut(date_value, search)

    return jsonify(
        _paginate_response(
            response,
            page,
            limit,
            possible_keys=[
                'data',
                'items',
                'records',
                'rows',
                'results',
                'movements',
                'activeAccounts',
                'accounts',
                'charges',
                'payments',
                'cash_cut',
                'corte_caja',
            ],
        )
    ), 200


def _accounts_response():
    search = request.args.get('search', '')
    page, limit = _pagination_params()

    response = AdministrativeService.get_active_accounts(search)

    return jsonify(
        _paginate_response(
            response,
            page,
            limit,
            possible_keys=[
                'data',
                'items',
                'accounts',
                'activeAccounts',
                'patients',
                'records',
                'rows',
                'results',
            ],
        )
    ), 200


def _account_detail_response(id_atencion):
    account = AdministrativeService.get_account_detail(id_atencion)

    if not account:
        return jsonify({'error': 'Cuenta no encontrada'}), 404

    return jsonify(account), 200


def _account_documents_response(id_atencion):
    account = AdministrativeService.get_account_detail(id_atencion)

    if not account:
        return jsonify({'error': 'Cuenta no encontrada'}), 404

    return jsonify(account.get('documents', [])), 200


def _add_charge_response(id_atencion):
    result, error = AdministrativeService.add_charge(id_atencion, _json_body())

    if error:
        return jsonify({'error': error}), 400

    return jsonify(result), 201


def _remove_charge_response(id_atencion, charge_id):
    if not AdministrativeService.remove_charge(id_atencion, charge_id):
        return jsonify({'error': 'Cargo no encontrado'}), 404

    return jsonify({'message': 'Cargo eliminado correctamente'}), 200


def _register_payment_response(id_atencion):
    result, error = AdministrativeService.register_payment(
        id_atencion,
        _json_body(),
        g.user['user_id']
    )

    if error:
        return jsonify({'error': error}), 400

    return jsonify(result), 201


@admin_bp.route('/options', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_admin_options():
    return _options_response()


@admin_bp.route('/gestion-pacientes', methods=['GET'])
@admin_bp.route('/gestion_pacientes', methods=['GET'])
@admin_bp.route('/patients', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_admin_patients():
    return _patients_response()


@admin_bp.route('/patients/search', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def search_admin_patients():
    query = request.args.get('q', request.args.get('search', ''))
    limit = min(request.args.get('limit', default=10, type=int), 50)

    return jsonify(AdministrativeService.quick_search(query, limit)), 200


@admin_bp.route('/gestion-pacientes/<int:id_exp>', methods=['GET'])
@admin_bp.route('/gestion_pacientes/<int:id_exp>', methods=['GET'])
@admin_bp.route('/patients/<int:id_exp>', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_admin_patient(id_exp):
    return _patient_detail_response(id_exp)


@admin_bp.route('/gestion-pacientes', methods=['POST'])
@admin_bp.route('/gestion_pacientes', methods=['POST'])
@admin_bp.route('/patients', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def create_admin_patient():
    return _create_patient_response()


@admin_bp.route('/gestion-pacientes/<int:id_exp>', methods=['PUT'])
@admin_bp.route('/gestion_pacientes/<int:id_exp>', methods=['PUT'])
@admin_bp.route('/patients/<int:id_exp>', methods=['PUT'])
@token_required
@role_required('admin', 'administrativo')
def update_admin_patient(id_exp):
    return _update_patient_response(id_exp)


@admin_bp.route('/documents/patients', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_admin_documents_patients():
    return jsonify(AdministrativeService.get_documents_patients()), 200


@admin_bp.route('/census', methods=['GET'])
@admin_bp.route('/censo', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_admin_census():
    return _census_response()


@admin_bp.route('/cash-cut', methods=['GET'])
@admin_bp.route('/corte-caja', methods=['GET'])
@admin_bp.route('/corte_caja', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_admin_cash_cut():
    return _cash_cut_response()


@admin_bp.route('/accounts', methods=['GET'])
@admin_bp.route('/cuenta-pacientes', methods=['GET'])
@admin_bp.route('/cuenta_pacientes', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_admin_accounts():
    return _accounts_response()


@admin_bp.route('/accounts/<int:id_atencion>', methods=['GET'])
@admin_bp.route('/cuenta-pacientes/<int:id_atencion>', methods=['GET'])
@admin_bp.route('/cuenta_pacientes/<int:id_atencion>', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_admin_account(id_atencion):
    return _account_detail_response(id_atencion)


@admin_bp.route('/accounts/<int:id_atencion>/documents', methods=['GET'])
@admin_bp.route('/cuenta-pacientes/<int:id_atencion>/documents', methods=['GET'])
@admin_bp.route('/cuenta_pacientes/<int:id_atencion>/documents', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_admin_account_documents(id_atencion):
    return _account_documents_response(id_atencion)


@admin_bp.route('/accounts/<int:id_atencion>/charges', methods=['POST'])
@admin_bp.route('/cuenta-pacientes/<int:id_atencion>/charges', methods=['POST'])
@admin_bp.route('/cuenta-pacientes/<int:id_atencion>/cargos', methods=['POST'])
@admin_bp.route('/cuenta_pacientes/<int:id_atencion>/charges', methods=['POST'])
@admin_bp.route('/cuenta_pacientes/<int:id_atencion>/cargos', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def add_admin_charge(id_atencion):
    return _add_charge_response(id_atencion)


@admin_bp.route('/accounts/<int:id_atencion>/charges/<charge_id>', methods=['DELETE'])
@admin_bp.route('/cuenta-pacientes/<int:id_atencion>/charges/<charge_id>', methods=['DELETE'])
@admin_bp.route('/cuenta-pacientes/<int:id_atencion>/cargos/<charge_id>', methods=['DELETE'])
@admin_bp.route('/cuenta_pacientes/<int:id_atencion>/charges/<charge_id>', methods=['DELETE'])
@admin_bp.route('/cuenta_pacientes/<int:id_atencion>/cargos/<charge_id>', methods=['DELETE'])
@token_required
@role_required('admin', 'administrativo')
def remove_admin_charge(id_atencion, charge_id):
    return _remove_charge_response(id_atencion, charge_id)


@admin_bp.route('/accounts/<int:id_atencion>/payments', methods=['POST'])
@admin_bp.route('/cuenta-pacientes/<int:id_atencion>/payments', methods=['POST'])
@admin_bp.route('/cuenta-pacientes/<int:id_atencion>/pagos', methods=['POST'])
@admin_bp.route('/cuenta_pacientes/<int:id_atencion>/payments', methods=['POST'])
@admin_bp.route('/cuenta_pacientes/<int:id_atencion>/pagos', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def register_admin_payment(id_atencion):
    return _register_payment_response(id_atencion)


def _close_account_response(id_atencion):
    result, error = AdministrativeService.close_account(
        id_atencion,
        g.user['user_id']
    )

    if error:
        return jsonify({'error': error}), 400

    return jsonify({
        'message': 'Cuenta cerrada exitosamente',
        'account': result,
    }), 200


@admin_bp.route('/accounts/<int:id_atencion>/close', methods=['POST'])
@admin_bp.route('/cuenta-pacientes/<int:id_atencion>/close', methods=['POST'])
@admin_bp.route('/cuenta-pacientes/<int:id_atencion>/cerrar', methods=['POST'])
@admin_bp.route('/cuenta_pacientes/<int:id_atencion>/close', methods=['POST'])
@admin_bp.route('/cuenta_pacientes/<int:id_atencion>/cerrar', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def close_admin_account(id_atencion):
    return _close_account_response(id_atencion)


@admin_bp.route('/cerrar-cuenta/<int:id_atencion>', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def close_admin_account_alias(id_atencion):
    return _close_account_response(id_atencion)


@mobile_admin_bp.route('/options', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_options():
    return _options_response()


@mobile_admin_bp.route('/admin-options', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_admin_options():
    return _options_response()


@mobile_admin_bp.route('/admin-patients', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_admin_patients():
    return _patients_response()


@mobile_admin_bp.route('/patients-admin', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_patients_admin():
    return _patients_response()


@mobile_admin_bp.route('/gestion-pacientes', methods=['GET'])
@mobile_admin_bp.route('/gestion_pacientes', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_patient_management():
    return _patients_response()


@mobile_admin_bp.route('/gestion-pacientes/search', methods=['GET'])
@mobile_admin_bp.route('/gestion_pacientes/search', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def search_mobile_patient_management():
    query = request.args.get('q', request.args.get('search', ''))
    limit = min(request.args.get('limit', default=10, type=int), 50)

    return jsonify(AdministrativeService.quick_search(query, limit)), 200


@mobile_admin_bp.route('/gestion-pacientes/<int:id_exp>', methods=['GET'])
@mobile_admin_bp.route('/gestion_pacientes/<int:id_exp>', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_patient_detail(id_exp):
    return _patient_detail_response(id_exp)


@mobile_admin_bp.route('/gestion-pacientes', methods=['POST'])
@mobile_admin_bp.route('/gestion_pacientes', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def create_mobile_patient():
    return _create_patient_response()


@mobile_admin_bp.route('/gestion-pacientes/<int:id_exp>', methods=['PUT'])
@mobile_admin_bp.route('/gestion_pacientes/<int:id_exp>', methods=['PUT'])
@token_required
@role_required('admin', 'administrativo')
def update_mobile_patient(id_exp):
    return _update_patient_response(id_exp)


@mobile_admin_bp.route('/census', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_census():
    return _census_response()


@mobile_admin_bp.route('/censo', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_censo():
    return _census_response()


@mobile_admin_bp.route('/cash-cut', methods=['GET'])
@mobile_admin_bp.route('/cash_drawer', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_cash_cut():
    return _cash_cut_response()


@mobile_admin_bp.route('/corte-caja', methods=['GET'])
@mobile_admin_bp.route('/corte_caja', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_corte_caja():
    return _cash_cut_response()


@mobile_admin_bp.route('/accounts', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_accounts():
    return _accounts_response()


@mobile_admin_bp.route('/cuenta-pacientes', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_patient_accounts():
    return _accounts_response()


@mobile_admin_bp.route('/cuenta_pacientes', methods=['GET'])
@mobile_admin_bp.route('/cuenta-paciente', methods=['GET'])
@mobile_admin_bp.route('/cuenta_paciente', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_patient_accounts_alias():
    return _accounts_response()


@mobile_admin_bp.route('/accounts/<int:id_atencion>', methods=['GET'])
@mobile_admin_bp.route('/cuenta-pacientes/<int:id_atencion>', methods=['GET'])
@mobile_admin_bp.route('/cuenta_pacientes/<int:id_atencion>', methods=['GET'])
@mobile_admin_bp.route('/cuenta-paciente/<int:id_atencion>', methods=['GET'])
@mobile_admin_bp.route('/cuenta_paciente/<int:id_atencion>', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_account(id_atencion):
    return _account_detail_response(id_atencion)


@mobile_admin_bp.route('/accounts/<int:id_atencion>/documents', methods=['GET'])
@mobile_admin_bp.route('/cuenta-pacientes/<int:id_atencion>/documents', methods=['GET'])
@mobile_admin_bp.route('/cuenta_pacientes/<int:id_atencion>/documents', methods=['GET'])
@mobile_admin_bp.route('/cuenta-paciente/<int:id_atencion>/documents', methods=['GET'])
@mobile_admin_bp.route('/cuenta_paciente/<int:id_atencion>/documents', methods=['GET'])
@token_required
@role_required('admin', 'administrativo')
def get_mobile_account_documents(id_atencion):
    return _account_documents_response(id_atencion)


@mobile_admin_bp.route('/accounts/<int:id_atencion>/charges', methods=['POST'])
@mobile_admin_bp.route('/cuenta-pacientes/<int:id_atencion>/charges', methods=['POST'])
@mobile_admin_bp.route('/cuenta-pacientes/<int:id_atencion>/cargos', methods=['POST'])
@mobile_admin_bp.route('/cuenta_pacientes/<int:id_atencion>/charges', methods=['POST'])
@mobile_admin_bp.route('/cuenta_pacientes/<int:id_atencion>/cargos', methods=['POST'])
@mobile_admin_bp.route('/cuenta-paciente/<int:id_atencion>/charges', methods=['POST'])
@mobile_admin_bp.route('/cuenta-paciente/<int:id_atencion>/cargos', methods=['POST'])
@mobile_admin_bp.route('/cuenta_paciente/<int:id_atencion>/charges', methods=['POST'])
@mobile_admin_bp.route('/cuenta_paciente/<int:id_atencion>/cargos', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def add_mobile_charge(id_atencion):
    return _add_charge_response(id_atencion)


@mobile_admin_bp.route('/accounts/<int:id_atencion>/charges/<charge_id>', methods=['DELETE'])
@mobile_admin_bp.route('/cuenta-pacientes/<int:id_atencion>/charges/<charge_id>', methods=['DELETE'])
@mobile_admin_bp.route('/cuenta-pacientes/<int:id_atencion>/cargos/<charge_id>', methods=['DELETE'])
@mobile_admin_bp.route('/cuenta_pacientes/<int:id_atencion>/charges/<charge_id>', methods=['DELETE'])
@mobile_admin_bp.route('/cuenta_pacientes/<int:id_atencion>/cargos/<charge_id>', methods=['DELETE'])
@mobile_admin_bp.route('/cuenta-paciente/<int:id_atencion>/charges/<charge_id>', methods=['DELETE'])
@mobile_admin_bp.route('/cuenta-paciente/<int:id_atencion>/cargos/<charge_id>', methods=['DELETE'])
@mobile_admin_bp.route('/cuenta_paciente/<int:id_atencion>/charges/<charge_id>', methods=['DELETE'])
@mobile_admin_bp.route('/cuenta_paciente/<int:id_atencion>/cargos/<charge_id>', methods=['DELETE'])
@token_required
@role_required('admin', 'administrativo')
def remove_mobile_charge(id_atencion, charge_id):
    return _remove_charge_response(id_atencion, charge_id)


@mobile_admin_bp.route('/accounts/<int:id_atencion>/payments', methods=['POST'])
@mobile_admin_bp.route('/cuenta-pacientes/<int:id_atencion>/payments', methods=['POST'])
@mobile_admin_bp.route('/cuenta-pacientes/<int:id_atencion>/pagos', methods=['POST'])
@mobile_admin_bp.route('/cuenta_pacientes/<int:id_atencion>/payments', methods=['POST'])
@mobile_admin_bp.route('/cuenta_pacientes/<int:id_atencion>/pagos', methods=['POST'])
@mobile_admin_bp.route('/cuenta-paciente/<int:id_atencion>/payments', methods=['POST'])
@mobile_admin_bp.route('/cuenta-paciente/<int:id_atencion>/pagos', methods=['POST'])
@mobile_admin_bp.route('/cuenta_paciente/<int:id_atencion>/payments', methods=['POST'])
@mobile_admin_bp.route('/cuenta_paciente/<int:id_atencion>/pagos', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def register_mobile_payment(id_atencion):
    return _register_payment_response(id_atencion)


@mobile_admin_bp.route('/accounts/<int:id_atencion>/close', methods=['POST'])
@mobile_admin_bp.route('/cuenta-pacientes/<int:id_atencion>/close', methods=['POST'])
@mobile_admin_bp.route('/cuenta-pacientes/<int:id_atencion>/cerrar', methods=['POST'])
@mobile_admin_bp.route('/cuenta_pacientes/<int:id_atencion>/close', methods=['POST'])
@mobile_admin_bp.route('/cuenta_pacientes/<int:id_atencion>/cerrar', methods=['POST'])
@mobile_admin_bp.route('/cuenta-paciente/<int:id_atencion>/close', methods=['POST'])
@mobile_admin_bp.route('/cuenta-paciente/<int:id_atencion>/cerrar', methods=['POST'])
@mobile_admin_bp.route('/cuenta_paciente/<int:id_atencion>/close', methods=['POST'])
@mobile_admin_bp.route('/cuenta_paciente/<int:id_atencion>/cerrar', methods=['POST'])
@mobile_admin_bp.route('/cerrar-cuenta/<int:id_atencion>', methods=['POST'])
@token_required
@role_required('admin', 'administrativo')
def close_mobile_account(id_atencion):
    return _close_account_response(id_atencion)
