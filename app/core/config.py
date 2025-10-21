from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    APP_NAME: str = "CareerPath-AI"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database Configuration
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"  # Pro docker

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")

    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")


settings = Settings()
