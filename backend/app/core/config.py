from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    ENV: str = "development"
    DEBUG: bool = True
    SETUP_TOKEN: str = "change-me-to-a-secure-setup-token"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://finapp:finapp@localhost:5432/finapp"

    # Auth
    JWT_SECRET: str = "change-me-to-a-random-256-bit-value"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Pluggy
    PLUGGY_CLIENT_ID: str = ""
    PLUGGY_CLIENT_SECRET: str = ""
    PLUGGY_BASE_URL: str = "https://api.pluggy.ai"
    PLUGGY_WEBHOOK_SECRET: str = "change-me"

    # CORS
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # Observability
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()
