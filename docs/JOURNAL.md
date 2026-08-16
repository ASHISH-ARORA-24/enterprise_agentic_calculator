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
