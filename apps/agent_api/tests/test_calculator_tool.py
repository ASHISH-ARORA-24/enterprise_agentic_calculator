from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Calculator Tool tests
#
# We mock httpx.AsyncClient so tests never make real HTTP calls.
# This means tests pass even when the calculator service is not running.
# ---------------------------------------------------------------------------


def make_mock_response(status_code: int, json_data: dict) -> MagicMock:
    """Helper — build a fake httpx response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    return mock


@pytest.mark.asyncio
async def test_calculate_success() -> None:
    """Successful calculation returns ToolResult with success=True and result."""
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

    with patch("agent_api.tools.calculator_tool.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await calculate("multiply", Decimal("25"), Decimal("8"), "test-corr")

    assert result.success is True
    assert result.code == "OK"
    assert result.data["result"] == "200"
    assert result.retryable is False
    assert result.correlation_id == "test-corr"


@pytest.mark.asyncio
async def test_calculate_divide_by_zero() -> None:
    """Divide by zero returns ToolResult with success=False and DIVIDE_BY_ZERO code."""
    from agent_api.tools.calculator_tool import calculate

    mock_response = make_mock_response(
        422,
        {
            "detail": {
                "code": "DIVIDE_BY_ZERO",
                "message": "Cannot divide by zero",
            }
        },
    )

    with patch("agent_api.tools.calculator_tool.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await calculate("divide", Decimal("5"), Decimal("0"))

    assert result.success is False
    assert result.code == "DIVIDE_BY_ZERO"
    assert result.retryable is False


@pytest.mark.asyncio
async def test_calculate_service_unavailable() -> None:
    """Connection error returns SERVICE_UNAVAILABLE with retryable=True."""
    import httpx
    from agent_api.tools.calculator_tool import calculate

    with patch("agent_api.tools.calculator_tool.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await calculate("add", Decimal("1"), Decimal("2"))

    assert result.success is False
    assert result.code == "SERVICE_UNAVAILABLE"
    assert result.retryable is True


@pytest.mark.asyncio
async def test_calculate_timeout() -> None:
    """Timeout returns TOOL_TIMEOUT with retryable=True."""
    import httpx
    from agent_api.tools.calculator_tool import calculate

    with patch("agent_api.tools.calculator_tool.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await calculate("add", Decimal("1"), Decimal("2"))

    assert result.success is False
    assert result.code == "TOOL_TIMEOUT"
    assert result.retryable is True


@pytest.mark.asyncio
async def test_calculate_unexpected_status() -> None:
    """Unexpected HTTP status returns SERVICE_UNAVAILABLE."""
    from agent_api.tools.calculator_tool import calculate

    mock_response = make_mock_response(503, {})

    with patch("agent_api.tools.calculator_tool.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await calculate("add", Decimal("1"), Decimal("2"))

    assert result.success is False
    assert result.code == "SERVICE_UNAVAILABLE"
    assert result.retryable is True
