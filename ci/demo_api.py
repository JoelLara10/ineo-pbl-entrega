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
parser.add_argument('--uat-regressions', action='store_true')
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
if args.uat_regressions:
    from bson import ObjectId
    from datetime import datetime
    db = db_instance.db
    user = dict(db.users.find_one({'username': 'admin.test'}))
    user.update(_id=ObjectId(f'{5:024x}'), id=5, username='administrativo.test', role='administrativo')
    db.users.insert_one(user)
    common = dict(id_atencion=1, Id_exp=1, id_enfermero=ObjectId(f'{3:024x}'),
                  fecha_registro=datetime(2026, 10, 29, 18, 30))
    db.nursing_assessment.insert_one(dict(common, id_valoracion=9001, valoracion=dict(
        estado_general='Estable', dolor='2', movilidad='Independiente', riesgo_caidas='Bajo',
        riesgo_upp='Bajo', observaciones='QA-UTC-1830')))
    db.fluid_balance.insert_one(dict(common, id_balance=9001, ingresos_orales=200,
        ingresos_iv=0, egresos_orina=100, egresos_drenajes=0, total_ingresos=200,
        total_egresos=100, balance_neto=100, observaciones='QA-UTC-1830'))
    db.nursing_care.insert_one(dict(common, id_cuidado=9001, diagnostico_enfermeria='QA-UTC-1830',
        objetivos='Confort', intervenciones='Vigilancia', evaluacion='Estable', estado='EN_PROCESO'))
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
