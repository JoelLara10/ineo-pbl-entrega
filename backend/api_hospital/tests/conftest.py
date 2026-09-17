from copy import deepcopy
import json
from pathlib import Path

import pytest


@pytest.fixture()
def app(monkeypatch):
    """Crea la aplicación Flask sin iniciar tareas programadas."""
    import app as app_module

    monkeypatch.setattr(app_module, "init_scheduler", lambda flask_app: None)

    flask_app = app_module.create_app()
    flask_app.config.update(
        TESTING=True,
        PROPAGATE_EXCEPTIONS=True,
    )

    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def synthetic_data():
    """Entrega una copia limpia de los datos sintéticos en cada prueba."""
    fixture_path = Path(__file__).parent / "fixtures" / "sprint1_data.json"
    with fixture_path.open(encoding="utf-8") as fixture_file:
        return deepcopy(json.load(fixture_file))
