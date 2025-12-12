"""
Repositorio PostgreSQL para gestión de triggers
"""
import psycopg2
import psycopg2.extras
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.trigger import Trigger, TriggerEjecucion


class TriggerRepository:
    """Repositorio para operaciones CRUD de triggers en PostgreSQL"""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Inicializa el repositorio
        
        Args:
            host: Host del servidor PostgreSQL
            port: Puerto del servidor PostgreSQL
            database: Nombre de la base de datos
            user: Usuario de la base de datos
            password: Contraseña del usuario
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self._crear_tabla()
    
    def _get_connection(self):
        """Crea una conexión a la base de datos PostgreSQL"""
        return psycopg2.connect(**self.connection_params)
    
    def _crear_tabla(self):
        """Crea la tabla de triggers si no existe"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS triggers (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                frecuencia TEXT NOT NULL DEFAULT 'diaria',
                hora TEXT NOT NULL DEFAULT '08:00',
                dias_semana TEXT,
                dia_mes INTEGER,
                intervalo_horas INTEGER,
                destinatarios TEXT NOT NULL,
                prioridades TEXT NOT NULL DEFAULT 'CRITICA,ALTA,MEDIA',
                activo INTEGER NOT NULL DEFAULT 1,
                ultima_ejecucion TEXT,
                proxima_ejecucion TEXT,
                creado_en TEXT NOT NULL,
                actualizado_en TEXT NOT NULL
            )
        """)
        
        # Crear tabla de historial de ejecuciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trigger_ejecuciones (
                id SERIAL PRIMARY KEY,
                trigger_id INTEGER NOT NULL,
                trigger_nombre TEXT NOT NULL,
                fecha_ejecucion TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'exitoso',
                notificaciones_enviadas INTEGER DEFAULT 0,
                empresas_procesadas INTEGER DEFAULT 0,
                error_mensaje TEXT,
                detalles TEXT,
                FOREIGN KEY (trigger_id) REFERENCES triggers(id) ON DELETE CASCADE
            )
        """)
        
        # Crear índices para mejorar consultas
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trigger_ejecuciones_trigger_id 
            ON trigger_ejecuciones(trigger_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trigger_ejecuciones_fecha 
            ON trigger_ejecuciones(fecha_ejecucion DESC)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def create(self, trigger: Trigger) -> Trigger:
        """
        Crea un nuevo trigger
        
        Args:
            trigger: Objeto Trigger a crear
            
        Returns:
            Trigger con ID asignado
        """
        now = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO triggers (
                nombre, descripcion, frecuencia, hora, dias_semana, dia_mes,
                intervalo_horas, destinatarios, prioridades, activo,
                ultima_ejecucion, proxima_ejecucion, creado_en, actualizado_en
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            trigger.nombre,
            trigger.descripcion,
            trigger.frecuencia,
            trigger.hora,
            trigger.dias_semana,
            trigger.dia_mes,
            trigger.intervalo_horas,
            trigger.destinatarios,
            trigger.prioridades,
            trigger.activo,
            trigger.ultima_ejecucion,
            trigger.proxima_ejecucion,
            now,
            now
        ))
        
        trigger.id = cursor.fetchone()[0]
        trigger.creado_en = now
        trigger.actualizado_en = now
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return trigger
    
    def get_by_id(self, trigger_id: int) -> Optional[Trigger]:
        """
        Obtiene un trigger por su ID
        
        Args:
            trigger_id: ID del trigger
            
        Returns:
            Trigger o None si no existe
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("SELECT * FROM triggers WHERE id = %s", (trigger_id,))
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if row:
            return Trigger.from_dict(dict(row))
        return None
    
    def get_all(self) -> List[Trigger]:
        """
        Obtiene todos los triggers
        
        Returns:
            Lista de triggers
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("SELECT * FROM triggers ORDER BY creado_en DESC")
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [Trigger.from_dict(dict(row)) for row in rows]
    
    def get_activos(self) -> List[Trigger]:
        """
        Obtiene todos los triggers activos
        
        Returns:
            Lista de triggers activos
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("SELECT * FROM triggers WHERE activo = 1 ORDER BY hora")
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [Trigger.from_dict(dict(row)) for row in rows]
    
    def update(self, trigger: Trigger) -> Trigger:
        """
        Actualiza un trigger existente
        
        Args:
            trigger: Trigger con datos actualizados
            
        Returns:
            Trigger actualizado
        """
        now = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE triggers SET
                nombre = %s,
                descripcion = %s,
                frecuencia = %s,
                hora = %s,
                dias_semana = %s,
                dia_mes = %s,
                intervalo_horas = %s,
                destinatarios = %s,
                prioridades = %s,
                activo = %s,
                ultima_ejecucion = %s,
                proxima_ejecucion = %s,
                actualizado_en = %s
            WHERE id = %s
        """, (
            trigger.nombre,
            trigger.descripcion,
            trigger.frecuencia,
            trigger.hora,
            trigger.dias_semana,
            trigger.dia_mes,
            trigger.intervalo_horas,
            trigger.destinatarios,
            trigger.prioridades,
            trigger.activo,
            trigger.ultima_ejecucion,
            trigger.proxima_ejecucion,
            now,
            trigger.id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        trigger.actualizado_en = now
        return trigger
    
    def delete(self, trigger_id: int) -> bool:
        """
        Elimina un trigger
        
        Args:
            trigger_id: ID del trigger a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM triggers WHERE id = %s", (trigger_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    def actualizar_ejecucion(self, trigger_id: int, proxima_ejecucion: Optional[str] = None) -> bool:
        """
        Actualiza las fechas de ejecución de un trigger
        
        Args:
            trigger_id: ID del trigger
            proxima_ejecucion: Fecha/hora de la próxima ejecución
            
        Returns:
            True si se actualizó correctamente
        """
        now = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE triggers SET
                ultima_ejecucion = %s,
                proxima_ejecucion = %s,
                actualizado_en = %s
            WHERE id = %s
        """, (now, proxima_ejecucion, now, trigger_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    # Métodos para gestión de historial de ejecuciones
    
    def registrar_ejecucion(self, ejecucion: TriggerEjecucion) -> TriggerEjecucion:
        """
        Registra una nueva ejecución de un trigger
        
        Args:
            ejecucion: Objeto TriggerEjecucion a registrar
            
        Returns:
            TriggerEjecucion con ID asignado
        """
        fecha = ejecucion.fecha_ejecucion or datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trigger_ejecuciones (
                trigger_id, trigger_nombre, fecha_ejecucion, estado,
                notificaciones_enviadas, empresas_procesadas, error_mensaje, detalles
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            ejecucion.trigger_id,
            ejecucion.trigger_nombre,
            fecha,
            ejecucion.estado,
            ejecucion.notificaciones_enviadas,
            ejecucion.empresas_procesadas,
            ejecucion.error_mensaje,
            ejecucion.detalles
        ))
        
        ejecucion.id = cursor.fetchone()[0]
        ejecucion.fecha_ejecucion = fecha
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return ejecucion
    
    def get_ejecuciones_by_trigger(self, trigger_id: int, limit: int = 50) -> List[TriggerEjecucion]:
        """
        Obtiene el historial de ejecuciones de un trigger específico
        
        Args:
            trigger_id: ID del trigger
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de ejecuciones ordenadas por fecha descendente
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM trigger_ejecuciones 
            WHERE trigger_id = %s 
            ORDER BY fecha_ejecucion DESC 
            LIMIT %s
        """, (trigger_id, limit))
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [TriggerEjecucion.from_dict(dict(row)) for row in rows]
    
    def get_todas_ejecuciones(self, limit: int = 100) -> List[TriggerEjecucion]:
        """
        Obtiene todas las ejecuciones de todos los triggers
        
        Args:
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de ejecuciones ordenadas por fecha descendente
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM trigger_ejecuciones 
            ORDER BY fecha_ejecucion DESC 
            LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [TriggerEjecucion.from_dict(dict(row)) for row in rows]
    
    def get_estadisticas_trigger(self, trigger_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de ejecución de un trigger
        
        Args:
            trigger_id: ID del trigger
            
        Returns:
            Diccionario con estadísticas
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total de ejecuciones
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ejecuciones,
                SUM(CASE WHEN estado = 'exitoso' THEN 1 ELSE 0 END) as exitosas,
                SUM(CASE WHEN estado = 'fallido' THEN 1 ELSE 0 END) as fallidas,
                SUM(notificaciones_enviadas) as total_notificaciones,
                SUM(empresas_procesadas) as total_empresas,
                MAX(fecha_ejecucion) as ultima_ejecucion
            FROM trigger_ejecuciones
            WHERE trigger_id = %s
        """, (trigger_id,))
        
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            'total_ejecuciones': row[0] or 0,
            'exitosas': row[1] or 0,
            'fallidas': row[2] or 0,
            'total_notificaciones': row[3] or 0,
            'total_empresas': row[4] or 0,
            'ultima_ejecucion': row[5],
            'tasa_exito': round((row[1] or 0) / (row[0] or 1) * 100, 2)
        }
    
    def limpiar_ejecuciones_antiguas(self, dias: int = 90) -> int:
        """
        Elimina ejecuciones antiguas del historial
        
        Args:
            dias: Número de días a conservar
            
        Returns:
            Número de registros eliminados
        """
        fecha_limite = (datetime.now() - timedelta(days=dias)).isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM trigger_ejecuciones 
            WHERE fecha_ejecucion < %s
        """, (fecha_limite,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return deleted_count
