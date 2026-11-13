from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Instancia del ORM SQLAlchemy (se vincula a la app dentro de create_app)
db = SQLAlchemy()

# Instancia del manejador de JWT (se vincula a la app dentro de create_app)
jwt = JWTManager()