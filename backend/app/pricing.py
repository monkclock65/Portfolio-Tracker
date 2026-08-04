import finnhub
from flask import current_app,jsonify
from app.extensions import db
from app.models.pricecache import PriceCache
from decimal import Decimal

class finnhub_api():
    _client = None

    def get_finnhub_client():
        if finnhub_api._client is None:
            finnhub_api._client = finnhub.Client(api_key=current_app.config['API_KEY'])
        return finnhub_api._client

    def get_price(symbol):
        quote = finnhub_api.get_finnhub_client().quote(symbol)
        if not quote or quote.get('c') in (None, 0): 
            return None
        return {
            'current_price': quote.get('c'),
            'high_price': quote.get('h'),
            'low_price': quote.get('l'),
            'previous_close': quote.get('pc')

        }
# for watchlist ui
    def get_stock_list(exchange_code):
        symbols = finnhub_api.get_finnhub_client().stock_symbols(exchange_code)
        return symbols

    def add_price(symbol):
        price = finnhub_api.get_price(symbol)
        if price == None:
            return jsonify({'message':'symbol not found'})
        current_price = price.get('current_price')
        current_price = Decimal(str(current_price))
        pricecache_update = db.session.query(PriceCache).filter_by(symbol=symbol).first()
        if pricecache_update:
            pricecache_update.price = current_price
            db.session.commit
            return jsonify({'message':'price updated'}), 201
        else:
            pricecache = PriceCache(symbol=symbol,price=current_price)
            db.session.add(pricecache)
            db.session.commit()
            return jsonify({'message':'price added'}), 201