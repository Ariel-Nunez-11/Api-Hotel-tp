# API REST de Gestión Hotelera (Flask + PostgreSQL + JWT)

Trabajo Práctico Integrador de Backend. API RESTful desarrollada en Python con **Flask**, **SQLAlchemy ORM**, **PostgreSQL (Docker)** y autenticación/autorización basada en **JSON Web Tokens (JWT)**.

## 1. Arquitectura y Tecnologías
- **Patrón de diseño:** Application Factory (`create_app`) + Separación en capas (`models`, `services`, `routes`, `utils`).
- **Base de datos:** PostgreSQL 15 en contenedor Docker (`esquema.sql` y ORM SQLAlchemy).
- **Seguridad:** Hash irreversible de contraseñas (`werkzeug.security`) y validación de identidad/roles en el payload del JWT (`flask-jwt-extended`) mediante el decorador personalizado `@rol_requerido`.
- **Testing:** Suite automatizada con `pytest` sobre base de datos en memoria.

## 2. Instalación y Puesta en Marcha

1. Levantar la base de datos PostgreSQL con Docker:
   ```powershell
   docker-compose up -d