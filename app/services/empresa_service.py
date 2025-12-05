"""
Servicio de lógica de negocio para Empresas
"""
from typing import List, Optional, Dict, Any
from app.models.empresa import Empresa
from app.repositories.empresa_repository import EmpresaRepository


class EmpresaService:
    """
    Servicio que maneja toda la lógica de negocio relacionada con empresas.
    Esta capa está completamente desacoplada de la base de datos.
    """

    def __init__(self, repository: EmpresaRepository):
        """
        Inicializa el servicio con un repositorio
        
        Args:
            repository: Repositorio de empresas (puede ser SQLite, MySQL, etc.)
        """
        self.repository = repository

    def crear_empresa(self, empresa: Empresa) -> Dict[str, Any]:
        """
        Crea una nueva empresa con validaciones de negocio
        
        Args:
            empresa: Objeto Empresa a crear
            
        Returns:
            Diccionario con el resultado de la operación
        """
        try:
            # Validación: verificar que el NIT no exista
            if self.repository.exists_by_nit(empresa.nit):
                return {
                    'success': False,
                    'error': f'Ya existe una empresa con el NIT {empresa.nit}'
                }

            # Validación: verificar que tenga al menos un módulo activo
            if not empresa.tiene_modulos_activos():
                return {
                    'success': False,
                    'error': 'La empresa debe tener al menos un módulo activo'
                }

            # Crear la empresa
            empresa_creada = self.repository.create(empresa)

            return {
                'success': True,
                'message': 'Empresa creada exitosamente',
                'data': empresa_creada.to_dict()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def obtener_empresa_por_nit(self, nit: str) -> Dict[str, Any]:
        """
        Obtiene una empresa por su NIT
        
        Args:
            nit: NIT de la empresa
            
        Returns:
            Diccionario con el resultado
        """
        try:
            empresa = self.repository.get_by_nit(nit)

            if not empresa:
                return {
                    'success': False,
                    'error': f'No se encontró la empresa con NIT {nit}'
                }

            return {
                'success': True,
                'data': empresa.to_dict()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def obtener_empresas_activas(self) -> Dict[str, Any]:
        """
        Obtiene todas las empresas activas con al menos un módulo activo
        
        Returns:
            Diccionario con la lista de empresas
        """
        try:
            empresas = self.repository.get_all({
                'estado': 'activo',
                'activos_solamente': True
            })

            return {
                'success': True,
                'data': [emp.to_dict() for emp in empresas],
                'total': len(empresas)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    def obtener_todas_empresas(self, estado: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene todas las empresas, opcionalmente filtradas por estado
        
        Args:
            estado: Estado opcional para filtrar (activo, inactivo, suspendido)
            
        Returns:
            Diccionario con la lista de empresas
        """
        try:
            filters = {}
            if estado:
                filters['estado'] = estado

            empresas = self.repository.get_all(filters)
            # print(empresas)  # Debugging line to check fetched companies
            return {
                'success': True,
                'data': [emp.to_dict() for emp in empresas],
                'total': len(empresas)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    def actualizar_empresa(self, empresa: Empresa) -> Dict[str, Any]:
        """
        Actualiza una empresa existente
        
        Args:
            empresa: Objeto Empresa con los datos actualizados
            
        Returns:
            Diccionario con el resultado
        """
        try:
            if not self.repository.exists(empresa.id):
                return {
                    'success': False,
                    'error': f'No existe la empresa con ID {empresa.id}'
                }

            success = self.repository.update(empresa)

            if success:
                return {
                    'success': True,
                    'message': 'Empresa actualizada exitosamente',
                    'data': empresa.to_dict()
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo actualizar la empresa'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def actualizar_estado_modulo(
        self, 
        nit: str, 
        modulo: str, 
        campo: str, 
        valor: int
    ) -> Dict[str, Any]:
        """
        Actualiza el estado de un campo específico de un módulo
        
        Args:
            nit: NIT de la empresa
            modulo: 'certificado', 'resolucion' o 'documento'
            campo: 'renovado' o 'facturado'
            valor: 0 o 1
            
        Returns:
            Diccionario con el resultado
        """
        try:
            # Validaciones
            if modulo not in ['certificado', 'resolucion', 'documento']:
                return {
                    'success': False,
                    'error': f'Módulo no válido: {modulo}'
                }

            if campo not in ['renovado', 'facturado']:
                return {
                    'success': False,
                    'error': f'Campo no válido: {campo}'
                }

            if valor not in [0, 1]:
                return {
                    'success': False,
                    'error': f'Valor no válido: {valor}. Debe ser 0 o 1'
                }

            # Verificar que la empresa existe
            if not self.repository.exists_by_nit(nit):
                return {
                    'success': False,
                    'error': f'No se encontró la empresa con NIT {nit}'
                }

            # Actualizar
            success = self.repository.update_field(nit, modulo, campo, valor)

            if success:
                return {
                    'success': True,
                    'message': 'Estado actualizado exitosamente',
                    'nit': nit,
                    'modulo': modulo,
                    'campo': campo,
                    'valor': valor
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo actualizar el estado'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def eliminar_empresa(self, empresa_id: int) -> Dict[str, Any]:
        """
        Elimina una empresa (soft delete cambiando estado a inactivo recomendado)
        
        Args:
            empresa_id: ID de la empresa
            
        Returns:
            Diccionario con el resultado
        """
        try:
            empresa = self.repository.get_by_id(empresa_id)

            if not empresa:
                return {
                    'success': False,
                    'error': f'No se encontró la empresa con ID {empresa_id}'
                }

            # Soft delete: cambiar estado a inactivo
            empresa.estado = 'inactivo'
            success = self.repository.update(empresa)

            if success:
                return {
                    'success': True,
                    'message': 'Empresa marcada como inactiva exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo desactivar la empresa'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
