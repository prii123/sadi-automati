"""
Factory para crear repositorios PostgreSQL
Patrón Factory para desacoplar la creación de repositorios
"""
from typing import Protocol
from app.config.settings import Settings
from app.repositories.empresa_repository import EmpresaRepository


class IRepositoryFactory(Protocol):
    """Interfaz para factories de repositorios"""
    
    def create_empresa_repository(self) -> EmpresaRepository:
        """Crea un repositorio de empresas"""
        ...


class DatabaseFactory:
    """
    Factory que crea repositorios PostgreSQL
    """
    
    def __init__(self, settings: Settings):
        """
        Inicializa el factory con la configuración
        
        Args:
            settings: Configuración del sistema
        """
        self.settings = settings
    
    def create_empresa_repository(self) -> EmpresaRepository:
        """
        Crea un repositorio de empresas PostgreSQL
        
        Returns:
            Repositorio de empresas configurado
        """
        return EmpresaRepository(
            host=self.settings.DB_HOST,
            port=self.settings.DB_PORT,
            database=self.settings.DB_NAME,
            user=self.settings.DB_USER,
            password=self.settings.DB_PASSWORD
        )
    
    @classmethod
    def from_settings(cls, settings: Settings) -> 'DatabaseFactory':
        """
        Método de conveniencia para crear el factory desde settings
        
        Args:
            settings: Configuración del sistema
            
        Returns:
            DatabaseFactory configurado
        """
        return cls(settings)
