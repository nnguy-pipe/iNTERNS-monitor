# AHMS Backend: Agentic Health Monitoring System

A robust Python backend for ingesting telemetry, normalizing data, running agentic reasoning for health scoring, and providing CI evaluation verdicts.

## Quick Start

### Prerequisites
- Python 3.12+
- pip/venv

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

### Run Server

```bash
# Development with auto-reload
python3 -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

The API documentation will be available at: **http://localhost:8000/api/docs**

### Run Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_health.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/ --ignore-missing-imports
```

## Project Structure

```
src/
├── api/          # FastAPI routes and endpoints
├── models/       # SQLAlchemy ORM models and Pydantic schemas
├── services/     # Business logic (ingestion, normalization, reasoning, etc.)
├── workers/      # Background jobs and async workers
└── store/        # Database and persistence layer

tests/
├── unit/         # Unit tests (isolated, no database)
└── integration/  # Integration tests (with database)

.github/workflows/  # GitHub Actions CI/CD pipeline
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check with database status |
| GET | `/api/agents/check` | Run lightweight agent checks and return summaries |
| GET | `/api/docs` | Swagger API documentation |

## Configuration

Environment variables (see `.env.example`):
- `PYTHONUNBUFFERED=1` — Unbuffered Python output
- `DATABASE_DIR=.` — Database file directory
- `SQL_ECHO=false` — SQLAlchemy query logging
- `ENVIRONMENT=development` — Execution environment (development/staging/production)

## Development Workflow

1. **Create feature branch**: `git checkout -b feature/my-feature`
2. **Write tests first** (TDD approach)
3. **Implement feature** in `src/`
4. **Run tests**: `pytest tests/ -v`
5. **Code quality**: `black src/ && flake8 src/ && mypy src/`
6. **Commit and push**: `git push origin feature/my-feature`
7. **Create pull request**

## Architecture

### Phase 1: Setup ✅
- FastAPI app with `/health` endpoint
- SQLite database configuration
- pytest test framework
- CI/CD pipeline

### Phase 2: Foundational (In Progress)
- Data models (events, reports, suggestions)
- Persistence layer with Alembic migrations
- API routes shell
- Telemetry ingestion harness

### Phase 3: Ingestion & Normalization
- Event ingestion endpoint
- Data normalization pipeline
- Ledger persistence
- Schema validation

### Phase 4: Agentic Reasoning & Detection
- Reasoning engine
- Correlation engine
- Anomaly detection
- Health report generation

### Phase 5: Orchestration, Governance & CI Verdicts
- Action orchestration
- Governance rules and approvals
- Audit logging
- CI evaluation API

### Final Phase: Polish & Handoff
- Report API contract: `specs/004-ahms-backend/contracts/report-api.md`
- Backend quickstart: `specs/004-ahms-backend/quickstart.md`
- Security scanning in CI (Bandit + Gitleaks)

## Key Report Endpoints

- POST /api/reports/generate
- GET /api/reports/latest
- GET /api/reports/user (json or markdown)
- POST /api/reports/user/generate (one-shot generation + user report output)

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR:
- Python 3.12 tests
- Linting with flake8
- Type checking with mypy
- Code coverage with pytest
- Codecov integration

## Database

**Development**: SQLite (file-based, `ahms.db`)

**Production Migration Path**: PostgreSQL (with Alembic migrations)

## Troubleshooting

### ImportError: No module named 'fastapi'
```bash
pip install -r requirements-dev.txt
```

### Database lock errors
Delete `ahms.db` and restart:
```bash
rm ahms.db && python3 -m uvicorn src.api.main:app --reload
```

### Tests not found
Ensure `tests/` and `tests/unit/` have `__init__.py` files.

## Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write unit tests for new features
4. Update README if adding new endpoints or config variables

## License

Proprietary — Copyrighted to Interns Monitor Project

## Contact

For issues, questions, or contributions, contact the development team.
