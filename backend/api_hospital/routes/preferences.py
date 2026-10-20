"""Only a non-clinical language preference can be synchronized offline."""
from flask import Blueprint, g, jsonify, request
from pymongo.errors import PyMongoError
from middleware.auth_middleware import token_required
from utils.database import get_collection

preferences_bp = Blueprint('preferences', __name__)


@preferences_bp.route('/preferences', methods=['GET', 'PUT'])
@token_required
def preferences():
    try:
        collection = get_collection('user_preferences')
        if request.method == 'PUT':
            data = request.get_json(silent=True)
            if (not isinstance(data, dict) or set(data) != {'language'}
                    or data.get('language') not in ('es', 'en')):
                return jsonify(error='Sólo se permite el idioma es o en.'), 400
            # PUT replaces one allowlisted value; replaying it is idempotent.
            collection.update_one({'_id': g.user['user_id']},
                                  {'$set': {'language': data['language']}}, upsert=True)
            return jsonify(language=data['language'])
        stored = collection.find_one({'_id': g.user['user_id']}) or {}
        return jsonify(language=stored.get('language', 'es'))
    except PyMongoError:
        return jsonify(error='Preferencias temporalmente no disponibles.'), 503
