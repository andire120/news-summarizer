from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_NAME: str = "csebuetnlp/mT5_multilingual_XLSum"
    CACHE_SIZE: int = 128

    class Config:
        env_file = ".env"

settings = Settings()