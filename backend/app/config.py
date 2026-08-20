import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/hidar")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Africa's Talking SMS
    AFRICASTALKING_USERNAME: str = os.getenv("AFRICASTALKING_USERNAME", "")
    AFRICASTALKING_API_KEY: str = os.getenv("AFRICASTALKING_API_KEY", "")
    SMS_SENDER_ID: str = os.getenv("SMS_SENDER_ID", "HIDAR")

    # Telebirr (for future integration)
    TELEBIRR_APP_ID: str = os.getenv("TELEBIRR_APP_ID", "")
    TELEBIRR_APP_KEY: str = os.getenv("TELEBIRR_APP_KEY", "")
    TELEBIRR_BASE_URL: str = os.getenv("TELEBIRR_BASE_URL", "https://196.188.120.3:38443")  # Sandbox URL[reference:1]

settings = Settings()
