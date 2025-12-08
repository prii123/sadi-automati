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


import sqlite3
from contextlib import contextmanager


class BaseRepository:
    """
    Clase base para repositorios que usan SQLite
    Proporciona métodos comunes para ejecutar queries
    """
    
    def __init__(self, db_path: str):
        """
        Inicializa el repositorio con la ruta de la base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Context manager para manejar conexiones a la BD"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        """
        Ejecuta una query que modifica datos (INSERT, UPDATE, DELETE)
        
        Args:
            query: Query SQL a ejecutar
            params: Parámetros de la query
            
        Returns:
            Cursor con el resultado
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor
    
    def fetch_one(self, query: str, params: tuple = ()):
        """
        Ejecuta una query y retorna un solo resultado
        
        Args:
            query: Query SQL a ejecutar
            params: Parámetros de la query
            
        Returns:
            Tupla con el resultado o None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()):
        """
        Ejecuta una query y retorna todos los resultados
        
        Args:
            query: Query SQL a ejecutar
            params: Parámetros de la query
            
        Returns:
            Lista de tuplas con los resultados
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
