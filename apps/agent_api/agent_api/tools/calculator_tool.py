import uuid
from decimal import Decimal

import httpx

# Import the shared ToolResult contract from the contracts package.
# Every tool returns this same shape — the agent always knows what to expect.
from contracts.tools import ToolResult

from agent_api.settings import settings

# ---------------------------------------------------------------------------
# Timeout and retry constants.
#
# These MUST be code-level constants, not prompt instructions.
# The spec is explicit: every network call must have a timeout and every
# retry loop must have a hard cap enforced in code.
# ---------------------------------------------------------------------------

TIMEOUT_SECONDS = settings.calculator_timeout_seconds  # 3.0s
MAX_RETRIES = settings.calculator_max_retries  # 1


async def calculate(
    operation: str,
    a: Decimal,
    b: Decimal,
    correlation_id: str = "",
) -> ToolResult:
    """
    Call the Calculator Service and return a typed ToolResult.

    This is the ONLY place in the codebase that knows how to talk to the
    calculator HTTP API. The agent calls this function — it never makes
    HTTP calls itself.

    On success: ToolResult(success=True, data={"result": "200"}, ...)
    On failure: ToolResult(success=False, code="SERVICE_UNAVAILABLE", ...)
    """

    if not correlation_id:
        correlation_id = str(uuid.uuid4())

    payload = {
        "operation": operation,
        "a": str(a),
        "b": str(b),
    }

    # Retry loop — bounded by MAX_RETRIES constant, never infinite.
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{settings.calculator_service_url}/api/v1/calculate",
                    json=payload,
                )

            # HTTP 200 — calculation succeeded
            if response.status_code == 200:
                data = response.json()
                return ToolResult(
                    success=True,
                    code="OK",
                    message="Calculation successful",
                    data={"result": data["result"], "request_id": data["request_id"]},
                    retryable=False,
                    correlation_id=correlation_id,
                )

            # HTTP 422 — domain error (e.g. divide by zero).
            # This is a permanent failure — do not retry.
            if response.status_code == 422:
                detail = response.json().get("detail", {})
                return ToolResult(
                    success=False,
                    code=detail.get("code", "INVALID_REQUEST"),
                    message=detail.get("message", "Invalid calculation request"),
                    retryable=False,
                    correlation_id=correlation_id,
                )

            # Any other HTTP error — treat as transient, allow retry.
            return ToolResult(
                success=False,
                code="SERVICE_UNAVAILABLE",
                message=f"Calculator returned unexpected status {response.status_code}",
                retryable=True,
                correlation_id=correlation_id,
            )

        except httpx.TimeoutException:
            last_error = Exception("timeout")
            # Timeout is transient — retry if attempts remain.
            if attempt < MAX_RETRIES:
                continue

        except httpx.ConnectError:
            last_error = Exception("connection error")
            # Connection refused — calculator is down. Retry once.
            if attempt < MAX_RETRIES:
                continue

        except Exception as exc:
            last_error = exc
            break

    # All attempts exhausted — return a typed failure.
    error_msg = str(last_error) if last_error else "unknown error"
    is_timeout = "timeout" in error_msg

    return ToolResult(
        success=False,
        code="TOOL_TIMEOUT" if is_timeout else "SERVICE_UNAVAILABLE",
        message=f"Calculator service is unreachable: {error_msg}",
        retryable=True,
        correlation_id=correlation_id,
    )
