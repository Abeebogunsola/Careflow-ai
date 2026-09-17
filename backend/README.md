# CareFlow AI — Backend Service

The backend layer for **CareFlow AI — HIV Care Retention & Support Platform**.

This service is built with **FastAPI**, **Pydantic**, **SQLAlchemy**, and **Alembic**, providing a modular and secure REST API that enforces the project's core safety and human-in-the-loop principles.

---

## 1. Directory Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # Application factory & entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py           # v1 route aggregator
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── health.py       # Health check endpoint (/api/v1/health)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py               # Pydantic settings & env validation
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                 # SQLAlchemy declarative base
│   │   └── session.py              # Session factory & engine configuration
│   └── models/
│       └── __init__.py             # Database models registry
├── alembic/
│   ├── env.py                      # Alembic migration environment
│   ├── script.py.mako              # Migration script template
│   └── versions/                   # Migration version files
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures and TestClient setup
│   └── test_health.py              # Health endpoint tests
├── alembic.ini                     # Alembic configuration
├── requirements.txt                # Foundation dependencies
├── .env.example                    # Environment variable template
├── Dockerfile                      # Container build definition
└── README.md                       # Backend documentation
```

---

## 2. Getting Started Locally

### Prerequisites
- Python 3.11+
- Virtual environment tool (`venv`)

### 1. Set Up Virtual Environment
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
```
Adjust `.env` parameters if needed for your local environment.

### 4. Run the Development Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- **API Base**: http://127.0.0.1:8000
- **Health Check**: http://127.0.0.1:8000/api/v1/health
- **Interactive OpenAPI Docs**: http://127.0.0.1:8000/api/v1/docs

---

## 3. Running Tests

Run the test suite using `pytest`:

```bash
pytest
```

To run with verbose output:
```bash
pytest -v
```

---

## 4. Architectural Rules & Next Phases

- **Phase 3 (Current)**: Backend foundation (routing, configuration, lazy DB session, tests).
- **Phase 4 (Next)**: Database schema & models (`docs/database-design.md`).
- **Phase 5**: Complete REST API endpoints (`docs/api.md`).
- **Phase 6**: Frontend integration (`React`).
- **Phase 7**: AI Agent integration (`docs/ai-agent-specification.md`).
- **Phase 8**: n8n automation workflows (`docs/workflows.md`).

For security and privacy guidelines, consult [`docs/safety-privacy.md`](../docs/safety-privacy.md).
