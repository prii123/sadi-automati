"""
Repositorios - Capa de abstracción de base de datos
"""
from .base_repository import IRepository
from .empresa_repository import EmpresaRepository

__all__ = ['IRepository', 'EmpresaRepository']
