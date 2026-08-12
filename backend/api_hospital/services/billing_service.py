from utils.database import get_collection, serialize_doc, get_next_sequence
from datetime import datetime
from decimal import Decimal

class BillingService:
    @staticmethod
    def get_patient_bill(id_atencion):
        """Obtiene la cuenta completa de un paciente"""
        db = get_collection('cuenta_paciente').database
        
        # Obtener información de atención
        atencion = db['atencion'].find_one({'id_atencion': id_atencion})
        if not atencion:
            return None
        
        # Obtener paciente
        paciente = db['pacientes'].find_one({'Id_exp': atencion['Id_exp']})
        
        # Obtener items
        items = list(db['cuenta_paciente'].find(
            {'id_atencion': id_atencion}
        ).sort('fecha', 1))
        
        # Calcular totales
        subtotal = sum(item.get('subtotal', 0) for item in items)
        iva = subtotal * Decimal('0.16')
        total = subtotal + iva
        
        # Obtener pagos
        payments = list(db['depositos_pserv'].find(
            {'id_atencion': id_atencion}
        ))
        
        total_paid = sum(payment.get('deposito', 0) for payment in payments)
        
        return {
            'id_atencion': id_atencion,
            'Id_exp': atencion['Id_exp'],
            'paciente': f"{paciente.get('papell', '')} {paciente.get('nom_pac', '')}" if paciente else '',
            'fecha_ing': atencion.get('fecha_ing').strftime('%Y-%m-%d %H:%M') if atencion.get('fecha_ing') else '',
            'items': [serialize_doc(item) for item in items],
            'subtotal': float(subtotal),
            'iva': float(iva),
            'total': float(total),
            'payments': [{'amount': float(p.get('deposito', 0)), 'date': p.get('fecha').strftime('%Y-%m-%d %H:%M')} for p in payments],
            'total_paid': float(total_paid),
            'balance': float(total - total_paid)
        }
    
    @staticmethod
    def add_billing_item(id_atencion, data):
        """Agrega un item a la cuenta del paciente"""
        collection = get_collection('cuenta_paciente')
        
        # Obtener Id_exp
        db = get_collection('atencion').database
        atencion = db['atencion'].find_one({'id_atencion': id_atencion})
        
        if not atencion:
            return None
        
        cantidad = int(data.get('cantidad', 1))
        precio = Decimal(str(data.get('precio', 0)))
        subtotal = precio * cantidad
        
        item = {
            'id_atencion': id_atencion,
            'Id_exp': atencion['Id_exp'],
            'fecha': datetime.now(),
            'descripcion': data.get('descripcion'),
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': subtotal,
            'tipo': data.get('tipo', 'SERVICIO'),
            'estado': 'PENDIENTE'
        }
        
        result = collection.insert_one(item)
        return serialize_doc(item)
    
    @staticmethod
    def remove_billing_item(id_atencion, item_id):
        """Elimina un item de la cuenta"""
        collection = get_collection('cuenta_paciente')
        
        # Nota: Necesitarías un campo único para identificar items
        # Por simplicidad, usamos _id
        from bson import ObjectId
        
        result = collection.delete_one({
            '_id': ObjectId(item_id),
            'id_atencion': id_atencion
        })
        
        return result.deleted_count > 0
    
    @staticmethod
    def register_payment(id_atencion, data, user_id):
        """Registra un pago"""
        collection = get_collection('depositos_pserv')
        
        payment = {
            'id_atencion': id_atencion,
            'deposito': Decimal(str(data.get('amount'))),
            'tipo_pago': data.get('payment_method'),
            'fecha': datetime.now(),
            'usuario_registro': user_id,
            'referencia': data.get('reference', ''),
            'observaciones': data.get('observations', '')
        }
        
        result = collection.insert_one(payment)
        return serialize_doc(payment)
    
    @staticmethod
    def get_payments(id_atencion):
        """Obtiene historial de pagos"""
        collection = get_collection('depositos_pserv')
        
        payments = list(collection.find(
            {'id_atencion': id_atencion}
        ).sort('fecha', -1))
        
        return [serialize_doc(p) for p in payments]
    
    @staticmethod
    def get_daily_report(date):
        """Reporte diario de ingresos"""
        db = get_collection('depositos_pserv').database
        
        start_date = datetime.strptime(date, '%Y-%m-%d')
        end_date = start_date.replace(hour=23, minute=59, second=59)
        
        # Ingresos por método de pago
        payments_by_method = list(db['depositos_pserv'].aggregate([
            {'$match': {
                'fecha': {'$gte': start_date, '$lte': end_date}
            }},
            {'$group': {
                '_id': '$tipo_pago',
                'total': {'$sum': '$deposito'},
                'count': {'$sum': 1}
            }}
        ]))
        
        # Total general
        total_income = sum(p['total'] for p in payments_by_method)
        
        # Atenciones del día
        attentions = db['atencion'].count_documents({
            'fecha_ing': {'$gte': start_date, '$lte': end_date}
        })
        
        return {
            'date': date,
            'total_income': float(total_income),
            'attentions': attentions,
            'payments_by_method': [{
                'method': p['_id'],
                'total': float(p['total']),
                'count': p['count']
            } for p in payments_by_method]
        }
    
    @staticmethod
    def get_monthly_report(year, month):
        """Reporte mensual de ingresos"""
        db = get_collection('depositos_pserv').database
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Ingresos diarios
        daily_income = list(db['depositos_pserv'].aggregate([
            {'$match': {
                'fecha': {'$gte': start_date, '$lt': end_date}
            }},
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$fecha'}},
                'total': {'$sum': '$deposito'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]))
        
        # Total del mes
        total_month = sum(d['total'] for d in daily_income)
        
        return {
            'year': year,
            'month': month,
            'total_income': float(total_month),
            'daily_breakdown': [{
                'date': d['_id'],
                'total': float(d['total']),
                'transactions': d['count']
            } for d in daily_income]
        }