import pytest

from src.settings.base import DBType, Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        APP_ENV="test",
        LOG_LEVEL="info",
        DB_TYPE=DBType.POSTGRESQL,
        DB_HOST="db.example.com",
        DB_NAME="example",
        DB_USER="user@example.com",
        DB_PASSWORD="p@ss:word/with special characters",
        DB_POOL_SIZE=1,
        DB_POOL_TIMEOUT=10,
        DB_POOL_RECYCLE=1800,
        DB_QUERY_RETRY_COUNT=3,
        DB_QUERY_RETRY_WAIT_ARGS={"factor": 0.1, "base": 1.5},
    )


def test_db_dsn_escapes_credentials(settings: Settings):
    assert (
        settings.db_dsn
        == "postgresql+asyncpg://user%40example.com:p%40ss%3Aword%2Fwith special characters@db.example.com/example"
    )


def test_db_safe_dsn_hides_password(settings: Settings):
    assert (
        settings.db_safe_dsn == "postgresql+asyncpg://user%40example.com:***@db.example.com/example"
    )
