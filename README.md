# Insured API — Django + DRF + JWT + drf-spectacular

REST API for registering, logging in, and editing **Insured** users, with **JWT** authentication, **Swagger/Redoc** docs via **drf-spectacular**, and infra with **Docker**, **Docker Compose**, and **PostgreSQL**.

> Django Admin uses the default `django.contrib.auth.models.User`.  
> The API authenticates with the **`Insured`** model (based on `AbstractBaseUser`) via **JWT**.

---

## Table of contents

- [Tech stack](#tech-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Environment (.env)](#environment-env)
- [Run with Docker](#run-with-docker)
- [Useful commands](#useful-commands)
- [API documentation](#api-documentation)
- [Authentication](#authentication)
- [Main endpoints](#main-endpoints)
- [Troubleshooting](#troubleshooting)
- [Dependencies (requirements.txt)](#dependencies-requirementstxt)
- [License](#license)

---

## Tech stack

- **Python** 3.10+
- **Django** 5.2.5
- **Django REST Framework** 3.16.1
- **JWT** (`djangorestframework-simplejwt` 5.5.1)
- **drf-spectacular** 0.28.0 (OpenAPI + Swagger/Redoc)
- **PostgreSQL** (via Docker)
- **CORS headers**, **psycopg2-binary**

---

## Architecture

- `Insured` (API “user”) — authenticates via **JWT**.
- `User` (Django **Admin** user) — accesses `/admin/` (optional).
- Routes:
  - **Public**: `POST /api/v1/insureds/` (register), `POST /api/v1/login/` (login)
  - **Protected**: `PATCH /api/v1/insureds/{id}/` (edit)

---

## Prerequisites

- **Docker** and **Docker Compose** installed.
- Port **8000** available (or adjust in your compose file).

---

## Environment (.env)

Create a **`.env`** file at the project root using **`.env-local`** as template:

---

## Run with Docker

```bash
# 1) build & start
docker compose up --build -d

# 2) apply migrations
docker compose exec web python manage.py migrate

# 3) (optional) create Django admin superuser
docker compose exec web python manage.py createsuperuser
```

---

## Useful commands

```bash
# follow logs
docker compose logs -f web

# Django shell
docker compose exec web python manage.py shell

# collect static (if/when needed)
docker compose exec web python manage.py collectstatic --noinput

# run tests
docker compose exec web python manage.py test
```

---

## API documentation

- **Swagger UI**: `http://localhost:8000/api/docs/swagger/`

> If the **Authorize** button is grey, see [Troubleshooting](#troubleshooting).

---

## Authentication

Use JWT **Bearer** tokens:

```
Authorization: Bearer <access_token>
```

Obtain tokens via `POST /api/v1/login/` (e.g. `{ "email": "...", "password": "..." }`).

---

## Main endpoints

### 1) Register insured (public)
`POST /api/v1/insureds/`

**Request**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "cpf": "12345678900",
  "password": "StrongPass123"
}
```

**Response 200**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "cpf": "12345678900",
  "created_at": "2025-08-08T14:35:00Z",
  "updated_at": "2025-08-08T14:35:00Z"
}
```

---

### 2) Login (public)
`POST /api/v1/login/`

**Request**
```json
{ "email": "john@example.com", "password": "StrongPass123" }
```

**Response 200**
```json
{
  "refresh": "jwt-refresh-token",
  "access": "jwt-access-token",
  "insured_id": 1,
  "email": "john@example.com"
}
```

---

### 3) Edit insured (protected)
`PATCH /api/v1/insureds/edit/`

Headers:
```
Authorization: Bearer <access_token>
```

**Request**
```json
{
  "name": "Updated Name",
  "password": "newsecurepassword",
  "password_confirmation": "newsecurepassword"
}
```

**Response 200**
```json
{
  "name": "Updated Name",
  "email": "john@example.com",
  "cpf": "12345678900",
  "created_at": "2025-08-08T14:35:00Z",
  "updated_at": "2025-08-08T15:20:00Z"
}
```

---

## Troubleshooting

- **“Authentication credentials were not provided.”**
  - Ensure your request/Swagger curl includes `Authorization: Bearer <access_token>`.
  - Check `SIMPLE_JWT['AUTH_HEADER_TYPES'] = ('Bearer',)`.
  - Public routes should use `@extend_schema(auth=[])`. Protected routes either inherit global security or set `auth=[{"BearerAuth": []}]`.

- **Authorize button locked/grey in Swagger**
  - `SPECTACULAR_SETTINGS` must define:
    - `SECURITY: [{"BearerAuth": []}]`
    - `COMPONENTS.securitySchemes.BearerAuth` with `type: http`, `scheme: bearer`.
  - Reload `/api/schema/` and confirm the scheme appears in the JSON.

- **Token invalid/expired**
  - Use the **access token** (not the refresh token) in the header.
  - Tune `ACCESS_TOKEN_LIFETIME` in `SIMPLE_JWT`.

- **CSRF header in Swagger curl**
  - If you use only JWT, you don’t need CSRF. Remove `SessionAuthentication` from DRF defaults.

- **`last_login` not updating on login**
  - Update it **in the view** after authentication:
    ```python
    from django.utils.timezone import now
    insured.last_login = now()
    insured.save(update_fields=['last_login'])
    ```

---

## Dependencies (requirements.txt)

```
asgiref==3.9.1
attrs==25.3.0
Django==5.2.5
django-cors-headers==4.7.0
django-decouple==2.1
djangorestframework==3.16.1
djangorestframework_simplejwt==5.5.1
drf-spectacular==0.28.0
inflection==0.5.1
jsonschema==4.25.0
jsonschema-specifications==2025.4.1
Markdown==3.8.2
psycopg2-binary==2.9.10
PyJWT==2.10.1
PyYAML==6.0.2
referencing==0.36.2
rpds-py==0.27.0
sqlparse==0.5.3
uritemplate==4.2.0
```

> **Note:** Django 5.2.x requires Python **3.10+**.

---
