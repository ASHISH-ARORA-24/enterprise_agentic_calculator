# Enterprise Agentic Calculator Operations Platform

> The calculator is intentionally boring. The enterprise architecture is the project.

A learning project that demonstrates how to build, secure, deploy, and operate
an agentic AI system to enterprise standards on Microsoft Azure.

A user asks a natural language question. An agent answers it by calling a tool —
never by doing mental arithmetic. When the tool is unavailable, the system
diagnoses the failure, proposes a remediation, waits for human approval, executes
the approved action, verifies recovery, and retries the original request — with a
full audit trail and end-to-end observability throughout.

---

## What this project covers

- Microsoft Entra ID authentication (OAuth 2.0 / OIDC)
- Role-based access control (User, Operator, Approver, Admin)
- Supervisor → Calculator / Diagnosis / Remediation agent pattern
- Model Context Protocol (MCP) as the tool boundary
- Deterministic policy controls — the LLM never authorises itself
- Human-in-the-loop approval before privileged actions
- Durable workflow state with PostgreSQL
- Async remediation via Azure Service Bus with DLQ handling
- Managed Identity and Key Vault for secrets-free service communication
- OpenTelemetry + Application Insights end-to-end observability
- Terraform infrastructure as code
- GitHub Actions CI/CD with Azure workload identity federation

---

## Architecture

```
User (Entra ID login)
  └─► Agent API (Azure Container App)
        └─► Supervisor Agent
              ├─► Calculator Agent ──► MCP Server ──► Calculator Service
              ├─► Diagnosis Agent  ──► MCP Server (read-only tools)
              └─► Remediation Agent ─► MCP Server (approved action only)

Cross-cutting:
  PostgreSQL     — durable workflow and audit state
  Service Bus    — async remediation commands
  Key Vault      — secrets management
  Managed Identity — workload-to-Azure authentication
  Application Insights — traces, metrics, logs
```

---

## Local quick start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — Python package manager
- Docker Desktop

### Setup

```bash
# Clone the repository
git clone git@github.com:ASHISH-ARORA-24/enterprise_agentic_calculator.git
cd enterprise_agentic_calculator

# Copy environment variable template and fill in your values
cp .env.example .env

# Install all dependencies
make setup
```

### Run locally

```bash
# Start all services
make up

# Run all tests
make test

# Check code quality
make lint
make typecheck
```

### Fault injection (for testing the failure path)

```bash
# Break the calculator — triggers the diagnosis and approval workflow
make fault-on

# Restore normal operation
make fault-off
```

### All available commands

```bash
make help
```

---

## Project structure

```
apps/
  calculator_service/   FastAPI calculator microservice
  agent_api/            User-facing agent API and orchestrator
  mcp_server/           MCP tool server (calculate, diagnose, remediate)

packages/
  contracts/            Shared Pydantic models used by all services
  telemetry/            Shared OpenTelemetry setup
  common/               Shared utilities (error codes, logging, retries)

infra/
  terraform/            Azure infrastructure as code

.github/workflows/      CI/CD pipelines (GitHub Actions)
docs/                   Architecture docs, ADRs, runbooks, demo script
scripts/                Local helper scripts
```

---

## Documentation

| Document | Description |
|---|---|
| [docs/ITERATIONS.md](docs/ITERATIONS.md) | Full build plan with detailed substeps |
| [docs/NOTES.md](docs/NOTES.md) | Concept explanations built up as we learn |
| [docs/JOURNAL.md](docs/JOURNAL.md) | Session-by-session progress log |
| docs/architecture/ | Architecture diagrams, ADRs, design decisions |
| docs/demo/ | 10-minute demo script |
| docs/runbooks/ | Operations runbook |

---

## Build status

| Iteration | Description | Status |
|---|---|---|
| 0 | Repository Bootstrap | 🔄 In progress |
| 1 | Calculator Service (local) | Not started |
| 2 | Simple Agent calls Calculator | Not started |
| 3 | Deploy to Azure | Not started |
| 4 | Entra ID + RBAC | Not started |
| 5 | Managed Identity + Key Vault | Not started |
| 6 | MCP Tool Server | Not started |
| 7 | Multi-Agent Orchestration | Not started |
| 8 | Durable Workflow State | Not started |
| 9 | Human Approval | Not started |
| 10 | Service Bus + Async Remediation | Not started |
| 11 | Privileged Remediation Tool | Not started |
| 12 | Enterprise Observability | Not started |
| 13 | CI/CD + Deployment Hardening | Not started |
| 14 | Security + Chaos Testing | Not started |
| 15 | Final Docs + Interview Pack | Not started |
