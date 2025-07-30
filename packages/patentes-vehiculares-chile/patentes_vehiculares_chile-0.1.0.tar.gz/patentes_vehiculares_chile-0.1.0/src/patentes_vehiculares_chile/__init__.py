"""
Patentes Vehiculares Chile

Una librería Python para validar y trabajar con patentes vehiculares chilenas.
"""

__version__ = "0.1.0"
__author__ = "Jorge Gallardo"
__email__ = "jorgito899@gmail.com"

from .validador import (
    validar_patente, 
    es_formato_valido, 
    detectar_tipo_patente, 
    limpiar_patente
)
from .tipos import TipoPatente, FormatoPatente

__all__ = [
    "validar_patente",
    "es_formato_valido",
    "detectar_tipo_patente",
    "limpiar_patente", 
    "TipoPatente",
    "FormatoPatente",
]