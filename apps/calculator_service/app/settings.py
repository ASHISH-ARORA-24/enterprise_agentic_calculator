from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configuration for the Calculator Service.

    Values are read from environment variables automatically by pydantic-settings.
    If a variable is missing and has no default, the service will refuse to start —
    which is intentional. A misconfigured service should not silently run with
    wrong settings.

    To set values locally, copy .env.example to .env and fill in your values.
    """

    model_config = SettingsConfigDict(
        # Read from a .env file if present. Useful for local development.
        # In production (Docker / Azure), real environment variables take precedence.
        env_file=".env",
        env_file_encoding="utf-8",
        # Ignore extra variables in .env that do not match any field here.
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Server settings
    # ------------------------------------------------------------------

    # Port the service listens on.
    calculator_port: int = Field(default=8000)

    # Host to bind to. 0.0.0.0 means "accept connections from any IP".
    # Use 127.0.0.1 (localhost only) if you do not want external access.
    calculator_host: str = Field(default="0.0.0.0")  # noqa: S104

    # ------------------------------------------------------------------
    # Fault injection — used only in non-production environments.
    # Lets us deliberately break the service to test the failure path.
    #
    # none         — normal operation
    # unhealthy    — /health/ready returns not_ready
    # slow         — /calculate sleeps 10 seconds before responding
    # calculate_500 — /calculate returns HTTP 500
    # ------------------------------------------------------------------

    fault_mode: str = Field(default="none")

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    log_level: str = Field(default="INFO")

    # ------------------------------------------------------------------
    # Service identity — returned by /api/v1/version
    # ------------------------------------------------------------------

    service_name: str = Field(default="calculator-service")
    service_version: str = Field(default="0.1.0")
    environment: str = Field(default="local")


# A single shared instance used across the application.
# Import this instead of instantiating Settings() in multiple places.
settings = Settings()
