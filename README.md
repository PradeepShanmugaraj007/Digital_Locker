# 🔐 Smart Storage Locker Management System

A production-ready REST API built with **Django 5** for managing smart storage lockers — users can reserve and release lockers, admins manage the fleet. Includes JWT authentication, Redis caching, structured logging, and full ELK stack integration.

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Clone & Local Setup](#-clone--local-setup)
- [Run with Docker](#-run-with-docker)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Swagger UI](#-swagger-ui)
- [Running Tests](#-running-tests)
- [Redis Caching](#-redis-caching)
- [Kibana Logging](#-kibana-logging)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.x + Django REST Framework |
| Database | PostgreSQL |
| Cache | Redis (`django-redis`) |
| Authentication | JWT (`djangorestframework-simplejwt`) |
| Logging | Python logging → Logstash → Kibana |
| API Docs | drf-spectacular (Swagger + Redoc) |
| Containerization | Docker + Docker Compose |

---

## 📁 Project Structure

```
digital_locker/
├── config/                   # Django project settings
│   ├── settings/
│   │   ├── base.py           # Shared settings
│   │   ├── development.py    # Dev overrides
│   │   └── production.py     # Prod hardening
│   ├── urls.py               # Root URL conf
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/             # User registration, login, JWT, permissions
│   ├── lockers/              # Locker CRUD + Redis-cached available list
│   └── reservations/         # Reserve / list / release reservations
│
├── core/                     # Shared utilities
│   ├── exceptions.py         # Custom exceptions + DRF error handler
│   ├── logging_config.py     # JSON log formatter for Kibana
│   ├── mixins.py             # api_response() helper
│   └── utils.py
│
├── logstash/pipeline/        # Logstash TCP → Elasticsearch pipeline
├── filebeat/                 # Filebeat config (tails logs/app.log)
├── logs/                     # App log files (auto-created)
├── docker-compose.yml        # Full stack: DB + Redis + ELK
├── manage.py
├── requirements.txt
└── .env                      # Environment config (copy from .env.example)
```

---

## 🚀 Clone & Local Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (running locally or via Docker)
- Redis (running locally or via Docker)
- Git

### Step 1 — Clone the repository

```bash
git clone <your-repo-url>
cd Digital_Locker
```

### Step 2 — Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure environment variables

Create a `.env` file in the project root:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Then edit `.env` with your values (see [Environment Variables](#-environment-variables) below).

Generate a secret key:

```bash
python -c "import secrets, string; chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'; print(''.join(secrets.choice(chars) for _ in range(50)))"
```

### Step 5 — Create the PostgreSQL database

Using pgAdmin or psql:

```sql
CREATE DATABASE digital_locker;
```

Or via psql CLI:

```bash
psql -U postgres -c "CREATE DATABASE digital_locker;"
```

### Step 6 — Run database migrations

```bash
python manage.py makemigrations accounts lockers reservations
python manage.py migrate
```

### Step 7 — Create a superuser (admin account)

```bash
python manage.py createsuperuser
```

When prompted, fill in email, name, and password. Then promote to admin role:

```bash
python manage.py shell -c "
from apps.accounts.models import User
u = User.objects.get(email='your@email.com')
u.role = 'admin'
u.is_staff = True
u.save()
print('Done — user is now admin.')
"
```

### Step 8 — Start the development server

```bash
python manage.py runserver
```

The API is now live at `http://127.0.0.1:8000`

---

## 🐳 Run with Docker

Docker Compose spins up the **entire stack** in one command:
PostgreSQL + Redis + Elasticsearch + Logstash + Kibana + Filebeat.

### Step 1 — Start all infrastructure services

```bash
docker-compose up -d
```

Wait ~30 seconds for Elasticsearch to become healthy. Check status:

```bash
docker-compose ps
```

All services should show `Up` or `Up (healthy)`.

### Step 2 — Update `.env` for Docker hostnames

When running inside Docker, update these values in `.env`:

```env
DB_HOST=db
REDIS_URL=redis://redis:6379/1
LOGSTASH_HOST=logstash
```

### Step 3 — Run migrations against the Docker DB

```bash
python manage.py migrate
```

### Step 4 — Run the Django server

```bash
python manage.py runserver
```

### Service URLs (Docker)

| Service | URL |
|---|---|
| Django API | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/api/schema/swagger-ui/` |
| Django Admin | `http://localhost:8000/admin/` |
| Kibana | `http://localhost:5601` |
| Elasticsearch | `http://localhost:9200` |

### Stop all services

```bash
docker-compose down
```

To also remove volumes (wipes DB and Redis data):

```bash
docker-compose down -v
```

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (required) | — |
| `DJANGO_DEBUG` | Enable debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `DJANGO_SETTINGS_MODULE` | Settings module to load | `config.settings.development` |
| `DB_NAME` | PostgreSQL database name | `digital_locker` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | — |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/1` |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Access token TTL in minutes | `30` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Refresh token TTL in days | `7` |
| `LOGSTASH_HOST` | Logstash host | `localhost` |
| `LOGSTASH_PORT` | Logstash TCP port | `5000` |
| `CACHE_TTL_SECONDS` | Available lockers cache TTL | `60` |

---

## 📡 API Endpoints

All responses follow a consistent envelope:

```json
// Success
{ "success": true, "message": "...", "data": { ... } }

// Error
{ "success": false, "error": { "code": "ERROR_CODE", "message": "...", "detail": null } }
```

### Authentication (`/api/auth/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/` | None | Register a new user |
| `POST` | `/api/auth/login/` | None | Login → get JWT access + refresh tokens |
| `POST` | `/api/auth/refresh/` | None | Refresh an expired access token |

**Register payload:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass@123",
  "password_confirm": "SecurePass@123"
}
```

**Login payload:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass@123"
}
```

**Using the token** — add to every protected request header:
```
Authorization: Bearer <access_token>
```

---

### Lockers (`/api/lockers/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/lockers/` | Any | List all lockers |
| `POST` | `/api/lockers/` | Admin | Create a new locker |
| `GET` | `/api/lockers/<id>/` | Any | Get locker details |
| `PUT` | `/api/lockers/<id>/` | Admin | Update a locker |
| `DELETE` | `/api/lockers/<id>/` | Admin | Deactivate a locker (soft delete) |
| `GET` | `/api/lockers/available/` | Any | List available lockers *(Redis cached, TTL=60s)* |

**Create locker payload (Admin):**
```json
{
  "locker_number": "A-101",
  "location": "Building A, Floor 1"
}
```

---

### Reservations (`/api/reservations/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/reservations/` | User/Admin | Reserve a locker |
| `GET` | `/api/reservations/` | User (own) / Admin (all) | List reservations |
| `GET` | `/api/reservations/<id>/` | Owner / Admin | Get reservation detail |
| `PUT` | `/api/reservations/<id>/release/` | Owner / Admin | Release the locker |

**Reserve payload:**
```json
{
  "locker_id": "uuid-of-the-locker"
}
```

---

## 📖 Swagger UI

Interactive API documentation is auto-generated and available at:

```
http://127.0.0.1:8000/api/schema/swagger-ui/
```

Alternative Redoc view:

```
http://127.0.0.1:8000/api/schema/redoc/
```

**How to authenticate in Swagger UI:**

1. Call `POST /api/auth/login/` with your credentials
2. Copy the `access` token from the response
3. Click the **Authorize 🔒** button (top right)
4. Enter: `Bearer <your_access_token>`
5. Click **Authorize** — all subsequent requests will include the token

---

## 🧪 Running Tests

Tests are organized per app and cover registration, login, locker CRUD, permission enforcement, Redis cache behavior, and reservation business logic.

### Run all tests

```bash
python manage.py test apps
```

### Run tests for a specific app

```bash
# Accounts only
python manage.py test apps.accounts

# Lockers only
python manage.py test apps.lockers

# Reservations only
python manage.py test apps.reservations
```

### Run with verbose output

```bash
python manage.py test apps --verbosity=2
```

### What is tested

| App | Test Coverage |
|---|---|
| `accounts` | Registration, duplicate email, password mismatch, login success, wrong password |
| `lockers` | Admin create, user forbidden create, list, deactivate, Redis cache HIT & MISS |
| `reservations` | Create, double-booking rejection, inactive locker guard, release, double-release guard, ownership enforcement, user sees own / admin sees all |

---

## ⚡ Redis Caching

The `GET /api/lockers/available/` endpoint is cached in Redis:

```
Request → Check Redis (key: "digital_locker:lockers:available")
               │
        ┌──────┴──────┐
      HIT             MISS
        │               │
   Return cache     Query PostgreSQL
                        │
                   Store in Redis (TTL = 60s)
                        │
                   Return data
```

- **Cache TTL:** 60 seconds (configurable via `CACHE_TTL_SECONDS` in `.env`)
- **Invalidation:** Natural TTL expiry only — no manual cache clearing on reserve/release
- **Graceful degradation:** If Redis is down, requests fall through to the database (`IGNORE_EXCEPTIONS=True`)

---

## 📊 Kibana Logging

All key events are logged as structured JSON and shipped to Kibana:

| Event | Log Level |
|---|---|
| User registered | `INFO` |
| Login attempt (success/fail) | `INFO` / `WARNING` |
| Locker created / updated / deactivated | `INFO` |
| Reservation created | `INFO` |
| Locker released | `INFO` |
| Cache HIT / MISS | `DEBUG` |
| Any exception or error | `ERROR` |

### View logs in Kibana

1. Start ELK via Docker: `docker-compose up -d elasticsearch logstash kibana filebeat`
2. Open Kibana: `http://localhost:5601`
3. Go to **Discover** → create an index pattern: `digital-locker-logs-*`
4. Use the **timestamp** field → browse and filter your logs in real time

### Log files

Application logs are also written locally to `logs/app.log` in JSON format for Filebeat to tail.

---

## 🔒 Security Notes

- Never commit your `.env` file — add it to `.gitignore`
- Change `DJANGO_SECRET_KEY` before any deployment
- Set `DJANGO_DEBUG=False` in production
- Use `config/settings/production.py` which enforces HTTPS, HSTS, and secure cookies