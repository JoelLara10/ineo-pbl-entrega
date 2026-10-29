"""Disposable HTTP API for local OAT: synthetic, in-memory data only."""
import argparse
import json
import os
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--ready-file', type=Path, required=True)
parser.add_argument('--port', type=int, default=0)
parser.add_argument('--database-down', action='store_true')
args = parser.parse_args()
os.environ.update(MONGO_URI='mongodb://127.0.0.1:1/', MONGO_DB='ineo_test_oat_demo',
                  SECRET_KEY='synthetic-oat-only-never-production', ENABLE_SCHEDULER='false')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend/api_hospital'))
import mongomock
from pymongo.errors import ConnectionFailure
from utils.database import db_instance
from testing.seed import reset
db_instance.client = mongomock.MongoClient()
db_instance.db = db_instance.client['ineo_test_oat_demo']
reset(db_instance.db)
if args.database_down:
    def unavailable(*a, **kw):
        raise ConnectionFailure('mongodb://synthetic:secret-canary@private-host/test')
    db_instance.db.command = unavailable
import app as module
module.init_scheduler = lambda app: None
from werkzeug.serving import make_server
server = make_server('127.0.0.1', args.port, module.create_app())
args.ready_file.write_text(json.dumps({'port': server.server_port, 'pid': os.getpid()}), encoding='utf8')
server.serve_forever()
