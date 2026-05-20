from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import pytest_flask

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
test = pytest_flask()