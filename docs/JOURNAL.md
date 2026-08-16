# Build Journal

Dated log of what we completed each session.

---

## 2026-08-16 — Iteration 0 complete

### What we did
- Read and understood the full project specification
- Agreed on learning approach: explain every concept before implementing it
- Created `docs/NOTES.md`, `docs/JOURNAL.md`, `docs/ITERATIONS.md`
- Initialised Git repository and pushed to GitHub
- Created full monorepo folder structure (`apps/`, `packages/`, `infra/`, `scripts/`, `.github/`)
- Created root `pyproject.toml` — uv workspace + Ruff + Pyright + pytest config
- Created `pyproject.toml` for all 6 workspace members (3 apps + 3 packages)
- Ran `uv sync` — installed Ruff, Pyright, pytest, pytest-asyncio, pytest-cov
- Created `.gitignore` — protects secrets, venv, caches, Terraform state
- Created `.env.example` — variable names only, no real values
- Created `Makefile` — setup, test, test-cov, check, lint, format, typecheck, up, down, fault-on, fault-off, help
- Created `README.md` skeleton with architecture overview and quick start
- Created `.github/workflows/ci.yml` — CI pipeline skeleton
- Created placeholder `__init__.py` and test files for all services
- Fixed pytest import mode for monorepo (importlib mode)

### Acceptance criteria — all met
- `make test` passes — 4 tests collected and passed
- `make lint` passes — 0 errors
- `make typecheck` passes — 0 errors
- `make check` runs all four steps in sequence

### Concepts learned
See `docs/NOTES.md` — monorepo, Git, uv, virtual environments, pyproject.toml,
Ruff, Pyright, pytest, Makefile, CI, .gitignore, .env vs .env.example

### Next
Iteration 1 — Calculator Service (local)

---

## 2026-08-16 — Iteration 1 complete

### What we built
- Full folder structure for `apps/calculator_service/` (api, domain, models, observability)
- `settings.py` — all config read from environment variables via pydantic-settings
- `app/domain/errors.py` — typed error codes and domain exceptions (DivideByZeroError)
- `app/domain/calculator.py` — pure Python arithmetic using Decimal (add, subtract, multiply, divide)
- `app/models/schemas.py` — Pydantic models (CalculationRequest, CalculationResponse, ErrorResponse, HealthResponse, VersionResponse)
- `app/api/routes.py` — all HTTP endpoints (POST /api/v1/calculate, GET /health/live, GET /health/ready, GET /api/v1/version)
- `app/main.py` — FastAPI app entry point
- `apps/calculator_service/conftest.py` — pytest path fix for monorepo
- `apps/calculator_service/Dockerfile` — multi-stage build, non-root user, health check
- `tests/test_domain.py` — 20 unit tests for arithmetic logic
- `tests/test_api.py` — 15 API tests covering all endpoints, validation, fault modes
- `make calculator-run` / `make calculator-stop` — start/stop service locally

### Acceptance criteria — all met
- All four operations work correctly
- Decimal precision correct (0.1 + 0.2 = 0.3)
- Divide by zero returns typed DIVIDE_BY_ZERO error
- Invalid input returns 422 automatically via Pydantic
- Fault injection modes work (unhealthy, calculate_500)
- Docker image builds and runs (224MB)
- 39 tests pass, 99% coverage, 0 lint errors, 0 type errors

### Concepts learned
See `docs/NOTES.md` — FastAPI, Pydantic, Decimal, HTTP status codes, health
endpoints, fault injection, Uvicorn, Docker, multi-stage builds, non-root user,
conftest.py, PID files

### Next
Iteration 2 — Simple Agent calls Calculator

---
