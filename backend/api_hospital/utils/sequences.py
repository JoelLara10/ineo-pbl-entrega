from utils.database import get_collection

def get_next_sequence(name):
    """
    Obtiene el siguiente valor de una secuencia
    Útil para IDs autoincrementales
    """
    collection = get_collection('counters')
    
    result = collection.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        upsert=True,
        return_document=True
    )
    
    return result['seq']

def reset_sequence(name, value=1):
    """Reinicia una secuencia a un valor específico"""
    collection = get_collection('counters')
    
    collection.update_one(
        {'_id': name},
        {'$set': {'seq': value}},
        upsert=True
    )

def get_current_sequence(name):
    """Obtiene el valor actual de una secuencia sin incrementar"""
    collection = get_collection('counters')
    
    result = collection.find_one({'_id': name})
    return result['seq'] if result else 0