from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    provider_base_url: str = "http://localhost:3001"
    provider_api_key: str = "test-dev-2026"
    provider_max_concurrent: int = 40
    provider_max_retries: int = 6
    provider_retry_multiplier: float = 0.5
    provider_retry_min_wait: float = 0.5
    provider_retry_max_wait: float = 8.0


settings = Settings()
