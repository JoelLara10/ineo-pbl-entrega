"""Clinical instants are stored in UTC and serialized with an explicit offset."""
from datetime import datetime, timezone
from utils.database import serialize_doc


def serialize_clinical_record(document):
    result = serialize_doc(document)
    if isinstance(document, dict) and isinstance(document.get('fecha_registro'), datetime):
        value = document['fecha_registro']
        # PyMongo returns naive UTC by default; never use the server local zone.
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        result['fecha_registro'] = value.astimezone(timezone.utc).isoformat()
    return result
