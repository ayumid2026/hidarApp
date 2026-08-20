import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # SQLite database (embedded in repo)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./hidar.db")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # SMS (optional)
    AFRICASTALKING_USERNAME: str = os.getenv("AFRICASTALKING_USERNAME", "")
    AFRICASTALKING_API_KEY: str = os.getenv("AFRICASTALKING_API_KEY", "")
    SMS_SENDER_ID: str = os.getenv("SMS_SENDER_ID", "HIDAR")

settings = Settings()
