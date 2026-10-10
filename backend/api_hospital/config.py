import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def _csv_env(name, default):
    value = os.getenv(name)
    if not value:
        return list(default)
    return [item.strip().rstrip('/') for item in value.split(',') if item.strip()]


class Config:
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGO_DB', 'ineo_db2')

    # JWT
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # API
    API_TITLE = "Hospital API"
    API_VERSION = "v1"
    API_PREFIX = "/api/v1"

    # CORS
    CORS_ORIGINS = _csv_env('CORS_ORIGINS', (
        'http://localhost:5173',
        'http://127.0.0.1:5173',
    ))

    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 1024 * 1024))
    LOGIN_MAX_ATTEMPTS = int(os.getenv('LOGIN_MAX_ATTEMPTS', 5))
    LOGIN_WINDOW_SECONDS = int(os.getenv('LOGIN_WINDOW_SECONDS', 15 * 60))

    # Paginación
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


config = Config()
