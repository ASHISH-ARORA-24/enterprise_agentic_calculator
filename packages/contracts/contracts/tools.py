from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """
    Standard envelope returned by every tool call.

    Every tool — calculate, check_health, restart_calculator — returns this
    same shape. This means the agent always knows what to expect regardless
    of which tool it called.

    Why a typed envelope instead of raw dicts?
    - The agent branches on `success` and `code` in deterministic code.
    - If tool output were free-form text, we'd have to parse strings — fragile.
    - A typed envelope is validated by Pydantic — no surprise fields.
    """

    # Did the tool call succeed?
    success: bool

    # Machine-readable result code.
    # Success example : "OK"
    # Failure examples: "SERVICE_UNAVAILABLE", "DIVIDE_BY_ZERO", "TOOL_TIMEOUT"
    # The agent and orchestrator branch on this — never on the message string.
    code: str

    # Human-readable description — for logs and user-facing messages.
    message: str

    # Optional payload — the actual result data (e.g. calculation result).
    data: dict = Field(default_factory=dict)

    # Should the caller retry this operation?
    # True for transient failures (network timeout, service temporarily down).
    # False for permanent failures (divide by zero, policy denied).
    retryable: bool = False

    # Correlation ID — ties this tool call to the parent request trace.
    # Set by the caller before invoking the tool.
    correlation_id: str = ""
