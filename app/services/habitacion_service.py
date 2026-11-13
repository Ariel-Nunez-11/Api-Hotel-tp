from app.extensions import db
from app.models.habitacion import Habitacion

class HabitacionService:
    """Servicio para la gestión administrativa de habitaciones del hotel."""

    @staticmethod
    def crear_habitacion(numero, precio):
        """Da de alta una nueva habitación validando número único y valores positivos."""
        if numero is None or precio is None:
            return {"error": "Debe enviar el 'numero' y el 'precio' de la habitación."}, 400

        try:
            numero_int = int(numero)
            precio_float = float(precio)
        except (ValueError, TypeError):
            return {"error": "El 'numero' debe ser un entero y el 'precio' un valor numérico."}, 400

        if numero_int <= 0 or precio_float <= 0:
            return {"error": "El número de habitación y el precio deben ser mayores a 0."}, 400

        existente = Habitacion.query.filter_by(numero=numero_int).first()
        if existente:
            return {"error": f"Ya existe la habitación número {numero_int}."}, 409

        nueva_habitacion = Habitacion(
            numero=numero_int,
            precio=precio_float,
            activa=True
        )

        db.session.add(nueva_habitacion)
        db.session.commit()

        return {
            "mensaje": "Habitación creada exitosamente.",
            "habitacion": nueva_habitacion.to_dict()
        }, 201

    @staticmethod
    def listar_todas():
        """Devuelve todas las habitaciones ordenadas por número."""
        habitaciones = Habitacion.query.order_by(Habitacion.numero.asc()).all()
        return {
            "total": len(habitaciones),
            "habitaciones": [h.to_dict() for h in habitaciones]
        }, 200

    @staticmethod
    def actualizar_precio(habitacion_id, nuevo_precio):
        """Modifica el precio de una habitación existente."""
        if nuevo_precio is None:
            return {"error": "Debe enviar el campo 'precio'."}, 400

        try:
            precio_float = float(nuevo_precio)
        except (ValueError, TypeError):
            return {"error": "El precio debe ser un valor numérico válido."}, 400

        if precio_float <= 0:
            return {"error": "El precio debe ser mayor a 0."}, 400

        habitacion = db.session.get(Habitacion, habitacion_id)
        if not habitacion:
            return {"error": f"No se encontró la habitación con ID {habitacion_id}."}, 404

        habitacion.precio = precio_float
        db.session.commit()

        return {
            "mensaje": "Precio actualizado correctamente.",
            "habitacion": habitacion.to_dict()
        }, 200

    @staticmethod
    def cambiar_estado(habitacion_id, activa=False):
        """Realiza la baja lógica (activa=False) o reactivación (activa=True) de una habitación."""
        habitacion = db.session.get(Habitacion, habitacion_id)
        if not habitacion:
            return {"error": f"No se encontró la habitación con ID {habitacion_id}."}, 404

        habitacion.activa = bool(activa)
        db.session.commit()

        accion = "reactivada" if habitacion.activa else "dada de baja (inactiva)"
        return {
            "mensaje": f"Habitación {habitacion.numero} {accion} correctamente.",
            "habitacion": habitacion.to_dict()
        }, 200 