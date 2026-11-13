from app.extensions import db


class Habitacion(db.Model):
    """Modelo que representa una habitación del hotel."""
    __tablename__ = "habitaciones"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    activa = db.Column(db.Boolean, default=True, nullable=False)

    # Relación 1 a N: Una habitación puede tener muchas reservas (días reservados)
    reservas = db.relationship("Reserva", back_populates="habitacion", lazy=True)

    def to_dict(self, incluir_reservas=False):
        """Serializa la habitación a diccionario. Opcionalmente incluye sus reservas."""
        datos = {
            "id": self.id,
            "numero": self.numero,
            "precio": self.precio,
            "activa": self.activa
        }
        if incluir_reservas:
            datos["reservas"] = [reserva.to_dict() for reserva in self.reservas]
        return datos   