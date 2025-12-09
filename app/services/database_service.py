"""
Servicio para operaciones de base de datos y consultas SQL
"""
import sqlite3
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from app.config.settings import Settings


class DatabaseService:
    """Servicio para ejecutar consultas SQL de lectura"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT de solo lectura
        
        Args:
            query: Consulta SQL (solo SELECT permitido)
            
        Returns:
            Lista de resultados como diccionarios
            
        Raises:
            ValueError: Si la consulta no es un SELECT
            Exception: Si hay error en la consulta
        """
        # Validar que solo sean consultas SELECT
        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            raise ValueError("Solo se permiten consultas SELECT")
        
        # Palabras prohibidas que podrían modificar datos
        forbidden_words = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
        for word in forbidden_words:
            if word in query_upper:
                raise ValueError(f"Palabra prohibida encontrada: {word}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Obtener nombres de columnas
            columns = [description[0] for description in cursor.description]
            
            # Convertir resultados a lista de diccionarios
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
    
    def get_tables(self) -> List[str]:
        """Obtiene la lista de tablas en la base de datos"""
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        results = self.execute_query(query)
        return [r['name'] for r in results]
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Obtiene el esquema de una tabla"""
        query = f"PRAGMA table_info({table_name})"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
    
    def get_table_count(self, table_name: str) -> int:
        """Obtiene el número de registros en una tabla"""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        results = self.execute_query(query)
        return results[0]['count'] if results else 0
    
    def get_all_table_info(self) -> List[Dict[str, Any]]:
        """Obtiene información de todas las tablas"""
        tables = self.get_tables()
        info = []
        
        for table in tables:
            try:
                count = self.get_table_count(table)
                schema = self.get_table_schema(table)
                info.append({
                    'name': table,
                    'count': count,
                    'columns': len(schema),
                    'schema': schema
                })
            except Exception as e:
                info.append({
                    'name': table,
                    'error': str(e)
                })
        
        return info
    
    def preview_table(self, table_name: str, limit: int = 100) -> Dict[str, Any]:
        """
        Obtiene una vista previa de una tabla
        
        Args:
            table_name: Nombre de la tabla
            limit: Número máximo de registros a retornar
            
        Returns:
            Diccionario con esquema y datos
        """
        schema = self.get_table_schema(table_name)
        count = self.get_table_count(table_name)
        
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        data = self.execute_query(query)
        
        return {
            'table': table_name,
            'total_rows': count,
            'showing': len(data),
            'schema': schema,
            'data': data
        }
