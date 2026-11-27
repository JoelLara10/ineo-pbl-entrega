from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest
from services.administrative_service import AdministrativeService as Admin


def payload(**changes):
    return {'curp': 'QA-ADMIN-UNICO', 'papell': 'PRUEBA', 'nom_pac': 'SINTETICO',
            'fecnac': '2000-01-01', 'area': 'Consulta', **changes}


@pytest.mark.parametrize('changes', [
    {'papell': '   '}, {'curp': 42}, {'fecnac': '2999-01-01'}, {'nom_pac': []},
])
def test_patient_rejects_invalid_input_without_writing(isolated_database, changes):
    before = isolated_database.pacientes.count_documents({})
    value, error = Admin.create_patient(payload(**changes))
    assert value is None and error
    assert isolated_database.pacientes.count_documents({}) == before


def test_duplicate_curp_and_occupied_bed_do_not_create_records(isolated_database):
    value, error = Admin.create_patient(payload(curp='sintetico-00000001'))
    assert value is None and error
    isolated_database.camas.update_one({'id_cama': 1}, {'$set': {'ocupada': 1}})
    before = isolated_database.pacientes.count_documents({})
    value, error = Admin.create_patient(payload(cama=1))
    assert value is None and error
    assert isolated_database.pacientes.count_documents({}) == before


@pytest.mark.parametrize('quantity', [0, -2, 1.5, 'bad'])
def test_invalid_charge_quantity_cannot_change_balance(isolated_database, quantity):
    result, error = Admin.add_charge(1, {'description': 'CARGO QA', 'price': 10, 'quantity': quantity})
    assert result is None and error
    assert isolated_database.cuenta_paciente.count_documents({}) == 0


def test_service_medicine_payment_and_close_lifecycle(isolated_database):
    isolated_database.cat_servicios.insert_one({'id_serv': 9, 'serv_desc': 'CONSULTA QA', 'serv_costo': 100})
    isolated_database.item.insert_one({'item_id': 45, 'item_name': 'MEDICAMENTO QA', 'item_price': 25})
    result, error = Admin.add_charge(1, {'id_serv': 9, 'quantity': 2})
    assert error is None and result['charges'][0]['descripcion'] == 'CONSULTA QA'
    result, error = Admin.add_charge(1, {'item_id': 45, 'quantity': 1})
    assert error is None and len(result['charges']) == 2
    before = result['balance']
    result, error = Admin.register_payment(1, {'amount': 50, 'method': 'Efectivo'}, 'qa')
    assert error is None and Decimal(str(result['balance'])) == Decimal(str(before)) - 50
    result, error = Admin.close_account(1, 'qa')
    assert error is None
    result, error = Admin.add_charge(1, {'description': 'NO GUARDAR', 'price': 1, 'quantity': 1})
    assert result is None and error
    result, error = Admin.register_payment(1, {'amount': 1}, 'qa')
    assert result is None and error


def test_recent_records_and_discharges_avoid_per_row_database_queries(isolated_database):
    for patient in isolated_database.pacientes.find({}):
        isolated_database.expedientes.insert_one({'id_exp': patient['Id_exp'], 'id_atencion': patient['Id_exp'], 'fecha_alta': datetime.now(), 'total_cuenta': 20})
    collection_type = type(isolated_database.pacientes)
    with patch.object(collection_type, 'find_one', side_effect=AssertionError('Consulta N+1')):
        groups = Admin.get_patient_groups()
    assert groups['summary']['expedientes'] == 8
    assert groups['summary']['altas'] == 8


def test_cash_cut_filter_income_matches_the_visible_movements(isolated_database):
    isolated_database.depositos_pserv.insert_many([
        {'id_atencion': 1, 'fecha': datetime.now(), 'deposito': 100, 'observaciones': 'COBRO VISIBLE'},
        {'id_atencion': 3, 'fecha': datetime.now(), 'deposito': 200, 'observaciones': 'OTRO COBRO'},
    ])
    result = Admin.get_cash_cut(search='COBRO VISIBLE')
    assert len(result['movements']) == 1
    assert result['summary']['income'] == 100


@pytest.mark.parametrize('path', ['/gestion-pacientes', '/censo', '/cuenta-pacientes', '/corte-caja', '/options', '/beds'])
def test_administrative_reads_require_authentication(client, path):
    assert client.get('/api/v1' + path).status_code == 401


@pytest.mark.parametrize('path', ['/gestion-pacientes', '/censo', '/cuenta-pacientes', '/corte-caja', '/options'])
def test_medical_role_cannot_read_administrative_data(client, path):
    from middleware.auth_middleware import generate_token
    token = generate_token('000000000000000000000002', 'medico.test', 'medico')
    assert client.get('/api/v1' + path, headers={'Authorization': 'Bearer ' + token}).status_code == 403


def test_admin_can_create_update_and_remove_a_synthetic_bed(client, isolated_database):
    from middleware.auth_middleware import generate_token
    token = generate_token('000000000000000000000001', 'admin.test', 'admin')
    headers = {'Authorization': 'Bearer ' + token}
    isolated_database.counters.update_one({'_id': 'camas_id_cama'}, {'$set': {'seq': 1}}, upsert=True)
    created = client.post('/api/v1/beds', headers=headers, json={'numero': 'QA-AUDIT-2', 'area': 'Consulta'})
    assert created.status_code == 201
    bed_id = created.get_json()['id_cama']
    assert client.put(f'/api/v1/beds/{bed_id}', headers=headers, json={'numero': 'QA-AUDIT-EDIT', 'area': 'Consulta'}).status_code == 200
    assert client.delete(f'/api/v1/beds/{bed_id}', headers=headers).status_code == 200
