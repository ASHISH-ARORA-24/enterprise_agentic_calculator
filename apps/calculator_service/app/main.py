from fastapi import FastAPI

from app.api.routes import calculator_router, health_router
from app.settings import settings

# ---------------------------------------------------------------------------
# FastAPI application factory.
#
# FastAPI automatically generates interactive API docs at:
#   /docs  — Swagger UI (try endpoints in the browser)
#   /redoc — ReDoc (cleaner read-only docs)
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Calculator Service",
    description="Enterprise Agentic Calculator — arithmetic microservice",
    version=settings.service_version,
)

# Mount routers — each router group is registered here.
app.include_router(health_router)
app.include_router(calculator_router)
