# Learning Notes

This file is our running reference. Every time we encounter a new concept —
OAuth, Entra ID, MCP, agents, Service Bus, etc. — we write a plain-language
explanation here before we implement it.

Use this as a glossary you built yourself.

---

## Table of Contents

Entries will be added here as we learn them.

---

<!-- New concepts go below this line, in the order we encounter them -->

---

## Iteration 1 Concepts

---

### FastAPI

A Python web framework for building HTTP APIs. It listens for incoming HTTP
requests and lets you write functions that handle them.

Why FastAPI over other frameworks (Flask, Django)?
- Automatic request validation via Pydantic — wrong input is rejected before your code runs
- Auto-generated interactive API docs at `/docs` (Swagger) and `/redoc`
- Built-in async support — important for agents calling multiple tools concurrently
- Very fast — one of the fastest Python frameworks

Key concepts:
- **Route** — a URL + HTTP method the server listens for (`POST /api/v1/calculate`)
- **APIRouter** — a group of related routes kept in one file, mounted in main.py
- **Request handler** — the function that runs when a matching request arrives

---

### Pydantic

A data validation library. You define a class with typed fields, and Pydantic:
- Validates incoming data automatically (wrong type → clear error, not a crash)
- Converts types where sensible (string `"25"` → Decimal `25`)
- Generates JSON schemas that FastAPI uses for auto-docs

`BaseModel` is the base class. `Literal` means only specific values are allowed.
`Field` adds metadata like descriptions for the docs.

```python
class CalculationRequest(BaseModel):
    operation: Literal["add", "subtract", "multiply", "divide"]
    a: Decimal
    b: Decimal
```

If someone sends `"operation": "explode"` — rejected automatically with a clear
422 error. You write zero validation code for this.

---

### Decimal vs Float

Python's `float` cannot represent all decimal numbers exactly:
```python
>>> 0.1 + 0.2
0.30000000000000004   # wrong!
```

This is a fundamental property of how binary floating point works.

`Decimal` is exact:
```python
>>> from decimal import Decimal
>>> Decimal("0.1") + Decimal("0.2")
Decimal("0.3")        # correct
```

Rule: always use `Decimal` in any application where precision matters
(calculators, financial systems, anything with money).

---

### HTTP Status Codes

Numbers that tell the caller what happened:

| Code | Meaning | When we use it |
|------|---------|----------------|
| 200 | OK | Successful calculation |
| 422 | Unprocessable Content | Invalid input (divide by zero, wrong type) |
| 500 | Internal Server Error | Simulated failure in fault mode |

The API always returns a typed JSON body alongside the status code so the
caller doesn't have to guess what went wrong.

---

### Health Endpoints

Two standard endpoints every service must have:

**`/health/live`** — Liveness probe. "Is the process alive?"
Returns 200 as long as the process is running. Never checks dependencies.
If this fails, the container is restarted.

**`/health/ready`** — Readiness probe. "Can this service accept traffic?"
Returns not_ready during fault injection, startup, or if dependencies are down.
If this fails, traffic is not sent to this instance (but it is not restarted).

Azure Container Apps and Kubernetes both use these two probes automatically.

---

### Fault Injection

A deliberate way to break the service for testing.

We read a `FAULT_MODE` environment variable:
- `none` — normal operation
- `unhealthy` — `/health/ready` returns not_ready
- `slow` — `/calculate` sleeps 10 seconds
- `calculate_500` — `/calculate` returns HTTP 500

This lets us test the failure path (Diagnosis Agent, approval workflow)
without actually breaking anything — we just toggle an env var.

Rule: fault injection must never be possible in production. Ours is read
from an env var that is simply not set in production.

---

### Uvicorn

The ASGI server that runs FastAPI. FastAPI defines what to do with a request —
Uvicorn is the engine that actually listens on a port and passes requests to FastAPI.

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`--reload` adds file watching — server restarts automatically when code changes.
Only use `--reload` in development, never in production.

---

### Docker

Docker packages your application into a portable unit called an **image**.
You run that image as a **container** — an isolated process that behaves
identically on any machine.

Key concepts:
- **Image** — the packaged application (read-only snapshot)
- **Container** — a running instance of an image
- **Dockerfile** — the recipe for building an image
- **Layer** — each instruction in a Dockerfile creates a layer; Docker caches layers

Why Docker for this project? Because all three services (calculator, agent API,
MCP server) need to run together in Azure Container Apps — Docker is how they
get there.

---

### Multi-Stage Docker Build

A technique to keep production images small and secure.

**Stage 1 (builder):** install all dependencies. Big and messy.
**Stage 2 (final):** copy only the installed packages. No build tools, no dev
dependencies, no package manager.

Result: the production image contains only what is needed to run the service.
Dev tools (Ruff, pytest, Pyright) are never shipped to production.

---

### Non-Root Docker User

By default, Docker runs as `root` inside the container — if an attacker
exploits a vulnerability, they get root access to the container.

We create a dedicated user (`appuser`) and switch to it before starting the
server. Now an attacker would get only `appuser` access — much less dangerous.

```dockerfile
RUN useradd --uid 1001 appuser
USER appuser
```

---

### conftest.py

A special pytest file that runs before tests are collected. We use it to add
the service directory to Python's module search path so imports work correctly
when pytest runs from the monorepo root.

pytest automatically loads every `conftest.py` it finds while traversing
directories — no import needed.

---

### PID File

When a process starts in the background, the OS assigns it a Process ID (PID).
A PID file saves that number to disk so another command can find and stop
the process later.

```bash
uvicorn app.main:app & echo $! > .calculator.pid   # save PID
kill $(cat .calculator.pid)                          # stop using PID
```

We use this for `make calculator-run` / `make calculator-stop`.

---

## Iteration 0 Concepts

---

### Monorepo

One Git repository that holds all services and shared packages together.

The alternative is a separate repo per service (called a polyrepo). For a
learning project, monorepo is simpler — you can see everything in one place,
share code easily, and run one `make test` to check everything at once.

---

### Git

Version control system. Tracks every change you make to every file. You can
go back in time, see what changed, and push code to GitHub for others to see.

Key commands:
- `git init` — start tracking a folder as a repository
- `git add .` — stage all changes (tell git "I want to include these in the next commit")
- `git commit -m "message"` — save a snapshot of the staged changes
- `git push` — send your commits to GitHub

---

### uv

Modern Python package manager. Does three things:
1. Creates and manages virtual environments (`.venv` folder)
2. Installs dependencies from `pyproject.toml`
3. Supports workspaces — manages multiple Python packages in one repo together

Key commands:
- `uv sync` — install all dependencies from pyproject.toml into .venv
- `uv run <command>` — run a command inside the virtual environment

Why not just `pip`? uv is dramatically faster, handles workspaces natively,
and manages the virtual environment for you automatically.

---

### Virtual Environment (`.venv`)

An isolated folder that contains Python and all the packages for this project.
Without it, installing packages would affect every Python project on your machine.

With `.venv`, each project has its own isolated set of packages. You never
commit `.venv` to Git — it is regenerated with `uv sync`.

---

### pyproject.toml

The standard Python project config file. Every Python project has one.
It declares:
- Project name and version
- What Python version it needs
- What libraries it depends on
- How dev tools (Ruff, Pyright, pytest) should behave

In a monorepo, the root `pyproject.toml` declares the workspace and shared
dev tooling. Each service has its own `pyproject.toml` for its runtime dependencies.

---

### Ruff

Python linter and formatter in one tool. Does two things:
- **Linting** — finds bugs and bad patterns (unused imports, undefined names, wrong naming)
- **Formatting** — enforces consistent code style (spacing, line length, import order)

Written in Rust — runs in milliseconds even on large codebases.
Replaces flake8, isort, and black.

Key commands:
- `uv run ruff check .` — lint, report problems (does not change files)
- `uv run ruff format .` — fix formatting (does change files)

---

### Pyright

Static type checker for Python. Python lets you add type hints:
```python
def add(a: int, b: int) -> int:
    return a + b
```
Pyright reads those hints and tells you if you pass the wrong type anywhere —
before you even run the code. Catches a whole class of bugs at zero runtime cost.

Key command:
- `uv run pyright` — check all type hints across the project

---

### pytest

Testing framework. You write functions that start with `test_`:
```python
def test_add():
    assert add(2, 3) == 5
```
pytest finds them automatically, runs them, and reports pass/fail.

Key commands:
- `uv run pytest` — run all tests
- `uv run pytest --cov=apps` — run tests and show coverage (which lines were not tested)

---

### Makefile

Simple automation file. Defines named targets (like `test`, `lint`, `up`) that
run one or more shell commands. Instead of remembering long commands, you just
type `make test`.

Key rule: indentation in a Makefile must use tabs, not spaces.

Key commands:
- `make help` — list all available commands
- `make check` — run test, test-cov, lint, typecheck in sequence
- `make setup` — install all dependencies

---

### CI — Continuous Integration (GitHub Actions)

Every time you push code to GitHub or open a pull request, GitHub automatically
runs a pipeline defined in `.github/workflows/ci.yml`.

Our pipeline runs: lint → format check → typecheck → tests.

If anything fails, GitHub shows a red cross on the PR. You cannot miss a
broken build because it is visible to everyone.

`.yml` files use YAML format — indentation-based config, no curly braces.

---

### `.gitignore`

A file that tells Git which files and folders to never track. Examples:
- `.env` — contains real secrets, must never be committed
- `.venv` — thousands of dependency files, regenerated with `uv sync`
- `__pycache__` — Python bytecode cache, auto-generated
- `.terraform` — Terraform working directory with potentially sensitive state

---

### `.env` vs `.env.example`

`.env` — your real config with real values. In `.gitignore`. Never committed.

`.env.example` — a template with all the variable names but no values.
Committed to Git. Anyone who clones the repo copies this to `.env` and fills
in their own values.

Rule: never put real values in `.env.example`.
