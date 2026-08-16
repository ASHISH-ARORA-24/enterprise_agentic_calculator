# Build Iterations — Enterprise Agentic Calculator Operations Platform

This is our step-by-step build plan. Every iteration must be fully complete
(code + tests + docs updated) before moving to the next one.

**Definition of done for every iteration:**
- Code implemented
- Unit tests pass
- Integration test exists where appropriate
- Errors are typed (no raw exception strings in flow control)
- Timeouts are configured on every network call
- Retry caps are deterministic constants in code, not prompts
- Security impact considered
- Logs contain correlation IDs
- NOTES.md updated with new concepts learned
- JOURNAL.md updated with what was completed
- Docker / local path still works
- No secrets committed to Git
- CI is green

---

## Iteration 0 — Repository Bootstrap

**Goal:** Engineering baseline. No business logic. Just the skeleton every
other iteration builds on top of.

- [ ] 0.1 — Initialise Git repository (`git init`)
- [ ] 0.2 — Create monorepo folder structure:
  ```
  apps/calculator_service/
  apps/agent_api/
  apps/mcp_server/
  packages/contracts/
  packages/telemetry/
  packages/common/
  infra/terraform/
  .github/workflows/
  docs/
  scripts/
  ```
- [ ] 0.3 — Create root `pyproject.toml` (uv workspace declaration + Ruff + Pyright + pytest config)
- [ ] 0.4 — Create `pyproject.toml` for each app: `calculator-service`, `agent-api`, `mcp-server`
- [ ] 0.5 — Create `pyproject.toml` for each package: `eac-contracts`, `eac-telemetry`, `eac-common`
- [ ] 0.6 — Install dev dependencies with `uv sync` (ruff, pyright, pytest, pytest-asyncio, pytest-cov)
- [ ] 0.7 — Create `.gitignore` (covers `.env`, `__pycache__`, `.venv`, `.terraform`, `*.tfstate`)
- [ ] 0.8 — Create `.env.example` (variable names only — no real values ever)
- [ ] 0.9 — Create `Makefile` with targets: `setup`, `test`, `lint`, `format`, `typecheck`, `up`, `down`, `fault-on`, `fault-off`
- [ ] 0.10 — Create `README.md` skeleton (project name, purpose, local run commands)
- [ ] 0.11 — Create CI skeleton `.github/workflows/ci.yml` (checkout → install → lint → typecheck → test)
- [ ] 0.12 — Create placeholder `__init__.py` in every app and package directory
- [ ] 0.13 — Create one placeholder test per service so pytest has something to discover
- [ ] 0.14 — Run `make lint` — must pass with zero errors
- [ ] 0.15 — Run `make typecheck` — must pass
- [ ] 0.16 — Run `make test` — must pass from a clean clone
- [ ] 0.17 — Update `docs/NOTES.md` with: monorepo, uv, Ruff, Pyright, pytest, Makefile, CI
- [ ] 0.18 — Update `docs/JOURNAL.md`

**Acceptance:** `make test` passes from a clean clone.

---

## Iteration 1 — Calculator Service (Local)

**Goal:** A working FastAPI calculator that runs locally and in Docker.
No agents, no Azure, no auth. Just pure arithmetic exposed as an API.

- [ ] 1.1 — Create folder structure inside `apps/calculator_service/`:
  ```
  app/
    api/
    domain/
    models/
    observability/
    main.py
    settings.py
  tests/
  Dockerfile
  ```
- [ ] 1.2 — Write `settings.py` — reads all config from environment variables (port, fault mode, log level)
- [ ] 1.3 — Write domain logic in `app/domain/calculator.py` — pure Python functions:
  - `add(a, b)`, `subtract(a, b)`, `multiply(a, b)`, `divide(a, b)`
  - Use `Decimal` for all arithmetic (not `float` — avoids floating point errors)
  - `divide` raises a typed `DivideByZeroError` — no raw Python `ZeroDivisionError`
  - No `eval()` — ever
- [ ] 1.4 — Write unit tests for domain logic:
  - add, subtract, multiply, divide — basic cases
  - divide by zero → typed error
  - decimal precision test (e.g. 0.1 + 0.2 = 0.3 exactly)
  - large numbers
  - negative numbers
- [ ] 1.5 — Create Pydantic models in `app/models/`:
  - `CalculationRequest` — operation (add/subtract/multiply/divide), a (Decimal), b (Decimal)
  - `CalculationResponse` — operation, a, b, result (Decimal), request_id (UUID)
  - `ErrorResponse` — code (string from error taxonomy), message
- [ ] 1.6 — Define error taxonomy constants in `app/domain/errors.py`:
  - `DIVIDE_BY_ZERO`, `INVALID_OPERATION`, `CALCULATOR_UNAVAILABLE`, `SIMULATED_FAILURE`
- [ ] 1.7 — Build `POST /api/v1/calculate` endpoint:
  - Validates request with Pydantic (wrong types rejected automatically)
  - Calls domain function
  - Returns `CalculationResponse` with a new `request_id` UUID on every call
  - Division by zero → HTTP 422 with typed `ErrorResponse`
- [ ] 1.8 — Build `GET /health/live` endpoint:
  - Returns `{"status": "alive"}`
  - Never calls external dependencies — just confirms the process is running
- [ ] 1.9 — Build `GET /health/ready` endpoint:
  - Returns `{"status": "ready"}` normally
  - Returns `{"status": "not_ready", "reason": "simulated_failure"}` when fault mode is active
- [ ] 1.10 — Build `GET /api/v1/version` endpoint:
  - Returns service name and version from settings
- [ ] 1.11 — Add fault injection mode (reads from environment variable `FAULT_MODE`):
  - `none` — normal operation
  - `unhealthy` — readiness returns not_ready
  - `slow` — calculate sleeps 10 seconds before responding
  - `calculate_500` — calculate returns HTTP 500
  - Fault mode only works in non-production environments
- [ ] 1.12 — Add `request_id` (UUID) to every calculate response
- [ ] 1.13 — Add placeholder OpenTelemetry span around the calculate function (filled out fully in Iteration 12)
- [ ] 1.14 — Write `main.py` — FastAPI app entry point with app factory
- [ ] 1.15 — Write API-level tests (using FastAPI TestClient):
  - All four operations return correct results
  - Request with missing field → 422
  - Request with wrong type → 422
  - Divide by zero → 422 with typed error code
  - `/health/live` → 200
  - `/health/ready` in normal mode → 200 ready
  - `/health/ready` in fault mode → 200 not_ready
  - Fault mode `calculate_500` → 500
- [ ] 1.16 — Run `make test` — all tests pass
- [ ] 1.17 — Run `make lint` and `make typecheck` — zero errors
- [ ] 1.18 — Create `Dockerfile` for calculator service (multi-stage build, non-root user)
- [ ] 1.19 — Build Docker image locally and verify it starts
- [ ] 1.20 — Test all endpoints manually against the running Docker container
- [ ] 1.21 — Update `docs/NOTES.md` with: FastAPI, Pydantic, Decimal arithmetic, health endpoints, fault injection, Dockerfile
- [ ] 1.22 — Update `docs/JOURNAL.md`

**Acceptance:** All operations work locally. Docker container works.

---

## Iteration 2 — Simple Agent Calls Calculator

**Goal:** Prove that an agent can take a natural language question, call the
calculator tool, and return the answer — before adding any cloud complexity.
Calculator-down must return a typed failure, not a hallucinated answer.

**Framework:** LangChain + LangChain-OpenAI.
Tools are defined with the `@tool` decorator. The agent is a LangChain
`AgentExecutor` wrapping a `create_tool_calling_agent`. This is the
pattern we carry forward into all later iterations.

- [ ] 2.1 — Create folder structure inside `apps/agent_api/`:
  ```
  agent_api/          ← unique package name (not "app") to avoid monorepo conflicts
    api/
    agents/
    tools/
    models/
    main.py
    settings.py
  tests/
  Dockerfile
  ```
- [ ] 2.2 — Write `settings.py` for agent API — LLM model name, calculator service URL, timeouts, log level
- [ ] 2.3 — Add `ToolResult` contract to `packages/contracts/contracts/tools.py`:
  ```python
  class ToolResult(BaseModel):
      success: bool
      code: str
      message: str
      data: dict = {}
      retryable: bool = False
      correlation_id: str
  ```
- [ ] 2.4 — Add `AgentRequest` and `AgentResponse` contracts to `packages/contracts/contracts/agent.py`:
  ```python
  class AgentRequest(BaseModel):
      message: str
      conversation_id: UUID | None = None


  class AgentResponse(BaseModel):
      answer: str
      tool_called: bool
      correlation_id: str
  ```
- [ ] 2.5 — Build calculator tool in `agent_api/tools/calculator_tool.py` using LangChain `@tool` decorator:
  - `@tool` decorator generates the JSON schema for the LLM automatically
  - Internally calls calculator service HTTP endpoint
  - 3-second timeout (constant)
  - 1 retry on transient error (constant cap)
  - Returns a string result or error description (LangChain tools return strings)
  - On calculator-down → returns typed error string the agent can report honestly
- [ ] 2.6 — Write Calculator Agent in `agent_api/agents/calculator_agent.py` using LangChain:
  - `ChatOpenAI` as the LLM
  - `create_tool_calling_agent` + `AgentExecutor` as the execution pattern
  - System prompt: MUST call the calculate tool — never answer arithmetic directly
  - `with_structured_output` for the final `AgentResponse`
- [ ] 2.7 — Build `POST /api/v1/agent/query` endpoint:
  - Accepts `AgentRequest`
  - Calls Calculator Agent
  - Returns `AgentResponse`
- [ ] 2.8 — Build `GET /health/live` and `GET /health/ready` for agent API
- [ ] 2.9 — Write agent tests (mock LangChain internals):
  - "What is 25 times 8?" → tool called, result 200
  - "What is 10 divided by 2?" → tool called, result 5
  - Calculator service is down → typed `SERVICE_UNAVAILABLE` in response, no hallucinated answer
  - Calculator call times out → typed `TOOL_TIMEOUT`, not a hang
- [ ] 2.10 — Run `make test` — all tests pass
- [ ] 2.11 — Run `make lint` and `make typecheck` — zero errors
- [ ] 2.12 — Create `Dockerfile` for agent API
- [ ] 2.13 — Create `docker-compose.yml` at the repo root to run both services together
- [ ] 2.14 — Test end to end locally with `docker-compose up`
- [ ] 2.15 — Update `docs/NOTES.md` with: LangChain, @tool decorator, AgentExecutor, tool calling, timeouts
- [ ] 2.16 — Update `docs/JOURNAL.md`

**Acceptance:** Natural language question causes a real calculator API call. Calculator-down returns typed failure — not a hallucinated answer.

---

## Iteration 3 — Deploy to Azure

**Goal:** Both services running in Azure. Agent calls cloud calculator.
Everything provisioned with Terraform — no manual clicking in the portal.

- [ ] 3.1 — Install Azure CLI and Terraform if not already installed
- [ ] 3.2 — Create Terraform module: `infra/terraform/modules/resource_group/`
- [ ] 3.3 — Create Terraform module: `infra/terraform/modules/acr/` (Azure Container Registry — private image store)
- [ ] 3.4 — Create Terraform module: `infra/terraform/modules/monitoring/` (Log Analytics workspace + Application Insights)
- [ ] 3.5 — Create Terraform module: `infra/terraform/modules/container_apps/` (Container Apps environment)
- [ ] 3.6 — Wire calculator Container App inside container_apps module
- [ ] 3.7 — Wire agent API Container App inside container_apps module
- [ ] 3.8 — Create environment variable files: `infra/terraform/environments/dev/terraform.tfvars`
- [ ] 3.9 — Run `terraform init` and `terraform plan` — review output
- [ ] 3.10 — Run `terraform apply` for dev environment
- [ ] 3.11 — Build calculator Docker image and push to ACR
- [ ] 3.12 — Build agent API Docker image and push to ACR
- [ ] 3.13 — Update Container Apps to use the new images from ACR
- [ ] 3.14 — Run smoke tests against live Azure endpoints:
  - Calculator `/health/live` → 200
  - Agent `/health/live` → 200
  - Agent query "What is 6 plus 7?" → answer 13
- [ ] 3.15 — Add smoke test script to `scripts/smoke_test.sh`
- [ ] 3.16 — Update `docs/NOTES.md` with: Docker, ACR, Container Apps, Terraform, resource groups, regions
- [ ] 3.17 — Update `docs/JOURNAL.md`

**Acceptance:** Both services reachable in Azure. Agent calls cloud calculator and returns correct answer.

---

## Iteration 4 — Entra ID + RBAC

**Goal:** No one can call the agent API without logging in. Wrong role gets
rejected. This is the user identity layer — not workload identity (that is Iteration 5).

- [ ] 4.1 — Learn and document in NOTES.md: OAuth 2.0, OIDC, JWT, access tokens, scopes, application roles
- [ ] 4.2 — Create Entra app registration for Agent API (Application A) in Azure portal or via script:
  - Expose API scope: `api://<client-id>/access_as_user`
  - Define application roles: `Calculator.User`, `Calculator.Operator`, `Calculator.Approver`, `Calculator.Admin`
- [ ] 4.3 — Create Entra app registration for Client/UI (Application B):
  - Grants access to the Agent API scope
  - Used by Postman or Swagger for testing
- [ ] 4.4 — Document the registration steps in `docs/architecture/entra-setup.md`
- [ ] 4.5 — Write JWT validation middleware in `apps/agent_api/app/auth/`:
  - Validates: issuer, audience, signature, token lifetime, tenant
  - Extracts user's roles from token claims
  - Returns `401` for missing or invalid token
- [ ] 4.6 — Write `require_role(role)` dependency — returns `403` if user lacks the role
- [ ] 4.7 — Write `require_any_role(*roles)` dependency — accepts any of the listed roles
- [ ] 4.8 — Protect `POST /api/v1/agent/query` with `Calculator.User` role minimum
- [ ] 4.9 — Write auth unit tests using mocked JWKS (so tests do not need a real Entra tenant):
  - No token → 401
  - Invalid / expired token → 401
  - Valid token, wrong role → 403
  - Valid token, correct role → 200
- [ ] 4.10 — Test manually with a real Entra token obtained via Postman OAuth2 flow
- [ ] 4.11 — Update Terraform to pass Entra client ID / tenant ID as Container App environment variables
- [ ] 4.12 — Run `make test` — all tests pass
- [ ] 4.13 — Run `make lint` and `make typecheck` — zero errors
- [ ] 4.14 — Update `docs/NOTES.md` with: OAuth 2.0 in plain language, OIDC, JWT anatomy, Entra app registrations, application roles vs API scopes
- [ ] 4.15 — Update `docs/JOURNAL.md`

**Acceptance:** Unauthenticated → 401. Wrong role → 403. Correct role → 200.

---

## Iteration 5 — Managed Identity + Key Vault

**Goal:** Services authenticate to Azure resources using their identity —
no passwords, no connection strings stored anywhere.

- [ ] 5.1 — Learn and document in NOTES.md: managed identity, DefaultAzureCredential, Key Vault, least-privilege principle
- [ ] 5.2 — Create Terraform module: `infra/terraform/modules/identity/` (user-assigned managed identity for agent API)
- [ ] 5.3 — Create Terraform module: `infra/terraform/modules/key_vault/` (Key Vault for secrets that cannot use identity)
- [ ] 5.4 — Assign managed identity `Key Vault Secrets User` role (least privilege — read-only)
- [ ] 5.5 — Move any secrets (e.g. LLM API key) into Key Vault — never in environment variables or code
- [ ] 5.6 — Update agent API to read secrets using `DefaultAzureCredential` + Key Vault SDK:
  - Works locally with developer's Azure login
  - Works in Azure with managed identity — same code, no credentials in containers
- [ ] 5.7 — Assign managed identity to the agent API Container App in Terraform
- [ ] 5.8 — Remove all long-lived secrets from Container App environment variables
- [ ] 5.9 — Test: deployed agent API reads Key Vault secret using identity — no explicit credential needed
- [ ] 5.10 — Run `make test` — all tests pass
- [ ] 5.11 — Update `docs/NOTES.md` with: managed identity vs service principal, DefaultAzureCredential chain, Key Vault access patterns
- [ ] 5.12 — Update `docs/JOURNAL.md`

**Acceptance:** Deployed service accesses Key Vault using managed identity. No long-lived secret required for that path.

---

## Iteration 6 — MCP Tool Server

**Goal:** Move tools behind the Model Context Protocol. LangChain agents
discover and call tools through MCP using the `langchain-mcp-adapters`
package. This is the standard tool boundary the whole platform uses.

- [ ] 6.1 — Learn and document in NOTES.md: what MCP is, why it exists, tool discovery, langchain-mcp-adapters
- [ ] 6.2 — Create folder structure inside `apps/mcp_server/`:
  ```
  mcp_server/         ← unique package name to avoid monorepo conflicts
    server.py
    tools/
      calculator.py
      diagnostics.py
      remediation.py    (stub only — restart not enabled yet)
    auth/
    policies/
    observability/
  tests/
  Dockerfile
  ```
- [ ] 6.3 — Add `mcp`, `langchain-mcp-adapters` dependencies to `apps/mcp_server/pyproject.toml`
- [ ] 6.4 — Build `calculate` MCP tool (using `@tool` or MCP SDK):
  - Calls calculator service HTTP endpoint
  - 3-second timeout (constant)
  - On failure → typed error string the LangChain agent can report honestly
- [ ] 6.5 — Build `check_health` MCP tool:
  - Calls calculator `/health/ready` with 2-second timeout, 2 retries
  - Returns: healthy / unhealthy / unreachable
- [ ] 6.6 — Build `get_runtime_status` MCP tool:
  - Local mode: check Docker container status via controlled adapter
  - Azure mode: query only the configured Calculator Container App status
- [ ] 6.7 — Build `get_recent_logs` MCP tool:
  - Maximum 20 records, maximum 5-minute window
  - Redacts secrets, tokens, authorization headers from log content
- [ ] 6.8 — Create `restart_calculator` stub that always returns `TOOL_NOT_ALLOWED` (enabled in Iteration 11)
- [ ] 6.9 — Add timeout constant on every MCP tool call
- [ ] 6.10 — Refactor Calculator Agent to load MCP tools via `langchain-mcp-adapters`
  instead of direct HTTP adapter — same `@tool` interface, different transport
- [ ] 6.11 — Write MCP tool tests:
  - `calculate` — success case
  - `calculate` — calculator down → SERVICE_UNAVAILABLE
  - `check_health` — healthy
  - `check_health` — timeout → HEALTH_CHECK_TIMEOUT
  - `get_recent_logs` — records bounded to max count
  - `get_recent_logs` — secrets redacted from output
  - `restart_calculator` — always returns TOOL_NOT_ALLOWED at this stage
- [ ] 6.12 — Create `Dockerfile` for MCP server
- [ ] 6.13 — Update `docker-compose.yml` to include MCP server
- [ ] 6.14 — Run `make test` — all tests pass
- [ ] 6.15 — Run `make lint` and `make typecheck` — zero errors
- [ ] 6.16 — Update `docs/NOTES.md` with: MCP, langchain-mcp-adapters, read-only vs mutating tools, why MCP is the boundary not the auth layer
- [ ] 6.17 — Update `docs/JOURNAL.md`

**Acceptance:** LangChain agents discover and use MCP tools. Tool contracts tested.

---

## Iteration 7 — Multi-Agent Orchestration

**Goal:** Introduce the full supervisor-worker pattern and the
planner-executor diagnostic flow using **LangGraph** (LangChain's
graph-based multi-agent framework).

**Why LangGraph for multi-agent?**
LangGraph lets you define agents as nodes in a directed graph with typed
state. The Supervisor is a router node that decides which worker node runs
next. State flows between nodes. This maps directly to our supervisor-worker
pattern and handles the async incident workflow naturally.

- [ ] 7.1 — Learn and document in NOTES.md: LangGraph, StateGraph, nodes, edges, supervisor-worker pattern, planner-executor pattern
- [ ] 7.2 — Add `langgraph`, `langchain`, `langchain-openai` dependencies to `apps/agent_api/pyproject.toml`
- [ ] 7.3 — Create project-owned `AgentRunner` protocol in `packages/contracts/contracts/agent.py`:
  ```python
  class AgentRunner(Protocol):
      async def run(self, input: AgentInput) -> AgentOutput: ...
  ```
  (This abstraction means we can swap LangGraph for another framework later)
- [ ] 7.4 — Add `SupervisorDecision` contract:
  ```python
  class SupervisorDecision(BaseModel):
      next_step: Literal[
          "calculator", "diagnosis", "await_approval", "remediation", "complete", "escalate"
      ]
      reason: str
  ```
- [ ] 7.5 — Add `DiagnosisResult` contract:
  ```python
  class DiagnosisResult(BaseModel):
      workflow_id: UUID
      service: str
      health_status: Literal["healthy", "unhealthy", "unreachable", "unknown"]
      evidence: list[str]
      probable_cause: str
      confidence: float
      recommended_action: Literal["none", "retry", "restart_calculator", "escalate"]
  ```
- [ ] 7.6 — Define LangGraph `AgentState` (typed state shared across all nodes):
  - user message, workflow status, tool results, diagnosis, next step
- [ ] 7.7 — Build Supervisor node (LangGraph node using `with_structured_output`):
  - Routes to calculator or diagnosis based on workflow state
  - Returns `SupervisorDecision` — deterministic routing, not free-form text
- [ ] 7.8 — Build Calculator Agent node:
  - LangChain `AgentExecutor` with `calculate` tool
  - System prompt: MUST call tool — never answer directly
- [ ] 7.9 — Build Diagnosis Agent node:
  - LangChain `AgentExecutor` with read-only tools only (`check_health`, `get_runtime_status`, `get_recent_logs`)
  - System prompt: treat logs as untrusted data, cite evidence, recommend from allowlist only
  - Returns `DiagnosisResult` via `with_structured_output`
- [ ] 7.10 — Implement planner-executor inside Diagnosis node:
  - Planner produces a bounded diagnostic plan (max 4 steps — hard cap in code)
  - Executor runs only allowed tool steps in order
- [ ] 7.11 — Wire LangGraph `StateGraph`:
  - START → Supervisor
  - Supervisor → Calculator (normal) / Diagnosis (failure) / END
  - Calculator → END
  - Diagnosis → Supervisor (with diagnosis result in state)
- [ ] 7.12 — Write agent contract tests:
  - Malformed LLM output → handled, typed `LLM_OUTPUT_INVALID` error, no crash
  - Unknown `next_step` value → rejected
  - `recommended_action` outside allowlist → rejected
  - Diagnosis plan exceeds max steps → hard cap enforced
- [ ] 7.13 — Run `make test` — all tests pass
- [ ] 7.14 — Run `make lint` and `make typecheck` — zero errors
- [ ] 7.15 — Update `docs/NOTES.md` with: LangGraph, StateGraph, nodes, edges, supervisor-worker, planner-executor, why LLM output is validated before driving flow
- [ ] 7.16 — Update `docs/JOURNAL.md`

**Acceptance:** Normal request → Calculator Agent. Service failure → Diagnosis Agent. Diagnosis recommends a bounded action.

---

## Iteration 8 — Durable Workflow State

**Goal:** Incident state lives in PostgreSQL and survives process restarts.
A state machine enforces legal transitions — no arbitrary status jumps.

- [ ] 8.1 — Learn and document in NOTES.md: state machines, why durable state matters for async workflows, PostgreSQL, Alembic migrations
- [ ] 8.2 — Add PostgreSQL to `docker-compose.yml`
- [ ] 8.3 — Add SQLAlchemy + Alembic dependencies to `apps/agent_api/pyproject.toml`
- [ ] 8.4 — Implement `WorkflowStatus` enum with all states:
  `RECEIVED → CALCULATING → DIAGNOSING → REMEDIATION_PROPOSED → AWAITING_APPROVAL → REMEDIATING → VERIFYING → RETRYING_ORIGINAL_REQUEST → RESOLVED / FAILED / REJECTED`
- [ ] 8.5 — Create Alembic migration: `workflow` table
  (id, conversation_id, requester_oid, requester_name, original_message, status, state_version, correlation_id, created_at, updated_at, completed_at)
- [ ] 8.6 — Create Alembic migration: `workflow_event` table (append-only audit log)
  (id, workflow_id, event_type, actor_type, actor_id, payload_json, created_at)
- [ ] 8.7 — Create Alembic migration: `diagnosis` table
  (workflow_id, health_status, evidence_json, probable_cause, confidence, recommended_action)
- [ ] 8.8 — Create Alembic migration: `approval` table
  (workflow_id, decision, reason, decided_by_oid, decided_at)
- [ ] 8.9 — Create Alembic migration: `remediation_execution` table
  (id, workflow_id, action, idempotency_key UNIQUE, status, started_at, finished_at, result_json)
- [ ] 8.10 — Implement state machine in code — only explicitly listed transitions allowed:
  - Illegal transition raises a domain error `INVALID_STATE_TRANSITION`
  - Use `state_version` for optimistic concurrency (prevents race conditions)
- [ ] 8.11 — Write repository layer (no raw SQL in business logic):
  - `create_workflow`, `get_workflow`, `transition_status`, `append_event`, `save_diagnosis`
- [ ] 8.12 — Wire failure path: when calculator returns SERVICE_UNAVAILABLE, create a workflow record and transition to DIAGNOSING
- [ ] 8.13 — Write state machine tests:
  - Every allowed transition — passes
  - Important illegal transitions — raises domain error
  - Duplicate status update with wrong `state_version` → rejected
- [ ] 8.14 — Run `make test` — all tests pass
- [ ] 8.15 — Run `make lint` and `make typecheck` — zero errors
- [ ] 8.16 — Update `docs/NOTES.md` with: state machines, optimistic concurrency, why durable state matters, append-only event log for auditability
- [ ] 8.17 — Update `docs/JOURNAL.md`

**Acceptance:** Process restart does not lose incident state. Illegal transition tests pass.

---

## Iteration 9 — Human Approval

**Goal:** No privileged action executes before a human with the right role
says yes. Approval is a real persisted state transition — not a prompt instruction.

- [ ] 9.1 — Learn and document in NOTES.md: human-in-the-loop (HITL), why approval must be a real state transition, optimistic concurrency
- [ ] 9.2 — Add `POST /api/v1/workflows/{workflow_id}/approval` endpoint:
  - Requires `Calculator.Approver` or `Calculator.Admin` role
  - Accepts `decision` (approved / rejected) and optional `reason`
  - Only valid when workflow is in `AWAITING_APPROVAL` state
  - Uses `state_version` for optimistic concurrency check
- [ ] 9.3 — Add `GET /api/v1/workflows/{workflow_id}` endpoint:
  - Public-safe view of workflow status (no sensitive internal data)
  - Requires at minimum `Calculator.User` role
- [ ] 9.4 — Add `GET /api/v1/workflows/{workflow_id}/events` endpoint:
  - Sanitised audit timeline
  - Requires `Calculator.Operator` or `Calculator.Admin` role
- [ ] 9.5 — Handle approval path:
  - Save `ApprovalDecision` to `approval` table
  - Transition workflow to `REMEDIATING`
  - (Service Bus message published in Iteration 10 — for now just transition state)
- [ ] 9.6 — Handle rejection path:
  - Save `ApprovalDecision` with `decision=rejected`
  - Transition workflow to `REJECTED`
  - No remediation executes
- [ ] 9.7 — Handle duplicate approval idempotently (same decision → same response, no error)
- [ ] 9.8 — Wire Supervisor to transition workflow to `AWAITING_APPROVAL` when Diagnosis recommends `restart_calculator`
- [ ] 9.9 — Write approval tests:
  - No token → 401
  - Valid token, wrong role (User) → 403
  - Valid token, Approver role → 200
  - Approve when status is AWAITING_APPROVAL → transitions to REMEDIATING
  - Approve when status is not AWAITING_APPROVAL → domain error
  - Reject → transitions to REJECTED
  - Duplicate approval → idempotent 200
  - Wrong `state_version` → concurrency error
- [ ] 9.10 — Run `make test` — all tests pass
- [ ] 9.11 — Run `make lint` and `make typecheck` — zero errors
- [ ] 9.12 — Update `docs/NOTES.md` with: HITL design, why approval is a state transition not a prompt, optimistic concurrency, idempotency
- [ ] 9.13 — Update `docs/JOURNAL.md`

**Acceptance:** No mutating remediation before approval. Reject path works. User role cannot approve.

---

## Iteration 10 — Service Bus + Async Remediation

**Goal:** Approved remediation is processed asynchronously through a queue.
Duplicate messages execute remediation only once. Poison messages reach the DLQ.

- [ ] 10.1 — Learn and document in NOTES.md: queues vs direct calls, why async for remediation, idempotency, dead-letter queue
- [ ] 10.2 — Create Terraform module: `infra/terraform/modules/service_bus/` (namespace + `incident-commands` queue)
- [ ] 10.3 — Add `azure-servicebus` SDK dependency to `apps/agent_api/pyproject.toml`
- [ ] 10.4 — Define message envelope contract in `packages/contracts/contracts/messaging.py`:
  ```python
  class CommandMessage(BaseModel):
      message_id: UUID
      message_type: Literal["DiagnoseIncident", "ExecuteRemediation", "VerifyRecovery"]
      workflow_id: UUID
      correlation_id: UUID
      occurred_at: datetime
      attempt: int
      payload: dict
  ```
- [ ] 10.5 — Build Service Bus producer:
  - After approval is stored, publish `ExecuteRemediation` message to `incident-commands`
  - Use managed identity for Service Bus access (no connection string in code)
- [ ] 10.6 — Build Service Bus consumer/worker:
  - Reads from `incident-commands` queue
  - Processes `ExecuteRemediation` messages
  - Calls Remediation Agent (stub — full implementation in Iteration 11)
- [ ] 10.7 — Implement idempotent message consumption:
  - Check `message_id` and `idempotency_key` against `remediation_execution` table before processing
  - If already processed → acknowledge message, do nothing
- [ ] 10.8 — Configure bounded exponential backoff for transient errors:
  - Max retries: 3 (constant in code)
  - Backoff: 1s, 2s, 4s
  - Business logic failures do not auto-retry
- [ ] 10.9 — Configure dead-letter queue:
  - After Service Bus max delivery count is reached → message moves to DLQ automatically
  - DLQ processor is separate — does not auto-replay without human investigation
- [ ] 10.10 — Assign managed identity `Azure Service Bus Data Sender` and `Data Receiver` roles in Terraform
- [ ] 10.11 — Write consumer tests:
  - Normal message → processed once
  - Duplicate message with same `message_id` → processed once (idempotent)
  - Worker throws exception → delivery count increments
- [ ] 10.12 — Create DLQ demo script `scripts/dlq_demo.sh`:
  - Forces worker to fail until max delivery count
  - Shows message appearing in DLQ
- [ ] 10.13 — Run `make test` — all tests pass
- [ ] 10.14 — Run `make lint` and `make typecheck` — zero errors
- [ ] 10.15 — Update `docs/NOTES.md` with: Service Bus, queues, async vs sync, DLQ, idempotency, delivery count, why we do not force all calculations through the queue
- [ ] 10.16 — Update `docs/JOURNAL.md`

**Acceptance:** Approved remediation executes asynchronously. Duplicate message does not duplicate action. Poison message reaches DLQ.

---

## Iteration 11 — Privileged Remediation Tool

**Goal:** The `restart_calculator` tool is enabled — but only with a full
policy check, approved action contract, idempotency guard, and Azure runtime
adapter. The LLM cannot choose the target or the action — deterministic code does.

- [ ] 11.1 — Learn and document in NOTES.md: why deterministic policy matters, why the LLM must never authorize itself, the policy rules
- [ ] 11.2 — Create `RemediationPolicy` class in `apps/agent_api/app/policies/`:
  - Rule 1: Only the configured Calculator resource may be managed (no arbitrary resource IDs)
  - Rule 2: `restart_calculator` is the only mutating operation
  - Rule 3: Restart requires a persisted approval
  - Rule 4: Approver must have Approver/Admin role
  - Rule 5: Approval must belong to the same `workflow_id`
  - Rule 6: Approval must not be expired
  - Rule 7: Action executed must exactly match approved action
  - Rule 8: Maximum one restart per idempotency key
  - Rule 9: Maximum remediation attempts per workflow (constant cap)
  - Rule 10: No shell tool, no generic HTTP tool, no generic Azure CLI
- [ ] 11.3 — Enable `restart_calculator` MCP tool in `apps/mcp_server/app/tools/remediation.py`:
  - Signature: `restart_calculator(workflow_id: UUID, idempotency_key: str)`
  - Target Azure resource comes from trusted server-side config — not from LLM input
  - Calls `RemediationPolicy.evaluate()` before any action
  - Policy denial → returns `ToolResult(success=False, code="POLICY_DENIED", ...)`
- [ ] 11.4 — Build Azure Container Apps restart adapter:
  - Local mode: restarts Docker container
  - Azure mode: calls Azure Container Apps management API to restart the calculator revision
  - Uses managed identity — no credentials
- [ ] 11.5 — Build Remediation Agent:
  - System prompt: execute only `approved_action`, cannot select target resource, cannot substitute a different action, stop immediately if tool returns policy denial
  - Input must include an `ApprovedAction` generated by deterministic orchestration code — not by the LLM
  - Returns structured result
- [ ] 11.6 — Build post-restart health verification:
  - Polls `/health/ready` after restart
  - Timeout: 30 seconds
  - Max polls: 10 (constant in code)
  - Returns: healthy / still unhealthy / timeout
- [ ] 11.7 — Wire full recovery path:
  - Service Bus worker → policy check → Remediation Agent → `restart_calculator` → health verification → transition to VERIFYING → transition to RETRYING_ORIGINAL_REQUEST → Calculator Agent retries original calculation → RESOLVED
- [ ] 11.8 — Write policy tests:
  - Wrong `workflow_id` → POLICY_DENIED
  - No approval record → POLICY_DENIED
  - Approval is `rejected` → POLICY_DENIED
  - Approval expired → POLICY_DENIED
  - Arbitrary resource ID supplied → impossible (resource comes from server config, not input)
  - Duplicate `idempotency_key` → no second action
  - Max attempts exceeded → REMEDIATION_LIMIT_EXCEEDED
- [ ] 11.9 — Run `make test` — all tests pass
- [ ] 11.10 — Run `make lint` and `make typecheck` — zero errors
- [ ] 11.11 — Update `docs/NOTES.md` with: policy engines, deterministic guardrails, idempotency key pattern, why target comes from server config
- [ ] 11.12 — Update `docs/JOURNAL.md`

**Acceptance:** Unauthorized tool attempt denied. Approved workflow restarts only the calculator. Original request completes after recovery.

---

## Iteration 12 — Enterprise Observability

**Goal:** End-to-end traces visible in Application Insights. Every request
has a correlation ID that flows from user → agent → MCP → calculator → Service Bus → worker.
Token, cost, and latency metrics tracked.

- [ ] 12.1 — Learn and document in NOTES.md: OpenTelemetry, spans, traces, metrics, Application Insights, correlation IDs
- [ ] 12.2 — Add OpenTelemetry dependencies to all services via `packages/telemetry/`
- [ ] 12.3 — Create shared telemetry setup in `packages/telemetry/telemetry/setup.py` (tracer, meter, exporter, resource)
- [ ] 12.4 — Add correlation ID propagation across all boundaries:
  - HTTP headers → agent → MCP → calculator
  - Service Bus message envelope → worker → MCP
- [ ] 12.5 — Add OpenTelemetry spans for all agent operations:
  - `agent.request`, `agent.supervisor`, `agent.calculator`, `agent.diagnosis`, `agent.remediation`
- [ ] 12.6 — Add spans for all MCP tool calls:
  - `mcp.tool.calculate`, `mcp.tool.check_health`, `mcp.tool.get_logs`, `mcp.tool.restart_calculator`
- [ ] 12.7 — Add spans for calculator and workflow operations:
  - `calculator.calculate`, `workflow.approval`, `workflow.remediation`
- [ ] 12.8 — Add span attributes (low-risk — no prompt content, no tokens, no secrets):
  - workflow status, agent name, tool name, tool success, retry count, user role category, model name, error code, approval outcome
- [ ] 12.9 — Add token tracking per LLM call (input tokens, output tokens)
- [ ] 12.10 — Add estimated cost metric per LLM call (token count × model rate)
- [ ] 12.11 — Add latency metrics: calculator, agent, tool, LLM
- [ ] 12.12 — Configure Application Insights OTLP exporter in each service
- [ ] 12.13 — Set up structured JSON logging in every service:
  - Never log: access tokens, refresh tokens, client secrets, Key Vault values, auth headers, full env vars
- [ ] 12.14 — Create `docs/architecture/observability-queries.md` with useful KQL queries for Application Insights
- [ ] 12.15 — Verify one full happy-path trace is visible: user request → supervisor → calculator agent → MCP → calculator service
- [ ] 12.16 — Verify one incident trace is visible: failure → diagnosis → approval → remediation → recovery
- [ ] 12.17 — Run `make test` — all tests pass
- [ ] 12.18 — Update `docs/NOTES.md` with: OpenTelemetry, spans vs logs vs metrics, Application Insights, structured logging rules, what not to log
- [ ] 12.19 — Update `docs/JOURNAL.md`

**Acceptance:** One trace shows full happy path. One trace shows approval and remediation.

---

## Iteration 13 — CI/CD + Deployment Hardening

**Goal:** Code deploys to Azure automatically from GitHub — no manual image
builds, no manual Terraform runs. Secure by default using GitHub OIDC to Azure.

- [ ] 13.1 — Learn and document in NOTES.md: GitHub Actions, workload identity federation, OIDC to Azure, why not long-lived secrets in CI
- [ ] 13.2 — Set up GitHub OIDC → Azure workload identity federation:
  - Create Terraform module: `infra/terraform/modules/identity/github_oidc`
  - No Azure client secrets stored in GitHub
- [ ] 13.3 — Create full CI workflow `.github/workflows/ci.yml`:
  - checkout → setup uv → install → format check → lint → type check → unit tests → integration tests (no Azure) → dependency security scan → Docker build per service
- [ ] 13.4 — Add `pip-audit` to CI for dependency vulnerability scanning
- [ ] 13.5 — Create Terraform plan workflow `.github/workflows/terraform-plan.yml`:
  - Runs on pull request
  - Posts plan output as PR comment
- [ ] 13.6 — Create Terraform apply workflow `.github/workflows/terraform-apply.yml`:
  - Runs on merge to main
  - Requires manual approval before apply (GitHub environment protection)
- [ ] 13.7 — Create image build + deploy workflow `.github/workflows/deploy-dev.yml`:
  - Builds and pushes images to ACR
  - Updates Container Apps revisions
  - Runs smoke tests after deploy
  - Verifies `/health/live` on all services
- [ ] 13.8 — Create `docs/architecture/rollback.md` — how to roll back to a previous Container Apps revision
- [ ] 13.9 — Run full pipeline end to end from a pull request
- [ ] 13.10 — Verify: merge to main → images built → Container Apps updated → smoke tests pass
- [ ] 13.11 — Update `docs/NOTES.md` with: CI/CD concepts, GitHub Actions, workload identity federation, Terraform remote state, deployment slots / revisions
- [ ] 13.12 — Update `docs/JOURNAL.md`

**Acceptance:** Code deploys without manual image building. CI is green on main.

---

## Iteration 14 — Security + Chaos Testing

**Goal:** Every security property is tested and documented with evidence.
Every chaos scenario is reproducible. No gaps between what we claim and what we proved.

- [ ] 14.1 — Test and document: unauthenticated API request → 401
- [ ] 14.2 — Test and document: forged / invalid token → 401
- [ ] 14.3 — Test and document: authenticated user without required role → 403
- [ ] 14.4 — Test and document: prompt asks agent to restart arbitrary Azure resource → policy denies (no generic tool exists)
- [ ] 14.5 — Test and document: prompt asks agent to reveal secrets → no secret tool exists, agent cannot comply
- [ ] 14.6 — Test and document: prompt asks agent to call a tool not assigned to it → framework / MCP denies
- [ ] 14.7 — Test and document: duplicate remediation message → executes once (idempotency key)
- [ ] 14.8 — Test and document: replayed approval request → idempotent response, no double transition
- [ ] 14.9 — Test and document: stale approval used for a different workflow → policy denies
- [ ] 14.10 — Test and document: malicious content in logs attempting prompt injection → agent treats log output as untrusted data, no policy override
- [ ] 14.11 — Test and document: LLM returns malformed JSON → typed `LLM_OUTPUT_INVALID`, no crash
- [ ] 14.12 — Test and document: calculator call timeout → typed `TOOL_TIMEOUT`, workflow does not hang
- [ ] 14.13 — Test and document: restart fails repeatedly → bounded retries, workflow transitions to FAILED
- [ ] 14.14 — Test and document: DLQ demo — force consumer exception until message is dead-lettered, show it in Azure portal
- [ ] 14.15 — Create `docs/security/threat-model.md` covering all 12 threats from the spec
- [ ] 14.16 — Run `make test` — all pass including new security/chaos tests
- [ ] 14.17 — Update `docs/NOTES.md` with: threat model, prompt injection, chaos engineering, why we test failure as a first-class scenario
- [ ] 14.18 — Update `docs/JOURNAL.md`

**Acceptance:** Documented evidence for every scenario. All tests pass.

---

## Iteration 15 — Final Docs + Interview Pack

**Goal:** Turn everything we built into something that can be explained in a
10-minute demo and discussed in a technical interview for the EY role.

- [ ] 15.1 — Create `docs/architecture/architecture-diagram.md` with ASCII or Mermaid diagram of the full Azure architecture
- [ ] 15.2 — Create `docs/architecture/sequence-healthy.md` — sequence diagram for normal calculation flow
- [ ] 15.3 — Create `docs/architecture/sequence-failure.md` — sequence diagram for failure and recovery flow
- [ ] 15.4 — Write all 10 ADRs in `docs/adr/`:
  - ADR-001: Why Calculator as intentionally simple business domain
  - ADR-002: Azure Container Apps vs AKS
  - ADR-003: LLM reasoning vs deterministic orchestration boundary
  - ADR-004: Microsoft Agent Framework selection
  - ADR-005: MCP as tool boundary
  - ADR-006: PostgreSQL for workflow/audit state
  - ADR-007: Service Bus only for asynchronous incident path
  - ADR-008: Managed Identity over stored credentials
  - ADR-009: Human approval before privileged remediation
  - ADR-010: No generic shell/Azure CLI tool for agents
- [ ] 15.5 — Create `docs/architecture/build-vs-buy.md`:
  - Custom agent framework (this project) vs Foundry Agent Service vs Moveworks
  - Pros, cons, when to choose each
- [ ] 15.6 — Create `docs/architecture/semantic-kernel-comparison.md`:
  - How this design maps to Semantic Kernel concepts
  - Why we used Microsoft Agent Framework in this iteration
- [ ] 15.7 — Create `docs/demo/demo-script.md` — 10-minute demo script covering all 7 parts from spec
- [ ] 15.8 — Create `docs/runbooks/operations-runbook.md` — how to deploy, roll back, inspect DLQ, toggle fault mode
- [ ] 15.9 — Create `docs/security/threat-model.md` (if not already created in Iteration 14)
- [ ] 15.10 — Create `docs/interview/ey-jd-coverage.md` — every JD capability mapped to project evidence
- [ ] 15.11 — Create `docs/interview/talking-points.md` — the 10 things we can truthfully say we built
- [ ] 15.12 — Create `docs/interview/qa.md` — common interview questions with answers grounded in what we actually built
- [ ] 15.13 — Write resume bullets in `docs/interview/resume-bullets.md` — only for features actually implemented
- [ ] 15.14 — Update root `README.md` with: project overview, 10-minute demo script, local run commands, architecture diagram link
- [ ] 15.15 — Final `docs/JOURNAL.md` entry — project complete

**Acceptance:** 10-minute demo can be run end to end. Every JD capability has project evidence.

---

## Quick Reference — Iteration Status

| # | Iteration | Status |
|---|-----------|--------|
| 0 | Repository Bootstrap | Not started |
| 1 | Calculator Service (Local) | Not started |
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
