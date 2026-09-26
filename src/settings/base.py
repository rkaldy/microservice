from enum import Enum

from pydantic_settings import BaseSettings
from sqlalchemy import URL


class DBType(Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"


DB_PROTOCOL_MAPPING: dict[DBType, str] = {
    DBType.MYSQL: "mysql+aiomysql",
    DBType.POSTGRESQL: "postgresql+asyncpg",
}


class Settings(BaseSettings):
    APP_ENV: str
    LOG_LEVEL: str
    SENTRY_DSN: str | None = None
    BEARER_TOKEN: str | None = None
    API_SERVER_WORKERS: int = 1

    DB_TYPE: DBType
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    DB_POOL_SIZE: int
    DB_POOL_TIMEOUT: int
    DB_POOL_RECYCLE: int

    DB_QUERY_RETRY_COUNT: int
    DB_QUERY_RETRY_WAIT_ARGS: dict[str, float]

    def _db_url(self) -> URL:
        return URL.create(
            drivername=DB_PROTOCOL_MAPPING[self.DB_TYPE],
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            database=self.DB_NAME,
        )

    @property
    def db_dsn(self) -> str:
        return self._db_url().render_as_string(hide_password=False)

    @property
    def db_safe_dsn(self) -> str:
        return self._db_url().render_as_string(hide_password=True)
