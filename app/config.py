from pydantic_settings import BaseSettings, SettingsConfigDict


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

    jwt_secret_key: str | None = None
    jwt_algorithm: str = "RS256"
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_days: int = 3
    admin_login: str = "admin"
    admin_password: str = "admin"
    jwt_keys_dir: str = "keys"  # Для filesystem backend
    jwt_storage_backend: str = "environment"  # "filesystem" | "environment"
    jwt_env_prefix: str = "JWT_KEY"  # Префикс переменных окружения


settings = Settings()
