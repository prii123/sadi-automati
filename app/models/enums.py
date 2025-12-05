"""
Enumeraciones y constantes del sistema
"""
from enum import Enum


class TipoEmpresa(str, Enum):
    """Tipos de empresa en el sistema"""
    PERSONA_NATURAL = "Persona Natural"
    PERSONA_JURIDICA = "Persona Jurídica"
    CONSORCIO = "Consorcio"
    OTRO = "Otro"


class EstadoEmpresa(str, Enum):
    """Estados posibles de una empresa"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"
