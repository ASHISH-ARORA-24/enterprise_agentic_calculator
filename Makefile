# Makefile — project automation for the Enterprise Agentic Calculator.
#
# Usage:
#   make setup      — install all dependencies
#   make test       — run all tests
#   make lint       — check code for errors and style issues
#   make format     — auto-fix formatting
#   make typecheck  — check type hints
#   make up         — start all services locally with Docker Compose
#   make down       — stop all services
#   make fault-on   — enable calculator fault injection (makes it fail)
#   make fault-off  — disable calculator fault injection (restore normal)
#
# .PHONY tells make these are command names, not file names.
# Without this, make would get confused if a file named "test" existed.
.PHONY: setup test test-cov check lint format typecheck up down fault-on fault-off help calculator-run calculator-stop

# ---------------------------------------------------------------------------
# Setup — install all workspace dependencies into .venv
# ---------------------------------------------------------------------------
setup:
	uv sync --all-packages

# ---------------------------------------------------------------------------
# Test — run all tests across all services
# ---------------------------------------------------------------------------
test:
	uv run pytest

# ---------------------------------------------------------------------------
# Test with coverage — shows which lines of code are not tested
# ---------------------------------------------------------------------------
test-cov:
	uv run pytest --cov=apps --cov=packages --cov-report=term-missing

# ---------------------------------------------------------------------------
# Check — run everything in sequence: coverage, lint, typecheck.
# Use this before committing or opening a pull request.
# Stops at the first failure so you see the most important error first.
# ---------------------------------------------------------------------------
check: test test-cov lint typecheck

# ---------------------------------------------------------------------------
# Lint — check code for errors, unused imports, bad naming, etc.
# Does not change any files — only reports problems.
# ---------------------------------------------------------------------------
lint:
	uv run ruff check .

# ---------------------------------------------------------------------------
# Format — auto-fix code style (spacing, import order, etc.)
# This DOES change files. Run before committing.
# ---------------------------------------------------------------------------
format:
	uv run ruff format .
	uv run ruff check . --fix

# ---------------------------------------------------------------------------
# Typecheck — verify type hints are correct across all services
# ---------------------------------------------------------------------------
typecheck:
	uv run pyright

# ---------------------------------------------------------------------------
# calculator-run  — start the calculator service in the background.
# calculator-stop — stop it using the saved PID file.
#
# A PID file (.calculator.pid) stores the process ID so calculator-stop
# knows exactly which process to kill.
# ---------------------------------------------------------------------------
calculator-run:
	@if lsof -i :8000 -t > /dev/null 2>&1; then \
		echo "Port 8000 is already in use — calculator may already be running."; \
		echo "  Swagger: http://localhost:8000/docs"; \
		echo "  Run 'make calculator-stop' to stop it first."; \
	else \
		cd apps/calculator_service && \
		uv run uvicorn app.main:app --port 8000 --host 0.0.0.0 --log-level warning & \
		echo $$! > ../../.calculator.pid; \
		sleep 2; \
		echo ""; \
		echo "  Calculator Service is running."; \
		echo ""; \
		echo "  API:     http://localhost:8000"; \
		echo "  Swagger: http://localhost:8000/docs"; \
		echo "  ReDoc:   http://localhost:8000/redoc"; \
		echo ""; \
		echo "  Run 'make calculator-stop' to stop it."; \
		echo ""; \
	fi

calculator-stop:
	@if [ -f .calculator.pid ]; then \
		kill $$(cat .calculator.pid) 2>/dev/null || true; \
		rm -f .calculator.pid; \
		echo "Calculator Service stopped."; \
	else \
		PIDS=$$(lsof -i :8000 -t 2>/dev/null); \
		if [ -n "$$PIDS" ]; then \
			kill $$PIDS 2>/dev/null || true; \
			echo "Calculator Service stopped."; \
		else \
			echo "Calculator Service is not running."; \
		fi \
	fi

# ---------------------------------------------------------------------------
# Docker Compose — start and stop all services locally
# Requires Docker to be running.
# docker-compose.yml is created in Iteration 2.
# ---------------------------------------------------------------------------
up:
	docker compose up --build -d

down:
	docker compose down

# ---------------------------------------------------------------------------
# Fault injection — toggle calculator failure mode for local testing.
# These use the Docker Compose service name "calculator".
# Implemented fully in Iteration 1.
# ---------------------------------------------------------------------------
fault-on:
	docker compose exec calculator sh -c 'echo "FAULT_MODE=unhealthy" >> /etc/environment'
	@echo "Fault injection enabled — calculator will report unhealthy"

fault-off:
	docker compose exec calculator sh -c 'sed -i "/FAULT_MODE/d" /etc/environment'
	@echo "Fault injection disabled — calculator restored to normal"

# ---------------------------------------------------------------------------
# Help — list all available commands with descriptions
# ---------------------------------------------------------------------------
help:
	@echo ""
	@echo "Enterprise Agentic Calculator — available commands"
	@echo ""
	@echo "SETUP"
	@echo "  make setup                   Install all dependencies into .venv"
	@echo ""
	@echo "CODE QUALITY"
	@echo "  make lint                    Check code for errors (does not change files)"
	@echo "  make format                  Auto-fix code style and import order"
	@echo "  make typecheck               Verify type hints are correct"
	@echo ""
	@echo "TESTING"
	@echo "  make test                    Run all tests across all services"
	@echo "  make test-cov                Run tests and show coverage report"
	@echo "  make check                   Run test-cov + lint + typecheck in sequence (use before committing)"
	@echo ""
	@echo "LOCAL SERVICES (no Docker needed)"
	@echo "  make calculator-run          Start calculator in background + print Swagger URL"
	@echo "  make calculator-stop         Stop the running calculator"
	@echo ""
	@echo "LOCAL SERVICES (requires Docker)"
	@echo "  make up                      Build and start all services"
	@echo "  make down                    Stop all services"
	@echo ""
	@echo "FAULT INJECTION (requires services running)"
	@echo "  make fault-on                Break the calculator (simulates failure)"
	@echo "  make fault-off               Restore the calculator to normal"
	@echo ""
	@echo "Parameters:"
	@echo "  make test-cov                No extra parameters"
	@echo "  make fault-on                No extra parameters — uses FAULT_MODE=unhealthy"
	@echo ""
