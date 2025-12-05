"""
Servicio de notificaciones
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.repositories.empresa_repository import EmpresaRepository
from app.models.empresa import Empresa


class NotificacionService:
    """
    Servicio que maneja las notificaciones del sistema
    """

    def __init__(self, repository: EmpresaRepository):
        """
        Inicializa el servicio con un repositorio
        
        Args:
            repository: Repositorio de empresas
        """
        self.repository = repository

    def obtener_notificaciones_pendientes(self, dias_anticipacion: int = 30) -> Dict[str, Any]:
        """
        Obtiene empresas que requieren notificación por:
        1. Vencimiento próximo (según fecha de notificación)
        2. Renovado pero no facturado
        
        Args:
            dias_anticipacion: Días de anticipación para notificar (no usado, usa fecha_notificacion)
            
        Returns:
            Diccionario con las empresas que requieren notificación
        """
        try:
            empresas = self.repository.get_all({
                'estado': 'activo',
                'activos_solamente': True
            })

            hoy = datetime.now()
            notificaciones = []

            for empresa in empresas:
                alertas = []

                # Verificar certificado
                if empresa.certificado.activo == 1:
                    # Solo mostrar si NO está renovado Y facturado (completamente resuelto)
                    if not (empresa.certificado.renovado == 1 and empresa.certificado.facturado == 1):
                        # Alerta por fecha de notificación alcanzada
                        if empresa.certificado.fecha_final:
                            notif_date = self._parse_date(empresa.certificado.notificacion)
                            if notif_date and hoy >= notif_date:
                                dias_restantes = (empresa.certificado.fecha_final - hoy).days
                                prioridad = self._calcular_prioridad(dias_restantes)
                                
                                alertas.append({
                                    'tipo': 'certificado',
                                    'modulo': 'Certificado de Facturación Electrónica',
                                    'fecha_vencimiento': empresa.certificado.fecha_final.isoformat(),
                                    'fecha_notificacion': empresa.certificado.notificacion,
                                    'dias_restantes': max(0, dias_restantes),
                                    'renovado': empresa.certificado.renovado == 1,
                                    'facturado': empresa.certificado.facturado == 1,
                                    'prioridad': prioridad,
                                    'motivo': 'Próximo a vencer'
                                })
                        
                        # Alerta por renovado pero no facturado
                        if empresa.certificado.renovado == 1 and empresa.certificado.facturado == 0:
                            # Si ya existe una alerta de vencimiento, actualizar motivo
                            alerta_existente = next((a for a in alertas if a['tipo'] == 'certificado'), None)
                            if alerta_existente:
                                alerta_existente['motivo'] = 'Próximo a vencer y renovado sin facturar'
                                alerta_existente['prioridad'] = 'CRITICA'
                            else:
                                alertas.append({
                                    'tipo': 'certificado',
                                    'modulo': 'Certificado de Facturación Electrónica',
                                    'fecha_vencimiento': empresa.certificado.fecha_final.isoformat() if empresa.certificado.fecha_final else None,
                                    'fecha_notificacion': empresa.certificado.notificacion,
                                    'dias_restantes': (empresa.certificado.fecha_final - hoy).days if empresa.certificado.fecha_final else None,
                                    'renovado': True,
                                    'facturado': False,
                                    'prioridad': 'ALTA',
                                    'motivo': 'Renovado pero no facturado'
                                })

                # Verificar resolución
                if empresa.resolucion.activo == 1:
                    # Solo mostrar si NO está renovado Y facturado (completamente resuelto)
                    if not (empresa.resolucion.renovado == 1 and empresa.resolucion.facturado == 1):
                        # Alerta por fecha de notificación alcanzada
                        if empresa.resolucion.fecha_final:
                            notif_date = self._parse_date(empresa.resolucion.notificacion)
                            if notif_date and hoy >= notif_date:
                                dias_restantes = (empresa.resolucion.fecha_final - hoy).days
                                prioridad = self._calcular_prioridad(dias_restantes)
                                
                                alertas.append({
                                    'tipo': 'resolucion',
                                    'modulo': 'Resolución de Facturación',
                                    'fecha_vencimiento': empresa.resolucion.fecha_final.isoformat(),
                                    'fecha_notificacion': empresa.resolucion.notificacion,
                                    'dias_restantes': max(0, dias_restantes),
                                    'renovado': empresa.resolucion.renovado == 1,
                                    'facturado': empresa.resolucion.facturado == 1,
                                    'prioridad': prioridad,
                                    'motivo': 'Próximo a vencer'
                                })
                        
                        # Alerta por renovado pero no facturado
                        if empresa.resolucion.renovado == 1 and empresa.resolucion.facturado == 0:
                            alerta_existente = next((a for a in alertas if a['tipo'] == 'resolucion'), None)
                            if alerta_existente:
                                alerta_existente['motivo'] = 'Próximo a vencer y renovado sin facturar'
                                alerta_existente['prioridad'] = 'CRITICA'
                            else:
                                alertas.append({
                                    'tipo': 'resolucion',
                                    'modulo': 'Resolución de Facturación',
                                    'fecha_vencimiento': empresa.resolucion.fecha_final.isoformat() if empresa.resolucion.fecha_final else None,
                                    'fecha_notificacion': empresa.resolucion.notificacion,
                                    'dias_restantes': (empresa.resolucion.fecha_final - hoy).days if empresa.resolucion.fecha_final else None,
                                    'renovado': True,
                                    'facturado': False,
                                    'prioridad': 'ALTA',
                                    'motivo': 'Renovado pero no facturado'
                                })

                # Verificar documento
                if empresa.documento.activo == 1:
                    # Solo mostrar si NO está renovado Y facturado (completamente resuelto)
                    if not (empresa.documento.renovado == 1 and empresa.documento.facturado == 1):
                        # Alerta por fecha de notificación alcanzada
                        if empresa.documento.fecha_final:
                            notif_date = self._parse_date(empresa.documento.notificacion)
                            if notif_date and hoy >= notif_date:
                                dias_restantes = (empresa.documento.fecha_final - hoy).days
                                prioridad = self._calcular_prioridad(dias_restantes)
                                
                                alertas.append({
                                    'tipo': 'documento',
                                    'modulo': 'Resolución Documentos Soporte',
                                    'fecha_vencimiento': empresa.documento.fecha_final.isoformat(),
                                    'fecha_notificacion': empresa.documento.notificacion,
                                    'dias_restantes': max(0, dias_restantes),
                                    'renovado': empresa.documento.renovado == 1,
                                    'facturado': empresa.documento.facturado == 1,
                                    'prioridad': prioridad,
                                    'motivo': 'Próximo a vencer'
                                })
                        
                        # Alerta por renovado pero no facturado
                        if empresa.documento.renovado == 1 and empresa.documento.facturado == 0:
                            alerta_existente = next((a for a in alertas if a['tipo'] == 'documento'), None)
                            if alerta_existente:
                                alerta_existente['motivo'] = 'Próximo a vencer y renovado sin facturar'
                                alerta_existente['prioridad'] = 'CRITICA'
                            else:
                                alertas.append({
                                    'tipo': 'documento',
                                    'modulo': 'Resolución Documentos Soporte',
                                    'fecha_vencimiento': empresa.documento.fecha_final.isoformat() if empresa.documento.fecha_final else None,
                                    'fecha_notificacion': empresa.documento.notificacion,
                                    'dias_restantes': (empresa.documento.fecha_final - hoy).days if empresa.documento.fecha_final else None,
                                    'renovado': True,
                                    'facturado': False,
                                    'prioridad': 'ALTA',
                                    'motivo': 'Renovado pero no facturado'
                                })

                if alertas:
                    notificaciones.append({
                        'empresa': {
                            'nit': empresa.nit,
                            'nombre': empresa.nombre,
                            'tipo': empresa.tipo
                        },
                        'alertas': alertas,
                        'total_alertas': len(alertas)
                    })

            # Ordenar por prioridad y días restantes
            prioridad_order = {'CRITICA': 0, 'ALTA': 1, 'MEDIA': 2}
            notificaciones.sort(
                key=lambda x: (
                    min(prioridad_order.get(a.get('prioridad', 'MEDIA'), 2) for a in x['alertas']),
                    min((a.get('dias_restantes') or 999) for a in x['alertas'])
                )
            )

            return {
                'success': True,
                'data': notificaciones,
                'total': len(notificaciones),
                'fecha_consulta': datetime.now().isoformat(),
                'dias_anticipacion': dias_anticipacion
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    def _parse_date(self, date_str: str) -> datetime:
        """Parsea una fecha en formato ISO string a datetime"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str)
        except:
            return None

    def _calcular_prioridad(self, dias_restantes: int) -> str:
        """Calcula la prioridad según días restantes"""
        if dias_restantes <= 5:
            return 'CRITICA'
        elif dias_restantes <= 30:
            return 'ALTA'
        elif dias_restantes <= 60:
            return 'MEDIA'
        else:
            return 'MEDIA'  # Más de 60 días también es media

    def obtener_vencimientos_mes_actual(self) -> Dict[str, Any]:
        """
        Obtiene todas las empresas con vencimientos en el mes actual
        
        Returns:
            Diccionario con vencimientos del mes
        """
        try:
            empresas = self.repository.get_all({
                'estado': 'activo',
                'activos_solamente': True
            })

            # Calcular primer y último día del mes actual
            hoy = datetime.now()
            primer_dia_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Último día del mes
            if hoy.month == 12:
                ultimo_dia_mes = hoy.replace(year=hoy.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                ultimo_dia_mes = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)
            
            ultimo_dia_mes = ultimo_dia_mes.replace(hour=23, minute=59, second=59)

            vencimientos = []

            for empresa in empresas:
                vencimientos_empresa = []

                # Certificado
                if (empresa.certificado.activo == 1 and 
                    empresa.certificado.fecha_final and
                    primer_dia_mes <= empresa.certificado.fecha_final <= ultimo_dia_mes):
                    vencimientos_empresa.append({
                        'tipo': 'certificado',
                        'fecha': empresa.certificado.fecha_final.isoformat(),
                        'renovado': empresa.certificado.renovado == 1,
                        'facturado': empresa.certificado.facturado == 1
                    })

                # Resolución
                if (empresa.resolucion.activo == 1 and 
                    empresa.resolucion.fecha_final and
                    primer_dia_mes <= empresa.resolucion.fecha_final <= ultimo_dia_mes):
                    vencimientos_empresa.append({
                        'tipo': 'resolucion',
                        'fecha': empresa.resolucion.fecha_final.isoformat(),
                        'renovado': empresa.resolucion.renovado == 1,
                        'facturado': empresa.resolucion.facturado == 1
                    })

                # Documento
                if (empresa.documento.activo == 1 and 
                    empresa.documento.fecha_final and
                    primer_dia_mes <= empresa.documento.fecha_final <= ultimo_dia_mes):
                    vencimientos_empresa.append({
                        'tipo': 'documento',
                        'fecha': empresa.documento.fecha_final.isoformat(),
                        'renovado': empresa.documento.renovado == 1,
                        'facturado': empresa.documento.facturado == 1
                    })

                if vencimientos_empresa:
                    vencimientos.append({
                        'empresa': {
                            'nit': empresa.nit,
                            'nombre': empresa.nombre
                        },
                        'vencimientos': vencimientos_empresa
                    })

            return {
                'success': True,
                'data': vencimientos,
                'total': len(vencimientos),
                'periodo': {
                    'mes': hoy.month,
                    'año': hoy.year,
                    'desde': primer_dia_mes.isoformat(),
                    'hasta': ultimo_dia_mes.isoformat()
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
