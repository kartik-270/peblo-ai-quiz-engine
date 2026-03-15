from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Peblo AI Content Ingestion + Adaptive Quiz Engine"
    HF_TOKEN: str = ""
    DATABASE_URL: str = "sqlite:///./quiz_engine.db"

    class Config:
        env_file = ".env"

settings = Settings()
