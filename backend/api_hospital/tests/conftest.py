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
