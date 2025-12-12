"""
Repositorio PostgreSQL para la gestión de usuarios
"""
import psycopg2
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.usuario import Usuario


class UsuarioRepository:
    """
    Repositorio que maneja la persistencia de usuarios en PostgreSQL
    """

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Inicializa el repositorio con los parámetros de conexión
        
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
        self._crear_usuario_admin_default()

    def _get_connection(self):
        """Crea una conexión a la base de datos PostgreSQL"""
        return psycopg2.connect(**self.connection_params)

    def _crear_tabla(self):
        """Crea la tabla de usuarios si no existe"""
        query = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
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
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()

    def _crear_usuario_admin_default(self):
        """Crea el usuario admin por defecto si no existe"""
        from app.services.auth_service import AuthService
        from app.config.settings import Settings
        
        settings = Settings()
        
        # Verificar si ya existe el usuario root
        usuario = self.get_by_username(settings.ROOT_USER)
        if usuario:
            return
        
        # Crear usuario root con credenciales desde variables de entorno
        password_hash = AuthService.hash_password(settings.ROOT_PASSWORD)
        usuario_admin = Usuario(
            username=settings.ROOT_USER,
            password_hash=password_hash,
            nombre=settings.ROOT_NAME,
            email=settings.ROOT_EMAIL,
            rol='admin'
        )
        
        self.create(usuario_admin)
        print(f"✅ Usuario root creado - Username: {settings.ROOT_USER}, Password: {settings.ROOT_PASSWORD}")

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
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, fecha_creacion
        """
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                query,
                (usuario.username, usuario.password_hash, usuario.nombre, 
                 usuario.email, usuario.rol, usuario.activo)
            )
            
            result = cursor.fetchone()
            usuario.id = result[0]
            usuario.fecha_creacion = result[1]
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'data': usuario.to_dict()
            }
        except psycopg2.IntegrityError as e:
            return {
                'success': False,
                'error': f'El usuario ya existe: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear usuario: {str(e)}'
            }

    def get_by_username(self, username: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su username
        
        Args:
            username: Username del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        query = "SELECT * FROM usuarios WHERE username = %s"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            return None
        
        return Usuario(
            id=row[0],
            username=row[1],
            password_hash=row[2],
            nombre=row[3],
            email=row[4],
            rol=row[5],
            activo=bool(row[6]),
            fecha_creacion=row[7],
            fecha_actualizacion=row[8],
            ultimo_acceso=row[9]
        )

    def get_by_id(self, user_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario si existe, None en caso contrario
        """
        query = "SELECT * FROM usuarios WHERE id = %s"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            return None
        
        return Usuario(
            id=row[0],
            username=row[1],
            password_hash=row[2],
            nombre=row[3],
            email=row[4],
            rol=row[5],
            activo=bool(row[6]),
            fecha_creacion=row[7],
            fecha_actualizacion=row[8],
            ultimo_acceso=row[9]
        )

    def get_all(self) -> List[Usuario]:
        """
        Obtiene todos los usuarios
        
        Returns:
            Lista de usuarios
        """
        query = "SELECT * FROM usuarios ORDER BY username"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        usuarios = []
        for row in rows:
            usuarios.append(Usuario(
                id=row[0],
                username=row[1],
                password_hash=row[2],
                nombre=row[3],
                email=row[4],
                rol=row[5],
                activo=bool(row[6]),
                fecha_creacion=row[7],
                fecha_actualizacion=row[8],
                ultimo_acceso=row[9]
            ))
        
        return usuarios

    def update(self, usuario: Usuario) -> Dict[str, Any]:
        """
        Actualiza un usuario existente
        
        Args:
            usuario: Usuario con los datos actualizados
            
        Returns:
            Diccionario con success y data o error
        """
        query = """
        UPDATE usuarios
        SET nombre = %s, email = %s, rol = %s, activo = %s,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                query,
                (usuario.nombre, usuario.email, usuario.rol, 
                 usuario.activo, usuario.id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'data': usuario.to_dict()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al actualizar usuario: {str(e)}'
            }

    def update_password(self, user_id: int, new_password_hash: str) -> Dict[str, Any]:
        """
        Actualiza la contraseña de un usuario
        
        Args:
            user_id: ID del usuario
            new_password_hash: Hash de la nueva contraseña
            
        Returns:
            Diccionario con success y mensaje o error
        """
        query = """
        UPDATE usuarios
        SET password_hash = %s, fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (new_password_hash, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'Contraseña actualizada correctamente'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al actualizar contraseña: {str(e)}'
            }

    def update_ultimo_acceso(self, user_id: int) -> None:
        """
        Actualiza la fecha de último acceso de un usuario
        
        Args:
            user_id: ID del usuario
        """
        query = "UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id = %s"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def delete(self, user_id: int) -> Dict[str, Any]:
        """
        Elimina un usuario
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            Diccionario con success y mensaje o error
        """
        query = "DELETE FROM usuarios WHERE id = %s"
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'Usuario eliminado correctamente'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al eliminar usuario: {str(e)}'
            }
