from app import create_app
from app.extensions import db
from app.models.holding import Holding
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.services.pricing import PriceService
import random
from decimal import Decimal

Demo_User = {
    'username': 'Demo_User',
    'password': 'Password123',
    'email': 'demo@gmail.com',
}
DEMO_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'NVDA', 'META', 'NFLX', 'JPM', 'V',
]


def reset_demo_user():
    app = create_app()
    with app.app_context():
        user = db.session.query(User).filter_by(username=Demo_User['username']).first()
        if not user:
            return None

        portfolios = db.session.query(Portfolio).filter_by(user_id=user.id).all()
        for portfolio in portfolios:
            holdings = db.session.query(Holding).filter_by(portfolio_id=portfolio.id).all()
            for holding in holdings:
                transactions = db.session.query(Transaction).filter_by(holding_id=holding.id).all()
                for transaction in transactions:
                    db.session.delete(transaction)
                db.session.delete(holding)
            db.session.delete(portfolio)

        db.session.commit()
        return user


def populate_transactions():
    print("populate_transactions started")
    symbol_list = list(DEMO_SYMBOLS)
    random_symbols = []
    stock_list = []
    transactions = []

    while len(random_symbols) < 10:
        random_symbol = random.choice(symbol_list)
        random_symbols.append(random_symbol)

    for symbol in random_symbols:
        current_symbol_price = PriceService.read_price(symbol)
        print(f"{symbol}: {current_symbol_price}")
        if current_symbol_price is None:
            continue
        stock = {'symbol': symbol, 'price': current_symbol_price}
        stock_list.append(stock)
        print(f"Symbols with valid prices: {len(stock_list)} / {len(random_symbols)}")

    for stock in stock_list:
        price = stock.get('price')
        stock_symbol = stock.get('symbol')
        num = random.uniform(0.05, 0.15)
        random_discount = price * Decimal(str(num))
        final_price = price - random_discount
        shares = random.randint(1, 10)
        transaction = {
            'symbol': stock_symbol,
            'shares': shares,
            'price': final_price,
            'type': 'BUY'
        }
        transactions.append(transaction)

    return transactions


def demo_seed():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        existing_user = db.session.query(User).filter_by(username=Demo_User['username']).first()
        if existing_user:
            print('Resetting existing demo user data...')
            portfolios = db.session.query(Portfolio).filter_by(user_id=existing_user.id).all()
            for portfolio in portfolios:
                holdings = db.session.query(Holding).filter_by(portfolio_id=portfolio.id).all()
                for holding in holdings:
                    transactions = db.session.query(Transaction).filter_by(holding_id=holding.id).all()
                    for transaction in transactions:
                        db.session.delete(transaction)
                    db.session.delete(holding)
                db.session.delete(portfolio)
            db.session.commit()

        register_resp = client.post('/auth/register', json=Demo_User)
        if register_resp.status_code not in (201, 400):
            print('Unexpected register response:', register_resp.status_code, register_resp.get_json())

        if register_resp.status_code == 400:
            user = db.session.query(User).filter_by(username=Demo_User['username']).first()
            if user is None:
                print('Could not register demo user:', register_resp.get_json())
                return

        login_resp = client.post('/auth/login', json={
            'username': Demo_User['username'],
            'password': Demo_User['password']
        })
        if login_resp.status_code != 200:
            print('Could not log in demo user:', login_resp.get_json())
            return

        access_token = login_resp.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}

        portfolio_resp = client.post('/portfolio/add_portfolio', json={
            'name': 'Demo Portfolio',
            'account_type': 'taxable',
        }, headers=headers)
        print('Create portfolio:', portfolio_resp.status_code, portfolio_resp.get_json())

        portfolios = client.get('/portfolio/read_portfolio', headers=headers).get_json()
        portfolio_id = portfolios[0]['id']

        transactions = populate_transactions()
        print(f'got {len(transactions)} transactions to post')
        for transaction in transactions:
            resp = client.post(
                f'/transaction/add_transaction/{portfolio_id}',
                json={
                    'symbol': transaction.get('symbol'),
                    'transaction_type': transaction.get('type'),
                    'shares': transaction.get('shares'),
                    'price': transaction.get('price'),
                },
                headers=headers,
            )
            print(f"{transaction.get('type')} {transaction.get('shares')} {transaction.get('symbol')} @ {transaction.get('price')}", resp.status_code)

        print(f"\nDemo portfolio ready. portfolio_id={portfolio_id}")
        print(f"Login with username='{Demo_User['username']}' password='{Demo_User['password']}'")


if __name__ == '__main__':
    demo_seed()



