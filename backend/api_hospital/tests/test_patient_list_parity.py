from datetime import datetime
from unittest.mock import MagicMock

from services.administrative_service import AdministrativeService
from models.patient import PatientModel


def test_clinical_lists_return_stable_patient_and_bed_ids(client, monkeypatch):
    """Aggregation order must not change visible pages in either client."""
    from middleware.auth_middleware import generate_token

    db = {name: MagicMock() for name in ('atencion', 'camas')}
    db['atencion'].aggregate.return_value = [
        {'id_atencion': 11, 'Id_exp': 21}, {'id_atencion': 2, 'Id_exp': 20},
    ]
    db['camas'].aggregate.side_effect = [
        [{'id_cama': 10, 'estatus': 'LIBRE'}, {'id_cama': 2, 'estatus': 'OCUPADA', 'Id_exp': 20}],
        [{'id_cama': 7}, {'id_cama': 1}],
    ]
    monkeypatch.setattr('routes.medical.get_db', lambda: db)
    token = generate_token('000000000000000000000001', 'admin.test', 'admin')
    response = client.get('/api/v1/medico', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert [row['id_atencion'] for row in response.json['beds_consulta']] == [2, 11]
    assert [row['id_cama'] for row in response.json['beds_preparacion']] == [2, 10]
    assert [row['id_cama'] for row in response.json['beds_recuperacion']] == [1, 7]
    assert response.json['beds_preparacion'][0]['Id_exp'] == 20
    assert response.json['beds_preparacion'][1]['estatus'] == 'LIBRE'


def test_same_admission_time_has_same_order_in_management_census_and_accounts(isolated_database):
    db = isolated_database
    db.atencion.delete_many({})
    db.pacientes.delete_many({})
    date = datetime(2026, 10, 21, 10)
    for identifier in [40, 20, 30]:
        db.pacientes.insert_one({'Id_exp': identifier, 'nom_pac': f'Sintetico {identifier}', 'papell': 'Prueba', 'fecnac': datetime(2000, 1, 1)})
        db.atencion.insert_one({'id_atencion': identifier, 'Id_exp': identifier, 'area': 'Ambulatorio', 'status': 'ABIERTA', 'fecha_ing': date})
    groups = AdministrativeService.get_patient_groups()
    census = AdministrativeService.get_census()
    accounts = AdministrativeService.get_active_accounts()
    assert [row['id_atencion'] for row in groups['groups'][0]['patients']] == [40, 30, 20]
    assert [row['id_atencion'] for row in census['sections'][0]['data']] == [40, 30, 20]
    assert [row['id_atencion'] for row in accounts] == [40, 30, 20]


def test_patient_search_paginates_the_same_record_order_as_patient_lists(isolated_database):
    db = isolated_database
    db.pacientes.delete_many({})
    for identifier in [4, 9, 2, 7]:
        db.pacientes.insert_one({'Id_exp': identifier, 'nom_pac': 'Sintetico', 'papell': 'Prueba'})
    assert [p['Id_exp'] for p in PatientModel.search('Sintetico', 1, 2)['data']] == [9, 7]
    assert [p['Id_exp'] for p in PatientModel.search('Sintetico', 2, 2)['data']] == [4, 2]
    assert [p['Id_exp'] for p in PatientModel.get_all_active(1, 2)['data']] == [9, 7]
