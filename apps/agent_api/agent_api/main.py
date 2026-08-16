from fastapi import FastAPI

from agent_api.api.routes import agent_router, health_router
from agent_api.settings import settings

app = FastAPI(
    title="Agent API",
    description="Enterprise Agentic Calculator — agent orchestration service",
    version=settings.service_version,
)

app.include_router(health_router)
app.include_router(agent_router)
