"""Real local HTTP/Mongo QA launcher; uses only the isolated test database."""
import os
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'backend/api_hospital'))
os.environ['MONGO_URI'] = 'mongodb://127.0.0.1:27029/'
os.environ['MONGO_DB'] = 'ineo_test_s10'
os.environ['SECRET_KEY'] = secrets.token_urlsafe(48)
os.environ['ENABLE_SCHEDULER'] = 'false'
os.environ['ANALYSIS_ENGINE'] = 'lightweight'
os.environ['CORS_ORIGINS'] = 'http://localhost:5173'

if __name__ == '__main__':
    from pymongo import MongoClient
    from testing.seed import reset
    from app import create_app
    with MongoClient(os.environ['MONGO_URI'], serverSelectionTimeoutMS=5000) as client:
        client.admin.command('ping')
        reset(client['ineo_test_s10'])
        client['ineo_test_s10'].nursing_assessment.delete_many({})
    create_app().run(host='127.0.0.1', port=5029, debug=False, use_reloader=False)
