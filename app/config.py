from typing import Literal
import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from sesc_auth_sdk.settings import TokenValidationSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url_override: str | None = Field(default=None, validation_alias="DATABASE_URL")

    postgres_host: str
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str

    @property
    def database_url(self) -> str:
        if self.database_url_override is not None:
            return self.database_url_override
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    admin_login: str = "admin"
    admin_password: str = "admin"
    internal_authentik_url: str = "http://authentik:9000"
    users_path: str = ''
    env_file_path: str = ".env"
    allowed_origins: list[str] = ["http://localhost:8000"]

    cookie_secure: bool = False
    cookie_samesite: Literal['lax', 'none', 'strict'] | None = "lax"
    cookie_domain: str | None = '.localhost'

    root_path: str = '/'

    token_validation_settings: TokenValidationSettings = Field(
        default_factory=lambda: TokenValidationSettings(_env_file=".env")
    )

    sa_auth_admin_app_api_token: str

settings = Settings()
