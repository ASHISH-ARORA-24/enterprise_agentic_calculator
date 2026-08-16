import json
from unittest.mock import AsyncMock, MagicMock, patch

from agent_api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers — build fake OpenAI responses
# ---------------------------------------------------------------------------


def make_tool_call_response(operation: str, a: float, b: float) -> MagicMock:
    """
    Fake first OpenAI response — LLM decides to call the calculate tool.
    This simulates OpenAI saying "I want to call calculate(operation, a, b)".
    """
    tool_call = MagicMock()
    tool_call.id = "call_test_123"
    tool_call.function.name = "calculate"
    tool_call.function.arguments = json.dumps({"operation": operation, "a": a, "b": b})

    message = MagicMock()
    message.tool_calls = [tool_call]
    message.content = None

    choice = MagicMock()
    choice.finish_reason = "tool_calls"
    choice.message = message

    response = MagicMock()
    response.choices = [choice]
    return response


def make_final_response(content: str) -> MagicMock:
    """
    Fake second OpenAI response — LLM forms the final answer after seeing tool result.
    """
    message = MagicMock()
    message.content = content
    message.tool_calls = None

    choice = MagicMock()
    choice.finish_reason = "stop"
    choice.message = message

    response = MagicMock()
    response.choices = [choice]
    return response


def make_no_tool_response(content: str) -> MagicMock:
    """
    Fake OpenAI response — LLM answers without calling a tool.
    Used for non-maths questions.
    """
    message = MagicMock()
    message.content = content
    message.tool_calls = None

    choice = MagicMock()
    choice.finish_reason = "stop"
    choice.message = message

    response = MagicMock()
    response.choices = [choice]
    return response


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------


def test_health_live() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_health_ready() -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


# ---------------------------------------------------------------------------
# Agent query — successful calculation
# ---------------------------------------------------------------------------


def test_agent_query_multiplication() -> None:
    """Natural language multiplication → tool called → correct answer."""
    with patch("agent_api.agents.calculator_agent._client") as mock_openai:
        mock_openai.chat.completions.create = AsyncMock(
            side_effect=[
                make_tool_call_response("multiply", 25, 8),  # first call: decide to use tool
                make_final_response("25 multiplied by 8 is 200."),  # second call: form answer
            ]
        )

        response = client.post(
            "/api/v1/agent/query",
            json={"message": "What is 25 multiplied by 8?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["tool_called"] is True
    assert "200" in data["answer"]
    assert data["correlation_id"] != ""


def test_agent_query_division() -> None:
    """Division works correctly."""
    with patch("agent_api.agents.calculator_agent._client") as mock_openai:
        mock_openai.chat.completions.create = AsyncMock(
            side_effect=[
                make_tool_call_response("divide", 100, 4),
                make_final_response("100 divided by 4 is 25."),
            ]
        )

        response = client.post(
            "/api/v1/agent/query",
            json={"message": "What is 100 divided by 4?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["tool_called"] is True
    assert "25" in data["answer"]


# ---------------------------------------------------------------------------
# Agent query — calculator errors
# ---------------------------------------------------------------------------


def test_agent_query_divide_by_zero() -> None:
    """
    Divide by zero — tool is called, calculator returns error,
    agent reports it honestly — no hallucinated answer.
    """
    with (
        patch("agent_api.agents.calculator_agent._client") as mock_openai,
        patch("agent_api.agents.calculator_agent.calculate") as mock_tool,
    ):
        from contracts.tools import ToolResult

        mock_tool.return_value = ToolResult(
            success=False,
            code="DIVIDE_BY_ZERO",
            message="Cannot divide by zero",
            retryable=False,
        )
        mock_openai.chat.completions.create = AsyncMock(
            side_effect=[
                make_tool_call_response("divide", 5, 0),
                make_final_response("I cannot divide by zero."),
            ]
        )

        response = client.post(
            "/api/v1/agent/query",
            json={"message": "What is 5 divided by 0?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["tool_called"] is True


def test_agent_query_calculator_unavailable() -> None:
    """
    Calculator service is down — agent reports SERVICE_UNAVAILABLE,
    does NOT hallucinate an answer.
    """
    with (
        patch("agent_api.agents.calculator_agent._client") as mock_openai,
        patch("agent_api.agents.calculator_agent.calculate") as mock_tool,
    ):
        from contracts.tools import ToolResult

        mock_tool.return_value = ToolResult(
            success=False,
            code="SERVICE_UNAVAILABLE",
            message="Calculator service is unreachable",
            retryable=True,
        )
        mock_openai.chat.completions.create = AsyncMock(
            side_effect=[
                make_tool_call_response("multiply", 6, 7),
                make_final_response(
                    "I cannot complete this calculation — the calculator service is unavailable."
                ),
            ]
        )

        response = client.post(
            "/api/v1/agent/query",
            json={"message": "What is 6 times 7?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["tool_called"] is True


# ---------------------------------------------------------------------------
# Agent query — non-maths question
# ---------------------------------------------------------------------------


def test_agent_query_non_maths() -> None:
    """Non-maths question — tool not called, polite decline."""
    with patch("agent_api.agents.calculator_agent._client") as mock_openai:
        mock_openai.chat.completions.create = AsyncMock(
            return_value=make_no_tool_response("I can only help with arithmetic calculations.")
        )

        response = client.post(
            "/api/v1/agent/query",
            json={"message": "What is the capital of France?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["tool_called"] is False
