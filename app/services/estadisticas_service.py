"""
Servicio de estadísticas del sistema
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from app.repositories.empresa_repository import EmpresaRepository


class EstadisticasService:
    """
    Servicio que calcula estadísticas del sistema
    """

    def __init__(self, repository: EmpresaRepository):
        """
        Inicializa el servicio con un repositorio
        
        Args:
            repository: Repositorio de empresas
        """
        self.repository = repository

    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """
        Calcula estadísticas generales del sistema
        
        Returns:
            Diccionario con estadísticas detalladas
        """
        try:
            empresas = self.repository.get_all({
                'estado': 'activo',
                'activos_solamente': True
            })

            stats = {
                'total_empresas': len(empresas),
                'certificados': {
                    'activos': 0,
                    'renovados': 0,
                    'facturados': 0,
                    'pendientes_renovacion': 0,
                    'pendientes_facturacion': 0
                },
                'resoluciones': {
                    'activos': 0,
                    'renovados': 0,
                    'facturados': 0,
                    'pendientes_renovacion': 0,
                    'pendientes_facturacion': 0
                },
                'documentos': {
                    'activos': 0,
                    'renovados': 0,
                    'facturados': 0,
                    'pendientes_renovacion': 0,
                    'pendientes_facturacion': 0
                }
            }

            for empresa in empresas:
                # Estadísticas de Certificados
                if empresa.certificado.activo == 1:
                    stats['certificados']['activos'] += 1
                    if empresa.certificado.renovado == 1:
                        stats['certificados']['renovados'] += 1
                    else:
                        stats['certificados']['pendientes_renovacion'] += 1
                    
                    if empresa.certificado.facturado == 1:
                        stats['certificados']['facturados'] += 1
                    else:
                        stats['certificados']['pendientes_facturacion'] += 1

                # Estadísticas de Resoluciones
                if empresa.resolucion.activo == 1:
                    stats['resoluciones']['activos'] += 1
                    if empresa.resolucion.renovado == 1:
                        stats['resoluciones']['renovados'] += 1
                    else:
                        stats['resoluciones']['pendientes_renovacion'] += 1
                    
                    if empresa.resolucion.facturado == 1:
                        stats['resoluciones']['facturados'] += 1
                    else:
                        stats['resoluciones']['pendientes_facturacion'] += 1

                # Estadísticas de Documentos
                if empresa.documento.activo == 1:
                    stats['documentos']['activos'] += 1
                    if empresa.documento.renovado == 1:
                        stats['documentos']['renovados'] += 1
                    else:
                        stats['documentos']['pendientes_renovacion'] += 1
                    
                    if empresa.documento.facturado == 1:
                        stats['documentos']['facturados'] += 1
                    else:
                        stats['documentos']['pendientes_facturacion'] += 1

            return {
                'success': True,
                'data': stats
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def obtener_empresas_pendientes(self) -> Dict[str, Any]:
        """
        Obtiene empresas con pendientes de renovación o facturación
        
        Returns:
            Diccionario con empresas pendientes por categoría
        """
        try:
            empresas = self.repository.get_all({
                'estado': 'activo',
                'activos_solamente': True
            })

            pendientes = {
                'pendientes_renovacion': [],
                'pendientes_facturacion': [],
                'totalmente_completadas': []
            }

            for empresa in empresas:
                tiene_pendiente_renovacion = False
                tiene_pendiente_facturacion = False

                # Verificar certificados
                if empresa.certificado.activo == 1:
                    if empresa.certificado.renovado == 0:
                        tiene_pendiente_renovacion = True
                    if empresa.certificado.facturado == 0:
                        tiene_pendiente_facturacion = True

                # Verificar resoluciones
                if empresa.resolucion.activo == 1:
                    if empresa.resolucion.renovado == 0:
                        tiene_pendiente_renovacion = True
                    if empresa.resolucion.facturado == 0:
                        tiene_pendiente_facturacion = True

                # Verificar documentos
                if empresa.documento.activo == 1:
                    if empresa.documento.renovado == 0:
                        tiene_pendiente_renovacion = True
                    if empresa.documento.facturado == 0:
                        tiene_pendiente_facturacion = True

                # Clasificar empresa
                empresa_dict = {
                    'nit': empresa.nit,
                    'nombre': empresa.nombre
                }

                if tiene_pendiente_renovacion:
                    pendientes['pendientes_renovacion'].append(empresa_dict)
                
                if tiene_pendiente_facturacion:
                    pendientes['pendientes_facturacion'].append(empresa_dict)
                
                if not tiene_pendiente_renovacion and not tiene_pendiente_facturacion:
                    pendientes['totalmente_completadas'].append(empresa_dict)

            return {
                'success': True,
                'data': pendientes,
                'resumen': {
                    'pendientes_renovacion': len(pendientes['pendientes_renovacion']),
                    'pendientes_facturacion': len(pendientes['pendientes_facturacion']),
                    'completadas': len(pendientes['totalmente_completadas'])
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def obtener_estadisticas_vencimientos_certificados(self) -> Dict[str, Any]:
        """
        Calcula estadísticas de vencimientos de certificados basándose en fechas
        
        Returns:
            Diccionario con conteo de vencidos, por vencer y vigentes
        """
        try:
            empresas = self.repository.get_all({
                'estado': 'activo',
                'activos_solamente': True
            })

            hoy = datetime.now()
            dias_alerta = 30  # Considerar "por vencer" si faltan menos de 30 días
            fecha_limite_alerta = hoy + timedelta(days=dias_alerta)

            stats = {
                'vencidos': 0,
                'por_vencer': 0,
                'vigentes': 0
            }

            for empresa in empresas:
                if empresa.certificado.activo == 1 and empresa.certificado.fecha_final:
                    fecha_final = empresa.certificado.fecha_final
                    
                    if fecha_final < hoy:
                        stats['vencidos'] += 1
                    elif fecha_final <= fecha_limite_alerta:
                        stats['por_vencer'] += 1
                    else:
                        stats['vigentes'] += 1

            return {
                'success': True,
                'data': stats
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def obtener_estadisticas_vencimientos_resoluciones(self) -> Dict[str, Any]:
        """
        Calcula estadísticas de vencimientos de resoluciones basándose en fechas
        
        Returns:
            Diccionario con conteo de vencidos, por vencer y vigentes
        """
        try:
            empresas = self.repository.get_all({
                'estado': 'activo',
                'activos_solamente': True
            })

            hoy = datetime.now()
            dias_alerta = 30
            fecha_limite_alerta = hoy + timedelta(days=dias_alerta)

            stats = {
                'vencidos': 0,
                'por_vencer': 0,
                'vigentes': 0
            }

            for empresa in empresas:
                if empresa.resolucion.activo == 1 and empresa.resolucion.fecha_final:
                    fecha_final = empresa.resolucion.fecha_final
                    
                    if fecha_final < hoy:
                        stats['vencidos'] += 1
                    elif fecha_final <= fecha_limite_alerta:
                        stats['por_vencer'] += 1
                    else:
                        stats['vigentes'] += 1

            return {
                'success': True,
                'data': stats
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def obtener_estadisticas_vencimientos_documentos(self) -> Dict[str, Any]:
        """
        Calcula estadísticas de vencimientos de documentos basándose en fechas
        
        Returns:
            Diccionario con conteo de vencidos, por vencer y vigentes
        """
        try:
            empresas = self.repository.get_all({
                'estado': 'activo',
                'activos_solamente': True
            })

            hoy = datetime.now()
            dias_alerta = 30
            fecha_limite_alerta = hoy + timedelta(days=dias_alerta)

            stats = {
                'vencidos': 0,
                'por_vencer': 0,
                'vigentes': 0
            }

            for empresa in empresas:
                if empresa.documento.activo == 1 and empresa.documento.fecha_final:
                    fecha_final = empresa.documento.fecha_final
                    
                    if fecha_final < hoy:
                        stats['vencidos'] += 1
                    elif fecha_final <= fecha_limite_alerta:
                        stats['por_vencer'] += 1
                    else:
                        stats['vigentes'] += 1

            return {
                'success': True,
                'data': stats
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
