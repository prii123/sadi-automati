"""
Interfaz base para repositorios
Define el contrato que deben cumplir todos los repositorios
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class IRepository(ABC):
    """
    Interfaz base para repositorios de datos.
    Cualquier implementación de base de datos debe implementar estos métodos.
    """

    @abstractmethod
    def create(self, entity: Any) -> Any:
        """
        Crea una nueva entidad en la base de datos
        
        Args:
            entity: La entidad a crear
            
        Returns:
            La entidad creada con su ID asignado
        """
        pass

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Any]:
        """
        Obtiene una entidad por su ID
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            La entidad encontrada o None
        """
        pass

    @abstractmethod
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Obtiene todas las entidades, opcionalmente filtradas
        
        Args:
            filters: Diccionario de filtros opcionales
            
        Returns:
            Lista de entidades
        """
        pass

    @abstractmethod
    def update(self, entity: Any) -> bool:
        """
        Actualiza una entidad existente
        
        Args:
            entity: La entidad con los datos actualizados
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """
        Elimina una entidad por su ID
        
        Args:
            entity_id: ID de la entidad a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        pass

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """
        Verifica si existe una entidad con el ID dado
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            True si existe, False en caso contrario
        """
        pass
