from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str
    LOG_LEVEL: str

    DB_PROTOCOL: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @property
    def db_dsn(self) -> str:
        return f"{self.DB_PROTOCOL}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def db_safe_dsn(self) -> str:
        return f"{self.DB_PROTOCOL}://{self.DB_USER}:******@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


base_settings = Settings()
