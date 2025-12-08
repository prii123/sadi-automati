"""
Repositorio para la gestión de usuarios en la base de datos
"""
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.usuario import Usuario
from app.repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository):
    """
    Repositorio que maneja la persistencia de usuarios
    """

    def __init__(self, db_path: str):
        """
        Inicializa el repositorio con la ruta de la base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        super().__init__(db_path)
        self._crear_tabla()
        self._crear_usuario_admin_default()

    def _crear_tabla(self):
        """Crea la tabla de usuarios si no existe"""
        query = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            rol TEXT DEFAULT 'usuario',
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_acceso TIMESTAMP
        )
        """
        self.execute_query(query)

    def _crear_usuario_admin_default(self):
        """Crea el usuario admin por defecto si no existe"""
        from app.services.auth_service import AuthService
        
        # Verificar si ya existe un admin
        usuario = self.get_by_username('admin')
        if usuario:
            return
        
        # Crear usuario admin con contraseña 'admin123'
        password_hash = AuthService.hash_password('admin123')
        usuario_admin = Usuario(
            username='admin',
            password_hash=password_hash,
            nombre='Administrador',
            email='admin@sadi.com',
            rol='admin'
        )
        
        self.create(usuario_admin)
        print("✅ Usuario admin creado - Username: admin, Password: admin123")

    def create(self, usuario: Usuario) -> Dict[str, Any]:
        """
        Crea un nuevo usuario
        
        Args:
            usuario: Instancia de Usuario a crear
            
        Returns:
            Diccionario con success y data o error
        """
        query = """
        INSERT INTO usuarios (username, password_hash, nombre, email, rol, activo)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.execute_query(
                query,
                (usuario.username, usuario.password_hash, usuario.nombre, 
                 usuario.email, usuario.rol, usuario.activo)
            )
            
            usuario.id = cursor.lastrowid
            usuario.fecha_creacion = datetime.now()
            
            return {
                'success': True,
                'data': usuario.to_dict()
            }
        except sqlite3.IntegrityError as e:
            return {
                'success': False,
                'error': f'Usuario ya existe: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_by_username(self, username: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su username
        
        Args:
            username: Username del usuario
            
        Returns:
            Usuario o None si no existe
        """
        query = "SELECT * FROM usuarios WHERE username = ?"
        result = self.fetch_one(query, (username,))
        
        if result:
            return Usuario(
                id=result[0],
                username=result[1],
                password_hash=result[2],
                nombre=result[3],
                email=result[4],
                rol=result[5],
                activo=result[6],
                fecha_creacion=datetime.fromisoformat(result[7]) if result[7] else None,
                fecha_actualizacion=datetime.fromisoformat(result[8]) if result[8] else None,
                ultimo_acceso=datetime.fromisoformat(result[9]) if result[9] else None
            )
        return None

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Usuario o None si no existe
        """
        query = "SELECT * FROM usuarios WHERE id = ?"
        result = self.fetch_one(query, (usuario_id,))
        
        if result:
            return Usuario(
                id=result[0],
                username=result[1],
                password_hash=result[2],
                nombre=result[3],
                email=result[4],
                rol=result[5],
                activo=result[6],
                fecha_creacion=datetime.fromisoformat(result[7]) if result[7] else None,
                fecha_actualizacion=datetime.fromisoformat(result[8]) if result[8] else None,
                ultimo_acceso=datetime.fromisoformat(result[9]) if result[9] else None
            )
        return None

    def update_ultimo_acceso(self, usuario_id: int):
        """Actualiza la fecha de último acceso del usuario"""
        query = "UPDATE usuarios SET ultimo_acceso = ? WHERE id = ?"
        self.execute_query(query, (datetime.now().isoformat(), usuario_id))

    def get_all(self) -> List[Usuario]:
        """
        Obtiene todos los usuarios
        
        Returns:
            Lista de usuarios
        """
        query = "SELECT * FROM usuarios WHERE activo = 1"
        results = self.fetch_all(query)
        
        usuarios = []
        for row in results:
            usuarios.append(Usuario(
                id=row[0],
                username=row[1],
                password_hash=row[2],
                nombre=row[3],
                email=row[4],
                rol=row[5],
                activo=row[6],
                fecha_creacion=datetime.fromisoformat(row[7]) if row[7] else None,
                fecha_actualizacion=datetime.fromisoformat(row[8]) if row[8] else None,
                ultimo_acceso=datetime.fromisoformat(row[9]) if row[9] else None
            ))
        
        return usuarios

    def update(self, usuario_id: int, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza un usuario
        
        Args:
            usuario_id: ID del usuario
            datos: Diccionario con los campos a actualizar
            
        Returns:
            Diccionario con success y data o error
        """
        campos_permitidos = ['nombre', 'email', 'rol', 'activo', 'password_hash']
        campos = []
        valores = []
        
        for campo, valor in datos.items():
            if campo in campos_permitidos:
                campos.append(f"{campo} = ?")
                valores.append(valor)
        
        if not campos:
            return {'success': False, 'error': 'No hay campos para actualizar'}
        
        campos.append("fecha_actualizacion = ?")
        valores.append(datetime.now().isoformat())
        valores.append(usuario_id)
        
        query = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = ?"
        
        try:
            self.execute_query(query, tuple(valores))
            usuario = self.get_by_id(usuario_id)
            
            return {
                'success': True,
                'data': usuario.to_dict() if usuario else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete(self, usuario_id: int) -> Dict[str, Any]:
        """
        Desactiva un usuario (soft delete)
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Diccionario con success
        """
        try:
            query = "UPDATE usuarios SET activo = 0, fecha_actualizacion = ? WHERE id = ?"
            self.execute_query(query, (datetime.now().isoformat(), usuario_id))
            
            return {'success': True}
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
