import os
from flask import Flask
from app.extensions import db, migrate, jwt, bcrypt, cors
from app.models.token_blocklist import TokenBlocklist
from app.routes.auth import auth_bp
from app.routes.portfolio import portfolio_bp
from app.routes.transaction import transaction_bp
from app.routes.holding import holding_bp
from app.routes.pricecache import pricecache_bp

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        app.config.from_object('app.config.DevelopmentConfig')
    else:
        app.config.from_mapping(test_config)
    app.register_blueprint(auth_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(holding_bp)
    app.register_blueprint(pricecache_bp)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:5174",
                "http://127.0.0.1:5174",
                "https://portfolio-tracker-lemon-sigma.vercel.app"
            ],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    @jwt.token_in_blocklist_loader
    def check_if_token_blocklisted(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return db.session.query(TokenBlocklist).filter_by(jti=jti).first() is not None

    with app.app_context():
        from app import routes, models
    return app