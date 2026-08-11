import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGO_DB', 'hospital_db')
    
    # JWT
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu-clave-secreta-muy-segura-cambiar-en-produccion')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-cambiar')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # API
    API_TITLE = "Hospital API"
    API_VERSION = "v1"
    API_PREFIX = "/api/v1"
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:8081",
        "http://localhost:19006",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.67:5173",
        "http://10.30.40.67:5173",
        "http://10.178.52.14:5173",
        "http://192.168.1.4:5173",
    ]
    
    # Paginación
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

config = Config()