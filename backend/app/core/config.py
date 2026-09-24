"""Environment-driven settings. See architecture doc Section 5.2 / 7.2 —
secrets are injected via environment variables, never committed to source
control."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "PPC CBE Tracking Application"
    environment: str = "development"  # development | staging | production

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ppc_cbe"

    # Auth
    jwt_secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Frontend — used to build absolute links sent in emails (e.g. the
    # M1 Forgot Password reset link). Override via env when the frontend
    # is served from a tunnel or a real domain instead of localhost.
    frontend_base_url: str = "http://localhost:3000"

    # SAP integration — REST API (confirmed). Exact endpoints/auth pending
    # SAP team confirmation (architecture doc Section 13, item 1).
    sap_base_url: str | None = None
    sap_api_key: str | None = None
    use_mock_sap_client: bool = True  # flip to False once SAP is confirmed and reachable

    # Mail
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None

    # Cache
    redis_url: str | None = None  # None = fall back to in-process TTL cache


settings = Settings()
