from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def rol_requerido(*roles_permitidos):
    """
    Decorador personalizado que verifica:
    1. Que la petición incluya un JWT válido (Autenticación -> 401).
    2. Que el rol dentro del payload del JWT esté autorizado (Autorización -> 403).
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            rol_usuario = claims.get("rol")

            if rol_usuario not in roles_permitidos:
                return jsonify({
                    "error": "Acceso denegado. No tiene permisos suficientes para esta operación.",
                    "rol_requerido": list(roles_permitidos),
                    "rol_actual": rol_usuario
                }), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper