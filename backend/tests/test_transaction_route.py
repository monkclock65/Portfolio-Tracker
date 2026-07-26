import pytest
from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models.holding import Holding
from app.models.transaction import Transaction, TransactionType


# ─────────────────────────────────────────────
# Fixtures  (mirrors your auth test setup)
# ─────────────────────────────────────────────

@pytest.fixture
def app():
    """Test app with an in-memory SQLite database."""
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
    return app.test_client()


@pytest.fixture
def registered_user(client):
    credentials = {
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'Password1',
    }
    client.post('/auth/register', json=credentials)
    return credentials


@pytest.fixture
def tokens(client, registered_user):
    response = client.post('/auth/login', json={
        'username': registered_user['username'],
        'password': registered_user['password'],
    })
    return response.get_json()


@pytest.fixture
def auth_headers(tokens):
    return {'Authorization': f'Bearer {tokens["access_token"]}'}


@pytest.fixture
def portfolio_id(client, auth_headers):
    """
    Create a portfolio via the API, then read its id back.

    Your /portfolio/add_portfolio route returns only a success message, so the
    id has to be fetched with a follow-up GET.

    Creates via POST /portfolio/add_portfolio, then reads the id back from
    GET /portfolio/read_portfolio (a JSON list of {name, account_type, id}).
    """
    client.post('/portfolio/add_portfolio', json={
        'name': 'Test Portfolio',
        'account_type': 'taxable',   # AccountType value (values: taxable / Roth / 401k)
    }, headers=auth_headers)

    resp = client.get('/portfolio/read_portfolio', headers=auth_headers)
    portfolios = resp.get_json()   # returns a JSON list of {name, account_type, id}
    return portfolios[0]['id']


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def post_txn(client, headers, portfolio_id, symbol, ttype, shares, price):
    return client.post(
        f'/transaction/add_transaction/{portfolio_id}',
        json={
            'symbol': symbol,
            'transaction_type': ttype,
            'shares': shares,
            'price': price,
        },
        headers=headers,
    )


def get_holding(portfolio_id, symbol):
    return (
        db.session.query(Holding)
        .filter_by(portfolio_id=portfolio_id, symbol=symbol)
        .first()
    )


def approx_dec(actual, expected, tol='0.0001'):
    """Decimal-safe compare; dodges repeating-decimal exactness issues."""
    return abs(Decimal(actual) - Decimal(expected)) < Decimal(tol)


# ─────────────────────────────────────────────
# Cost-basis math  (assert on persisted DB state)
# ─────────────────────────────────────────────

class TestTransactionMath:

    def test_first_buy_creates_holding(self, client, auth_headers, portfolio_id):
        resp = post_txn(client, auth_headers, portfolio_id, 'AAPL', 'BUY', 10, 10)
        assert resp.status_code in (200, 201)

        h = get_holding(portfolio_id, 'AAPL')
        assert h is not None
        assert approx_dec(h.shares, '10')
        assert approx_dec(h.avg_cost_basis, '10')      # first txn: avg == price

        txns = db.session.query(Transaction).filter_by(holding_id=h.id).all()
        assert len(txns) == 1
        assert txns[0].transaction_type == TransactionType.BUY

    def test_second_buy_averages(self, client, auth_headers, portfolio_id):
        post_txn(client, auth_headers, portfolio_id, 'AAPL', 'BUY', 10, 10)
        post_txn(client, auth_headers, portfolio_id, 'AAPL', 'BUY', 5, 20)

        h = get_holding(portfolio_id, 'AAPL')
        assert approx_dec(h.shares, '15')
        # (10*10 + 5*20) / 15 = 200/15 = 13.3333...
        assert approx_dec(h.avg_cost_basis, '13.3333')

    def test_sell_reduces_shares_keeps_avg(self, client, auth_headers, portfolio_id):
        post_txn(client, auth_headers, portfolio_id, 'AAPL', 'BUY', 10, 10)
        post_txn(client, auth_headers, portfolio_id, 'AAPL', 'BUY', 5, 20)
        # Sell at a wild price to prove sale price doesn't move the average.
        post_txn(client, auth_headers, portfolio_id, 'AAPL', 'SELL', 5, 999)

        h = get_holding(portfolio_id, 'AAPL')
        assert approx_dec(h.shares, '10')              # 15 - 5
        assert approx_dec(h.avg_cost_basis, '13.3333')  # unchanged by the sell

    def test_buy_after_sell_uses_replayed_count(self, client, auth_headers, portfolio_id):
        post_txn(client, auth_headers, portfolio_id, 'AAPL', 'BUY', 10, 10)
        post_txn(client, auth_headers, portfolio_id, 'AAPL', 'BUY', 5, 20)
        post_txn(client, auth_headers, portfolio_id, 'AAPL', 'SELL', 5, 999)
        post_txn(client, auth_headers, portfolio_id, 'AAPL', 'BUY', 10, 16)

        h = get_holding(portfolio_id, 'AAPL')
        assert approx_dec(h.shares, '20')
        # remaining basis after sell: 10 * 13.3333 = 133.333
        # + new buy 10*16 = 160  ->  293.333 / 20 = 14.6667
        assert approx_dec(h.avg_cost_basis, '14.6667')


# ─────────────────────────────────────────────
# Error / guard paths
# ─────────────────────────────────────────────

class TestTransactionGuards:

    def test_sell_without_holding_404(self, client, auth_headers, portfolio_id):
        resp = post_txn(client, auth_headers, portfolio_id, 'TSLA', 'SELL', 5, 100)
        assert resp.status_code == 404

    def test_invalid_transaction_type_400(self, client, auth_headers, portfolio_id):
        resp = post_txn(client, auth_headers, portfolio_id, 'AAPL', 'GIFT', 5, 100)
        assert resp.status_code == 400

    def test_portfolio_not_owned_404(self, client, auth_headers):
        import uuid
        resp = post_txn(client, auth_headers, uuid.uuid4(), 'AAPL', 'BUY', 5, 100)
        assert resp.status_code == 404

    def test_requires_auth_401(self, client, portfolio_id):
        resp = client.post(
            f'/transaction/add_transaction/{portfolio_id}',
            json={'symbol': 'AAPL', 'transaction_type': 'BUY',
                  'shares': 5, 'price': 100},
        )  # no auth header
        assert resp.status_code == 401


# ─────────────────────────────────────────────
# Known gaps — xfail acts as a to-do list.
# These flip to passing once you make the fixes we discussed.
# ─────────────────────────────────────────────

class TestKnownGaps:

    @pytest.mark.xfail(reason="route returns no body/201 yet; add `return jsonify(...), 201`")
    def test_success_returns_201_with_body(self, client, auth_headers, portfolio_id):
        resp = post_txn(client, auth_headers, portfolio_id, 'AAPL', 'BUY', 10, 10)
        assert resp.status_code == 201
        body = resp.get_json()
        assert body is not None
        assert 'symbol' in body or 'id' in body

    @pytest.mark.xfail(reason="no oversell guard yet; SELL can drive shares negative")
    def test_oversell_rejected(self, client, auth_headers, portfolio_id):
        post_txn(client, auth_headers, portfolio_id, 'AAPL', 'BUY', 5, 10)
        resp = post_txn(client, auth_headers, portfolio_id, 'AAPL', 'SELL', 999, 10)
        assert resp.status_code == 400
        h = get_holding(portfolio_id, 'AAPL')
        assert h.shares >= 0
