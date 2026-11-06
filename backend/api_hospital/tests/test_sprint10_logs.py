def test_request_log_has_correlation_without_user_input(client, caplog):
    import logging
    with caplog.at_level(logging.INFO):
        response = client.get('/synthetic-patient-canary?token=token-canary',
                              headers={'Authorization': 'Bearer auth-canary'})
    assert response.status_code == 404
    correlation = response.headers['X-Request-ID']
    assert len(correlation) == 32 and correlation in caplog.text
    for marker in ('synthetic-patient-canary', 'token-canary', 'auth-canary'):
        assert marker not in caplog.text


def test_request_ids_are_generated_not_trusted(client):
    first = client.get('/health', headers={'X-Request-ID': 'untrusted'})
    second = client.get('/health')
    assert first.headers['X-Request-ID'] != 'untrusted'
    assert first.headers['X-Request-ID'] != second.headers['X-Request-ID']
