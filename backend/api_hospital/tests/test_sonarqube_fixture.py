from sonarqube_fixture import evaluar_entrada


def test_fixture_existe():
    assert callable(evaluar_entrada)