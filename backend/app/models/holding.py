from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.services.types import GUID

class Holding(db.Model):
    __tablename__ = 'holding'
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    portfolio_id = db.Column(GUID, db.ForeignKey('portfolio.id'), nullable=False)
    symbol = db.Column(db.String, nullable=False)
    shares = db.Column(db.Numeric, nullable=False)
    avg_cost_basis = db.Column(db.Numeric, nullable=False)

    transactions = db.relationship('Transaction', backref='holding', lazy=True)
    