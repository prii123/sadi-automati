"""
Factory para crear repositorios según el tipo de base de datos configurado
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
    Factory que crea repositorios según la configuración.
    
    Para cambiar de SQLite a MySQL:
    1. Crear MySQLEmpresaRepository que implemente IRepository
    2. Agregar el caso 'mysql' en create_empresa_repository
    3. Cambiar DB_TYPE en Settings o variable de entorno
    
    ¡No se necesita cambiar nada más en el código!
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
        Crea un repositorio de empresas según la configuración
        
        Returns:
            Repositorio de empresas configurado
            
        Raises:
            ValueError: Si el tipo de base de datos no está soportado
        """
        db_type = self.settings.DB_TYPE.lower()
        
        if db_type == 'sqlite':
            return EmpresaRepository(self.settings.DB_PATH)
        
        elif db_type == 'mysql':
            # Aquí irá la implementación de MySQL cuando esté lista
            # from app.repositories.mysql_empresa_repository import MySQLEmpresaRepository
            # return MySQLEmpresaRepository(
            #     host=self.settings.DB_HOST,
            #     port=self.settings.DB_PORT,
            #     database=self.settings.DB_NAME,
            #     user=self.settings.DB_USER,
            #     password=self.settings.DB_PASSWORD
            # )
            raise NotImplementedError(
                "MySQL no está implementado aún. "
                "Para implementarlo, crea MySQLEmpresaRepository "
                "que implemente IRepository y descomenta el código aquí."
            )
        
        else:
            raise ValueError(
                f"Tipo de base de datos no soportado: {db_type}. "
                f"Tipos soportados: sqlite, mysql"
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
