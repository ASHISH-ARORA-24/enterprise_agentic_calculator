import asyncio
import uuid
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from app.domain import calculator
from app.domain.errors import DivideByZeroError
from app.models.schemas import (
    CalculationRequest,
    CalculationResponse,
    ErrorResponse,
    HealthResponse,
    VersionResponse,
)
from app.settings import settings

# ---------------------------------------------------------------------------
# Routers — group related endpoints together.
# main.py mounts these routers onto the FastAPI app.
# ---------------------------------------------------------------------------

# Health endpoints — no authentication needed, used by Azure for health probes
health_router = APIRouter(tags=["Health"])

# Calculator endpoints — the actual business API
calculator_router = APIRouter(prefix="/api/v1", tags=["Calculator"])


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------


@health_router.get("/health/live", response_model=HealthResponse)
async def liveness() -> HealthResponse:
    """
    Liveness probe — is the process alive?

    Returns 200 as long as the process is running.
    Never checks external dependencies — if the process is up, it is alive.
    Azure / Kubernetes uses this to decide whether to restart the container.
    """
    return HealthResponse(status="alive")


@health_router.get("/health/ready", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    """
    Readiness probe — can this service accept traffic?

    Returns not_ready when fault injection is active.
    Azure uses this to decide whether to send traffic to this instance.
    """
    if settings.fault_mode == "unhealthy":
        return HealthResponse(status="not_ready", reason="simulated_failure")
    return HealthResponse(status="ready")


# ---------------------------------------------------------------------------
# Calculator endpoint
# ---------------------------------------------------------------------------


@calculator_router.post(
    "/calculate",
    response_model=CalculationResponse,
    responses={
        # Tell FastAPI (and its auto-generated docs) that 422 returns an ErrorResponse.
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    },
)
async def calculate(request: CalculationRequest) -> CalculationResponse:
    """
    Perform an arithmetic calculation.

    Pydantic validates the request before this function runs — invalid
    operation or wrong types are rejected automatically with 422.
    """

    # Fault injection — simulate a 500 error for testing the failure path.
    if settings.fault_mode == "calculate_500":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                code="SIMULATED_FAILURE",
                message="Calculator is in fault mode: calculate_500",
            ).model_dump(),
        )

    # Fault injection — simulate a slow response.
    if settings.fault_mode == "slow":
        await asyncio.sleep(10)

    # Map operation string to the correct domain function.
    # We do NOT use eval() or getattr() — explicit mapping only.
    operation_map: dict[str, object] = {
        "add": calculator.add,
        "subtract": calculator.subtract,
        "multiply": calculator.multiply,
        "divide": calculator.divide,
    }
    fn = operation_map[request.operation]

    try:
        result: Decimal = fn(request.a, request.b)  # type: ignore[operator]
    except DivideByZeroError as e:
        # Translate domain error into an HTTP 422 response with a typed error body.
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorResponse(code=e.code, message=e.message).model_dump(),
        ) from e

    return CalculationResponse(
        operation=request.operation,
        a=request.a,
        b=request.b,
        result=result,
        request_id=uuid.uuid4(),
    )


# ---------------------------------------------------------------------------
# Version endpoint
# ---------------------------------------------------------------------------


@calculator_router.get("/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    """Return service identity — useful for verifying which version is deployed."""
    return VersionResponse(
        service=settings.service_name,
        version=settings.service_version,
        environment=settings.environment,
    )
