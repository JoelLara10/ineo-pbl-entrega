"""Local-only UAT simulation using a dedicated synthetic MongoDB instance.

Run: python -m testing.uat_server
Requires MongoDB on 127.0.0.1:27029. Never use this launcher for a deployed service.
"""
import os
import secrets

os.environ['MONGO_URI'] = 'mongodb://127.0.0.1:27029/'
os.environ['MONGO_DB'] = 'ineo_test_uat_simulation'
os.environ['SECRET_KEY'] = secrets.token_urlsafe(48)
os.environ['ENABLE_SCHEDULER'] = 'false'
os.environ['CORS_ORIGINS'] = 'http://127.0.0.1:5189,http://localhost:5189'


def main():
    from pymongo import MongoClient
    from utils.database import db_instance
    from testing.seed import reset
    from services import spark_service
    from services.analysis_lightweight import analyze
    from app import create_app
    from bson import ObjectId
    import bcrypt

    original_client = db_instance.client
    db_instance.client = MongoClient(os.environ['MONGO_URI'], serverSelectionTimeoutMS=3000)
    db_instance.db = db_instance.client[os.environ['MONGO_DB']]
    original_client.close()
    db = db_instance.db
    reset(db)
    db.atencion.update_many({}, {'$set': {'area': 'Ambulatorio'}})
    db.users.insert_one({'_id': ObjectId('000000000000000000000005'), 'id': 5,
        'username': 'administrativo.test', 'role': 'administrativo', 'activo': True,
        'nombre': 'Administración', 'papell': 'SIMULADA',
        'password': bcrypt.hashpw(b'Prueba-Sprint7!', bcrypt.gensalt(rounds=4))})
    db.signos_vitales.update_many({}, {'$set': {'fecha_registro': '2026-01-05T12:00:00Z'}})
    # The same real lightweight engine exercised by API regressions, no Spark subprocess.
    spark_service.run_engine = analyze
    for kind in spark_service.TYPES:
        spark_service.start(kind)
        # start uses its regular asynchronous worker; UI can also execute new jobs.
    create_app().run(host='127.0.0.1', port=5019, debug=False, use_reloader=False)


if __name__ == '__main__':
    main()
