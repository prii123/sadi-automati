"""
Servicio de autenticación y autorización
"""
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario import Usuario


class AuthService:
    """
    Servicio que maneja autenticación y tokens
    """
    
    # Tokens en memoria (en producción usar Redis o base de datos)
    _tokens: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, repository: UsuarioRepository):
        """
        Inicializa el servicio con un repositorio
        
        Args:
            repository: Repositorio de usuarios
        """
        self.repository = repository

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashea una contraseña usando SHA-256
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
        """
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica una contraseña contra su hash
        
        Args:
            password: Contraseña en texto plano
            password_hash: Hash almacenado
            
        Returns:
            True si coincide, False si no
        """
        return AuthService.hash_password(password) == password_hash

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Autentica un usuario y genera un token
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Diccionario con success, token y usuario
        """
        try:
            # Buscar usuario
            usuario = self.repository.get_by_username(username)
            
            if not usuario:
                return {
                    'success': False,
                    'error': 'Usuario o contraseña incorrectos'
                }
            
            if usuario.activo != 1:
                return {
                    'success': False,
                    'error': 'Usuario inactivo'
                }
            
            # Verificar contraseña
            if not self.verify_password(password, usuario.password_hash):
                return {
                    'success': False,
                    'error': 'Usuario o contraseña incorrectos'
                }
            
            # Generar token
            token = secrets.token_urlsafe(32)
            expiracion = datetime.now() + timedelta(hours=24)
            
            # Guardar token
            self._tokens[token] = {
                'usuario_id': usuario.id,
                'username': usuario.username,
                'rol': usuario.rol,
                'expiracion': expiracion
            }
            
            # Actualizar último acceso
            self.repository.update_ultimo_acceso(usuario.id)
            
            return {
                'success': True,
                'token': token,
                'usuario': usuario.to_dict(),
                'expiracion': expiracion.isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def logout(self, token: str) -> Dict[str, Any]:
        """
        Invalida un token de sesión
        
        Args:
            token: Token a invalidar
            
        Returns:
            Diccionario con success
        """
        if token in self._tokens:
            del self._tokens[token]
        
        return {'success': True}

    def validar_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Valida un token y retorna los datos del usuario
        
        Args:
            token: Token a validar
            
        Returns:
            Datos del token o None si es inválido
        """
        if token not in self._tokens:
            return None
        
        datos_token = self._tokens[token]
        
        # Verificar expiración
        if datetime.now() > datos_token['expiracion']:
            del self._tokens[token]
            return None
        
        return datos_token

    def validar_rol(self, token: str, roles_permitidos: list) -> bool:
        """
        Valida que un token tenga uno de los roles permitidos
        
        Args:
            token: Token a validar
            roles_permitidos: Lista de roles permitidos
            
        Returns:
            True si tiene permiso, False si no
        """
        datos_token = self.validar_token(token)
        
        if not datos_token:
            return False
        
        return datos_token['rol'] in roles_permitidos

    def obtener_usuario_actual(self, token: str) -> Optional[Usuario]:
        """
        Obtiene el usuario asociado a un token
        
        Args:
            token: Token del usuario
            
        Returns:
            Usuario o None
        """
        datos_token = self.validar_token(token)
        
        if not datos_token:
            return None
        
        return self.repository.get_by_id(datos_token['usuario_id'])

    def cambiar_password(self, usuario_id: int, password_actual: str, password_nueva: str) -> Dict[str, Any]:
        """
        Cambia la contraseña de un usuario
        
        Args:
            usuario_id: ID del usuario
            password_actual: Contraseña actual
            password_nueva: Nueva contraseña
            
        Returns:
            Diccionario con success
        """
        try:
            usuario = self.repository.get_by_id(usuario_id)
            
            if not usuario:
                return {
                    'success': False,
                    'error': 'Usuario no encontrado'
                }
            
            # Verificar contraseña actual
            if not self.verify_password(password_actual, usuario.password_hash):
                return {
                    'success': False,
                    'error': 'Contraseña actual incorrecta'
                }
            
            # Actualizar contraseña
            nuevo_hash = self.hash_password(password_nueva)
            resultado = self.repository.update(usuario_id, {'password_hash': nuevo_hash})
            
            return resultado
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def limpiar_tokens_expirados(self):
        """Elimina tokens expirados de la memoria"""
        ahora = datetime.now()
        tokens_expirados = [
            token for token, datos in self._tokens.items()
            if datos['expiracion'] < ahora
        ]
        
        for token in tokens_expirados:
            del self._tokens[token]
