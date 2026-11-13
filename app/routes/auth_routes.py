from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from app.services.auth_service import AuthService
from app.utils.seguridad import rol_requerido

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/registro", methods=["POST"])
def registrar():
    """Endpoint para dar de alta usuarios (Cliente o Empleado)."""
    datos = request.get_json(silent=True) or {}
    respuesta, codigo = AuthService.registrar_usuario(
        username=datos.get("username"),
        password=datos.get("password"),
        rol=datos.get("rol")
    )
    return jsonify(respuesta), codigo

@auth_bp.route("/login", methods=["POST"])
def iniciar_sesion():
    """Endpoint para autenticar usuario y obtener el token JWT."""
    datos = request.get_json(silent=True) or {}
    respuesta, codigo = AuthService.login(
        username=datos.get("username"),
        password=datos.get("password")
    )
    return jsonify(respuesta), codigo

@auth_bp.route("/perfil", methods=["GET"])
@rol_requerido("Cliente", "Empleado")
def ver_perfil():
    """Endpoint protegido de prueba para verificar los datos dentro del payload del JWT."""
    claims = get_jwt()
    return jsonify({
        "mensaje": "Token JWT válido.",
        "usuario_id": claims.get("sub"),
        "username": claims.get("username"),
        "rol": claims.get("rol")
    }), 200