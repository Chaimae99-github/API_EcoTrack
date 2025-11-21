# app/core/config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    PROJECT_NAME: str = "EcoTrack API"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey123")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

settings = Settings()

