"""
Configuración general del sistema
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Settings:
    """
    Configuración centralizada del sistema.
    Puede cargar valores desde variables de entorno o usar valores por defecto.
    """
    
    # Base de datos
    DB_TYPE: str = os.getenv('DB_TYPE', 'sqlite')  # 'sqlite' o 'mysql'
    DB_PATH: str = os.getenv('DB_PATH', 'data/facturacion.db')  # Para SQLite
    
    # MySQL (si se usa)
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '3306'))
    DB_NAME: str = os.getenv('DB_NAME', 'facturacion')
    DB_USER: str = os.getenv('DB_USER', 'root')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    
    # API
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '5000'))
    API_DEBUG: bool = os.getenv('API_DEBUG', 'True').lower() == 'true'
    API_BASE_URL: str = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
    
    # Notificaciones
    NOTIFICACION_DIAS_ANTICIPACION: int = int(os.getenv('NOTIFICACION_DIAS_ANTICIPACION', '30'))
    
    # Seguridad
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Crea una instancia de Settings desde variables de entorno"""
        return cls()
    
    def get_db_connection_string(self) -> str:
        """
        Obtiene la cadena de conexión según el tipo de base de datos
        
        Returns:
            Cadena de conexión
        """
        if self.DB_TYPE == 'sqlite':
            return self.DB_PATH
        elif self.DB_TYPE == 'mysql':
            return f"mysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            raise ValueError(f"Tipo de base de datos no soportado: {self.DB_TYPE}")
    
    def to_dict(self) -> dict:
        """Convierte la configuración a diccionario (ocultando datos sensibles)"""
        return {
            'db_type': self.DB_TYPE,
            'api_host': self.API_HOST,
            'api_port': self.API_PORT,
            'api_debug': self.API_DEBUG,
            'notificacion_dias': self.NOTIFICACION_DIAS_ANTICIPACION
        }
