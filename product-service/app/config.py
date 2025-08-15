from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "product-service"
    APP_PORT: int = 8002

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres_products:5432/product_service"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
