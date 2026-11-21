"""A diagnostic must never send the Sonar credential to another origin."""
import importlib.util
import io
import json
from pathlib import Path
from urllib.parse import parse_qs
import pytest

spec = importlib.util.spec_from_file_location('sonar_diagnostics', Path(__file__).with_name('sonar_task_diagnostics.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('url', [
    'https://other.example/api/ce/task?id=test',
    'http://sonar.example/api/ce/task?id=test',
    'https://sonar.example:8443/api/ce/task?id=test',
    'https://sonar.example/another/path',
    'https://user@sonar.example/api/ce/task?id=test',
])
def test_rejects_other_origins_or_endpoints(url):
    with pytest.raises(ValueError):
        module.trusted_task_url('https://sonar.example', url)


def test_accepts_only_configured_task_origin():
    url = 'https://sonar.example/api/ce/task?id=test'
    assert module.trusted_task_url('https://sonar.example/', url) == url


def test_redirects_are_not_followed():
    assert module.NoRedirect().redirect_request(None, None, 302, 'Found', {}, 'https://other.example') is None


@pytest.mark.parametrize('visibility', ['public', 'private'])
def test_visibility_action_targets_only_authorized_project_and_verifies_response(monkeypatch, visibility):
    calls = []

    class Opener:
        def open(self, request, timeout):
            calls.append(request)
            assert timeout == 30
            if request.get_method() == 'POST':
                return io.BytesIO(b'')
            return io.BytesIO(json.dumps({'component': {'visibility': visibility}}).encode())

    monkeypatch.setattr(module, 'build_opener', lambda handler: Opener())
    if visibility == 'private':
        with pytest.raises(RuntimeError):
            module.make_project_public('https://sonar.example', 'fixture-' * 4)
    else:
        module.make_project_public('https://sonar.example', 'fixture-' * 4)
    assert len(calls) == 2
    assert calls[0].full_url == 'https://sonar.example/api/projects/update_visibility'
    assert parse_qs(calls[0].data.decode()) == {'project': ['jaimediaz25'], 'visibility': ['public']}
    assert calls[1].full_url == 'https://sonar.example/api/components/show?component=jaimediaz25'
