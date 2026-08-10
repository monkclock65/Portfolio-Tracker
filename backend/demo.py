from app import create_app
from app.extensions import db
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


def populate_transactions():
    print("populate_transactions started")
    symbols = DEMO_SYMBOLS
    symbol_list = []
    random_symbols = []
    stock_list = []
    transactions = []
    i = 0
    for item in symbols:
        symbol_list.append(item)
    while i < 10:
        random_symbol = random.choice(symbol_list)
        i = i +1
        random_symbols.append(random_symbol)
    for symbol in random_symbols:
        current_symbol_price = PriceService.read_price(symbol)
        print(f"{symbol}: {current_symbol_price}")
        if current_symbol_price is None:
            continue
        stock = {'symbol':symbol,'price':current_symbol_price}
        stock_list.append(stock)
        print(f"Symbols with valid prices: {len(stock_list)} / {len(random_symbols)}")
    for stock in stock_list:
        price = stock.get('price')
        stock_symbol = stock.get('symbol')
        num = random.uniform(0.05,0.15)
        random_discount = price * Decimal(num)
        final_price = price - random_discount
        shares= random.randint(1,10)
        transaction = {'symbol':stock_symbol,'shares':shares,'price':final_price,'type':'BUY'}
        transactions.append(transaction)
    return transactions


def demo_seed():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        register_resp = client.post('/auth/register',json=Demo_User)
        if register_resp.status_code !=201:
            print("could not register demo user:", register_resp.get_json())

        login_resp = client.post('/auth/login',json={
            'username': Demo_User['username'],
            'password': Demo_User['password']
        })
        if login_resp.status_code != 200:
            print("Could not log in demo user:", login_resp.get_json())
            return

        access_token = login_resp.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}

        # Create a demo portfolio
        portfolio_resp = client.post('/portfolio/add_portfolio', json={
            'name': 'Demo Portfolio',
            'account_type': 'taxable',
        }, headers=headers)
        print("Create portfolio:", portfolio_resp.status_code, portfolio_resp.get_json())

        portfolios = client.get('/portfolio/read_portfolio', headers=headers).get_json()
        portfolio_id = portfolios[0]['id']

        transactions = populate_transactions()
        print(f"got {len(transactions)} transactions to post")
        for transaction in transactions:
            resp = client.post(f'/transaction/add_transaction/{portfolio_id}',json= {
                'symbol': transaction.get('symbol'),
                'transaction_type': transaction.get('type'),
                'shares': transaction.get('shares'),
                'price': transaction.get('price'),
                 } ,headers=headers)
            print(f"{transaction.get('type')} {transaction.get('shares')} {transaction.get('symbol')} @ {transaction.get('price')}", resp.status_code)

        print(f"\nDemo portfolio ready. portfolio_id={portfolio_id}")
        print(f"Login with username='{Demo_User['username']}' password='{Demo_User['password']}'")


if __name__ == '__main__':
    demo_seed()



