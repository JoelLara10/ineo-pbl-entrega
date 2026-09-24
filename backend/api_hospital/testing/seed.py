"""Repeatable synthetic dataset using the application's real collection names."""
from datetime import datetime
import os
from urllib.parse import urlsplit

import bcrypt
from bson import ObjectId

ROLES = ('admin', 'medico', 'enfermeria', 'estudios')
COLLECTIONS = ('users', 'pacientes', 'atencion', 'signos_vitales', 'catalogo_examenes',
               'examenes_det', 'camas', 'counters', 'spark_jobs')


def reset(db):
    if not db.name.startswith('ineo_test_'):
        raise ValueError('La base debe comenzar con ineo_test_.')
    for name in COLLECTIONS:
        db[name].delete_many({})
    for index, role in enumerate(ROLES, 1):
        db.users.insert_one({'_id': ObjectId(f'{index:024x}'), 'id': index,
                             'username': role + '.test', 'role': role, 'activo': True,
                             'nombre': 'Usuario sintético', 'papell': role,
                             'password': bcrypt.hashpw(b'Prueba-Sprint7!', bcrypt.gensalt(rounds=4))})
    for index in range(1, 9):
        db.pacientes.insert_one({'Id_exp': index, 'nom_pac': f'SINTETICO {index}',
                                  'papell': 'PRUEBA', 'curp': f'SINTETICO-{index:08d}',
                                  'fecnac': datetime(2000, 1, index)})
        db.atencion.insert_one({'id_atencion': index, 'Id_exp': index, 'area': 'PRUEBA',
                                 'status': 'ABIERTA' if index % 2 else 'CERRADA',
                                 'fecha_ing': datetime(2026, 1, index)})
        db.signos_vitales.insert_one({'id_atencion': index, 'fc': float(60 + index * 5),
                                      'fr': float(12 + index), 'temp': 36.0 + index / 10,
                                      'spo2': float(100 - index)})
    db.catalogo_examenes.insert_one({'id_catalogo': 1, 'tipo': 'LABORATORIO', 'nombre': 'PRUEBA'})
    db.examenes_det.insert_one({'id_examen': 1, 'id_catalogo': 1, 'id_atencion': 1, 'estado': 'PENDIENTE'})
    db.camas.insert_one({'id_cama': 1, 'numero': 'TEST-1', 'ocupada': 0})
    db.counters.insert_one({'_id': 'pacientes_Id_exp', 'seq': 8})


def main():
    from pymongo import MongoClient
    uri = os.environ.get('MONGO_URI', '')
    name = os.environ.get('MONGO_DB', '')
    if (os.environ.get('INEO_TEST_RESET') != 'YES' or not name.startswith('ineo_test_')
            or urlsplit(uri).hostname not in ('localhost', '127.0.0.1', 'mongo-test')):
        raise SystemExit('Reset bloqueado: requiere INEO_TEST_RESET=YES, Mongo local y base ineo_test_*.')
    with MongoClient(uri, serverSelectionTimeoutMS=3000) as client:
        reset(client[name])
    print('Datos sintéticos restablecidos.')


if __name__ == '__main__':
    main()
