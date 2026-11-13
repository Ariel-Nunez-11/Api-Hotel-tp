import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def client():
    """Crea una instancia aislada de la API con SQLite en memoria para cada test."""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "clave_secreta_super_larga_para_testing_mayor_a_32_bytes"
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def obtener_token(client, username, password, rol):
    """Función auxiliar que registra un usuario, hace login y devuelve su token JWT."""
    client.post("/auth/registro", json={"username": username, "password": password, "rol": rol})
    resp = client.post("/auth/login", json={"username": username, "password": password})
    return resp.get_json()["access_token"]


def test_flujo_completo_hotel(client):
    # 1. Obtenemos tokens para un Empleado y un Cliente
    token_emp = obtener_token(client, "admin_emp", "1234", "Empleado")
    token_cli = obtener_token(client, "huesped_cli", "1234", "Cliente")

    headers_emp = {"Authorization": f"Bearer {token_emp}"}
    headers_cli = {"Authorization": f"Bearer {token_cli}"}

    # 2. Un Cliente NO puede dar de alta una habitación (debe devolver 403 Forbidden)
    resp_prohibido = client.post("/habitaciones", json={"numero": 201, "precio": 50000}, headers=headers_cli)
    assert resp_prohibido.status_code == 403

    # 3. Un Empleado SÍ puede dar de alta la habitación 201 (debe devolver 201 Created)
    resp_alta = client.post("/habitaciones", json={"numero": 201, "precio": 50000}, headers=headers_emp)
    assert resp_alta.status_code == 201

    # 4. El Cliente reserva la habitación 201 para una fecha (debe devolver 201 Created)
    resp_reserva = client.post(
        "/reservas",
        json={"numero_habitacion": 201, "fecha": "2026-12-25"},
        headers=headers_cli
    )
    assert resp_reserva.status_code == 201

    # 5. Intentar reservar la misma habitación en la misma fecha devuelve 409 Conflict
    resp_duplicada = client.post(
        "/reservas",
        json={"numero_habitacion": 201, "fecha": "2026-12-25"},
        headers=headers_cli
    )
    assert resp_duplicada.status_code == 409

    # 6. El Cliente cancela su reserva exitosamente (200 OK)
    reserva_id = resp_reserva.get_json()["reservas"][0]["id"]
    resp_cancelar = client.delete(f"/reservas/{reserva_id}", headers=headers_cli)
    assert resp_cancelar.status_code == 200