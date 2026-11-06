"""PBL-30 SIT server. Dedicated local Mongo only; no deployed credentials."""
import os
import secrets

os.environ['MONGO_URI'] = 'mongodb://127.0.0.1:27029/'
os.environ['MONGO_DB'] = 'ineo_test_contract_sprint10'
os.environ['SECRET_KEY'] = secrets.token_urlsafe(48)
os.environ['ENABLE_SCHEDULER'] = 'false'
os.environ['ANALYSIS_ENGINE'] = 'lightweight'
os.environ['CORS_ORIGINS'] = 'http://localhost:5173'


def main():
    from pymongo import MongoClient
    from testing.seed import reset
    from app import create_app
    with MongoClient(os.environ['MONGO_URI'], serverSelectionTimeoutMS=3000) as mongo:
        mongo.admin.command('ping')
        reset(mongo[os.environ['MONGO_DB']])
    create_app().run(host='127.0.0.1', port=5029, debug=False, use_reloader=False)


if __name__ == '__main__':
    main()
