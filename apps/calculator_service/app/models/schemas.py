from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CalculationRequest(BaseModel):
    """
    Input for POST /api/v1/calculate.

    Pydantic validates this automatically — if the caller sends a wrong type
    or an unsupported operation, FastAPI returns a 422 before our code runs.
    """

    # Literal means only these exact four strings are accepted.
    # Anything else → automatic 422 validation error.
    operation: Literal["add", "subtract", "multiply", "divide"]

    # Decimal for exact arithmetic — never float.
    # Pydantic converts numeric strings to Decimal automatically.
    a: Decimal = Field(description="First operand")
    b: Decimal = Field(description="Second operand")

    model_config = {"json_schema_extra": {"examples": [{"operation": "multiply", "a": 25, "b": 8}]}}


class CalculationResponse(BaseModel):
    """
    Output for POST /api/v1/calculate.

    Echoes back the operation and operands so the caller can verify
    the response matches what they sent. request_id ties this response
    to a specific call for tracing.
    """

    operation: str
    a: Decimal
    b: Decimal
    result: Decimal

    # A unique ID generated per request — used for tracing and correlation.
    request_id: UUID

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "operation": "multiply",
                    "a": 25,
                    "b": 8,
                    "result": 200,
                    "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """
    Returned when a request fails.

    Using a typed error code (not just a message string) means the caller
    can branch on code without parsing human-readable text.
    """

    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error description")

    model_config = {
        "json_schema_extra": {
            "examples": [{"code": "DIVIDE_BY_ZERO", "message": "Cannot divide by zero"}]
        }
    }


class HealthResponse(BaseModel):
    """Returned by /health/live and /health/ready."""

    status: str
    reason: str | None = None


class VersionResponse(BaseModel):
    """Returned by /api/v1/version."""

    service: str
    version: str
    environment: str
