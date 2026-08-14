from typing import Literal, Any
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

from sesc_auth_sdk.settings import AuthRouterSettings, M2MSettings, TokenValidationSettings
from sesc_openfga_sdk.settings import OpenFGASettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "auth"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


    admin_login: str = "admin"
    admin_password: str = "admin"
    authentik_url: str = "http://authentik:9000"
    users_path: str = ''
    env_file_path: str = ".env"
    allowed_origins:list[str] = ["http://localhost:8000"]

    # Cookie settings
    cookie_secure: bool = False
    cookie_samesite: Literal['lax', 'none', 'strict'] | None = "lax"
    cookie_domain: str | None = '.localhost'

    root_path: str = '/'

    token_validation_settings: TokenValidationSettings = TokenValidationSettings(_env_file='.env')

    sa_auth_admin_app_api_token: str

settings = Settings()

