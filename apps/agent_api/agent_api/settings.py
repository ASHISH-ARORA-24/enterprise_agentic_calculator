from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configuration for the Agent API.

    Values are read from environment variables automatically.
    Copy .env.example to .env and fill in your values for local development.
    In Azure, real environment variables are injected by Container Apps.
    """

    model_config = SettingsConfigDict(
        # Look for .env starting from this file's location, walking up to the repo root.
        # This works whether uvicorn is started from the service directory or the repo root.
        env_file=[".env", "../../.env"],
        env_file_encoding="utf-8",
        extra="ignore",
        # Skip env vars that are defined but empty — use the field default instead.
        # This means AGENT_API_PORT= in .env is ignored and port 8001 is used.
        env_ignore_empty=True,
    )

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------

    agent_api_port: int = Field(default=8001)
    agent_api_host: str = Field(default="0.0.0.0")  # noqa: S104

    # ------------------------------------------------------------------
    # Calculator Service
    # The agent calls the calculator via HTTP. This is the base URL.
    # In docker-compose it will be http://calculator:8000
    # Locally it is http://localhost:8000
    # ------------------------------------------------------------------

    calculator_service_url: str = Field(default="http://localhost:8000")

    # ------------------------------------------------------------------
    # Timeouts — enforced in code, not prompts.
    # Every HTTP call to the calculator must respect these.
    # ------------------------------------------------------------------

    # Seconds to wait for the calculator to respond before giving up.
    calculator_timeout_seconds: float = Field(default=3.0)

    # Maximum number of retries on transient network errors.
    # After this many attempts we return a typed failure — no infinite loops.
    calculator_max_retries: int = Field(default=1)

    # Seconds to wait for the LLM to respond.
    llm_timeout_seconds: float = Field(default=30.0)

    # ------------------------------------------------------------------
    # LLM — OpenAI
    # ------------------------------------------------------------------

    # Your OpenAI API key — stored in .env, never in code.
    llm_api_key: str = Field(default="")

    # Model to use. gpt-4o has excellent tool calling support.
    llm_model_name: str = Field(default="gpt-4o")

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    log_level: str = Field(default="INFO")

    # ------------------------------------------------------------------
    # Service identity
    # ------------------------------------------------------------------

    service_name: str = Field(default="agent-api")
    service_version: str = Field(default="0.1.0")
    environment: str = Field(default="local")


settings = Settings()
