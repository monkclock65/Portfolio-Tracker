from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String, db.ForeignKey('price_cache.symbol'), nullable=False)
