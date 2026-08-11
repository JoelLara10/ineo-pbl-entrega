from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from datetime import datetime
from bson import ObjectId
from bson.decimal128 import Decimal128
from decimal import Decimal

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        # MongoClient conecta de forma diferida. Así Flask puede iniciar aunque
        # Atlas esté temporalmente sin conexión y /backup/health puede reportarlo.
        self.client = MongoClient(
            os.getenv('MONGO_URI', 'mongodb://localhost:27017/'),
            serverSelectionTimeoutMS=5000,
            connect=False
        )
        self.db = self.client[os.getenv('MONGO_DB', 'hospital_db')]
    
    def get_db(self):
        return self.db
    
    def get_collection(self, name):
        return self.db[name]
    
    def close(self):
        if self.client:
            self.client.close()

# Singleton instance
db_instance = Database()

def get_db():
    return db_instance.get_db()

def get_collection(name):
    return db_instance.get_collection(name)

# Helper para serializar ObjectId
def serialize_doc(doc):
    """Convierte documentos MongoDB a JSON serializable"""
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == '_id':
                result['id'] = str(value)
            elif isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Decimal128):
                result[key] = float(value.to_decimal())
            elif isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    return doc

def get_next_sequence(name):
    """Obtiene el siguiente valor de una secuencia"""
    db = get_db()
    counters = db['counters']
    
    result = counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return result['seq']
