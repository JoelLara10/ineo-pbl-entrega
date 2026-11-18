"""Launch the real application using a dedicated synthetic database only."""
import os
from pathlib import Path
import secrets
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'backend/api_hospital'))
os.environ.update(MONGO_URI='mongodb://127.0.0.1:27111/',MONGO_DB='ineo_test_s11',
    SECRET_KEY=secrets.token_urlsafe(48), ENABLE_SCHEDULER='false',
    ANALYSIS_ENGINE='lightweight',CORS_ORIGINS='http://127.0.0.1:5111,http://localhost:5111',
    LOGIN_MAX_ATTEMPTS='1000')
if __name__=='__main__':
    from pymongo import MongoClient
    from testing.seed import reset
    from app import create_app
    with MongoClient(os.environ['MONGO_URI'],serverSelectionTimeoutMS=5000) as mongo:
        mongo.admin.command('ping');db=mongo['ineo_test_s11'];reset(db)
        db.fluid_balance.delete_many({});db.revoked_tokens.delete_many({})
    # Threaded HTTP is intentional for the concurrent load campaign.
    create_app().run(host='127.0.0.1',port=5110,threaded=True,debug=False,use_reloader=False)
