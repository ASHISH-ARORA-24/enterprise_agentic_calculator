import uuid

from contracts.agent import AgentRequest, AgentResponse
from fastapi import APIRouter

from agent_api.agents import calculator_agent
from agent_api.settings import settings

health_router = APIRouter(tags=["Health"])
agent_router = APIRouter(prefix="/api/v1", tags=["Agent"])


@health_router.get("/health/live")
async def liveness() -> dict:
    return {"status": "alive"}


@health_router.get("/health/ready")
async def readiness() -> dict:
    return {"status": "ready"}


@agent_router.post("/agent/query", response_model=AgentResponse)
async def agent_query(request: AgentRequest) -> AgentResponse:
    """
    Accept a natural language question and return the agent's answer.

    The agent will call the calculator tool to answer arithmetic questions.
    It will never answer arithmetic directly — tool use is enforced by the
    system prompt and verified by the tool_called field in the response.
    """
    correlation_id = str(uuid.uuid4())
    return await calculator_agent.run(
        message=request.message,
        correlation_id=correlation_id,
    )


@agent_router.get("/version")
async def version() -> dict:
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
    }
