import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base de la aplicación Flask."""
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_por_defecto_insegura")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_por_defecto_inseguro")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    # Configuración de la base de datos SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False