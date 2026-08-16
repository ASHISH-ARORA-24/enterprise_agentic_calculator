from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Calculator Tool tests — mock httpx so tests never call the real service
# ---------------------------------------------------------------------------


def make_mock_response(status_code: int, json_data: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    return mock


@pytest.mark.asyncio
async def test_calculate_success() -> None:
    """Successful calculation returns SUCCESS string with result."""
    from agent_api.tools.calculator_tool import calculate

    mock_response = make_mock_response(
        200,
        {
            "operation": "multiply",
            "a": "25",
            "b": "8",
            "result": "200",
            "request_id": "test-id",
        },
    )

    with patch("agent_api.tools.calculator_tool.httpx.AsyncClient") as mock_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await calculate.ainvoke({"operation": "multiply", "a": 25.0, "b": 8.0})

    assert "SUCCESS" in result
    assert "200" in result


@pytest.mark.asyncio
async def test_calculate_divide_by_zero() -> None:
    """Divide by zero returns ERROR string with DIVIDE_BY_ZERO code."""
    from agent_api.tools.calculator_tool import calculate

    mock_response = make_mock_response(
        422, {"detail": {"code": "DIVIDE_BY_ZERO", "message": "Cannot divide by zero"}}
    )

    with patch("agent_api.tools.calculator_tool.httpx.AsyncClient") as mock_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await calculate.ainvoke({"operation": "divide", "a": 5.0, "b": 0.0})

    assert "ERROR" in result
    assert "DIVIDE_BY_ZERO" in result


@pytest.mark.asyncio
async def test_calculate_service_unavailable() -> None:
    """Connection error returns SERVICE_UNAVAILABLE error string."""
    import httpx
    from agent_api.tools.calculator_tool import calculate

    with patch("agent_api.tools.calculator_tool.httpx.AsyncClient") as mock_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await calculate.ainvoke({"operation": "add", "a": 1.0, "b": 2.0})

    assert "ERROR" in result
    assert "SERVICE_UNAVAILABLE" in result


@pytest.mark.asyncio
async def test_calculate_timeout() -> None:
    """Timeout returns TOOL_TIMEOUT error string."""
    import httpx
    from agent_api.tools.calculator_tool import calculate

    with patch("agent_api.tools.calculator_tool.httpx.AsyncClient") as mock_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
        mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await calculate.ainvoke({"operation": "add", "a": 1.0, "b": 2.0})

    assert "ERROR" in result
    assert "TOOL_TIMEOUT" in result
