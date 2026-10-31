"""Regression checks for the paths and disclosure reported by CodeQL."""
import logging

import pytest

from middleware.auth_middleware import generate_token
from utils.safe_files import confined_file


def admin_headers():
    return {'Authorization': 'Bearer ' + generate_token(
        '000000000000000000000001', 'admin.test', 'admin')}


@pytest.mark.parametrize('name', ['../outside.txt', '..\\outside.txt', '/absolute.txt',
                                  'C:outside.txt', '.', '..', '', 'folder/file.pdf'])
def test_file_paths_reject_traversal_before_io(tmp_path, name):
    with pytest.raises(ValueError):
        confined_file(tmp_path, name)


def test_confined_file_keeps_valid_names_and_contents(tmp_path):
    path = confined_file(tmp_path, 'informe_clinico.pdf')
    path.write_bytes(b'resultado sintetico')
    assert confined_file(tmp_path, path.name).read_bytes() == b'resultado sintetico'


def test_confined_file_rejects_symlinks(tmp_path):
    outside = tmp_path / 'outside'
    outside.write_text('privado')
    folder = tmp_path / 'uploads'
    folder.mkdir()
    link = folder / 'informe.pdf'
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip('This Windows account cannot create symlinks; Linux CI verifies it')
    with pytest.raises(ValueError):
        confined_file(folder, link.name)


def test_study_download_rejects_escape_and_serves_valid_file(client, monkeypatch, tmp_path):
    from routes import studies
    folder = tmp_path / 'studies'
    folder.mkdir()
    (folder / 'informe.pdf').write_bytes(b'resultado sintetico')
    (tmp_path / 'outside.txt').write_text('privado')
    monkeypatch.setattr(studies, 'UPLOAD_FOLDER_GAB', str(folder))
    monkeypatch.setattr(studies, 'UPLOAD_FOLDER_LAB', str(folder))
    headers = admin_headers()
    good = client.get('/api/v1/file/informe.pdf', headers=headers)
    assert good.status_code == 200
    assert good.data == b'resultado sintetico'
    bad = client.get('/api/v1/file/../outside.txt', headers=headers)
    assert bad.status_code == 404
    assert b'privado' not in bad.data


@pytest.mark.parametrize('route,target', [
    ('/api/v1/dashboard', 'routes.analytics.get_db'),
    ('/api/v1/exams/catalog', 'routes.exams.get_db'),
    ('/api/v1/medico', 'routes.medical.get_db'),
])
def test_internal_database_errors_are_not_sent_to_browser(client, monkeypatch, route, target):
    def unavailable():
        raise RuntimeError('private-database-host /private/server/path')
    monkeypatch.setattr(target, unavailable)
    response = client.get(route, headers=admin_headers())
    assert response.status_code == 500
    assert response.json == {'error': 'Error interno del servidor'}
    assert b'private-database-host' not in response.data


def test_backup_errors_do_not_disclose_os_details(client, monkeypatch):
    def unavailable(**_kwargs):
        raise OSError('/private/server/path')
    monkeypatch.setattr('routes.backup.realizar_backup', unavailable)
    response = client.post('/api/v1/backup/create', headers=admin_headers(), json={})
    assert response.status_code == 400
    assert b'/private/server/path' not in response.data


def test_exam_edit_cannot_delete_files_not_owned_by_exam(isolated_database, monkeypatch, tmp_path):
    from services.exam_service import ExamService
    monkeypatch.chdir(tmp_path)
    folder = tmp_path / 'static/resultados/laboratorio'
    folder.mkdir(parents=True)
    foreign = folder / 'otro_examen.pdf'
    foreign.write_bytes(b'conservar')
    isolated_database.examenes_det.insert_one({
        'id_examen': 101, 'id_catalogo': 1, 'archivo_resultado': 'propio.pdf'})
    monkeypatch.setattr(ExamService, '_get_catalog_ids_by_type', lambda _kind: [1])
    ExamService.update_edit(101, 'LABORATORIO', [], ['otro_examen.pdf', '../outside.txt'], '')
    assert foreign.read_bytes() == b'conservar'
    assert isolated_database.examenes_det.find_one({'id_examen': 101})['archivo_resultado'] == 'propio.pdf'


def test_request_log_does_not_interpolate_untrusted_url_or_username(app, caplog):
    from flask import g
    from utils.helpers import log_request
    @log_request
    def sample_handler():
        return 'ok'
    with app.test_request_context('/path%0Aforged-log'):
        g.user = {'username': 'name\nforged-log'}
        with caplog.at_level(logging.INFO, logger='utils.helpers'):
            assert sample_handler() == 'ok'
    assert 'Request handler=sample_handler' in caplog.text
    assert 'forged-log' not in caplog.text
