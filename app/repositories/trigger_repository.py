"""
Repositorio para gestión de triggers en la base de datos
"""
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.models.trigger import Trigger


class TriggerRepository:
    """Repositorio para operaciones CRUD de triggers"""
    
    def __init__(self, db_path: str):
        """
        Inicializa el repositorio
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self._crear_tabla()
    
    def _crear_tabla(self):
        """Crea la tabla de triggers si no existe"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            conn.commit()
    
    def create(self, trigger: Trigger) -> Trigger:
        """
        Crea un nuevo trigger
        
        Args:
            trigger: Objeto Trigger a crear
            
        Returns:
            Trigger con ID asignado
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO triggers (
                    nombre, descripcion, frecuencia, hora, dias_semana, dia_mes,
                    intervalo_horas, destinatarios, prioridades, activo,
                    ultima_ejecucion, proxima_ejecucion, creado_en, actualizado_en
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            conn.commit()
            trigger.id = cursor.lastrowid
            trigger.creado_en = now
            trigger.actualizado_en = now
        
        return trigger
    
    def get_by_id(self, trigger_id: int) -> Optional[Trigger]:
        """
        Obtiene un trigger por su ID
        
        Args:
            trigger_id: ID del trigger
            
        Returns:
            Trigger o None si no existe
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM triggers WHERE id = ?", (trigger_id,))
            row = cursor.fetchone()
            
            if row:
                return Trigger.from_dict(dict(row))
            return None
    
    def get_all(self) -> List[Trigger]:
        """
        Obtiene todos los triggers
        
        Returns:
            Lista de triggers
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM triggers ORDER BY creado_en DESC")
            rows = cursor.fetchall()
            
            return [Trigger.from_dict(dict(row)) for row in rows]
    
    def get_activos(self) -> List[Trigger]:
        """
        Obtiene todos los triggers activos
        
        Returns:
            Lista de triggers activos
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM triggers WHERE activo = 1 ORDER BY hora")
            rows = cursor.fetchall()
            
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
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE triggers SET
                    nombre = ?,
                    descripcion = ?,
                    frecuencia = ?,
                    hora = ?,
                    dias_semana = ?,
                    dia_mes = ?,
                    intervalo_horas = ?,
                    destinatarios = ?,
                    prioridades = ?,
                    activo = ?,
                    ultima_ejecucion = ?,
                    proxima_ejecucion = ?,
                    actualizado_en = ?
                WHERE id = ?
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
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM triggers WHERE id = ?", (trigger_id,))
            conn.commit()
            return cursor.rowcount > 0
    
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
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE triggers SET
                    ultima_ejecucion = ?,
                    proxima_ejecucion = ?,
                    actualizado_en = ?
                WHERE id = ?
            """, (now, proxima_ejecucion, now, trigger_id))
            conn.commit()
            return cursor.rowcount > 0
