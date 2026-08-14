from datetime import datetime, date

def calcular_edad(fecnac):
    """
    Calcula edad con manejo robusto de múltiples formatos de fecha
    """
    if not fecnac:
        return 0
    
    try:
        # Caso 1: Ya es datetime
        if isinstance(fecnac, datetime):
            fecha_nac = fecnac.date()
        # Caso 2: Ya es date
        elif isinstance(fecnac, date):
            fecha_nac = fecnac
        # Caso 3: Es string
        elif isinstance(fecnac, str):
            fecha_limpia = fecnac.strip()
            
            # Quitar hora si existe
            if 'T' in fecha_limpia:
                fecha_limpia = fecha_limpia.split('T')[0]
            elif ' ' in fecha_limpia:
                fecha_limpia = fecha_limpia.split(' ')[0]
            
            # Probar diferentes formatos
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y%m%d']
            fecha_nac = None
            
            for fmt in formatos:
                try:
                    fecha_nac = datetime.strptime(fecha_limpia, fmt).date()
                    break
                except ValueError:
                    continue
            
            if not fecha_nac:
                return 0
        else:
            return 0
        
        hoy = date.today()
        
        if fecha_nac > hoy:
            return 0
        
        edad = hoy.year - fecha_nac.year
        if (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day):
            edad -= 1
        
        return edad
    
    except Exception:
        return 0

def format_fecha(fecha, formato='%d/%m/%Y'):
    """Formatea una fecha a string"""
    if not fecha:
        return ''
    
    if isinstance(fecha, str):
        try:
            fecha = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
        except:
            return fecha
    
    if hasattr(fecha, 'strftime'):
        return fecha.strftime(formato)
    
    return str(fecha)

def fecha_actual():
    """Retorna la fecha actual en formato ISO"""
    return datetime.now().isoformat()