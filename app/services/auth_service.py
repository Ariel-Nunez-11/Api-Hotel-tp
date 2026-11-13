from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.usuario import Usuario

class AuthService:
    """Servicio encargado del registro, validación de credenciales y emisión de JWT."""

    ROLES_VALIDOS = ("Cliente", "Empleado")

    @staticmethod
    def registrar_usuario(username, password, rol):
        """Registra un nuevo usuario validando datos y hasheando su contraseña."""
        if not username or not password or not rol:
            return {"error": "Faltan campos obligatorios (username, password, rol)."}, 400

        if rol not in AuthService.ROLES_VALIDOS:
            return {"error": f"El rol debe ser uno de: {AuthService.ROLES_VALIDOS}."}, 400

        usuario_existente = Usuario.query.filter_by(username=username).first()
        if usuario_existente:
            return {"error": f"El nombre de usuario '{username}' ya está registrado."}, 409

        password_hasheada = generate_password_hash(password)

        nuevo_usuario = Usuario(
            username=username.strip(),
            password_hash=password_hasheada,
            rol=rol
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return {
            "mensaje": "Usuario registrado exitosamente.",
            "usuario": nuevo_usuario.to_dict()
        }, 201

    @staticmethod
    def login(username, password):
        """Valida credenciales y genera un token JWT con el rol en el payload."""
        if not username or not password:
            return {"error": "Debe enviar username y password."}, 400

        usuario = Usuario.query.filter_by(username=username).first()

        if not usuario or not check_password_hash(usuario.password_hash, password):
            return {"error": "Credenciales inválidas (usuario o contraseña incorrectos)."}, 401

        token = create_access_token(
            identity=str(usuario.id),
            additional_claims={
                "username": usuario.username,
                "rol": usuario.rol
            }
        ) 

        return {
            "mensaje": "Autenticación exitosa.",
            "access_token": token,
            "usuario": usuario.to_dict()
        }, 200 