import finnhub
from flask import current_app,jsonify
from app.extensions import db
from app.models.pricecache import PriceCache
from decimal import Decimal
from datetime import datetime,timezone,timedelta

class PriceService():
    _client = None

    def get_finnhub_client():
        if PriceService._client is None:
            PriceService._client = finnhub.Client(api_key=current_app.config['API_KEY'])
        return PriceService._client

    def get_price(symbol):
        quote = PriceService.get_finnhub_client().quote(symbol)
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
        symbols = PriceService.get_finnhub_client().stock_symbols(exchange_code)
        return symbols

    def add_price(symbol):
        price = PriceService.get_price(symbol)
        if price == None:
            return jsonify({'message':'symbol not found'})
        current_price = price.get('current_price')
        current_price = Decimal(str(current_price))
        if current_price is None:
            return jsonify({'message':'api error or other issue returning no price. try again later'})
        pricecache_update = db.session.query(PriceCache).filter_by(symbol=symbol).first()
        if pricecache_update:
            pricecache_update.price = current_price
            pricecache_update.fetched_at=datetime.now(timezone.utc)
            db.session.commit()
            return pricecache_update.price
        else:
            pricecache = PriceCache(symbol=symbol,price=current_price)
            db.session.add(pricecache)
            db.session.commit()
            return pricecache.price
    
    def read_price(symbol):
        pricecache = db.session.query(PriceCache).filter_by(symbol=symbol).first()
        if not pricecache:
            return PriceService.add_price(symbol)
        else:
            is_current = datetime.now(timezone.utc) - pricecache.fetched_at < timedelta(minutes=15)
            if not is_current:
                return PriceService.add_price(symbol)

        return pricecache.price

