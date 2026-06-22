# Habit Tracker App

A full-stack habit tracking application built with Django (backend) and React (frontend), Object-Oriented based Programming.
applying best practices and relevant security measures.
can be assessed from https://meinhabit.de/

**Routing (all HTTPS):**

| Hostname                                                             | Serves |
|----------------------------------------------------------------------|--------|
| [meinhabit.de](https://meinhabit.de/)                                | Frontend (React SPA) |
| [api.meinhabit.de](https://api.meinhabit.de)                         | Backend (Django API ) |
| [api.meinhabit.de/api/v1/docs](https://api.meinhabit.de/api/v1/docs) | Backend ( Swagger) |
| [docs.meinhabit.de](https://docs.meinhabit.de/)                                       | Sphinx documentation |

## Tech Stack

**Backend**
- Python 3.13 + Django 5.1 + Django REST Framework
- PostgreSQL (database), Redis (Celery broker)
- Celery + Celery Beat (scheduled tasks)
- JWT (authentication) Using ("HS256 encryption")
- drf-spectacular (Swagger docs)
- pytest (testing, 80% coverage threshold)
- Sphinx (API documentation)

**Frontend**
- React 19 + TypeScript + Vite
- MUI (Material UI)
- React Router v7, TanStack Query, Zustand, React Hook Form + Zod
- nginx (static file serving in Docker)

---

## Running with Docker (recommended)

### Prerequisites
- Docker and Docker Compose installed

### Steps

```bash
# 1. Clone / enter the project
cd habit_app103

# 2. Start all services
docker-compose up --build

# Services:
# → http://localhost/          Frontend (React)
# → http://localhost:8000/api/v1/docs/   Swagger UI
# → http://localhost:8000/admin/         Django admin
```

The `backend` service automatically runs `python manage.py migrate` on startup, which seeds all list and habit templates.

---

## Running Locally (development)

### Backend

```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your local DB credentials

# Run migrations (requires PostgreSQL running)
python manage.py migrate

# Start development server
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A celery_app worker --loglevel=info

# Start Celery Beat scheduler (separate terminal)
celery -A celery_app beat --loglevel=info
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server (proxies /api to localhost:8000)
npm run dev
# → http://localhost:3000/
```

---

## Running Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests with coverage
pytest

# Run specific test module
pytest apps/habits/tests/test_analytics.py -v

# Check type safety
mypy apps/ config/
```

---

## Building Sphinx Documentation

```bash
cd backend
source .venv/bin/activate

pip install Sphinx sphinx-rtd-theme sphinxcontrib-django

cd docs
make html

# Open docs/_build/html/index.html in browser
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register new user |
| POST | `/api/v1/auth/login/` | Login |
| POST | `/api/v1/auth/refresh/` | Refresh JWT token |
| GET  | `/api/v1/auth/me/` | Current user profile |
| GET  | `/api/v1/habits/` | List habits (paginated) |
| POST | `/api/v1/habits/` | Create habit |
| GET  | `/api/v1/habits/:id/` | Get habit |
| PUT  | `/api/v1/habits/:id/` | Update habit |
| DELETE | `/api/v1/habits/:id/` | Delete habit |
| POST | `/api/v1/habits/:id/check-in/` | Check in habit |
| GET  | `/api/v1/lists/` | List all lists |
| POST | `/api/v1/lists/` | Create list |
| PUT  | `/api/v1/lists/:id/` | Update list |
| DELETE | `/api/v1/lists/:id/` | Delete list |
| GET  | `/api/v1/dashboard/` | Habits due in next 30 days |
| GET  | `/api/v1/dashboard/:list_id/` | Habits in list, due in 30 days |
| GET  | `/api/v1/report/general/` | General analytics |
| GET  | `/api/v1/report/all/` | All habits |
| GET  | `/api/v1/report/habit/:id/` | Single habit history |

Swagger UI: `http://localhost:8000/api/v1/docs/`

---

## Project Structure

```
habit_app103/
├── docker-compose.yml
├── backend/
│   ├── config/          # Django settings package
│   ├── apps/
│   │   ├── common/      # BaseModel, SoftDeleteManager, pagination
│   │   ├── users/       # Auth, registration, JWT
│   │   ├── lists/       # Habit list management
│   │   └── habits/      # Habits, analytics, Celery tasks
│   ├── celery_app/      # Celery configuration
│   ├── docs/            # Sphinx documentation + class diagram
│   └── manage.py
└── frontend/
    ├── src/
    │   ├── api/         # Axios client + endpoints
    │   ├── pages/       # Auth, Dashboard, Lists, Reports
    │   ├── components/  # Layout, modals
    │   ├── store/       # Zustand auth store
    │   └── context/     # Auth context
    └── Dockerfile
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_NAME` | `habit_tracker` | Database name |
| `JWT_ACCESS_MINUTES` | `60` | Access token lifetime (minutes) |
| `JWT_REFRESH_DAYS` | `7` | Refresh token lifetime (days) |
| `STREAK_THRESHOLD` | `10` | Check-ins needed to achieve a streak |
| `CELERY_BEAT_INTERVAL_MINUTES` | `10` | How often to check overdue habits |
| `LOG_LEVEL` | `INFO` | Application log level |
