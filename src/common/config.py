from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = '.env'


def get_settings() -> Settings:
    return Settings()
