from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
import enum

class AccountType(enum.Enum):
    taxable = 'taxable'
    roth = 'Roth'
    k401 = '401k'

class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)


    holdings = db.relationship('Holding', backref='portfolio', lazy=True)