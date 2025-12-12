"""
Servicio para operaciones de base de datos y consultas SQL
"""
import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from app.config.settings import Settings


class DatabaseService:
    """Servicio para ejecutar consultas SQL de lectura en PostgreSQL"""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = psycopg2.connect(**self.connection_params)
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
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query)
            
            # Convertir resultados a lista de diccionarios
            results = [dict(row) for row in cursor.fetchall()]
            
            return results
    
    def get_tables(self) -> List[str]:
        """Obtiene la lista de tablas en la base de datos PostgreSQL"""
        query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        results = self.execute_query(query)
        return [r['tablename'] for r in results]
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Obtiene el esquema de una tabla en PostgreSQL"""
        query = f"""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = '{table_name}'
            ORDER BY ordinal_position
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
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
