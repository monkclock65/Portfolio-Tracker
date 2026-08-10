import os
import uuid
from decimal import Decimal
import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Create a test app with an in-memory SQLite database."""
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key-long-enough-for-hmac',
        'SECRET_KEY': 'test-secret-key-long-enough-for-hmac',
        'API_KEY': os.getenv('API_KEY'),
    }
    app = create_app(test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for making requests against the Flask app."""
    return app.test_client()


@pytest.fixture
def registered_user(client):
    """Register a user and return their credentials."""
    credentials = {
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'Password1',
    }
    client.post('/auth/register', json=credentials)
    return credentials


@pytest.fixture
def tokens(client, registered_user):
    """Log in and return valid access and refresh tokens."""
    response = client.post('/auth/login', json={
        'username': registered_user['username'],
        'password': registered_user['password'],
    })
    assert response.status_code == 200
    return response.get_json()


@pytest.fixture
def auth_headers(tokens):
    """Standard authorization header for protected endpoints."""
    return {'Authorization': f'Bearer {tokens["access_token"]}'}


@pytest.fixture
def portfolio_id(client, auth_headers):
    """Create a portfolio and return its UUID."""
    response = client.post('/portfolio/add_portfolio', json={
        'name': 'Test Portfolio',
        'account_type': 'taxable',
    }, headers=auth_headers)
    assert response.status_code == 200

    response = client.get('/portfolio/read_portfolio', headers=auth_headers)
    assert response.status_code == 200
    portfolios = response.get_json()
    assert isinstance(portfolios, list)
    assert len(portfolios) == 1
    return portfolios[0]['id']


def test_auth_flow_register_login_refresh_logout(client):
    """Verify the auth lifecycle: register, login, refresh, and logout."""
    response = client.post('/auth/register', json={
        'username': 'apiuser',
        'email': 'api@test.com',
        'password': 'Password1',
    })
    assert response.status_code == 201

    response = client.post('/auth/login', json={
        'username': 'apiuser',
        'password': 'Password1',
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data

    refresh_response = client.post('/auth/refresh', headers={
        'Authorization': f'Bearer {data["refresh_token"]}'
    })
    assert refresh_response.status_code == 200
    assert 'access_token' in refresh_response.get_json()

    logout_response = client.delete('/auth/logout', headers={
        'Authorization': f'Bearer {data["access_token"]}'
    })
    assert logout_response.status_code == 200
    assert 'revoked' in logout_response.get_json()['message'].lower()

    # Verify revoked token can no longer access a protected endpoint.
    forbidden = client.get('/portfolio/read_portfolio', headers={
        'Authorization': f'Bearer {data["access_token"]}'
    })
    assert forbidden.status_code in (401, 422)


def test_portfolio_crud_and_deletion(client, auth_headers):
    """Cover portfolio creation, reading, updating, and deletion."""
    create_resp = client.post('/portfolio/add_portfolio', json={
        'name': 'My Portfolio',
        'account_type': 'taxable',
    }, headers=auth_headers)
    assert create_resp.status_code == 200

    list_resp = client.get('/portfolio/read_portfolio', headers=auth_headers)
    assert list_resp.status_code == 200
    portfolios = list_resp.get_json()
    assert isinstance(portfolios, list)
    assert portfolios[0]['name'] == 'My Portfolio'

    portfolio_id = portfolios[0]['id']

    read_resp = client.get(f'/portfolio/{portfolio_id}', headers=auth_headers)
    assert read_resp.status_code == 200
    assert read_resp.get_json()['id'] == portfolio_id

    update_resp = client.patch(f'/portfolio/{portfolio_id}', json={'name': 'Updated Portfolio'}, headers=auth_headers)
    assert update_resp.status_code == 200

    read_updated = client.get(f'/portfolio/{portfolio_id}', headers=auth_headers)
    assert read_updated.status_code == 200
    assert read_updated.get_json()['name'] == 'Updated Portfolio'

    delete_resp = client.delete(f'/portfolio/{portfolio_id}', headers=auth_headers)
    assert delete_resp.status_code == 200

    read_after_delete = client.get(f'/portfolio/{portfolio_id}', headers=auth_headers)
    assert read_after_delete.status_code == 404


def test_transaction_flow_and_holdings_summary(client, auth_headers, monkeypatch):
    """Cover transactions, derived holdings, and portfolio summary math."""
    create_resp = client.post('/portfolio/add_portfolio', json={
        'name': 'Transactions Portfolio',
        'account_type': 'taxable',
    }, headers=auth_headers)
    assert create_resp.status_code == 200

    read_resp = client.get('/portfolio/read_portfolio', headers=auth_headers)
    portfolio_id = read_resp.get_json()[0]['id']

    monkeypatch.setattr('app.services.pricing.PriceService.read_price', staticmethod(lambda symbol: Decimal('100')))

    buy1 = client.post(f'/transaction/add_transaction/{portfolio_id}', json={
        'symbol': 'AAPL',
        'transaction_type': 'BUY',
        'shares': 10,
        'price': 10,
    }, headers=auth_headers)
    assert buy1.status_code == 201

    buy2 = client.post(f'/transaction/add_transaction/{portfolio_id}', json={
        'symbol': 'AAPL',
        'transaction_type': 'BUY',
        'shares': 5,
        'price': 20,
    }, headers=auth_headers)
    assert buy2.status_code == 201

    sell = client.post(f'/transaction/add_transaction/{portfolio_id}', json={
        'symbol': 'AAPL',
        'transaction_type': 'SELL',
        'shares': 5,
        'price': 15,
    }, headers=auth_headers)
    assert sell.status_code == 201

    holdings_summary = client.get(f'/holding/read_holdings/{portfolio_id}', headers=auth_headers)
    assert holdings_summary.status_code == 200
    payload = holdings_summary.get_json()
    assert 'portfolio_summary' in payload

    portfolio_summary = payload['portfolio_summary']
    assert Decimal(portfolio_summary['total_value']) == Decimal('1000')
    assert Decimal(portfolio_summary['total_cost_basis']) == Decimal('133.33333333300000000000')
    assert Decimal(portfolio_summary['total_gain_loss']) == Decimal('866.66666666700000000000')


def test_create_holding_and_reading(client, auth_headers, monkeypatch):
    """Verify manual holding creation still works while the route exists."""
    create_resp = client.post('/portfolio/add_portfolio', json={
        'name': 'Holding Portfolio',
        'account_type': 'taxable',
    }, headers=auth_headers)
    assert create_resp.status_code == 200

    portfolio_id = client.get('/portfolio/read_portfolio', headers=auth_headers).get_json()[0]['id']

    create_holding = client.post('/holding/create_holding', json={
        'portfolio_id': portfolio_id,
        'symbol': 'MSFT',
        'shares': 5,
        'avg_cost_basis': 50,
    }, headers=auth_headers)
    assert create_holding.status_code == 201

    holding_list = client.get(f'/holding/read_holdings/{portfolio_id}', headers=auth_headers)
    assert holding_list.status_code == 200
    assert holding_list.get_json()['holdings_summary'][0]['symbol'] == 'MSFT'

    holding_id = holding_list.get_json()['holdings_summary'][0]['id']

    monkeypatch.setattr('app.services.pricing.PriceService.read_price', staticmethod(lambda symbol: Decimal('55')))
    read_holding = client.get(f'/holding/{holding_id}', headers=auth_headers)
    assert read_holding.status_code == 200
    assert read_holding.get_json()['symbol'] == 'MSFT'


def test_pricecache_endpoint_returns_cached_price(client, auth_headers, monkeypatch):
    """Test the price cache route with a mocked price lookup."""
    monkeypatch.setattr('app.services.pricing.PriceService.read_price', staticmethod(lambda symbol: Decimal('123.45')))
    response = client.get('/pricecache/read_price/AAPL', headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()['price'] == '123.45'


def test_pricecache_endpoint_fails_gracefully(client, auth_headers, monkeypatch):
    """Test the price cache route when the external price lookup returns None."""
    monkeypatch.setattr('app.services.pricing.PriceService.read_price', staticmethod(lambda symbol: None))
    response = client.get('/pricecache/read_price/INVALID', headers=auth_headers)
    assert response.status_code == 400
    assert 'failure' in response.get_json()['message'].lower()

@pytest.mark.skipif(os.getenv('API_KEY') is None, reason='Finnhub API key not configured')
def test_actual_finnhub_api_returns_price(app):
    """Verify the live Finnhub API returns a current price for a real symbol."""
    from app.services.pricing import PriceService

    with app.app_context():
        result = PriceService.get_price('AAPL')

    assert result is not None
    assert 'current_price' in result
    assert Decimal(str(result['current_price'])) > 0
    assert 'high_price' in result
    assert 'low_price' in result
    assert 'previous_close' in result
