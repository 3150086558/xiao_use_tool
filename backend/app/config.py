from functools import lru_cache
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取 .env 文件的绝对路径
env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(env_path), case_sensitive=False, extra="ignore")

    app_host: str = "0.0.0.0"
    app_port: int = 1112
    app_env: str = "development"
    app_debug: bool = True

    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_name: str = "my_tools"
    db_user: str = "my_tools_user"
    db_password: str = ""

    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    jwt_secret_key: str = "change_me_to_a_very_long_random_secret_key_for_jwt_signing"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    db_cipher_key: str = "change_me_to_32byte_base64_encryption_key"

    celery_broker_url: str = "redis://127.0.0.1:6379/1"
    celery_result_backend: str = "redis://127.0.0.1:6379/2"

    cors_origins: str = "http://localhost:1111,http://127.0.0.1:1111"

    rate_limit_per_minute: int = 60

    @property
    def database_url(self) -> str:
        if self.db_password:
            return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            return f"postgresql+psycopg2://{self.db_user}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
