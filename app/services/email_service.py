"""
Servicio de envío de emails
Permite enviar notificaciones por correo electrónico usando Gmail
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from datetime import datetime
import os


class EmailService:
    """
    Servicio para enviar emails usando Gmail SMTP
    """

    def __init__(self, smtp_user: str = None, smtp_password: str = None):
        """
        Inicializa el servicio de email
        
        Args:
            smtp_user: Email de Gmail para enviar
            smtp_password: Contraseña de aplicación de Gmail
        """
        # Configuración SMTP de Gmail
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Credenciales desde parámetros o variables de entorno
        self.smtp_user = smtp_user or os.getenv('SMTP_USER')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        
        # Email por defecto para envíos
        self.from_email = self.smtp_user
        self.from_name = "Sistema de Gestión de Facturación"

    def enviar_notificaciones_vencimientos(
        self, 
        destinatarios: List[str], 
        notificaciones: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Envía un email con el resumen de notificaciones de vencimientos
        
        Args:
            destinatarios: Lista de emails destino
            notificaciones: Lista de notificaciones a enviar
            
        Returns:
            Diccionario con el resultado del envío
        """
        try:
            if not self.smtp_user or not self.smtp_password:
                return {
                    'success': False,
                    'error': 'Credenciales SMTP no configuradas'
                }

            if not destinatarios:
                return {
                    'success': False,
                    'error': 'No hay destinatarios especificados'
                }

            if not notificaciones:
                return {
                    'success': True,
                    'message': 'No hay notificaciones para enviar'
                }

            # Agrupar notificaciones por prioridad
            criticas = []
            altas = []
            medias = []

            for notif in notificaciones:
                for alerta in notif.get('alertas', []):
                    prioridad = alerta.get('prioridad', 'MEDIA')
                    alerta_info = {
                        'empresa': notif['empresa'],
                        **alerta
                    }
                    
                    if prioridad == 'CRITICA':
                        criticas.append(alerta_info)
                    elif prioridad == 'ALTA':
                        altas.append(alerta_info)
                    else:
                        medias.append(alerta_info)

            # Generar HTML del email
            html_content = self._generar_html_notificaciones(criticas, altas, medias)
            
            # Crear mensaje
            mensaje = MIMEMultipart('alternative')
            mensaje['Subject'] = f'Notificaciones de Vencimientos - {datetime.now().strftime("%d/%m/%Y")}'
            mensaje['From'] = f'{self.from_name} <{self.from_email}>'
            mensaje['To'] = ', '.join(destinatarios)
            
            # Agregar contenido HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            mensaje.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(mensaje)
            
            return {
                'success': True,
                'message': f'Email enviado exitosamente a {len(destinatarios)} destinatario(s)',
                'destinatarios': destinatarios,
                'total_notificaciones': len(criticas) + len(altas) + len(medias)
            }

        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'error': 'Error de autenticación SMTP. Verifica las credenciales de Gmail.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al enviar email: {str(e)}'
            }

    def _generar_html_notificaciones(
        self, 
        criticas: List[Dict], 
        altas: List[Dict], 
        medias: List[Dict]
    ) -> str:
        """
        Genera el contenido HTML del email de notificaciones
        
        Args:
            criticas: Lista de alertas críticas
            altas: Lista de alertas de alta prioridad
            medias: Lista de alertas de prioridad media
            
        Returns:
            HTML del email
        """
        total = len(criticas) + len(altas) + len(medias)
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #1f2937;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .summary {{
            background-color: #f3f4f6;
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
        }}
        .notification-group {{
            margin: 20px 0;
        }}
        .notification-group h3 {{
            padding: 10px;
            border-radius: 8px;
            color: white;
        }}
        .critica {{
            background-color: #ef4444;
        }}
        .alta {{
            background-color: #f59e0b;
        }}
        .media {{
            background-color: #3b82f6;
        }}
        .notification-card {{
            background-color: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}
        .empresa-nombre {{
            font-size: 18px;
            font-weight: bold;
            color: #1f2937;
        }}
        .empresa-nit {{
            color: #6b7280;
            font-size: 14px;
        }}
        .modulo {{
            color: #3b82f6;
            font-weight: bold;
            margin: 10px 0;
        }}
        .motivo {{
            background-color: #fef3c7;
            padding: 8px;
            border-radius: 4px;
            margin: 5px 0;
        }}
        .meta {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
            font-size: 14px;
        }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge-renovado {{
            background-color: #dbeafe;
            color: #1e40af;
        }}
        .badge-facturado {{
            background-color: #d1fae5;
            color: #065f46;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #6b7280;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Sistema de Gestión de Facturación</h1>
        <p>Notificaciones de Vencimientos</p>
    </div>
    
    <div class="summary">
        <h2>Resumen del Día: {datetime.now().strftime('%d/%m/%Y')}</h2>
        <p><strong>Total de notificaciones:</strong> {total}</p>
        <p>
            🚨 Críticas: {len(criticas)} | 
            ⚠️ Alta prioridad: {len(altas)} | 
            ℹ️ Prioridad media: {len(medias)}
        </p>
    </div>
"""

        # Notificaciones críticas
        if criticas:
            html += self._generar_grupo_notificaciones('🚨 Críticas', criticas, 'critica')
        
        # Notificaciones alta prioridad
        if altas:
            html += self._generar_grupo_notificaciones('⚠️ Alta Prioridad', altas, 'alta')
        
        # Notificaciones prioridad media
        if medias:
            html += self._generar_grupo_notificaciones('ℹ️ Prioridad Media', medias, 'media')

        html += """
    <div class="footer">
        <p>Este es un mensaje automático del Sistema de Gestión de Facturación.</p>
        <p>Por favor no responder a este email.</p>
    </div>
</body>
</html>
"""
        return html

    def _generar_grupo_notificaciones(self, titulo: str, alertas: List[Dict], tipo: str) -> str:
        """Genera HTML para un grupo de notificaciones"""
        html = f"""
    <div class="notification-group">
        <h3 class="{tipo}">{titulo} ({len(alertas)})</h3>
"""
        
        for alerta in alertas:
            empresa = alerta['empresa']
            dias = alerta.get('dias_restantes', 'N/A')
            fecha_venc = alerta.get('fecha_vencimiento', '')
            
            # Formatear fecha
            fecha_formateada = 'Sin fecha'
            if fecha_venc:
                try:
                    fecha_obj = datetime.fromisoformat(fecha_venc)
                    fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
                except:
                    fecha_formateada = fecha_venc
            
            # Badges de estado
            badges = ''
            if alerta.get('renovado'):
                badges += '<span class="badge badge-renovado">🔄 Renovado</span> '
            if alerta.get('facturado'):
                badges += '<span class="badge badge-facturado">💰 Facturado</span> '
            
            html += f"""
        <div class="notification-card">
            <div class="empresa-nombre">{empresa['nombre']}</div>
            <div class="empresa-nit">NIT: {empresa['nit']}</div>
            <div class="modulo">{alerta.get('modulo', '')}</div>
            <div class="motivo">{alerta.get('motivo', '')}</div>
            <div class="meta">
                <span>📅 Vence: {fecha_formateada}</span>
                <span>⏰ {dias} días restantes</span>
            </div>
            <div style="margin-top: 10px;">
                {badges}
            </div>
        </div>
"""
        
        html += """
    </div>
"""
        return html

    def enviar_email_simple(
        self, 
        destinatario: str, 
        asunto: str, 
        mensaje: str
    ) -> Dict[str, Any]:
        """
        Envía un email simple de texto
        
        Args:
            destinatario: Email destino
            asunto: Asunto del email
            mensaje: Contenido del mensaje
            
        Returns:
            Diccionario con el resultado
        """
        try:
            if not self.smtp_user or not self.smtp_password:
                return {
                    'success': False,
                    'error': 'Credenciales SMTP no configuradas'
                }

            msg = MIMEMultipart()
            msg['Subject'] = asunto
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = destinatario
            
            msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return {
                'success': True,
                'message': 'Email enviado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
