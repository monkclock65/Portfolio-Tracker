import pytest
from app import create_app
from app.extensions import db


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def app():
    """Create a test app with an in-memory SQLite database."""
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret',
        'SECRET_KEY': 'test-secret',
    }
    app = create_app(test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for making requests."""
    return app.test_client()


@pytest.fixture
def registered_user(client):
    """Register a user and return their credentials."""
    credentials = {
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'Password1'
    }
    client.post('/auth/register', json=credentials)
    return credentials


@pytest.fixture
def tokens(client, registered_user):
    """Log in and return access and refresh tokens."""
    response = client.post('/auth/login', json={
        'username': registered_user['username'],
        'password': registered_user['password']
    })
    return response.get_json()


# ─────────────────────────────────────────────
# Register tests
# ─────────────────────────────────────────────

class TestRegister:

    def test_register_success(self, client):
        response = client.post('/auth/register', json={
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'Password1'
        })
        assert response.status_code == 201
        assert 'User registered successfully' in response.get_json()['message']

    def test_register_missing_username(self, client):
        response = client.post('/auth/register', json={
            'email': 'test@test.com',
            'password': 'Password1'
        })
        assert response.status_code == 400

    def test_register_missing_email(self, client):
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'Password1'
        })
        assert response.status_code == 400

    def test_register_missing_password(self, client):
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@test.com'
        })
        assert response.status_code == 400

    def test_register_duplicate_username(self, client, registered_user):
        response = client.post('/auth/register', json={
            'username': registered_user['username'],
            'email': 'different@test.com',
            'password': 'Password1'
        })
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['Error']

    def test_register_duplicate_email(self, client, registered_user):
        response = client.post('/auth/register', json={
            'username': 'differentuser',
            'email': registered_user['email'],
            'password': 'Password1'
        })
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['Error']

    def test_register_password_too_short(self, client):
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'Pass1'
        })
        assert response.status_code == 400

    def test_register_password_no_digit(self, client):
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'PasswordOnly'
        })
        assert response.status_code == 400

    def test_register_password_no_letter(self, client):
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@test.com',
            'password': '12345678'
        })
        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'notanemail',
            'password': 'Password1'
        })
        assert response.status_code == 400


# ─────────────────────────────────────────────
# Login tests
# ─────────────────────────────────────────────

class TestLogin:

    def test_login_success(self, client, registered_user):
        response = client.post('/auth/login', json={
            'username': registered_user['username'],
            'password': registered_user['password']
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_login_wrong_password(self, client, registered_user):
        response = client.post('/auth/login', json={
            'username': registered_user['username'],
            'password': 'WrongPassword1'
        })
        assert response.status_code == 401

    def test_login_wrong_username(self, client, registered_user):
        response = client.post('/auth/login', json={
            'username': 'doesnotexist',
            'password': registered_user['password']
        })
        assert response.status_code == 401

    def test_login_missing_username(self, client):
        response = client.post('/auth/login', json={
            'password': 'Password1'
        })
        assert response.status_code == 400

    def test_login_missing_password(self, client):
        response = client.post('/auth/login', json={
            'username': 'testuser'
        })
        assert response.status_code == 400


# ─────────────────────────────────────────────
# Refresh tests
# ─────────────────────────────────────────────

class TestRefresh:

    def test_refresh_success(self, client, tokens):
        response = client.post('/auth/refresh', headers={
            'Authorization': f'Bearer {tokens["refresh_token"]}'
        })
        assert response.status_code == 200
        assert 'access_token' in response.get_json()

    def test_refresh_with_access_token_fails(self, client, tokens):
        """Access tokens should not be accepted on the refresh endpoint."""
        response = client.post('/auth/refresh', headers={
            'Authorization': f'Bearer {tokens["access_token"]}'
        })
        assert response.status_code == 422

    def test_refresh_no_token(self, client):
        response = client.post('/auth/refresh')
        assert response.status_code == 401


# ─────────────────────────────────────────────
# Logout tests
# ─────────────────────────────────────────────

class TestLogout:

    def test_logout_success(self, client, tokens):
        response = client.delete('/auth/logout', headers={
            'Authorization': f'Bearer {tokens["access_token"]}'
        })
        assert response.status_code == 200
        assert 'revoked' in response.get_json()['message'].lower()

    def test_token_rejected_after_logout(self, client, tokens):
        """Access token should be blocklisted after logout."""
        client.delete('/auth/logout', headers={
            'Authorization': f'Bearer {tokens["access_token"]}'
        })
        # Try to use the same token again
        response = client.delete('/auth/logout', headers={
            'Authorization': f'Bearer {tokens["access_token"]}'
        })
        assert response.status_code == 401

    def test_logout_no_token(self, client):
        response = client.delete('/auth/logout')
        assert response.status_code == 401
