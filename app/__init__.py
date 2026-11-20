from flask import Flask, jsonify
from sqlalchemy import text
from app.config import Config
from app.extensions import db, jwt


def create_app(config_overrides=None):
    """Fábrica de la aplicación (Application Factory Pattern)."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Permite inyectar configuración de prueba (ej. base de datos en memoria para pytest)
    if config_overrides:
        app.config.update(config_overrides)

    # Inicializamos las extensiones con la app
    db.init_app(app)
    jwt.init_app(app)

    # Importamos los modelos y creamos las tablas si no existen en PostgreSQL
    with app.app_context():
        from app import models
        db.create_all()


    # Registramos los Blueprints (Rutas)
    from app.routes.auth_routes import auth_bp
    from app.routes.habitacion_routes import habitacion_bp
    from app.routes.reserva_routes import reserva_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(habitacion_bp)
    app.register_blueprint(reserva_bp)    

    # Ruta raíz para servir el Frontend Web (app/static/index.html)
    @app.route("/", methods=["GET"])
    def index():
        return app.send_static_file("index.html")

    @app.route("/health", methods=["GET"])
    def health_check():
        try:
            db.session.execute(text("SELECT 1"))
            estado_bd = "conectada (PostgreSQL)"
        except Exception as e:
            estado_bd = f"error de conexión: {str(e)}"

        return jsonify({
            "estado": "activo",
            "base_de_datos": estado_bd,
            "mensaje": "API de Gestión Hotelera funcionando correctamente"
        }), 200

# Manejadores globales para devolver siempre JSON en lugar de HTML
    @app.errorhandler(404)
    def recurso_no_encontrado(error):
        return jsonify({"error": "El endpoint o recurso solicitado no existe (404)."}), 404

    @app.errorhandler(405)
    def metodo_no_permitido(error):
        return jsonify({"error": "Método HTTP no permitido para esta ruta (405)."}), 405

    return app 