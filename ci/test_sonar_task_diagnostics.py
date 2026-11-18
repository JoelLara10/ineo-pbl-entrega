"""A diagnostic must never send the Sonar credential to another origin."""
import importlib.util
from pathlib import Path
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
