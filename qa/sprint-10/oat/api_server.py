"""Run the real Flask application against the disposable Docker Mongo only."""
import argparse
import logging
import os
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--mongo-port', type=int, required=True)
parser.add_argument('--port', type=int, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root / 'backend/api_hospital'))
# Set before importing dotenv/config/database. Never inherit production settings.
os.environ.update(MONGO_URI=f'mongodb://127.0.0.1:{args.mongo_port}/',
                  MONGO_DB='ineo_test_s10', ENABLE_SCHEDULER='false',
                  SECRET_KEY='sprint10-disposable-local-test-only-key',
                  JWT_SECRET_KEY='sprint10-disposable-local-test-only-key')
logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
from app import create_app
from werkzeug.serving import run_simple

run_simple('127.0.0.1', args.port, create_app(), use_reloader=False)
