# app\core\config.py
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig
from pathlib import Path
import os

load_dotenv()


class Settings:
    APP_NAME: str = "CareerPath-AI"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    FRONTEND_HOST: str = os.getenv("FRONTEND_HOST")

    # Database Configuration
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"  # Pro docker

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    # Email
    conf = ConnectionConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_FROM=os.getenv("MAIL_FROM"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
        MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
        MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
        USE_CREDENTIALS=os.getenv("USE_CREDENTIALS", "True").lower() == "true",
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
    )
    RESET_PASSWORD_TOKEN_EXPIRE_HOURS = 1

    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")


settings = Settings()
