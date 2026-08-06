from app.extensions import db
from datetime import datetime,timezone
class PriceCache(db.Model):
    __tablename__ = 'price_cache'
    symbol = db.Column(db.String, nullable=False, primary_key=True)
    price = db.Column(db.Numeric, nullable=False)
    fetched_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    watchlist = db.relationship('Watchlist', backref='price_cache', lazy=True)