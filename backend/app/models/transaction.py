from app.extensions import db 
import uuid
from sqlalchemy.dialects.postgresql import UUID
import enum
from datetime import datetime, timezone
from app.services.types import GUID

class TransactionType(enum.Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    holding_id = db.Column(GUID, db.ForeignKey('holding.id'), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    shares = db.Column(db.Numeric, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    transacted_at = db.Column(db.DateTime(timezone=True), nullable=False,default=lambda:datetime.now(timezone.utc))

