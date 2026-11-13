from app.extensions import db

class Usuario(db.Model):
    """Modelo que representa a los usuarios del Sistema (Empleado y cliente)."""
    __tablename__ = "usuarios"

    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol= db.Column(db.String(20), nullable=False)  # Puede ser 'empleado' o 'cliente'

    #Relacion 1 a N: un usuario puede tener muchas reservas
    reservas = db.relationship("Reserva", back_populates="usuario", lazy=True)

    def to_dict(self):
        """Convierte el objeto Usuario a un diccionario para facilitar la serialización.(ocultando password_hash por seguridad)"""
        return {
            "id": self.id,
            "username": self.username,
            "rol": self.rol
        }  