from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    APP_NAME: str = "FoodDelivery API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fooddelivery"
    DB_ECHO: bool = False

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "your-super-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    STRIPE_SECRET_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8501"]

    RATE_LIMIT_LOGIN: int = 5
    RATE_LIMIT_GENERAL: int = 100


settings = Settings()
