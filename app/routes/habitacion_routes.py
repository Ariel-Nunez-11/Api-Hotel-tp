from flask import Blueprint, request, jsonify
from app.services.habitacion_service import HabitacionService
from app.utils.seguridad import rol_requerido

habitacion_bp = Blueprint("habitaciones", __name__, url_prefix="/habitaciones")

@habitacion_bp.route("", methods=["POST"])
@rol_requerido("Empleado")
def crear():
    """Alta de habitación (Solo Empleados)."""
    datos = request.get_json(silent=True) or {}
    respuesta, codigo = HabitacionService.crear_habitacion(
        numero=datos.get("numero"),
        precio=datos.get("precio")
    )
    return jsonify(respuesta), codigo

@habitacion_bp.route("", methods=["GET"])
@rol_requerido("Empleado", "Cliente")
def listar():
    """Listado general de habitaciones (Empleados y Clientes autenticados)."""
    respuesta, codigo = HabitacionService.listar_todas()
    return jsonify(respuesta), codigo

@habitacion_bp.route("/<int:habitacion_id>", methods=["PUT"])
@rol_requerido("Empleado")
def modificar_precio(habitacion_id):
    """Modificación del precio de una habitación por su ID (Solo Empleados)."""
    datos = request.get_json(silent=True) or {}
    respuesta, codigo = HabitacionService.actualizar_precio(
        habitacion_id=habitacion_id,
        nuevo_precio=datos.get("precio")
    )
    return jsonify(respuesta), codigo

@habitacion_bp.route("/<int:habitacion_id>", methods=["DELETE"])
@rol_requerido("Empleado")
def dar_de_baja(habitacion_id):
    """Baja lógica de una habitación: pasa activa a False (Solo Empleados)."""
    respuesta, codigo = HabitacionService.cambiar_estado(habitacion_id, activa=False)
    return jsonify(respuesta), codigo

@habitacion_bp.route("/<int:habitacion_id>/reactivar", methods=["PATCH"])
@rol_requerido("Empleado")
def reactivar(habitacion_id):
    """Reactivación de una habitación dada de baja: pasa activa a True (Solo Empleados)."""
    respuesta, codigo = HabitacionService.cambiar_estado(habitacion_id, activa=True)
    return jsonify(respuesta), codigo

@habitacion_bp.route("", methods=["GET"])
@rol_requerido("Empleado")
def listar_todas_las_habitaciones():
    from app.models.habitacion import Habitacion
    habitaciones = Habitacion.query.order_by(Habitacion.numero).all()
    return jsonify([h.to_dict() for h in habitaciones]), 200