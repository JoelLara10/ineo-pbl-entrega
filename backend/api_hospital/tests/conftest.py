from copy import deepcopy
import json
from pathlib import Path

import pytest
import os

# Before importing application modules or dotenv: no external database access.
os.environ['MONGO_URI'] = 'mongodb://127.0.0.1:27017/'
os.environ['MONGO_DB'] = 'ineo_test_pytest'
os.environ['SECRET_KEY'] = 'ineo-test-only-secret-32-characters'


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch):
    import mongomock
    from utils.database import db_instance
    from testing.seed import reset

    client = mongomock.MongoClient()
    db = client['ineo_test_pytest']
    reset(db)
    monkeypatch.setattr(db_instance, 'db', db)
    monkeypatch.setattr(db_instance, 'client', client)
    yield db
    client.drop_database(db.name)
    client.close()


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
