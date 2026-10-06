# SDG Sorting Hat — Backend REST API

Independent REST API backend for the SDG (Setif Developers Group) Sorting Hat Welcome Day experience.

Built using Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, and SQLite.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Requirements](#requirements)
6. [Installation](#installation)
7. [Environment Configuration](#environment-configuration)
8. [Database Setup](#database-setup)
9. [Seed Data](#seed-data)
10. [Running the Development Server](#running-the-development-server)
11. [Running Tests](#running-tests)
12. [API Documentation](#api-documentation)
13. [API Endpoint Reference](#api-endpoint-reference)
14. [Frontend Integration](#frontend-integration)
15. [Deployment](#deployment)
16. [Environment Variables Reference](#environment-variables-reference)
17. [Troubleshooting](#troubleshooting)

---

## Project Overview

The SDG Sorting Hat backend is a standalone REST API that processes participant questionnaire submissions and assigns each participant to one of four SDG departments based on a configurable weighted scoring model.

The four departments are:

- **Development** — Technical thinking, problem solving, software building
- **Design** — Creativity, visual aesthetics, design identity
- **Events** — Leadership, event organization, team coordination
- **Social Media** — Communication, promotion, community outreach

The backend is the exclusive source of truth for:

- Questionnaire data (questions and answers)
- Department definitions and scoring rules
- Sorting algorithm execution
- Participant data and session management
- Sorting results and historical snapshots
- Admin configuration and statistics

The frontend communicates with the backend exclusively through HTTP REST requests and JSON responses.

---

## Architecture

The backend follows a clean layered architecture with strict separation of concerns:

```
HTTP Request
      |
   API Router (app/api/)
      |
   Service Layer (app/services/)
      |
   Database Layer (app/models/ + SQLAlchemy)
      |
   SQLite Database (sorting_hat.db)
```

Key architectural decisions:

- The sorting algorithm is implemented exclusively in the backend. The frontend does not implement or replicate any sorting logic.
- Sorting results store an immutable JSON snapshot of scores at the time of sorting. Historical results are not affected by future changes to scoring rules.
- Public API endpoints never expose internal scoring weights, hidden categories, or department target assignments for individual answers.
- All admin endpoints are protected by JWT Bearer authentication.
- CORS origins are configured via environment variables, not hardcoded.

---

## Technology Stack

| Component         | Technology                        |
|-------------------|-----------------------------------|
| Language          | Python 3.12+                      |
| Framework         | FastAPI                           |
| Data Validation   | Pydantic v2                       |
| ORM               | SQLAlchemy 2.0                    |
| Database          | SQLite (development)              |
| Migrations        | Alembic                           |
| Authentication    | JWT via python-jose (OAuth2 Bearer) |
| Password Hashing  | passlib with pbkdf2_sha256        |
| ASGI Server       | Uvicorn                           |
| Testing           | Pytest + HTTPX                    |

---

## Project Structure

```
sorting-hat-backend/
|
|-- app/
|   |-- main.py                         # FastAPI application, middleware, routes
|   |
|   |-- core/
|   |   |-- config.py                   # Application settings via pydantic-settings
|   |   |-- database.py                 # SQLAlchemy engine, session, and Base
|   |   |-- security.py                 # Password hashing and JWT token utilities
|   |
|   |-- models/
|   |   |-- department.py               # Department ORM model
|   |   |-- question.py                 # Question ORM model
|   |   |-- answer.py                   # Answer ORM model
|   |   |-- scoring_rule.py             # ScoringRule ORM model
|   |   |-- participant.py              # Participant ORM model
|   |   |-- response.py                 # Questionnaire Response ORM model
|   |   |-- sorting_result.py           # SortingResult ORM model
|   |   |-- interest.py                 # DepartmentInterest ORM model
|   |   |-- admin_user.py               # AdminUser ORM model
|   |
|   |-- schemas/
|   |   |-- department.py               # Pydantic schemas for Department
|   |   |-- question.py                 # Pydantic schemas for Question
|   |   |-- answer.py                   # Pydantic schemas for Answer
|   |   |-- scoring_rule.py             # Pydantic schemas for ScoringRule
|   |   |-- participant.py              # Pydantic schemas for Participant
|   |   |-- sorting.py                  # Pydantic schemas for Sort request/response
|   |   |-- interest.py                 # Pydantic schemas for DepartmentInterest
|   |   |-- admin.py                    # Pydantic schemas for Admin auth and stats
|   |
|   |-- api/
|   |   |-- deps.py                     # FastAPI dependencies (db session, admin auth)
|   |   |-- departments.py              # GET /api/departments
|   |   |-- questions.py                # GET /api/questions
|   |   |-- participants.py             # POST /api/participants
|   |   |-- sorting.py                  # POST /api/sort
|   |   |-- results.py                  # GET /api/results/{id}, POST interest
|   |   |-- admin_auth.py               # POST /api/admin/login, logout, me
|   |   |-- admin.py                    # Admin CRUD and statistics
|   |
|   |-- services/
|   |   |-- sorting_service.py          # Sorting calculation, tie-breaking, result persistence
|   |   |-- statistics_service.py       # Admin dashboard statistics calculation
|   |
|   |-- seed/
|       |-- seed_data.py                # Idempotent database seeder
|
|-- migrations/                         # Alembic migration scripts
|   |-- versions/
|
|-- tests/
|   |-- test_sorting.py                 # Sorting engine unit tests
|   |-- test_questions.py               # Questionnaire API tests
|   |-- test_participants.py            # Participant registration tests
|   |-- test_public_api.py              # Public API integration tests
|   |-- test_results.py                 # Result retrieval and interest tests
|   |-- test_auth.py                    # Admin authentication tests
|   |-- test_admin_api.py               # Admin dashboard API tests
|
|-- .env                                # Local environment variables (not committed)
|-- .env.example                        # Environment variable template
|-- .gitignore
|-- alembic.ini
|-- requirements.txt
|-- README.md
```

---

## Requirements

- Python 3.10 or higher (Python 3.12 recommended)
- pip package manager

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/brahimmihoubi/sorting_hat_backend.git
cd sorting_hat_backend
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Copy the example environment file and edit values as needed:

```bash
cp .env.example .env
```

Default development configuration:

```ini
PROJECT_NAME="SDG Sorting Hat API"
ENVIRONMENT="development"
API_V1_STR="/api"

JWT_SECRET_KEY="sdg_sorting_hat_secret_key_change_in_production"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=120

DATABASE_URL="sqlite:///./sorting_hat.db"

CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"

SCORING_VERSION="v1.0"
```

In production, replace `JWT_SECRET_KEY` with a strong random secret and update `CORS_ORIGINS` to the production frontend URL.

---

## Database Setup

Apply all Alembic migrations to create the database schema:

```bash
alembic upgrade head
```

This creates `sorting_hat.db` in the project root directory containing all required tables.

---

## Seed Data

Populate the database with departments, questionnaire questions, answers, scoring rules, and a default admin user:

```bash
python3 -m app.seed.seed_data
```

The seed script is idempotent. Running it multiple times will not create duplicate records.

Default seeded data:

- 4 departments: Development, Design, Events, Social Media
- 8 questionnaire questions (Q1 through Q8)
- 32 answer options (A through D for each question)
- Scoring rules for all question/answer/department combinations
- Question 6 leadership trait rules (0.40, 0.40, 0.70, 0.90)
- Default admin user: `admin@sdg.dz` / `admin123`

---

## Running the Development Server

```bash
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or, if the virtual environment is activated:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Available URLs:

| URL                              | Description                            |
|----------------------------------|----------------------------------------|
| http://localhost:8000/api/docs   | Interactive Swagger UI documentation   |
| http://localhost:8000/api/redoc  | ReDoc API documentation                |
| http://localhost:8000/health     | Backend health check                   |

---

## Running Tests

Execute the complete test suite:

```bash
PYTHONPATH=. pytest -v
```

Run a specific test file:

```bash
PYTHONPATH=. pytest tests/test_sorting.py -v
PYTHONPATH=. pytest tests/test_auth.py -v
```

The test suite covers 17 cases including:

- Pure department sorting logic (Development, Design, Events, Social Media)
- Sorting engine idempotency (duplicate submission prevention)
- Question 6 leadership trait scoring
- Missing and incomplete response validation
- Questionnaire retrieval with hidden data protection
- Participant session creation
- Sorting result retrieval
- Department interest submission
- Admin login and JWT token validation
- Unauthorized access rejection
- Admin CRUD operations
- Real-time statistics calculation

---

## API Documentation

When the server is running, interactive documentation is available at:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

All endpoints, request schemas, response schemas, and HTTP status codes are documented in the OpenAPI specification.

---

## API Endpoint Reference

### Public Endpoints

#### GET /api/departments

Returns a list of active departments ordered by display order.

Response: Array of department objects containing `id`, `name`, `slug`, `description`, `short_description`, `icon`, `color`, `active`, `display_order`.

---

#### GET /api/questions

Returns active questionnaire questions with their answer options.

Scoring weights and hidden categories are excluded from this response.

Response: Array of question objects, each containing `id`, `text`, `type`, `display_order`, `required`, and an `answers` array.

---

#### POST /api/participants

Register a participant session before questionnaire submission.

Request body:

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "academic_year": "Master 1"
}
```

Response: Participant object including `id`, `full_name`, `email`, `academic_year`, `session_token`, `status`, `created_at`.

HTTP Status: 201 Created

---

#### POST /api/sort

Submit questionnaire responses and execute the sorting algorithm.

Request body:

```json
{
  "participant_id": "participant-uuid",
  "responses": [
    {
      "question_id": "question-uuid",
      "answer_id": "answer-uuid"
    }
  ]
}
```

Response:

```json
{
  "result_id": "result-uuid",
  "department": {
    "id": "dept-uuid",
    "name": "Development",
    "slug": "development",
    "icon": "code",
    "color": "#3B82F6"
  },
  "total_score": 87.0,
  "scores": {
    "development": 87.0,
    "design": 61.0,
    "events": 72.0,
    "social_media": 51.0
  },
  "scoring_version": "v1.0"
}
```

Error responses:

| Status | Condition                                       |
|--------|-------------------------------------------------|
| 400    | Invalid or incomplete questionnaire submission  |
| 404    | Participant not found                           |
| 409    | Participant has already been sorted             |

---

#### GET /api/results/{result_id}

Retrieve a completed sorting result by its ID.

Response: Same structure as the POST /api/sort response.

---

#### POST /api/results/{result_id}/interest

Submit a department interest or contact request linked to a sorting result.

Request body:

```json
{
  "interested": true,
  "message": "Optional message text",
  "contact_preference": "Email"
}
```

---

### Admin Endpoints (Protected — JWT Bearer Token Required)

#### POST /api/admin/login

Authenticate with admin credentials and receive a JWT access token.

Request body:

```json
{
  "email": "admin@sdg.dz",
  "password": "admin123"
}
```

Response includes `access_token`, `token_type`, `admin_name`, `admin_email`.

---

#### POST /api/admin/logout

Invalidate the current admin session on the client side.

---

#### GET /api/admin/me

Return the profile of the currently authenticated admin user.

---

#### GET /api/admin/statistics

Return real-time dashboard statistics.

Response:

```json
{
  "total_participants": 100,
  "completed_sortings": 87,
  "completion_rate_percentage": 87.0,
  "department_distribution": {
    "development": 24,
    "design": 21,
    "events": 19,
    "social_media": 23
  },
  "department_percentages": {
    "development": 27.59,
    "design": 24.14,
    "events": 21.84,
    "social_media": 26.44
  },
  "total_interests_submitted": 45
}
```

---

#### GET /api/admin/participants

Return a paginated list of registered participants.

Query parameters: `skip` (default 0), `limit` (default 50), `status` (optional: `started` or `completed`).

---

#### GET /api/admin/results

Return a paginated list of completed sorting results with score snapshots.

---

#### GET /api/admin/departments

Return all departments, including inactive ones.

#### POST /api/admin/departments

Create a new department.

#### PUT /api/admin/departments/{dept_id}

Update department details.

---

#### GET /api/admin/questions

Return all questions with their answers.

#### POST /api/admin/questions

Create a new question.

#### PUT /api/admin/questions/{question_id}

Update question text or status.

---

#### POST /api/admin/answers

Create a new answer for a question.

#### PUT /api/admin/answers/{answer_id}

Update answer text or status.

---

#### GET /api/admin/scoring-rules

Return all scoring rules.

#### POST /api/admin/scoring-rules

Create a new scoring rule.

#### PUT /api/admin/scoring-rules/{rule_id}

Update an existing scoring rule weight or trait value.

---

## Frontend Integration

The React frontend configures the backend base URL in its `.env` file:

```ini
VITE_API_BASE_URL=http://localhost:8000/api
```

In production:

```ini
VITE_API_BASE_URL=https://api.sorting.sdg.example/api
```

All frontend-to-backend communication occurs via standard HTTP requests with JSON payloads. The frontend does not contain any sorting logic, scoring data, or database access.

---

## Deployment

### Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Recommended)

Use Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

For production deployments:

- Set `ENVIRONMENT=production` in environment variables
- Replace `JWT_SECRET_KEY` with a strong random secret
- Update `CORS_ORIGINS` to match the exact production frontend domain
- Configure a reverse proxy (Nginx or similar) for HTTPS termination
- Use PostgreSQL by updating `DATABASE_URL` to a valid PostgreSQL connection string
- Store environment variables securely (environment file, secrets manager, or container environment)

---

## Environment Variables Reference

| Variable                     | Required | Description                                           | Example                             |
|------------------------------|----------|-------------------------------------------------------|-------------------------------------|
| PROJECT_NAME                 | No       | Application display name                             | SDG Sorting Hat API                 |
| ENVIRONMENT                  | No       | Runtime environment identifier                       | development                         |
| API_V1_STR                   | No       | API route prefix                                      | /api                                |
| JWT_SECRET_KEY               | Yes      | Secret key for JWT signing (change in production)    | your-secret-key-here                |
| JWT_ALGORITHM                | No       | JWT signing algorithm                                 | HS256                               |
| ACCESS_TOKEN_EXPIRE_MINUTES  | No       | JWT token expiry in minutes                           | 120                                 |
| DATABASE_URL                 | Yes      | SQLAlchemy database connection string                | sqlite:///./sorting_hat.db          |
| CORS_ORIGINS                 | Yes      | Allowed frontend origins, comma-separated            | http://localhost:5173               |
| SCORING_VERSION              | No       | Version label stored in sorting result snapshots     | v1.0                                |

---

## Troubleshooting

**ModuleNotFoundError on startup**

Ensure all dependencies are installed in the correct virtual environment:

```bash
.venv/bin/pip install -r requirements.txt
```

Run uvicorn using the virtual environment explicitly:

```bash
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

**Swagger UI not accessible**

Confirm the server started without errors. Access Swagger UI at:

```
http://localhost:8000/api/docs
```

---

**Alembic migration errors**

Reset and reapply migrations:

```bash
alembic downgrade base
alembic upgrade head
```

---

**Duplicate seed data error**

The seed script is idempotent. If errors occur, ensure the database schema is up to date before running the seeder:

```bash
alembic upgrade head
python3 -m app.seed.seed_data
```

---

**CORS errors from frontend**

Verify `CORS_ORIGINS` in `.env` exactly matches the frontend origin, including protocol, hostname, and port:

```ini
CORS_ORIGINS=http://localhost:5173
```
