import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv('MONGODB_URL')

    class Config:
        if not os.getenv('DOCKER'):
            env_file = '.env'
        from_attributes = True


settings = Settings()
