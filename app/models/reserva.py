from app.extensions import db

class Reserva(db.Model):
    """Modelo que representa las reservas de habitaciones en el hotel."""
    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    habitacion_id = db.Column(db.Integer, db.ForeignKey("habitaciones.id"), nullable=False)  # ID de la habitación reservada
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)  # Relación con Usuario
    fecha = db.Column(db.Date, nullable=False, server_default=db.func.now())  # Fecha de creación de la reserva

    __table_args__ = (
        db.UniqueConstraint('habitacion_id', 'fecha', name='uq_habitacion_fecha'),
    )

    habitacion = db.relationship("Habitacion", back_populates="reservas", lazy=True)
    usuario = db.relationship("Usuario", back_populates="reservas", lazy=True)

    def to_dict(self):
        """Convierte el objeto Reserva a un diccionario para facilitar la serialización."""
        return {
            "id": self.id,
            "habitacion_id": self.habitacion_id,
            "numero_habitacion": self.habitacion.numero if self.habitacion else None,
            "usuario_id": self.usuario_id,
            "fecha": self.fecha.isoformat()
        }