# MatchPoint API

Backend REST API powering MatchPoint, a tennis court reservation platform.

The API is built with Django REST Framework and exposes endpoints used by both the web frontend and the mobile application.

![Python](https://img.shields.io/badge/Python-3.13-blue)![Django](https://img.shields.io/badge/Django-5.x-success)![License](https://img.shields.io/badge/license-MIT-green)![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)

## Features

Current features include:

- User authentication (JWT)
- User profiles
- Clubs
- Courts
- Reservations
- Court availability
- Club employees

Upcoming features:

- Club analytics
- Dynamic pricing recommendations
- Player rankings
- Match history
- Tournaments

---

## Tech Stack

- Python 3.13+
- Django
- Django REST Framework
- PostgreSQL
- drf-spectacular (OpenAPI)
- pytest

---

## Project structure

```
src/
  matchpoint/
    clubs/
    common/
    courts/
    exceptionalunavailability/
    openinghours/
    pricings/
    reservations/
    profiles/
    tests/
    users/
```

Each application is responsible for a single business domain.

Business logic is implemented inside service classes whenever possible.

---

## Running locally

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- PostgreSQL (provided through Docker)

### 1. Clone the repository

```bash
git clone https://github.com/Corentin-dupriez/matchpoint.git
cd matchpoint
```

---

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it

Linux / macOS

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

For dev environment, use

```bash
pip install -r requirements-dev.txt
```

---

### 4. Configure environment variables

Rename `.env.example` file to `.env` and update the values for Google and secret
key.

---

### 5. Start PostgreSQL

The project uses PostgreSQL through Docker.

```bash
docker compose up -d 
```

---

### 6. Run migrations

```bash
python manage.py migrate
```

---

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

---

### 8. Seed data

Coming soon.

The project will provide a seed command to create demo clubs, courts and users for frontend development and API testing.

### 9. Start the server

```bash
python manage.py runserver
```

API available at

```
http://localhost:8000/api/
```

Swagger documentation

```
http://localhost:8000/api/schema/swagger-ui/
```

OpenAPI schema

```
http://localhost:8000/api/schema/
```

---

## Running tests

Run all tests

```bash
pytest
```

Run with coverage

```bash
pytest --cov --cov-report=term-missing
```

---

## Formatting

Format the project

```bash
ruff format .
```

Lint

```bash
ruff check .
```

---

## API Authentication

Authentication uses JWT.

Obtain a token

```
POST /api/token/
```

Refresh

```
POST /api/token/refresh/
```

Include the token

```
Authorization: Bearer <access_token>
```

---

## Development Guidelines

- Business logic belongs in service classes.
- Keep views thin.
- Prefer TDD when adding new features.
- Document every endpoint with drf-spectacular.
- Write type hints whenever possible.
- staging branch is the reference for FE implementation
- Unit test coverage should be around 85% min

---

## Current Roadmap

### MVP

- Clubs
- Courts
- Reservations
- Availability
- Profiles

### Phase 2

- Club analytics
- Dashboards
- Revenue metrics
- Occupancy reports

### Phase 3

- Rankings
- Match history
- Tournaments
- Gamification

---

## Future Architecture

The long-term architecture will consist of multiple services:

- MatchPoint API (Django)
- PostgreSQL
- Analytics service
- DuckDB
- Frontend (PWA)
