"""Server-only application configuration."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from the repository-root .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_password: str = Field(min_length=1)
    llm_endpoint_url: str = ""
    llm_api_key: str = ""
    llm_provider: str = "openai_compatible"
    llm_model: str = "demo-model"
    session_ttl_seconds: int = Field(default=28_800, gt=0)
    request_timeout_seconds: float = Field(default=30, gt=0, le=120)

    @property
    def upstream_configured(self) -> bool:
        return bool(self.llm_endpoint_url.strip())

    @property
    def uses_azure_openai(self) -> bool:
        return self.llm_provider.strip().lower() in {"azure_openai", "azure_openai_v1"}

    @property
    def uses_azure_openai_v1(self) -> bool:
        return self.llm_provider.strip().lower() == "azure_openai_v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
