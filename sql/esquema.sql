-- Esqueleto de Base de Datos - API de Gestión Hotelera (PostgreSQL)

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('Cliente', 'Empleado'))
);

CREATE TABLE IF NOT EXISTS habitaciones (
    id SERIAL PRIMARY KEY,
    numero INTEGER UNIQUE NOT NULL CHECK (numero > 0),
    precio DOUBLE PRECISION NOT NULL CHECK (precio > 0),
    activa BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS reservas (
    id SERIAL PRIMARY KEY,
    habitacion_id INTEGER NOT NULL REFERENCES habitaciones(id),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    fecha DATE NOT NULL,
    CONSTRAINT uq_habitacion_fecha UNIQUE (habitacion_id, fecha)
);