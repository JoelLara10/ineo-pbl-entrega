from services.administrative_service import AdministrativeService


def test_close_and_reactivate_patient_moves_attention_between_states(isolated_database):
    isolated_database.counters.update_one(
        {'_id': 'atencion_id_atencion'},
        {'$set': {'seq': 8}},
        upsert=True,
    )

    created, error = AdministrativeService.create_patient({
        'curp': 'QA-REACTIVACION-0001',
        'papell': 'PRUEBA',
        'sapell': 'INEO',
        'nom_pac': 'PACIENTE SINTETICO',
        'fecnac': '2000-01-01',
        'area': 'Consulta',
        'motivo': 'Consulta',
        'especialidad': 'Oftalmologia',
    })
    assert error is None

    id_exp = created['rawPatient']['Id_exp']
    first_attention = created['activeAppointment']['id_atencion']
    # The display brand must not change the numeric patient identifier.
    assert AdministrativeService._record_label(id_exp) == f'OFTALCORE-{id_exp:06d}'
    assert created['activeAppointment']['status'] == 'ABIERTA'
    assert AdministrativeService.quick_search('QA-REACTIVACION')[0]['hasActiveAttention'] is True

    _, error = AdministrativeService.close_account(first_attention, 'usuario-qa')
    assert error is None
    assert AdministrativeService.get_patient_detail(id_exp)['activeAppointment'] is None
    assert AdministrativeService.quick_search('QA-REACTIVACION')[0]['hasActiveAttention'] is False

    closed_again, error = AdministrativeService.close_account(first_attention, 'usuario-qa')
    assert closed_again is None
    assert error == 'Atencion no encontrada o ya cerrada'

    reactivated, error = AdministrativeService.update_patient(id_exp, {
        'area': 'Consulta',
        'motivo': 'Consulta',
        'especialidad': 'Oftalmologia',
    })
    assert error is None
    new_attention = reactivated['activeAppointment']
    assert new_attention['status'] == 'ABIERTA'
    assert new_attention['id_atencion'] != first_attention
    assert AdministrativeService.quick_search('QA-REACTIVACION')[0]['hasActiveAttention'] is True
