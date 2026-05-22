from app.extensions import db
import datetime
class PriceCache(db.Model):
    __tablename__ = 'price_cache'
    symbol = db.Column(db.String, nullable=False, primary_key=True)
    price = db.Column(db.Numeric, nullable=False)
    fetched_at = db.Column(db.DateTime, nullable=False)

    watchlist = db.relationship('Watchlist', backref='price_cache', lazy=True)