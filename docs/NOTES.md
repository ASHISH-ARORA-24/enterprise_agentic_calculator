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
