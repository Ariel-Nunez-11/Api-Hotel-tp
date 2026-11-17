# API REST de Gestión Hotelera (Flask + PostgreSQL + JWT)

Trabajo Práctico Integrador de Backend. API RESTful desarrollada en Python con **Flask**, **SQLAlchemy ORM**, **PostgreSQL (Docker)** y autenticación/autorización basada en **JSON Web Tokens (JWT)**.

## 1. Arquitectura y Tecnologías
- **Patrón de diseño:** Application Factory (`create_app`) + Separación en capas (`models`, `services`, `routes`, `utils`).
- **Base de datos:** PostgreSQL 15 en contenedor Docker (`sql/esquema.sql` y ORM `Flask-SQLAlchemy`).
- **Seguridad:** Hash irreversible de contraseñas (`werkzeug.security`) y validación de identidad/roles en el payload del JWT (`flask-jwt-extended`) mediante el decorador personalizado `@rol_requerido`.
- **Servidor WSGI:** Preparado para despliegue con **Gunicorn** (`run:app`).
- **Testing:** Suite automatizada con `pytest` sobre base de datos en memoria.

## 2. Instalación y Puesta en Marcha

1. **Levantar la base de datos PostgreSQL con Docker:**
   `docker-compose up -d`

2. **Crear y activar el entorno virtual:**
   - Windows (PowerShell): `python -m venv venv` y luego `.\venv\Scripts\Activate.ps1`
   - Linux/macOS: `python3 -m venv venv` y luego `source venv/bin/activate`

3. **Instalar las dependencias:**
   `pip install -r requirements.txt`

4. **Ejecutar el servidor en modo desarrollo:**
   `python run.py`

5. **Ejecutar con servidor WSGI Gunicorn (Producción / Linux):**
   `gunicorn -w 4 -b 0.0.0.0:5000 "run:app"`

6. **Ejecutar la suite de pruebas automatizadas:**
   `pytest -v`

## 3. Documentación de Endpoints

Base URL por defecto: `http://127.0.0.1:5000`
*(Para endpoints protegidos, enviar header `Authorization: Bearer <token_jwt>`)*

### A. Autenticación (`/auth`)

#### 1. Registrar Usuario
- **Endpoint:** `POST /auth/registro`
- **Acceso:** Público
- **Parámetros (JSON Body):** `{"username": "empleado1", "password": "123", "rol": "Empleado"}` *(Roles admitidos: `"Cliente"` o `"Empleado"`)*
- **Resumen de funcionalidad:** Registra un nuevo usuario en la base de datos aplicando hash seguro a la contraseña.
- **Resultado:**
  - `201 Created`: `{"mensaje": "Usuario registrado exitosamente", "usuario": {"id": 1, "username": "empleado1", "rol": "Empleado"}}`
  - `400 Bad Request`: Si el usuario ya existe o el rol es inválido.

#### 2. Iniciar Sesión (Login)
- **Endpoint:** `POST /auth/login`
- **Acceso:** Público
- **Parámetros (JSON Body):** `{"username": "empleado1", "password": "123"}`
- **Resumen de funcionalidad:** Valida credenciales y retorna un token JWT firmado que incluye el ID del usuario y su rol en los claims.
- **Resultado:**
  - `200 OK`: `{"access_token": "<token_jwt>", "rol": "Empleado", "username": "empleado1"}`
  - `401 Unauthorized`: `{"error": "Credenciales inválidas"}`

### B. Habitaciones (`/habitaciones`)

#### 3. Dar de Alta Habitación
- **Endpoint:** `POST /habitaciones`
- **Acceso:** Protegido (`@rol_requerido("Empleado")`)
- **Parámetros (JSON Body):** `{"numero": 101, "precio": 45000.0}`
- **Resumen de funcionalidad:** Crea una nueva habitación activa validando que el número sea único y mayor a cero, al igual que su precio.
- **Resultado:**
  - `201 Created`: `{"id": 1, "numero": 101, "precio": 45000.0, "activa": true}`
  - `400 Bad Request` / `403 Forbidden`: Si los datos son inválidos o el usuario no es Empleado.

#### 4. Modificar Precio de Habitación
- **Endpoint:** `PUT /habitaciones/<int:habitacion_id>`
- **Acceso:** Protegido (`@rol_requerido("Empleado")`)
- **Parámetros:** `habitacion_id` en URL y JSON Body `{"precio": 52000.0}`
- **Resumen de funcionalidad:** Actualiza el precio por noche de una habitación existente.
- **Resultado:**
  - `200 OK`: `{"id": 1, "numero": 101, "precio": 52000.0, "activa": true}`
  - `400 Bad Request`: Si la habitación no existe o el precio es menor/igual a 0.

#### 5. Baja Lógica de Habitación
- **Endpoint:** `DELETE /habitaciones/<int:habitacion_id>`
- **Acceso:** Protegido (`@rol_requerido("Empleado")`)
- **Parámetros:** `habitacion_id` en URL.
- **Resumen de funcionalidad:** Deshabilita una habitación (`activa = false`) para que no pueda ser reservada, preservando el historial de reservas.
- **Resultado:**
  - `200 OK`: `{"mensaje": "Habitación dada de baja", "habitacion": {"id": 1, "numero": 101, "precio": 52000.0, "activa": false}}`

#### 6. Reactivar Habitación
- **Endpoint:** `PUT /habitaciones/<int:habitacion_id>/activar`
- **Acceso:** Protegido (`@rol_requerido("Empleado")`)
- **Parámetros:** `habitacion_id` en URL.
- **Resumen de funcionalidad:** Vuelve a habilitar una habitación dada de baja (`activa = true`).
- **Resultado:**
  - `200 OK`: `{"mensaje": "Habitación activada", "habitacion": {"id": 1, "numero": 101, "precio": 52000.0, "activa": true}}`

#### 7. Buscar Habitaciones Disponibles
- **Endpoint:** `GET /habitaciones/disponibles`
- **Acceso:** Protegido (Clientes y Empleados con JWT válido)
- **Parámetros (Query Params):**
  - `fecha_inicio` (obligatorio, formato `YYYY-MM-DD`)
  - `fecha_fin` (opcional, formato `YYYY-MM-DD`, por defecto igual a `fecha_inicio`)
  - `precio_max` (opcional, numérico)
- ** Ejemplo de URL:** `/habitaciones/disponibles?fecha_inicio=2026-12-20&fecha_fin=2026-12-22&precio_max=60000`
- **Resumen de funcionalidad:** Retorna las habitaciones activas que no posean ninguna reserva registrada en el rango de fechas solicitado y cuyo precio no supere el tope indicado.
- **Resultado:**
  - `200 OK`: `[{"id": 1, "numero": 101, "precio": 52000.0, "activa": true}]`

### C. Reservas (`/reservas`)

#### 8. Crear Reserva (Por Día o Rango de Fechas)
- **Endpoint:** `POST /reservas`
- **Acceso:** Protegido (`@rol_requerido("Cliente")`)
- **Parámetros (JSON Body):** `{"habitacion_id": 1, "fecha_inicio": "2026-12-20", "fecha_fin": "2026-12-21"}`
- **Resumen de funcionalidad:** Verifica que la habitación esté activa y libre en todos los días del rango solicitado; de ser así, registra las reservas de forma atómica asociándolas al cliente autenticado en el token JWT.
- **Resultado:**
  - `201 Created`: `{"mensaje": "Reserva creada con éxito", "reservas": [{"id": 1, "habitacion_id": 1, "usuario_id": 2, "fecha": "2026-12-20"}, {"id": 2, "habitacion_id": 1, "usuario_id": 2, "fecha": "2026-12-21"}]}`
  - `400 Bad Request`: Si la habitación está inactiva o ya ocupada en alguna de las fechas.

#### 9. Consultar Reservas por Fecha
- **Endpoint:** `GET /reservas/fecha/<string:fecha_str>`
- **Acceso:** Protegido (`@rol_requerido("Empleado")`)
- **Parámetros:** `fecha_str` en URL (formato `YYYY-MM-DD`, ej. `/reservas/fecha/2026-12-20`).
- **Resumen de funcionalidad:** Lista todas las reservas registradas para una fecha específica.
- **Resultado:**
  - `200 OK`: `[{"id": 1, "habitacion_id": 1, "usuario_id": 2, "fecha": "2026-12-20"}]`

#### 10. Cancelar / Eliminar Reserva
- **Endpoint:** `DELETE /reservas/<int:reserva_id>`
- **Acceso:** Protegido (Clientes y Empleados con JWT válido)
- **Parámetros:** `reserva_id` en URL.
- **Resumen de funcionalidad:** Elimina una reserva existente. Si quien solicita es un `Cliente`, valida que sea el titular de la reserva; si es un `Empleado`, permite cancelar cualquier reserva del hotel.
- **Resultado:**
  - `200 OK`: `{"mensaje": "Reserva cancelada exitosamente"}`
  - `400 Bad Request`: Si la reserva no existe o el cliente intenta cancelar una reserva ajena.