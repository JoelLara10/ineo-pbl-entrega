from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime

class LoginSchema(BaseModel):
    username: str
    password: str

class UserCreateSchema(BaseModel):
    username: str
    password: str
    role: str = 'user'
    nombre: Optional[str] = ''
    papell: Optional[str] = ''
    sapell: Optional[str] = ''
    email: Optional[str] = ''
    telefono: Optional[str] = ''

class PatientCreateSchema(BaseModel):
    curp: str
    papell: str
    sapell: Optional[str] = ''
    nom_pac: str
    fecnac: str  # YYYY-MM-DD
    tel: Optional[str] = ''
    email: Optional[str] = ''
    
    @validator('fecnac')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
    
    @validator('curp')
    def validate_curp(cls, v):
        if len(v) != 18:
            raise ValueError('CURP debe tener 18 caracteres')
        return v.upper()

class AppointmentCreateSchema(BaseModel):
    area: str
    id_cama: Optional[int] = None
    motivo: str
    especialidad: str
    alergias: Optional[str] = ''
    medicos: List[int] = []

class VitalSignsSchema(BaseModel):
    ta: Optional[str] = ''
    fc: Optional[str] = ''
    fr: Optional[str] = ''
    temp: Optional[str] = ''
    spo2: Optional[str] = ''
    peso: Optional[str] = ''
    talla: Optional[str] = ''

class MedicalNoteSchema(BaseModel):
    subjetivo: str
    objetivo: str
    analisis: str
    plan: str

class DiagnosisSchema(BaseModel):
    diagnostico_principal: str
    diagnosticos_secundarios: Optional[str] = ''
    observaciones: Optional[str] = ''

class PrescriptionSchema(BaseModel):
    medicamentos: List[dict] = Field(..., description="Lista de medicamentos con dosis, frecuencia, etc.")

class BillingItemSchema(BaseModel):
    descripcion: str
    cantidad: int = 1
    precio: float
    tipo: Optional[str] = 'SERVICIO'

class PaymentSchema(BaseModel):
    amount: float
    payment_method: str  # EFECTIVO, TARJETA, TRANSFERENCIA
    reference: Optional[str] = ''
    observations: Optional[str] = ''

class ExamRequestSchema(BaseModel):
    id_atencion: int
    exams: List[int]
    observations: Optional[str] = ''

class ExamResultSchema(BaseModel):
    id_catalogo: int
    resultado: str