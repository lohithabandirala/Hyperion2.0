from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "NTRO Gen AI Platform"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./ntro.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Configuration
    LLM_PROVIDER: str = "gemini" # gemini, openai, groq, mock
    MODEL_NAME: str = "gemini-2.5-flash"
    GEMINI_API_KEY: Optional[str] = ""
    OPENAI_API_KEY: Optional[str] = ""
    GROQ_API_KEY: Optional[str] = ""
    
    # Security
    SECRET_KEY: str = "ntro-super-secret-key-change-in-production-26154"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    MAX_FILE_SIZE_MB: int = 50
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
