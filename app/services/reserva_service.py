from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.habitacion import Habitacion
from app.models.reserva import Reserva
from app.models.usuario import Usuario


class ReservaService:
    """Servicio encargado de la disponibilidad, creación y cancelación de reservas."""

    @staticmethod
    def _parsear_rango_fechas(fecha_inicio_str, fecha_fin_str=None):
        """Convierte fechas YYYY-MM-DD y devuelve la lista de días del rango (inclusive)."""
        if not fecha_inicio_str:
            return None, "Debe indicar al menos 'fecha_inicio' (formato YYYY-MM-DD)."

        if not fecha_fin_str:
            fecha_fin_str = fecha_inicio_str

        try:
            inicio = datetime.strptime(str(fecha_inicio_str), "%Y-%m-%d").date()
            fin = datetime.strptime(str(fecha_fin_str), "%Y-%m-%d").date()
        except ValueError:
            return None, "Formato de fecha inválido. Use YYYY-MM-DD (ej. 2026-12-15)."

        if fin < inicio:
            return None, "La 'fecha_fin' no puede ser anterior a 'fecha_inicio'."

        cantidad_dias = (fin - inicio).days + 1
        if cantidad_dias > 60:
            return None, "El rango máximo permitido por operación es de 60 días."

        lista_fechas = [inicio + timedelta(days=i) for i in range(cantidad_dias)]
        return lista_fechas, None

    @staticmethod
    def buscar_disponibles(fecha_inicio_str, fecha_fin_str=None):
        """Devuelve las habitaciones activas que no tienen reservas en el rango de fechas."""
        fechas, error = ReservaService._parsear_rango_fechas(fecha_inicio_str, fecha_fin_str)
        if error:
            return {"error": error}, 400

        # Subconsulta: IDs de habitaciones ya ocupadas en cualquiera de esas fechas
        ocupadas_subquery = (
            db.session.query(Reserva.habitacion_id)
            .filter(Reserva.fecha.in_(fechas))
            .distinct()
        )

        # Filtramos habitaciones activas cuyo ID NO esté en la subconsulta de ocupadas
        disponibles = (
            Habitacion.query
            .filter(Habitacion.activa.is_(True))
            .filter(~Habitacion.id.in_(ocupadas_subquery))
            .order_by(Habitacion.numero.asc())
            .all()
        )

        return {
            "fecha_inicio": fechas[0].isoformat(),
            "fecha_fin": fechas[-1].isoformat(),
            "dias_consultados": len(fechas),
            "total_disponibles": len(disponibles),
            "habitaciones_disponibles": [
                {
                    **h.to_dict(),
                    "costo_total_estadia": round(h.precio * len(fechas), 2)
                }
                for h in disponibles
            ]
        }, 200

    @staticmethod
    def crear_reserva(usuario_actual_id, rol_actual, datos):
        """Crea reservas para una habitación en una fecha o rango de fechas."""
        habitacion_id = datos.get("habitacion_id")
        numero_habitacion = datos.get("numero_habitacion")

        # Permitimos indicar 'fecha' (un solo día) o 'fecha_inicio' y 'fecha_fin'
        fecha_inicio_str = datos.get("fecha_inicio") or datos.get("fecha")
        fecha_fin_str = datos.get("fecha_fin") or fecha_inicio_str

        if not habitacion_id and not numero_habitacion:
            return {"error": "Debe indicar 'habitacion_id' o 'numero_habitacion'."}, 400

        fechas, error = ReservaService._parsear_rango_fechas(fecha_inicio_str, fecha_fin_str)
        if error:
            return {"error": error}, 400

        # Buscamos la habitación por ID o por número
        if habitacion_id:
            habitacion = db.session.get(Habitacion, habitacion_id)
        else:
            habitacion = Habitacion.query.filter_by(numero=numero_habitacion).first()

        if not habitacion:
            return {"error": "La habitación solicitada no existe."}, 404

        if not habitacion.activa:
            return {"error": f"La habitación {habitacion.numero} se encuentra inactiva (fuera de servicio)."}, 400

        # Si es Empleado, puede opcionalmente indicar 'cliente_id' para reservarle a un cliente
        usuario_destino_id = int(usuario_actual_id)
        if rol_actual == "Empleado" and datos.get("cliente_id"):
            cliente = db.session.get(Usuario, datos.get("cliente_id"))
            if not cliente:
                return {"error": f"No existe el usuario con ID {datos.get('cliente_id')}."}, 404
            usuario_destino_id = cliente.id

        # Verificamos si alguna de las fechas ya está reservada para esa habitación
        conflictos = (
            Reserva.query
            .filter(Reserva.habitacion_id == habitacion.id, Reserva.fecha.in_(fechas))
            .all()
        )
        if conflictos:
            fechas_ocupadas = [c.fecha.isoformat() for c in conflictos]
            return {
                "error": f"La habitación {habitacion.numero} ya está reservada en las fechas: {fechas_ocupadas}."
            }, 409

        nuevas_reservas = [
            Reserva(
                habitacion_id=habitacion.id,
                usuario_id=usuario_destino_id,
                fecha=f
            )
            for f in fechas
        ]

        try:
            db.session.add_all(nuevas_reservas)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"error": "Conflicto de concurrencia: una de las fechas acaba de ser reservada."}, 409

        return {
            "mensaje": "Reserva registrada exitosamente.",
            "habitacion_numero": habitacion.numero,
            "cantidad_dias": len(nuevas_reservas),
            "costo_total": round(habitacion.precio * len(nuevas_reservas), 2),
            "reservas": [r.to_dict() for r in nuevas_reservas]
        }, 201

    @staticmethod
    def listar_reservas(usuario_actual_id, rol_actual):
        """Empleado ve todas las reservas del hotel; Cliente solo ve las suyas."""
        consulta = Reserva.query.order_by(Reserva.fecha.asc())
        if rol_actual == "Cliente":
            consulta = consulta.filter_by(usuario_id=int(usuario_actual_id))

        reservas = consulta.all()
        return {
            "total": len(reservas),
            "reservas": [r.to_dict() for r in reservas]
        }, 200

    @staticmethod
    def cancelar_reserva(reserva_id, usuario_actual_id, rol_actual):
        """Cancela una reserva validando que un Cliente solo pueda cancelar las propias."""
        reserva = db.session.get(Reserva, reserva_id)
        if not reserva:
            return {"error": f"No se encontró la reserva con ID {reserva_id}."}, 404

        if rol_actual == "Cliente" and reserva.usuario_id != int(usuario_actual_id):
            return {
                "error": "Acceso denegado. Un cliente solo puede cancelar sus propias reservas."
            }, 403

        datos_eliminados = reserva.to_dict()
        db.session.delete(reserva)
        db.session.commit()

        return {
            "mensaje": "Reserva cancelada exitosamente.",
            "reserva_cancelada": datos_eliminados
        }, 200