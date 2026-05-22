from app.extensions import db 
import uuid
from sqlalchemy.dialects.postgresql import UUID
import enum
import datetime
class TransactionType(enum.Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    holding_id = db.Column(UUID(as_uuid=True), db.ForeignKey('holding.id'), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    shares = db.Column(db.Numeric, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    transacted_at = db.Column(db.DateTime, nullable=False)

