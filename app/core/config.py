from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # --- Environment ---
    ENVIRONMENT: str = "development"  # development | staging | production

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./erp.db"

    # --- Secrets / JWT ---
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Redis (used by future modules: caching, background jobs) ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Feature flags (toggle modules/behaviors without code changes) ---
    FEATURE_MFA_ENABLED: bool = False
    FEATURE_EMAIL_NOTIFICATIONS: bool = False
    FEATURE_SMS_NOTIFICATIONS: bool = False

    class Config:
        env_file = ".env"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key_in_production(cls, v, info):
        # Config validation (Phase 6): refuse to boot with the default secret
        # once ENVIRONMENT is production, to prevent an insecure deploy.
        values = info.data
        if values.get("ENVIRONMENT") == "production" and v == "change-this-to-a-random-secret-key-in-production":
            raise ValueError(
                "SECRET_KEY must be overridden via environment variable in production"
            )
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()
