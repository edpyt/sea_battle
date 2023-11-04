import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET: str = "SECRET"
    MONGODB_URL: str = os.getenv('MONGODB_URL')

    class Config:
        if not os.getenv('DOCKER'):
            env_file = '.env'
        from_attributes = True


settings = Settings()
