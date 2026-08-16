import uuid
from decimal import Decimal, InvalidOperation

import httpx
from langchain_core.tools import tool

from agent_api.settings import settings

# ---------------------------------------------------------------------------
# Timeout and retry constants — enforced in code, not prompts.
# ---------------------------------------------------------------------------

TIMEOUT_SECONDS = settings.calculator_timeout_seconds  # 3.0s
MAX_RETRIES = settings.calculator_max_retries  # 1


@tool
async def calculate(operation: str, a: float, b: float) -> str:
    """
    Perform an arithmetic calculation by calling the Calculator Service.

    Use this tool for ALL arithmetic questions — add, subtract, multiply, divide.
    Never calculate mentally. Always call this tool.

    Args:
        operation: One of "add", "subtract", "multiply", "divide"
        a: First number
        b: Second number

    Returns:
        The result as a string, or an error description if the calculation failed.
    """
    # The @tool decorator reads this docstring and type hints to generate
    # the JSON schema that the LLM uses to decide how to call this tool.

    correlation_id = str(uuid.uuid4())

    # Convert floats to Decimal strings for exact arithmetic in the service.
    try:
        a_decimal = str(Decimal(str(a)))
        b_decimal = str(Decimal(str(b)))
    except InvalidOperation:
        return "ERROR:INVALID_INPUT — cannot parse operands as numbers"

    payload = {"operation": operation, "a": a_decimal, "b": b_decimal}

    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{settings.calculator_service_url}/api/v1/calculate",
                    json=payload,
                )

            if response.status_code == 200:
                data = response.json()
                # Return the result as a plain string — LangChain tool results
                # are strings that the LLM reads to form the final answer.
                return f"SUCCESS:{data['result']} (correlation_id={correlation_id})"

            if response.status_code == 422:
                detail = response.json().get("detail", {})
                code = detail.get("code", "INVALID_REQUEST")
                msg = detail.get("message", "Invalid request")
                # Not retryable — divide by zero, invalid operation.
                return f"ERROR:{code} — {msg}"

            return f"ERROR:SERVICE_UNAVAILABLE — unexpected status {response.status_code}"

        except httpx.TimeoutException:
            last_error = Exception("timeout")
            if attempt < MAX_RETRIES:
                continue

        except httpx.ConnectError:
            last_error = Exception("connection refused")
            if attempt < MAX_RETRIES:
                continue

        except Exception as exc:
            last_error = exc
            break

    error_msg = str(last_error) if last_error else "unknown error"
    code = "TOOL_TIMEOUT" if "timeout" in error_msg else "SERVICE_UNAVAILABLE"
    return f"ERROR:{code} — calculator service is unreachable: {error_msg}"
