from unittest.mock import AsyncMock, patch

from agent_api.main import app
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

client = TestClient(app)


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
# Helpers — build fake LangChain 1.x agent results
# LangChain 1.x returns {"messages": [HumanMessage, AIMessage, ToolMessage, AIMessage]}
# ---------------------------------------------------------------------------


def make_agent_result_with_tool(answer: str) -> dict:
    """Simulates a result where the LLM called a tool."""
    return {
        "messages": [
            HumanMessage(content="What is 25 times 8?"),
            AIMessage(
                content="",
                tool_calls=[{"name": "calculate", "args": {}, "id": "t1", "type": "tool_call"}],
            ),
            ToolMessage(content="SUCCESS:200", name="calculate", tool_call_id="t1"),
            AIMessage(content=answer),
        ]
    }


def make_agent_result_no_tool(answer: str) -> dict:
    """Simulates a result where the LLM answered without calling a tool."""
    return {
        "messages": [
            HumanMessage(content="What is the capital of France?"),
            AIMessage(content=answer),
        ]
    }


# ---------------------------------------------------------------------------
# Agent query tests
# ---------------------------------------------------------------------------


def test_agent_query_multiplication() -> None:
    with patch("agent_api.agents.calculator_agent._agent") as mock_agent:
        mock_agent.ainvoke = AsyncMock(
            return_value=make_agent_result_with_tool("25 multiplied by 8 is 200.")
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
    with patch("agent_api.agents.calculator_agent._agent") as mock_agent:
        mock_agent.ainvoke = AsyncMock(
            return_value=make_agent_result_with_tool("100 divided by 4 is 25.")
        )
        response = client.post(
            "/api/v1/agent/query",
            json={"message": "What is 100 divided by 4?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["tool_called"] is True
    assert "25" in data["answer"]


def test_agent_query_divide_by_zero() -> None:
    with patch("agent_api.agents.calculator_agent._agent") as mock_agent:
        mock_agent.ainvoke = AsyncMock(
            return_value=make_agent_result_with_tool("I cannot divide by zero.")
        )
        response = client.post(
            "/api/v1/agent/query",
            json={"message": "What is 5 divided by 0?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["tool_called"] is True


def test_agent_query_calculator_unavailable() -> None:
    with patch("agent_api.agents.calculator_agent._agent") as mock_agent:
        mock_agent.ainvoke = AsyncMock(
            return_value=make_agent_result_with_tool("The calculator service is unavailable.")
        )
        response = client.post(
            "/api/v1/agent/query",
            json={"message": "What is 6 times 7?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["tool_called"] is True


def test_agent_query_non_maths() -> None:
    with patch("agent_api.agents.calculator_agent._agent") as mock_agent:
        mock_agent.ainvoke = AsyncMock(
            return_value=make_agent_result_no_tool("I can only help with arithmetic calculations.")
        )
        response = client.post(
            "/api/v1/agent/query",
            json={"message": "What is the capital of France?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["tool_called"] is False
