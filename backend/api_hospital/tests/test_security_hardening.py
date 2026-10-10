from middleware.auth_middleware import generate_token
from models.user import UserModel


def test_security_headers_are_added(client):
    response = client.get('/health')
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert response.headers['Referrer-Policy'] == 'no-referrer'
    assert response.headers['Cache-Control'] == 'no-store'


def test_cors_rejects_unknown_origin(client):
    response = client.options(
        '/api/v1/auth/login',
        headers={
            'Origin': 'https://attacker.example',
            'Access-Control-Request-Method': 'POST',
        },
    )
    assert 'Access-Control-Allow-Origin' not in response.headers


def test_login_is_temporarily_limited(client, monkeypatch):
    monkeypatch.setattr(
        'routes.auth.AuthService.login',
        lambda *_args: (None, 'Credenciales inválidas'),
    )
    payload = {'username': 'objetivo', 'password': 'incorrecta'}
    for _ in range(5):
        assert client.post('/api/v1/auth/login', json=payload).status_code == 401

    blocked = client.post('/api/v1/auth/login', json=payload)
    assert blocked.status_code == 429
    assert int(blocked.headers['Retry-After']) > 0


def test_successful_login_clears_failed_attempts(client, monkeypatch):
    calls = {'count': 0}

    def login(*_args):
        calls['count'] += 1
        if calls['count'] < 3:
            return None, 'Credenciales inválidas'
        return {'token': 'ok', 'user': {'username': 'demo'}}, None

    monkeypatch.setattr('routes.auth.AuthService.login', login)
    payload = {'username': 'demo', 'password': 'secreto'}
    assert client.post('/api/v1/auth/login', json=payload).status_code == 401
    assert client.post('/api/v1/auth/login', json=payload).status_code == 401
    assert client.post('/api/v1/auth/login', json=payload).status_code == 200

    calls['count'] = 0
    assert client.post('/api/v1/auth/login', json=payload).status_code == 401


def test_logout_revokes_current_token(client, monkeypatch):
    monkeypatch.setattr(
        UserModel,
        'find_by_id',
        lambda _user_id: {'username': 'admin', 'role': 'admin', 'activo': True},
    )
    token = generate_token('507f1f77bcf86cd799439011', 'admin', 'admin')
    headers = {'Authorization': f'Bearer {token}'}

    assert client.post('/api/v1/auth/logout', headers=headers).status_code == 200
    assert client.get('/api/v1/auth/me', headers=headers).status_code == 401


def test_new_password_policy_rejects_weak_password(client, monkeypatch):
    monkeypatch.setattr(
        UserModel,
        'find_by_id',
        lambda _user_id: {'username': 'admin', 'role': 'admin', 'activo': True},
    )
    token = generate_token('507f1f77bcf86cd799439011', 'admin', 'admin')
    response = client.post(
        '/api/v1/auth/change-password',
        headers={'Authorization': f'Bearer {token}'},
        json={'old_password': 'anterior', 'new_password': '123456'},
    )
    assert response.status_code == 400
    assert '12 caracteres' in response.get_json()['error']


def test_request_body_limit(client):
    response = client.post(
        '/api/v1/auth/login',
        data=b'x' * (1024 * 1024 + 1),
        content_type='application/json',
    )
    assert response.status_code == 413
