"""
Validador de patentes vehiculares chilenas.
"""

import re
from typing import Optional

from .tipos import (
    TipoPatente, 
    FORMATO_VEHICULO_ANTIGUO, 
    FORMATO_VEHICULO_NUEVO,
    FORMATO_MOTOCICLETA_ANTIGUO,
    FORMATO_MOTOCICLETA_NUEVO,
    FORMATO_REMOLQUE
)


def es_formato_valido(patente: str) -> bool:
    """
    Verifica si una patente tiene un formato válido.
    
    Args:
        patente: La patente a validar
        
    Returns:
        True si el formato es válido, False en caso contrario
    """
    if not isinstance(patente, str):
        return False
    
    patente = patente.upper().strip()
    
    # Verificar formato vehículo antiguo
    if re.match(FORMATO_VEHICULO_ANTIGUO.patron, patente):
        return True
    
    # Verificar formato vehículo nuevo
    if re.match(FORMATO_VEHICULO_NUEVO.patron, patente):
        return True
    
    # Verificar formato motocicleta antiguo
    if re.match(FORMATO_MOTOCICLETA_ANTIGUO.patron, patente):
        return True
    
    # Verificar formato motocicleta nuevo
    if re.match(FORMATO_MOTOCICLETA_NUEVO.patron, patente):
        return True
    
    # Verificar formato remolque
    if re.match(FORMATO_REMOLQUE.patron, patente):
        return True
    
    return False


def detectar_tipo_patente(patente: str) -> Optional[TipoPatente]:
    """
    Detecta el tipo de patente basado en su formato.
    
    Args:
        patente: La patente a analizar
        
    Returns:
        El tipo de patente o None si no es válida
    """
    if not isinstance(patente, str):
        return None
    
    patente = patente.upper().strip()
    
    # Verificar formatos antiguos (vehículos y motocicletas)
    if re.match(FORMATO_VEHICULO_ANTIGUO.patron, patente) or re.match(FORMATO_MOTOCICLETA_ANTIGUO.patron, patente):
        return TipoPatente.ANTIGUA
    # Verificar formatos nuevos (vehículos y motocicletas)  
    elif re.match(FORMATO_VEHICULO_NUEVO.patron, patente) or re.match(FORMATO_MOTOCICLETA_NUEVO.patron, patente):
        return TipoPatente.NUEVA
    
    return None


def validar_patente(patente: str) -> bool:
    """
    Valida si una patente vehicular chilena es válida.
    
    Args:
        patente: La patente a validar
        
    Returns:
        True si la patente es válida, False en caso contrario
        
    Examples:
        >>> validar_patente("AB1234")
        True
        >>> validar_patente("BCDF12") 
        True
        >>> validar_patente("123ABC")
        False
    """
    return es_formato_valido(patente)


def limpiar_patente(patente: str) -> str:
    """
    Limpia y normaliza una patente removiendo espacios y convirtiendo a mayúsculas.
    
    Args:
        patente: La patente a limpiar
        
    Returns:
        La patente limpia y normalizada
    """
    if not isinstance(patente, str):
        raise ValueError("La patente debe ser una cadena de texto")
    
    return patente.upper().strip().replace(" ", "").replace("-", "").replace("_", "").replace(".", "").replace(",", "").replace(";", "").replace(":", "")