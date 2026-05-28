from app.extensions import db
from datetime import datetime,timezone

class TokenBlocklist(db.Model): 
    jti=db.Column(db.String,primary_key=True)
    created_at =db.Column(db.DateTime(timezone=True), nullable=False,default=lambda:datetime.now(timezone.utc))
    