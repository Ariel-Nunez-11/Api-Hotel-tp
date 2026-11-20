from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.services.reserva_service import ReservaService
from app.utils.seguridad import rol_requerido

reserva_bp = Blueprint("reservas", __name__, url_prefix="/reservas")


@reserva_bp.route("/disponibles", methods=["GET"])
@rol_requerido("Cliente", "Empleado")
def consultar_disponibles():
    """
    Consulta habitaciones activas y libres en una fecha o rango.
    Ejemplo: GET /reservas/disponibles?fecha_inicio=2026-12-10&fecha_fin=2026-12-12
    """
    fecha_inicio = request.args.get("fecha_inicio") or request.args.get("fecha")
    fecha_fin = request.args.get("fecha_fin")
    respuesta, codigo = ReservaService.buscar_disponibles(fecha_inicio, fecha_fin)
    return jsonify(respuesta), codigo


@reserva_bp.route("", methods=["POST"])
@rol_requerido("Cliente", "Empleado")
def crear():
    """Crea una reserva para una habitación en una fecha o rango de fechas."""
    datos = request.get_json(silent=True) or {}
    usuario_id = get_jwt_identity()
    rol = get_jwt().get("rol")

    respuesta, codigo = ReservaService.crear_reserva(
        usuario_actual_id=usuario_id,
        rol_actual=rol,
        datos=datos
    )
    return jsonify(respuesta), codigo


@reserva_bp.route("", methods=["GET"])
@rol_requerido("Cliente", "Empleado")
def listar():
    """Lista todas las reservas (Empleado) o solo las reservas propias (Cliente)."""
    usuario_id = get_jwt_identity()
    rol = get_jwt().get("rol")
    respuesta, codigo = ReservaService.listar_reservas(usuario_id, rol)
    return jsonify(respuesta), codigo


@reserva_bp.route("/<int:reserva_id>", methods=["DELETE"])
@rol_requerido("Cliente", "Empleado")
def cancelar(reserva_id):
    """Cancela una reserva por ID (Cliente: solo propias | Empleado: cualquiera)."""
    usuario_id = get_jwt_identity()
    rol = get_jwt().get("rol")
    respuesta, codigo = ReservaService.cancelar_reserva(reserva_id, usuario_id, rol)
    return jsonify(respuesta), codigo


@reserva_bp.route("/mis-reservas", methods=["GET"])
@rol_requerido("Cliente")
def obtener_mis_reservas():
    from flask_jwt_extended import get_jwt_identity
    from app.models.reserva import Reserva
    usuario_id = int(get_jwt_identity())
    reservas = Reserva.query.filter_by(usuario_id=usuario_id).order_by(Reserva.fecha).all()
    return jsonify([r.to_dict() for r in reservas]), 200


@reserva_bp.route("/todas", methods=["GET"])
@rol_requerido("Empleado")
def obtener_todas_las_reservas():
    from app.models.reserva import Reserva
    reservas = Reserva.query.order_by(Reserva.fecha).all()
    return jsonify([r.to_dict() for r in reservas]), 200    