import finnhub
from flask import current_app

_client = None

def get_finnhub_client():
    global _client
    if _client is None:
        _client = finnhub.Client(api_key=current_app.config['API_KEY'])
    return _client

def get_price(symbol):
    quote = get_finnhub_client().quote(symbol)
    return {
        'current_price': quote.get('c'),
        'high_price': quote.get('h'),
        'low_price': quote.get('l'),
        'previous_close': quote.get('pc')

    }
# for watchlist ui
def get_stock_list(exchange_code):
    symbols = get_finnhub_client().stock_symbols(exchange_code)
    return symbols

