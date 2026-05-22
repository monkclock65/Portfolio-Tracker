from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    hashed_passwd = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime)
    
    portfolio = db.relationship('Portfolio', backref='user', lazy=True)
    watchlist = db.relationship('Watchlist', backref='user', lazy=True)
