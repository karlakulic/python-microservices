from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    ALGORITHM: str

    class Config:
        env_file = ".env"

settings = Settings()