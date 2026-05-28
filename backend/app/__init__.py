import os
from flask import Flask
from app.extensions import db, migrate, jwt, bcrypt, cors
from app.models.token_blocklist import TokenBlocklist
from app.routes.auth import auth_bp

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        app.config.from_object('app.config.DevelopmentConfig')
    else:
        app.config.from_mapping(test_config)
    app.register_blueprint(auth_bp)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "http://localhost:5173"}})

    @jwt.token_in_blocklist_loader
    def check_if_token_blocklisted(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return db.session.query(TokenBlocklist).filter_by(jti=jti).first() is not None

    with app.app_context():
        from app import routes, models
    return app