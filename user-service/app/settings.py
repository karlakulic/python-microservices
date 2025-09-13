from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "user-service"
    APP_PORT: int = 8001

    SECRET_KEY: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)
    ALGORITHM: str = "HS256"

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres_users:5432/user_service"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

settings = Settings()