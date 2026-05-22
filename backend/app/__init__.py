import os
from flask import Flask
from app.config import Config
from app.extensions import db, migrate, jwt
from flask_migrate import Migrate

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    with app.app_context():
        from app import routes, models
        
    return app