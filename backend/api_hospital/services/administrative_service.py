from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation

from bson import ObjectId
from bson.decimal128 import Decimal128

from config import config
from utils.database import get_collection, get_next_sequence, serialize_doc


class AdministrativeService:
    AREA_SECTION = {
        'Ambulatorio': 'consulta',
        'Consulta': 'consulta',
        'Urgencias': 'preparacion',
        'Preparacion': 'preparacion',
        'Preparaci\u00f3n': 'preparacion',
        'Hospitalizado': 'recuperacion',
        'Recuperacion': 'recuperacion',
        'Recuperaci\u00f3n': 'recuperacion',
    }

    SECTION_META = {
        'consulta': {
            'title': 'Pacientes en consulta',
            'accent': '#4299e1',
            'icon': 'people-outline',
            'roomLabel': 'Consultorio',
        },
        'preparacion': {
            'title': 'Pacientes en preparacion',
            'accent': '#f56565',
            'icon': 'alert-circle-outline',
            'roomLabel': 'Espacio',
        },
        'recuperacion': {
            'title': 'Pacientes en recuperacion',
            'accent': '#48bb78',
            'icon': 'bed-outline',
            'roomLabel': 'Consultorio',
        },
    }

    @staticmethod
    def _db():
        return get_collection('pacientes').database

    @staticmethod
    def _to_decimal(value):
        if value is None or value == '':
            return Decimal('0')
        if isinstance(value, Decimal128):
            return value.to_decimal()
        if isinstance(value, Decimal):
            return value
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal('0')

    @staticmethod
    def _to_int(value):
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, time.min)
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return None

            try:
                parsed = datetime.fromisoformat(raw.replace('Z', '+00:00'))
                return parsed.replace(tzinfo=None)
            except ValueError:
                pass

            candidates = [raw]
            if 'T' in raw:
                candidates.append(raw.split('T')[0].strip())
            if ' ' in raw:
                candidates.append(raw.split(' ')[0].strip())

            for candidate in dict.fromkeys(candidates):
                for fmt in (
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%d/%m/%Y %H:%M:%S',
                    '%d/%m/%Y %H:%M',
                    '%Y-%m-%d',
                    '%d/%m/%Y',
                ):
                    try:
                        return datetime.strptime(candidate, fmt)
                    except ValueError:
                        continue
        return None

    @staticmethod
    def _date_query(field, start, end):
        return {
            '$or': [
                {field: {'$gte': start, '$lt': end}},
                {field: {'$regex': f'^{start.strftime("%Y-%m-%d")}'}},
                {field: {'$regex': f'^{start.strftime("%d/%m/%Y")}'}},
            ]
        }

    @staticmethod
    def _sort_date(value):
        return AdministrativeService._parse_date(value) or datetime.min

    @staticmethod
    def _format_time(value):
        parsed = AdministrativeService._parse_date(value)
        return parsed.strftime('%H:%M') if parsed else ''

    @staticmethod
    def _format_any_date(value):
        parsed = AdministrativeService._parse_date(value)
        if parsed:
            return parsed.isoformat()
        return str(value or '')

    @staticmethod
    def _format_date(value):
        parsed = AdministrativeService._parse_date(value)
        return parsed.strftime('%Y-%m-%d') if parsed else ''

    @staticmethod
    def _format_datetime(value):
        parsed = AdministrativeService._parse_date(value)
        return parsed.isoformat() if parsed else ''

    @staticmethod
    def _date_bounds(value=None):
        parsed = AdministrativeService._parse_date(value) or datetime.now()
        start = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=1)

    @staticmethod
    def _calculate_age(value):
        birth = AdministrativeService._parse_date(value)
        if not birth:
            return 0
        today = datetime.now().date()
        born = birth.date()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @staticmethod
    def _patient_name(patient):
        if not patient:
            return ''
        parts = [
            patient.get('papell', ''),
            patient.get('sapell', ''),
            patient.get('nom_pac', ''),
        ]
        return ' '.join(str(part).strip() for part in parts if part).strip()

    @staticmethod
    def _record_label(id_exp):
        try:
            return f"INEO-{int(id_exp):06d}"
        except (TypeError, ValueError):
            return str(id_exp or '')

    @staticmethod
    def _attention_label(id_atencion):
        return f"A-{id_atencion}" if id_atencion is not None else ''

    @staticmethod
    def _resolve_bed_id(db, data):
        value = data.get('id_cama')
        if value is None:
            value = data.get('cama', data.get('bed'))

        bed_id = AdministrativeService._to_int(value)
        if bed_id is not None:
            return bed_id

        if isinstance(value, str) and value.strip():
            bed = db['camas'].find_one({'numero': value.strip()})
            return bed.get('id_cama') if bed else None

        return None

    @staticmethod
    def _bed_label(db, appointment):
        if not appointment:
            return ''

        id_cama = appointment.get('id_cama')
        if id_cama:
            bed = db['camas'].find_one({'id_cama': id_cama})
            if bed:
                return bed.get('numero') or str(id_cama)

        area = appointment.get('area')
        if AdministrativeService.AREA_SECTION.get(area) == 'consulta':
            return f"Consulta {appointment.get('id_atencion')}"

        return 'Sin cama'

    @staticmethod
    def _normalize_doctor_ids(db, data):
        raw = (
            data.get('medicos')
            or data.get('doctores')
            or data.get('assignedDoctors')
            or data.get('doctors')
            or []
        )
        if isinstance(raw, (str, int)):
            raw = [raw]

        doctor_ids = []
        for item in raw[:5]:
            value = item
            if isinstance(item, dict):
                value = item.get('id') or item.get('id_medico') or item.get('_id') or item.get('username')

            doctor_id = AdministrativeService._to_int(value)
            if doctor_id is None and isinstance(value, str) and value.strip():
                user = None
                try:
                    user = db['users'].find_one({'_id': ObjectId(value)})
                except Exception:
                    pass
                if not user:
                    text = value.strip()
                    user = db['users'].find_one({
                        '$or': [
                            {'username': text},
                            {'nombre': text},
                            {'papell': text},
                        ]
                    })
                doctor_id = user.get('id') if user else None

            if doctor_id is not None and doctor_id not in doctor_ids:
                doctor_ids.append(doctor_id)

        return doctor_ids[:5]

    @staticmethod
    def _doctor_names(db, id_atencion):
        medicos = list(db['atencion_medicos'].find({'id_atencion': id_atencion}))
        ids = [m.get('id_medico') for m in medicos if m.get('id_medico') is not None]
        if not ids:
            return []

        users = list(db['users'].find({'id': {'$in': ids}}))
        by_id = {user.get('id'): user for user in users}
        names = []
        for doctor_id in ids:
            user = by_id.get(doctor_id)
            if not user:
                continue
            name = ' '.join(
                part.strip()
                for part in [
                    str(user.get('nombre', '') or ''),
                    str(user.get('papell', '') or ''),
                ]
                if part
            ).strip()
            names.append(name or user.get('username') or str(doctor_id))
        return names

    @staticmethod
    def _matches_search(row, search):
        query = (search or '').strip().lower()
        if not query:
            return True
        values = [
            row.get('record'),
            row.get('attention'),
            row.get('name'),
            row.get('patient'),
            row.get('phone'),
            row.get('bed'),
            row.get('area'),
            row.get('doctor'),
            row.get('reason'),
        ]
        text = ' '.join(str(value or '') for value in values).lower()
        return query in text

    @staticmethod
    def _appointment_patient_row(db, appointment, patient=None):
        patient = patient or db['pacientes'].find_one({'Id_exp': appointment.get('Id_exp')})
        if not patient:
            return None

        doctor_names = AdministrativeService._doctor_names(db, appointment.get('id_atencion'))
        doctor = ', '.join(doctor_names) if doctor_names else 'Sin medico'
        bed = AdministrativeService._bed_label(db, appointment)
        name = AdministrativeService._patient_name(patient)
        id_exp = patient.get('Id_exp')
        id_atencion = appointment.get('id_atencion')

        return {
            'Id_exp': id_exp,
            'id_atencion': id_atencion,
            'record': AdministrativeService._record_label(id_exp),
            'attention': AdministrativeService._attention_label(id_atencion),
            'account': AdministrativeService._attention_label(id_atencion),
            'name': name,
            'patient': name,
            'age': AdministrativeService._calculate_age(patient.get('fecnac')),
            'birthDate': AdministrativeService._format_date(patient.get('fecnac')),
            'phone': patient.get('tel', ''),
            'bed': bed,
            'room': bed,
            'area': appointment.get('area', ''),
            'section': AdministrativeService.AREA_SECTION.get(appointment.get('area'), 'consulta'),
            'doctor': doctor,
            'doctors': doctor_names,
            'admittedAt': AdministrativeService._format_datetime(appointment.get('fecha_ing')),
            'reason': appointment.get('motivo', ''),
            'specialty': appointment.get('especialidad', ''),
            'allergies': appointment.get('alergias', ''),
            'notice': appointment.get('alergias') or 'Sin aviso',
            'status': appointment.get('status', ''),
        }


    @staticmethod
    def _appointment_rows_bulk(db, appointments):
        """Construye filas administrativas evitando consultas N+1 a MongoDB."""
        if not appointments:
            return []

        patient_ids = {
            appointment.get('Id_exp')
            for appointment in appointments
            if appointment.get('Id_exp') is not None
        }
        attention_ids = {
            appointment.get('id_atencion')
            for appointment in appointments
            if appointment.get('id_atencion') is not None
        }
        bed_ids = {
            appointment.get('id_cama')
            for appointment in appointments
            if appointment.get('id_cama') is not None
        }

        patients_by_id = {
            patient.get('Id_exp'): patient
            for patient in db['pacientes'].find({'Id_exp': {'$in': list(patient_ids)}})
        }

        beds_by_id = {}
        if bed_ids:
            beds_by_id = {
                bed.get('id_cama'): bed
                for bed in db['camas'].find(
                    {'id_cama': {'$in': list(bed_ids)}},
                    {'id_cama': 1, 'numero': 1, 'area': 1}
                )
            }

        doctor_links = []
        if attention_ids:
            doctor_links = list(
                db['atencion_medicos'].find(
                    {'id_atencion': {'$in': list(attention_ids)}},
                    {'id_atencion': 1, 'id_medico': 1}
                )
            )

        doctor_ids = {
            link.get('id_medico')
            for link in doctor_links
            if link.get('id_medico') is not None
        }
        users_by_id = {}
        if doctor_ids:
            users_by_id = {
                user.get('id'): user
                for user in db['users'].find(
                    {'id': {'$in': list(doctor_ids)}},
                    {'id': 1, 'username': 1, 'nombre': 1, 'papell': 1, 'sapell': 1}
                )
            }

        doctors_by_attention = defaultdict(list)
        for link in doctor_links:
            user = users_by_id.get(link.get('id_medico'))
            if not user:
                continue
            name = ' '.join(
                str(part).strip()
                for part in [
                    user.get('nombre', ''),
                    user.get('papell', ''),
                    user.get('sapell', ''),
                ]
                if part
            ).strip()
            doctors_by_attention[link.get('id_atencion')].append(
                name or user.get('username') or str(link.get('id_medico'))
            )

        rows = []
        for appointment in appointments:
            patient = patients_by_id.get(appointment.get('Id_exp'))
            if not patient:
                continue

            id_atencion = appointment.get('id_atencion')
            id_exp = patient.get('Id_exp')
            doctor_names = doctors_by_attention.get(id_atencion, [])
            doctor = ', '.join(doctor_names) if doctor_names else 'Sin medico'

            bed = ''
            id_cama = appointment.get('id_cama')
            if id_cama is not None:
                bed_doc = beds_by_id.get(id_cama)
                if bed_doc:
                    bed = bed_doc.get('numero') or str(id_cama)

            area = appointment.get('area', '')
            if not bed:
                if AdministrativeService.AREA_SECTION.get(area) == 'consulta':
                    bed = f'Consulta {id_atencion}'
                else:
                    bed = 'Sin cama'

            name = AdministrativeService._patient_name(patient)
            rows.append({
                'Id_exp': id_exp,
                'id_atencion': id_atencion,
                'record': AdministrativeService._record_label(id_exp),
                'attention': AdministrativeService._attention_label(id_atencion),
                'account': AdministrativeService._attention_label(id_atencion),
                'name': name,
                'patient': name,
                'age': AdministrativeService._calculate_age(patient.get('fecnac')),
                'birthDate': AdministrativeService._format_date(patient.get('fecnac')),
                'phone': patient.get('tel', ''),
                'bed': bed,
                'room': bed,
                'area': area,
                'section': AdministrativeService.AREA_SECTION.get(area, 'consulta'),
                'doctor': doctor,
                'doctors': doctor_names,
                'admittedAt': AdministrativeService._format_datetime(appointment.get('fecha_ing')),
                'reason': appointment.get('motivo', ''),
                'specialty': appointment.get('especialidad', ''),
                'allergies': appointment.get('alergias', ''),
                'notice': appointment.get('alergias') or 'Sin aviso',
                'status': appointment.get('status', ''),
            })

        return rows

    @staticmethod
    def _patient_record_row(db, patient):
        appointment = db['atencion'].find_one(
            {'Id_exp': patient.get('Id_exp')},
            sort=[('fecha_ing', -1)]
        )

        if appointment:
            return AdministrativeService._appointment_patient_row(db, appointment, patient)

        name = AdministrativeService._patient_name(patient)
        id_exp = patient.get('Id_exp')
        return {
            'Id_exp': id_exp,
            'id_atencion': None,
            'record': AdministrativeService._record_label(id_exp),
            'attention': '',
            'account': '',
            'name': name,
            'patient': name,
            'age': AdministrativeService._calculate_age(patient.get('fecnac')),
            'birthDate': AdministrativeService._format_date(patient.get('fecnac')),
            'phone': patient.get('tel', ''),
            'bed': '',
            'room': '',
            'area': '',
            'section': 'expedientes',
            'doctor': '',
            'doctors': [],
            'admittedAt': '',
            'reason': '',
            'specialty': '',
            'allergies': '',
            'notice': 'Sin aviso',
            'status': '',
        }

    @staticmethod
    def _recent_discharge_rows(db, limit=20):
        expedientes = list(db['expedientes'].find({}).sort('fecha_alta', -1).limit(limit))
        rows = []
        for expediente in expedientes:
            patient = db['pacientes'].find_one({'Id_exp': expediente.get('id_exp')})
            appointment = db['atencion'].find_one({'id_atencion': expediente.get('id_atencion')})
            if not patient:
                continue
            row = (
                AdministrativeService._appointment_patient_row(db, appointment, patient)
                if appointment
                else AdministrativeService._patient_record_row(db, patient)
            )
            row['dischargedAt'] = AdministrativeService._format_datetime(expediente.get('fecha_alta'))
            row['totalCuenta'] = float(AdministrativeService._to_decimal(expediente.get('total_cuenta')))
            rows.append(row)
        return rows


    @staticmethod
    def get_patient_groups(search=''):
        db = AdministrativeService._db()

        active_appointments = list(
            db['atencion'].find({'status': 'ABIERTA'}).sort('fecha_ing', -1)
        )
        active = [
            row
            for row in AdministrativeService._appointment_rows_bulk(db, active_appointments)
            if AdministrativeService._matches_search(row, search)
        ]

        patients = list(db['pacientes'].find({}).sort('Id_exp', -1).limit(30))
        recent = [
            row for row in
            (AdministrativeService._patient_record_row(db, patient) for patient in patients)
            if row and AdministrativeService._matches_search(row, search)
        ]

        discharged = [
            row for row in AdministrativeService._recent_discharge_rows(db)
            if AdministrativeService._matches_search(row, search)
        ]

        return {
            'summary': {
                'activos': len(active),
                'expedientes': len(recent),
                'altas': len(discharged),
            },
            'groups': [
                {
                    'key': 'activos',
                    'title': 'Pacientes activos',
                    'accent': '#667eea',
                    'icon': 'people-outline',
                    'patients': serialize_doc(active),
                },
                {
                    'key': 'expedientes',
                    'title': 'Expedientes recientes',
                    'accent': '#ed8936',
                    'icon': 'folder-open-outline',
                    'patients': serialize_doc(recent),
                },
                {
                    'key': 'altas',
                    'title': 'Altas recientes',
                    'accent': '#48bb78',
                    'icon': 'checkmark-circle-outline',
                    'patients': serialize_doc(discharged),
                },
            ],
        }

    @staticmethod
    def quick_search(query='', limit=10):
        db = AdministrativeService._db()
        regex = {'$regex': f'.*{query or ""}.*', '$options': 'i'}
        mongo_query = {
            '$or': [
                {'curp': regex},
                {'nom_pac': regex},
                {'papell': regex},
                {'sapell': regex},
                {'tel': regex},
            ]
        }
        patients = list(db['pacientes'].find(mongo_query).sort('Id_exp', -1).limit(limit))
        return serialize_doc([
            AdministrativeService._patient_record_row(db, patient)
            for patient in patients
        ])

    @staticmethod
    def get_options(current_id_cama=None):
        db = AdministrativeService._db()
        bed_query = {'ocupada': 0}
        if current_id_cama:
            bed_query = {'$or': [{'ocupada': 0}, {'id_cama': current_id_cama}]}

        beds = list(db['camas'].find(
            bed_query,
            {'id_cama': 1, 'numero': 1, 'area': 1, 'ocupada': 1}
        ).sort('numero', 1))

        medicos = list(db['users'].find(
            {'role': 'medico'},
            {'id': 1, 'username': 1, 'nombre': 1, 'papell': 1, 'sapell': 1}
        ).sort('username', 1))

        services = list(db['cat_servicios'].find(
            {'serv_activo': {'$ne': 'NO'}},
            {'id_serv': 1, 'serv_desc': 1, 'serv_cve': 1, 'serv_costo': 1, 'tipo': 1}
        ).sort('serv_desc', 1).limit(100))

        medicines = list(db['item'].find(
            {},
            {'item_id': 1, 'item_code': 1, 'item_name': 1, 'item_price': 1}
        ).sort('item_name', 1).limit(100))

        return serialize_doc({
            'areas': ['Consulta', 'Preparacion', 'Recuperacion'],
            'areaMap': {
                'Consulta': 'Ambulatorio',
                'Preparacion': 'Urgencias',
                'Recuperacion': 'Hospitalizado',
            },
            'motivos': ['Consulta', 'Cirugia', 'Urgencia', 'Estudio'],
            'especialidades': ['Oftalmologia', 'Retina', 'Cornea', 'Glaucoma'],
            'camas': beds,
            'medicos': medicos,
            'servicios': services,
            'medicamentos': medicines,
        })

    @staticmethod
    def _normalize_area(value):
        if not value:
            return 'Ambulatorio'
        area_map = {
            'consulta': 'Ambulatorio',
            'ambulatorio': 'Ambulatorio',
            'preparacion': 'Urgencias',
            'preparaci\u00f3n': 'Urgencias',
            'urgencias': 'Urgencias',
            'recuperacion': 'Hospitalizado',
            'recuperaci\u00f3n': 'Hospitalizado',
            'hospitalizado': 'Hospitalizado',
        }
        key = str(value).strip().lower()
        return area_map.get(key, value)

    @staticmethod
    def _family_payload(data):
        family = data.get('family') or data.get('familiar_data') or {}
        if not isinstance(family, dict):
            family = {}

        name = family.get('nombre') or data.get('fam_nombre')
        if not name and isinstance(data.get('familiar'), str):
            name = data.get('familiar')

        return {
            'nombre': name or '',
            'parentesco': (
                family.get('parentesco')
                or data.get('fam_parentesco')
                or data.get('parentesco')
                or ''
            ),
            'telefono': (
                family.get('telefono')
                or data.get('fam_tel')
                or data.get('famTel')
                or ''
            ),
        }

    @staticmethod
    def create_patient(data):
        db = AdministrativeService._db()
        required = ['curp', 'papell', 'nom_pac', 'fecnac']
        for field in required:
            if not data.get(field):
                return None, f'Campo requerido: {field}'

        birth_date = AdministrativeService._parse_date(data.get('fecnac'))
        if not birth_date:
            return None, 'Fecha de nacimiento invalida'

        id_exp = get_next_sequence('pacientes_Id_exp')
        patient = {
            'Id_exp': id_exp,
            'curp': data.get('curp', '').strip().upper(),
            'papell': data.get('papell', '').strip(),
            'sapell': data.get('sapell', '').strip(),
            'nom_pac': data.get('nom_pac', '').strip(),
            'fecnac': birth_date,
            'tel': data.get('tel') or data.get('phone') or '',
            'email': data.get('email', ''),
            'created_at': datetime.now(),
        }
        db['pacientes'].insert_one(patient)

        appointment = None
        if data.get('area') or data.get('motivo') or data.get('especialidad'):
            id_atencion = get_next_sequence('atencion_id_atencion')
            id_cama = AdministrativeService._resolve_bed_id(db, data)
            appointment = {
                'id_atencion': id_atencion,
                'Id_exp': id_exp,
                'area': AdministrativeService._normalize_area(data.get('area')),
                'id_cama': id_cama,
                'motivo': data.get('motivo', ''),
                'especialidad': data.get('especialidad', ''),
                'alergias': data.get('alergias', ''),
                'fecha_ing': datetime.now(),
                'status': 'ABIERTA',
            }
            db['atencion'].insert_one(appointment)

            for doctor_id in AdministrativeService._normalize_doctor_ids(db, data):
                db['atencion_medicos'].insert_one({
                    'id_atencion': id_atencion,
                    'id_medico': doctor_id,
                })

            if id_cama:
                db['camas'].update_one({'id_cama': id_cama}, {'$set': {'ocupada': 1}})

        family = AdministrativeService._family_payload(data)
        if family.get('nombre') or family.get('telefono') or family.get('parentesco'):
            family['Id_exp'] = id_exp
            db['familiares'].insert_one(family)

        return AdministrativeService.get_patient_detail(id_exp), None

    @staticmethod
    def update_patient(id_exp, data):
        db = AdministrativeService._db()
        id_exp = int(id_exp)
        patient = db['pacientes'].find_one({'Id_exp': id_exp})
        if not patient:
            return None, 'Paciente no encontrado'

        patient_update = {}
        for field in ['curp', 'papell', 'sapell', 'nom_pac', 'email']:
            if field in data:
                patient_update[field] = data[field]
        if 'tel' in data or 'phone' in data:
            patient_update['tel'] = data.get('tel') or data.get('phone') or ''
        if data.get('fecnac'):
            birth_date = AdministrativeService._parse_date(data.get('fecnac'))
            if not birth_date:
                return None, 'Fecha de nacimiento invalida'
            patient_update['fecnac'] = birth_date

        if patient_update:
            db['pacientes'].update_one({'Id_exp': id_exp}, {'$set': patient_update})

        appointment = db['atencion'].find_one({'Id_exp': id_exp, 'status': 'ABIERTA'})
        appointment_fields = ['area', 'motivo', 'especialidad', 'alergias', 'id_cama', 'cama', 'bed']
        should_touch_appointment = any(field in data for field in appointment_fields) or any(
            key in data for key in ['medicos', 'doctores', 'assignedDoctors', 'doctors']
        )

        id_atencion = appointment.get('id_atencion') if appointment else None
        old_id_cama = appointment.get('id_cama') if appointment else None
        new_id_cama = AdministrativeService._resolve_bed_id(db, data) if should_touch_appointment else old_id_cama

        if should_touch_appointment:
            appointment_update = {
                'area': AdministrativeService._normalize_area(data.get('area') or (appointment or {}).get('area')),
                'id_cama': new_id_cama,
                'motivo': data.get('motivo', (appointment or {}).get('motivo', '')),
                'especialidad': data.get('especialidad', (appointment or {}).get('especialidad', '')),
                'alergias': data.get('alergias', (appointment or {}).get('alergias', '')),
                'status': 'ABIERTA',
            }

            if appointment:
                db['atencion'].update_one({'id_atencion': id_atencion}, {'$set': appointment_update})
            else:
                id_atencion = get_next_sequence('atencion_id_atencion')
                appointment_update.update({
                    'id_atencion': id_atencion,
                    'Id_exp': id_exp,
                    'fecha_ing': datetime.now(),
                })
                db['atencion'].insert_one(appointment_update)

            if new_id_cama != old_id_cama:
                if old_id_cama:
                    db['camas'].update_one({'id_cama': old_id_cama}, {'$set': {'ocupada': 0}})
                if new_id_cama:
                    db['camas'].update_one({'id_cama': new_id_cama}, {'$set': {'ocupada': 1}})

            if any(key in data for key in ['medicos', 'doctores', 'assignedDoctors', 'doctors']):
                db['atencion_medicos'].delete_many({'id_atencion': id_atencion})
                for doctor_id in AdministrativeService._normalize_doctor_ids(db, data):
                    db['atencion_medicos'].insert_one({
                        'id_atencion': id_atencion,
                        'id_medico': doctor_id,
                    })

        family = AdministrativeService._family_payload(data)
        if family.get('nombre') or family.get('telefono') or family.get('parentesco'):
            db['familiares'].update_one(
                {'Id_exp': id_exp},
                {'$set': family},
                upsert=True
            )

        return AdministrativeService.get_patient_detail(id_exp), None

    @staticmethod
    def get_patient_detail(id_exp):
        db = AdministrativeService._db()
        id_exp = int(id_exp)
        patient = db['pacientes'].find_one({'Id_exp': id_exp})
        if not patient:
            return None

        active = db['atencion'].find_one({'Id_exp': id_exp, 'status': 'ABIERTA'})
        appointments = list(db['atencion'].find({'Id_exp': id_exp}).sort('fecha_ing', -1))
        family = db['familiares'].find_one({'Id_exp': id_exp})
        active_row = AdministrativeService._appointment_patient_row(db, active, patient) if active else None

        return serialize_doc({
            'patient': AdministrativeService._patient_record_row(db, patient),
            'rawPatient': patient,
            'activeAppointment': active_row,
            'appointments': appointments,
            'family': family,
            'account': (
                AdministrativeService.get_account_detail(active.get('id_atencion'))
                if active else None
            ),
        })

    @staticmethod
    def get_documents_metadata(id_exp, id_atencion):
        prefix = config.API_PREFIX
        return [
            {
                'key': 'initial-sheet',
                'title': 'Hoja inicial',
                'icon': 'document-text-outline',
                'color': '#667eea',
                'filename': f'hoja_inicial_{id_atencion}.pdf',
                'endpoint': f'{prefix}/pdf/initial-sheet/{id_exp}/{id_atencion}',
            },
            {
                'key': 'front-sheet',
                'title': 'Hoja frontal',
                'icon': 'reader-outline',
                'color': '#48bb78',
                'filename': f'hoja_frontal_{id_atencion}.pdf',
                'endpoint': f'{prefix}/pdf/front-sheet/{id_exp}/{id_atencion}',
            },
            {
                'key': 'contract',
                'title': 'Contrato',
                'icon': 'briefcase-outline',
                'color': '#ed8936',
                'filename': f'contrato_{id_atencion}.pdf',
                'endpoint': f'{prefix}/pdf/contract/{id_exp}/{id_atencion}',
            },
            {
                'key': 'consent',
                'title': 'Consentimiento',
                'icon': 'shield-checkmark-outline',
                'color': '#38b2ac',
                'filename': f'consentimiento_{id_atencion}.pdf',
                'endpoint': f'{prefix}/pdf/consent/{id_exp}/{id_atencion}',
            },
            {
                'key': 'identification-sheet',
                'title': 'Ficha',
                'icon': 'id-card-outline',
                'color': '#9f7aea',
                'filename': f'ficha_identificacion_{id_atencion}.pdf',
                'endpoint': f'{prefix}/pdf/identification-sheet/{id_exp}/{id_atencion}',
            },
        ]


    @staticmethod
    def get_census(search=''):
        db = AdministrativeService._db()
        sections = {
            key: {**meta, 'key': key, 'data': []}
            for key, meta in AdministrativeService.SECTION_META.items()
        }

        appointments = list(
            db['atencion'].find({'status': 'ABIERTA'}).sort('fecha_ing', -1)
        )
        rows = AdministrativeService._appointment_rows_bulk(db, appointments)

        for row in rows:
            if not AdministrativeService._matches_search(row, search):
                continue

            section_key = row.get('section') or 'consulta'
            if section_key not in sections:
                section_key = 'consulta'

            sections[section_key]['data'].append({
                'id_atencion': row['id_atencion'],
                'Id_exp': row['Id_exp'],
                'account': row['account'],
                'room': row['room'],
                'admittedAt': row['admittedAt'],
                'patient': row['patient'],
                'age': row['age'],
                'reason': row['reason'],
                'record': row['record'],
                'doctor': row['doctor'],
                'notice': row['notice'],
                'area': row['area'],
            })

        section_list = []
        notice_count = 0
        total = 0
        for section in sections.values():
            section['count'] = len(section['data'])
            total += section['count']
            notice_count += sum(
                1 for item in section['data']
                if item.get('notice') and item.get('notice') != 'Sin aviso'
            )
            section_list.append(section)

        return serialize_doc({
            'summary': {
                'activos': total,
                'areas': len(section_list),
                'avisos': notice_count,
            },
            'sections': section_list,
        })

    @staticmethod
    def _item_subtotal(item):
        subtotal = item.get('subtotal')
        if subtotal is not None:
            return AdministrativeService._to_decimal(subtotal)
        return (
            AdministrativeService._to_decimal(item.get('precio'))
            * AdministrativeService._to_decimal(item.get('cantidad', 1))
        )

    @staticmethod
    def _payments_for_attention(db, id_atencion):
        payments = list(db['depositos_pserv'].find({'id_atencion': id_atencion}))
        try:
            if 'depositos_atencion' in db.list_collection_names():
                payments.extend(list(db['depositos_atencion'].find({'id_atencion': id_atencion})))
        except Exception:
            pass
        return payments

    @staticmethod
    def _payment_amount(payment):
        return AdministrativeService._to_decimal(
            payment.get('deposito', payment.get('monto', payment.get('amount')))
        )

    @staticmethod
    def _account_totals(items, payments):
        subtotal = sum((AdministrativeService._item_subtotal(item) for item in items), Decimal('0'))
        iva = subtotal * Decimal('0.16')
        total = subtotal + iva
        paid = sum((AdministrativeService._payment_amount(payment) for payment in payments), Decimal('0'))
        return {
            'subtotal': float(subtotal),
            'iva': float(iva),
            'tax': float(iva),
            'total': float(total),
            'advance': float(paid),
            'total_paid': float(paid),
            'balance': float(total - paid),
            'pending': float(total - paid),
        }


    @staticmethod
    def get_active_accounts(search=''):
        db = AdministrativeService._db()
        appointments = list(
            db['atencion'].find({'status': 'ABIERTA'}).sort('fecha_ing', -1)
        )
        if not appointments:
            return []

        rows = AdministrativeService._appointment_rows_bulk(db, appointments)
        rows_by_attention = {
            row.get('id_atencion'): row
            for row in rows
            if row.get('id_atencion') is not None
        }
        attention_ids = list(rows_by_attention.keys())

        items_by_attention = defaultdict(list)
        for item in db['cuenta_paciente'].find(
            {'id_atencion': {'$in': attention_ids}}
        ):
            items_by_attention[item.get('id_atencion')].append(item)

        payments_by_attention = defaultdict(list)
        for payment in db['depositos_pserv'].find(
            {'id_atencion': {'$in': attention_ids}}
        ):
            payments_by_attention[payment.get('id_atencion')].append(payment)

        try:
            if 'depositos_atencion' in db.list_collection_names():
                for payment in db['depositos_atencion'].find(
                    {'id_atencion': {'$in': attention_ids}}
                ):
                    payments_by_attention[payment.get('id_atencion')].append(payment)
        except Exception:
            pass

        accounts = []
        for appointment in appointments:
            id_atencion = appointment.get('id_atencion')
            row = rows_by_attention.get(id_atencion)
            if not row:
                continue

            items = items_by_attention.get(id_atencion, [])
            payments = payments_by_attention.get(id_atencion, [])
            totals = AdministrativeService._account_totals(items, payments)
            account = {
                **row,
                **totals,
                'chargesCount': len(items),
                'paymentsCount': len(payments),
            }
            if AdministrativeService._matches_search(account, search):
                accounts.append(account)

        return serialize_doc(accounts)

    @staticmethod
    def get_account_detail(id_atencion):
        db = AdministrativeService._db()
        id_atencion = int(id_atencion)
        appointment = db['atencion'].find_one({'id_atencion': id_atencion})
        if not appointment:
            return None

        patient = db['pacientes'].find_one({'Id_exp': appointment.get('Id_exp')})
        row = AdministrativeService._appointment_patient_row(db, appointment, patient) if patient else {}
        items = list(db['cuenta_paciente'].find({'id_atencion': id_atencion}).sort('fecha', 1))
        payments = AdministrativeService._payments_for_attention(db, id_atencion)
        totals = AdministrativeService._account_totals(items, payments)

        charges = []
        for item in items:
            charge = serialize_doc(item)
            charge['charge_id'] = str(item.get('id_cargo') or item.get('_id'))
            charge['subtotal'] = float(AdministrativeService._item_subtotal(item))
            charges.append(charge)

        normalized_payments = []
        for payment in payments:
            normalized = serialize_doc(payment)
            normalized['amount'] = float(AdministrativeService._payment_amount(payment))
            normalized['method'] = payment.get('tipo_pago') or payment.get('payment_method') or ''
            normalized_payments.append(normalized)

        return serialize_doc({
            **row,
            **totals,
            'charges': charges,
            'items': charges,
            'payments': normalized_payments,
            'documents': AdministrativeService.get_documents_metadata(
                appointment.get('Id_exp'),
                id_atencion
            ),
        })

    @staticmethod
    def add_charge(id_atencion, data):
        db = AdministrativeService._db()
        id_atencion = int(id_atencion)
        appointment = db['atencion'].find_one({'id_atencion': id_atencion})
        if not appointment:
            return None, 'Atencion no encontrada'

        quantity = AdministrativeService._to_int(data.get('cantidad') or data.get('quantity')) or 1
        description = data.get('descripcion') or data.get('description') or ''
        price = AdministrativeService._to_decimal(data.get('precio', data.get('price')))
        charge_type = (data.get('tipo') or data.get('type') or 'SERVICIO').upper()

        id_serv = AdministrativeService._to_int(data.get('id_serv') or data.get('service_id'))
        item_id = AdministrativeService._to_int(data.get('item_id') or data.get('medicamento_id'))

        if id_serv and (not description or price == 0):
            service = db['cat_servicios'].find_one({'id_serv': id_serv})
            if service:
                description = description or service.get('serv_desc', '')
                price = price or AdministrativeService._to_decimal(service.get('serv_costo'))
                charge_type = 'SERVICIO'

        if item_id and (not description or price == 0):
            item = db['item'].find_one({'item_id': item_id})
            if item:
                description = description or item.get('item_name', '')
                price = price or AdministrativeService._to_decimal(item.get('item_price'))
                charge_type = 'MEDICAMENTO'

        if not description:
            return None, 'Descripcion requerida'
        if price <= 0:
            return None, 'Precio invalido'

        subtotal = price * Decimal(quantity)
        charge = {
            'id_cargo': get_next_sequence('cuenta_paciente_id_cargo'),
            'id_atencion': id_atencion,
            'Id_exp': appointment.get('Id_exp'),
            'fecha': datetime.now(),
            'descripcion': description,
            'cantidad': quantity,
            'precio': price,
            'subtotal': subtotal,
            'tipo': charge_type,
            'estado': data.get('estado', 'PENDIENTE'),
        }
        if id_serv:
            charge['id_serv'] = id_serv
        if item_id:
            charge['item_id'] = item_id

        db['cuenta_paciente'].insert_one(charge)
        return AdministrativeService.get_account_detail(id_atencion), None

    @staticmethod
    def remove_charge(id_atencion, charge_id):
        db = AdministrativeService._db()
        filters = []

        int_id = AdministrativeService._to_int(charge_id)
        if int_id is not None:
            filters.append({'id_cargo': int_id})

        try:
            filters.append({'_id': ObjectId(charge_id)})
        except Exception:
            pass

        if not filters:
            return False

        result = db['cuenta_paciente'].delete_one({
            'id_atencion': int(id_atencion),
            '$or': filters,
        })
        return result.deleted_count > 0

    @staticmethod
    def register_payment(id_atencion, data, user_id):
        db = AdministrativeService._db()
        id_atencion = int(id_atencion)
        appointment = db['atencion'].find_one({'id_atencion': id_atencion})
        if not appointment:
            return None, 'Atencion no encontrada'

        amount = AdministrativeService._to_decimal(
            data.get('amount', data.get('monto', data.get('deposito')))
        )
        if amount <= 0:
            return None, 'Monto invalido'

        payment = {
            'id_deposito': get_next_sequence('depositos_pserv_id_deposito'),
            'id_atencion': id_atencion,
            'Id_exp': appointment.get('Id_exp'),
            'deposito': amount,
            'tipo_pago': data.get('payment_method') or data.get('tipo_pago') or data.get('method') or 'Efectivo',
            'fecha': datetime.now(),
            'usuario_registro': user_id,
            'referencia': data.get('reference') or data.get('referencia') or '',
            'observaciones': data.get('observations') or data.get('observaciones') or 'Anticipo',
        }
        db['depositos_pserv'].insert_one(payment)
        return AdministrativeService.get_account_detail(id_atencion), None

    @staticmethod
    def close_account(id_atencion, user_id):
        db = AdministrativeService._db()
        id_atencion = int(id_atencion)
        appointment = db['atencion'].find_one({'id_atencion': id_atencion})
        if not appointment or appointment.get('status') != 'ABIERTA':
            return None, 'Atencion no encontrada o ya cerrada'

        items = list(db['cuenta_paciente'].find({'id_atencion': id_atencion}))
        payments = AdministrativeService._payments_for_attention(db, id_atencion)
        totals = AdministrativeService._account_totals(items, payments)

        if not db['expedientes'].find_one({'id_atencion': id_atencion}):
            db['expedientes'].insert_one({
                'id_expediente': get_next_sequence('expedientes_id_expediente'),
                'id_exp': appointment.get('Id_exp'),
                'id_atencion': id_atencion,
                'fecha_alta': datetime.now(),
                'usuario_alta': user_id,
                'total_cuenta': totals['total'],
            })

        db['atencion'].update_one(
            {'id_atencion': id_atencion},
            {'$set': {'status': 'CERRADA', 'fecha_alta': datetime.now()}}
        )

        if appointment.get('id_cama'):
            db['camas'].update_one(
                {'id_cama': appointment.get('id_cama')},
                {'$set': {'ocupada': 0}}
            )

        return AdministrativeService.get_account_detail(id_atencion), None

    @staticmethod
    def get_cash_cut(date_value=None, search=''):
        db = AdministrativeService._db()
        start, end = AdministrativeService._date_bounds(date_value)

        payment_query = AdministrativeService._date_query('fecha', start, end)
        payments = list(db['depositos_pserv'].find(payment_query))
        try:
            if 'depositos_atencion' in db.list_collection_names():
                payments.extend(list(db['depositos_atencion'].find(payment_query)))
        except Exception:
            pass

        payments.sort(key=lambda payment: AdministrativeService._sort_date(payment.get('fecha')), reverse=True)

        movements = []
        income = Decimal('0')
        for payment in payments:
            amount = AdministrativeService._payment_amount(payment)
            income += amount
            appointment = db['atencion'].find_one({'id_atencion': payment.get('id_atencion')}) or {}
            patient = db['pacientes'].find_one({'Id_exp': appointment.get('Id_exp')}) or {}
            patient_name = AdministrativeService._patient_name(patient)
            movement = {
                'id': str(payment.get('_id')),
                'date': AdministrativeService._format_any_date(payment.get('fecha')),
                'time': AdministrativeService._format_time(payment.get('fecha')),
                'patient': patient_name,
                'concept': payment.get('observaciones') or 'Anticipo',
                'method': payment.get('tipo_pago', ''),
                'amount': float(amount),
                'id_atencion': payment.get('id_atencion'),
                'record': AdministrativeService._record_label(appointment.get('Id_exp')),
                'attention': AdministrativeService._attention_label(payment.get('id_atencion')),
            }
            if AdministrativeService._matches_search(movement, search):
                movements.append(movement)

        active_accounts = AdministrativeService.get_active_accounts(search)
        pending = sum(AdministrativeService._to_decimal(account.get('balance')) for account in active_accounts)

        return serialize_doc({
            'period': {
                'date': start.strftime('%Y-%m-%d'),
                'label': start.strftime('%d/%m/%Y'),
            },
            'summary': {
                'income': float(income),
                'pending': float(pending),
                'movements': len(movements),
                'accounts': len(active_accounts),
            },
            'movements': movements,
            'activeAccounts': active_accounts,
        })

    @staticmethod
    def get_documents_patients():
        db = AdministrativeService._db()
        appointments = list(db['atencion'].find({}).sort('fecha_ing', -1).limit(100))
        rows = []
        for appointment in appointments:
            patient = db['pacientes'].find_one({'Id_exp': appointment.get('Id_exp')})
            if not patient:
                continue
            row = AdministrativeService._appointment_patient_row(db, appointment, patient)
            row['documents'] = AdministrativeService.get_documents_metadata(
                appointment.get('Id_exp'),
                appointment.get('id_atencion')
            )
            rows.append(row)
        return serialize_doc(rows)
