"""
Rutas de la API REST
Contiene todos los endpoints de la API
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path, Body, status, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from datetime import datetime
from io import BytesIO

from app.api.schemas import EmpresaRequest, ActualizarModuloRequest
from app.models.empresa import Empresa, ModuloEmpresa
from app.services.empresa_service import EmpresaService
from app.services.estadisticas_service import EstadisticasService
from app.services.notificacion_service import NotificacionService
from app.services.email_service import EmailService
from app.services.trigger_service import TriggerService
from app.services.importacion_service import ImportacionService


# Crear routers
router = APIRouter()
info_router = APIRouter(tags=["Info"])
empresas_router = APIRouter(prefix="/api/empresas", tags=["Empresas"])
estadisticas_router = APIRouter(prefix="/api/estadisticas", tags=["Estadísticas"])
notificaciones_router = APIRouter(prefix="/api/notificaciones", tags=["Notificaciones"])
email_router = APIRouter(prefix="/api/email", tags=["Email"])
triggers_router = APIRouter(prefix="/api/triggers", tags=["Triggers"])


# Variables globales para servicios (se inicializarán desde api.py)
empresa_service: EmpresaService = None
stats_service: EstadisticasService = None
notif_service: NotificacionService = None
email_service: EmailService = None
trigger_service: TriggerService = None
importacion_service: ImportacionService = None


def init_services(emp_service: EmpresaService, stat_service: EstadisticasService, notif_serv: NotificacionService, trig_service: TriggerService = None):
    """Inicializa los servicios para las rutas"""
    global empresa_service, stats_service, notif_service, email_service, trigger_service, importacion_service
    empresa_service = emp_service
    stats_service = stat_service
    notif_service = notif_serv
    email_service = EmailService()  # Inicializar servicio de email
    trigger_service = trig_service  # Inicializar servicio de triggers
    importacion_service = ImportacionService(emp_service.repository)  # Inicializar servicio de importación


def normalize_response(resultado: Dict) -> Dict:
    """Normaliza la respuesta del servicio para usar 'datos' en lugar de 'data'"""
    if 'data' in resultado:
        resultado['datos'] = resultado.pop('data')
    return resultado


# ========================================
# RUTAS DE INFORMACIÓN
# ========================================

@info_router.get("/api")
async def index():
    """Información de la API"""
    return {
        'nombre': 'Sistema de Gestión de Facturación',
        'version': '2.0.0',
        'framework': 'FastAPI',
        'docs': '/docs',
        'redoc': '/redoc',
        'endpoints': {
            'empresas': {
                'GET /api/empresas': 'Obtener todas las empresas activas',
                'GET /api/empresas/{nit}': 'Obtener empresa por NIT',
                'POST /api/empresas': 'Crear nueva empresa',
                'PATCH /api/empresas/{nit}/modulo': 'Actualizar estado de módulo',
                'DELETE /api/empresas/{id}': 'Desactivar empresa'
            },
            'estadisticas': {
                'GET /api/estadisticas/resumen': 'Estadísticas generales',
                'GET /api/estadisticas/por-estado': 'Empresas por estado',
                'GET /api/estadisticas/certificados': 'Estadísticas de certificados',
                'GET /api/estadisticas/resoluciones': 'Estadísticas de resoluciones',
                'GET /api/estadisticas/documentos': 'Estadísticas de documentos'
            },
            'notificaciones': {
                'GET /api/notificaciones/vencimientos': 'Notificaciones de vencimientos',
                'GET /api/notificaciones/criticas': 'Notificaciones críticas',
                'GET /api/notificaciones/conteo': 'Conteo de notificaciones'
            }
        }
    }


@info_router.get("/health")
async def health():
    """Endpoint de salud del sistema"""
    return {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'framework': 'FastAPI'
    }


# ========================================
# RUTAS DE EMPRESAS
# ========================================

# IMPORTANTE: Las rutas específicas (con paths literales) deben ir ANTES
# de las rutas dinámicas (con parámetros como {nit}) para evitar conflictos

# ========================================
# RUTAS DE IMPORTACIÓN MASIVA (ANTES de rutas dinámicas)
# ========================================

@empresas_router.get("/plantilla-excel")
async def descargar_plantilla_excel():
    """
    Descarga una plantilla Excel de ejemplo para importación masiva
    """
    print("🔥 EJECUTANDO ENDPOINT /plantilla-excel")
    try:
        # Generar plantilla
        excel_content = importacion_service.generar_plantilla_excel()
        print(f"✅ Plantilla generada, tamaño: {len(excel_content)} bytes")
        
        # Crear respuesta con el archivo
        return StreamingResponse(
            BytesIO(excel_content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=plantilla_empresas.xlsx"
            }
        )
        
    except Exception as e:
        print(f"❌ Error al generar plantilla: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar plantilla: {str(e)}")


@empresas_router.post("/importar")
async def importar_empresas_excel(
    file: UploadFile = File(..., description="Archivo Excel con empresas")
):
    """
    Importa empresas masivamente desde un archivo Excel
    
    El archivo debe tener las siguientes columnas:
    - NIT, RAZON_SOCIAL, ESTADO
    - CERTIFICADO_VENCIMIENTO, CERTIFICADO_RENOVADO, CERTIFICADO_FACTURADO
    - RESOLUCION_VENCIMIENTO, RESOLUCION_RENOVADO, RESOLUCION_FACTURADO
    - DOCUMENTO_VENCIMIENTO, DOCUMENTO_RENOVADO, DOCUMENTO_FACTURADO
    """
    print(f"🔥 EJECUTANDO ENDPOINT /importar - Archivo: {file.filename}")
    # Validar tipo de archivo
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400, 
            detail="El archivo debe ser un Excel (.xlsx o .xls)"
        )
    
    try:
        # Leer contenido del archivo
        contents = await file.read()
        print(f"✅ Archivo leído, tamaño: {len(contents)} bytes")
        
        # Procesar importación
        resultado = importacion_service.importar_desde_excel(contents)
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado.get('error'))
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error al procesar archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")


@empresas_router.get("/buscar/nombre")
async def buscar_por_nombre(nombre: str = Query(..., description="Nombre a buscar")):
    """Busca empresas por nombre"""
    resultado = empresa_service.buscar_por_nombre(nombre)
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    return resultado


@empresas_router.get("/filtrar/estado")
async def filtrar_por_estado(estado: str = Query(..., description="Estado a filtrar")):
    """Filtra empresas por estado"""
    resultado = empresa_service.filtrar_por_estado(estado)
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    return resultado


# ========================================
# RUTAS BÁSICAS DE EMPRESAS
# ========================================

@empresas_router.get("")
async def obtener_empresas():
    """Obtiene todas las empresas activas"""
    resultado = empresa_service.obtener_empresas_activas()
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    return normalize_response(resultado)


@empresas_router.get("/{nit}")
async def obtener_empresa(nit: str = Path(..., description="NIT de la empresa")):
    """Obtiene una empresa por NIT"""
    resultado = empresa_service.obtener_empresa_por_nit(nit)
    if not resultado['success']:
        raise HTTPException(status_code=404, detail=resultado.get('error'))
    return normalize_response(resultado)


@empresas_router.post("", status_code=status.HTTP_201_CREATED)
async def crear_empresa(empresa_data: EmpresaRequest):
    """Crea una nueva empresa"""
    try:
        # Crear módulos
        certificado = ModuloEmpresa(
            **empresa_data.certificado.dict() if empresa_data.certificado else {}
        )
        resolucion = ModuloEmpresa(
            **empresa_data.resolucion.dict() if empresa_data.resolucion else {}
        )
        documento = ModuloEmpresa(
            **empresa_data.documento.dict() if empresa_data.documento else {}
        )
        
        # Crear empresa
        empresa = Empresa(
            nit=empresa_data.nit,
            nombre=empresa_data.nombre,
            tipo=empresa_data.tipo,
            estado=empresa_data.estado,
            certificado=certificado,
            resolucion=resolucion,
            documento=documento
        )
        
        resultado = empresa_service.crear_empresa(empresa)
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado.get('error'))
        return normalize_response(resultado)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@empresas_router.put("/{nit}")
async def actualizar_empresa(
    nit: str = Path(..., description="NIT de la empresa"),
    empresa_data: EmpresaRequest = Body(...)
):
    """Actualiza una empresa existente"""
    try:
        # Primero obtener la empresa existente para tener el ID
        empresa_existente = empresa_service.obtener_empresa_por_nit(nit)
        if not empresa_existente['success']:
            raise HTTPException(status_code=404, detail=f"Empresa con NIT {nit} no encontrada")
        
        empresa_id = empresa_existente.get('data', {}).get('id')
        
        # Crear módulos con manejo de None
        certificado = None
        if empresa_data.certificado:
            cert_dict = empresa_data.certificado.dict()
            if any(cert_dict.values()):  # Solo crear si tiene valores
                certificado = ModuloEmpresa(**cert_dict)
        
        resolucion = None
        if empresa_data.resolucion:
            res_dict = empresa_data.resolucion.dict()
            if any(res_dict.values()):  # Solo crear si tiene valores
                resolucion = ModuloEmpresa(**res_dict)
        
        documento = None
        if empresa_data.documento:
            doc_dict = empresa_data.documento.dict()
            if any(doc_dict.values()):  # Solo crear si tiene valores
                documento = ModuloEmpresa(**doc_dict)
        
        # Crear empresa con el ID existente
        empresa = Empresa(
            id=empresa_id,
            nit=empresa_data.nit,
            nombre=empresa_data.nombre,
            tipo=empresa_data.tipo,
            estado=empresa_data.estado,
            certificado=certificado,
            resolucion=resolucion,
            documento=documento
        )
        
        resultado = empresa_service.actualizar_empresa(empresa)
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado.get('error'))
        return normalize_response(resultado)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@empresas_router.patch("/{nit}/modulo")
async def actualizar_estado_modulo(
    nit: str = Path(..., description="NIT de la empresa"),
    datos: ActualizarModuloRequest = Body(...)
):
    """
    Actualiza el estado de un módulo específico
    
    - **modulo**: certificado, resolucion o documento
    - **campo**: renovado o facturado
    - **valor**: 0 o 1
    """
    resultado = empresa_service.actualizar_estado_modulo(
        nit, datos.modulo, datos.campo, datos.valor
    )
    if not resultado['success']:
        raise HTTPException(status_code=400, detail=resultado.get('error'))
    return resultado


@empresas_router.delete("/{nit}")
async def eliminar_empresa(nit: str = Path(..., description="NIT de la empresa")):
    """Desactiva una empresa (soft delete)"""
    # Primero obtener la empresa para conseguir su ID
    resultado_empresa = empresa_service.obtener_empresa_por_nit(nit)
    if not resultado_empresa['success']:
        raise HTTPException(status_code=404, detail=resultado_empresa.get('error'))
    
    # El servicio devuelve 'data', no 'datos'
    empresa_id = resultado_empresa.get('data', {}).get('id')
    if not empresa_id:
        raise HTTPException(status_code=404, detail="No se pudo obtener el ID de la empresa")
    
    resultado = empresa_service.eliminar_empresa(empresa_id)
    if not resultado['success']:
        raise HTTPException(status_code=404, detail=resultado.get('error'))
    return resultado


# ========================================
# RUTAS DE ESTADÍSTICAS
# ========================================

@estadisticas_router.get("/resumen")
async def obtener_resumen():
    """Obtiene resumen general del sistema"""
    resultado = stats_service.obtener_estadisticas_generales()
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    
    stats = resultado.get('data', {})
    
    # Calcular totales
    total_empresas = stats.get('total_empresas', 0)
    empresas_activas = total_empresas  # Todas son activas por el filtro
    
    cert = stats.get('certificados', {})
    res = stats.get('resoluciones', {})
    doc = stats.get('documentos', {})
    
    # Obtener estadísticas de vencimientos para alertas críticas
    venc_cert = stats_service.obtener_estadisticas_vencimientos_certificados()
    venc_res = stats_service.obtener_estadisticas_vencimientos_resoluciones()
    venc_doc = stats_service.obtener_estadisticas_vencimientos_documentos()
    
    # Calcular alertas críticas (vencidos + por vencer)
    alertas_criticas = 0
    if venc_cert['success']:
        alertas_criticas += venc_cert['data'].get('vencidos', 0) + venc_cert['data'].get('por_vencer', 0)
    if venc_res['success']:
        alertas_criticas += venc_res['data'].get('vencidos', 0) + venc_res['data'].get('por_vencer', 0)
    if venc_doc['success']:
        alertas_criticas += venc_doc['data'].get('vencidos', 0) + venc_doc['data'].get('por_vencer', 0)
    
    return {
        'success': True,
        'datos': {
            'total_empresas': total_empresas,
            'empresas_activas': empresas_activas,
            'total_certificados': cert.get('activos', 0),
            'total_resoluciones': res.get('activos', 0),
            'total_documentos': doc.get('activos', 0),
            'alertas_criticas': alertas_criticas,
            'certificados': cert,
            'resoluciones': res,
            'documentos': doc
        }
    }


@estadisticas_router.get("/por-estado")
async def obtener_por_estado():
    """Obtiene distribución de empresas por estado"""
    # Obtener todas las empresas activas y contar por estado
    empresas = empresa_service.obtener_empresas_activas()
    if not empresas['success']:
        raise HTTPException(status_code=500, detail=empresas.get('error'))
    
    # Contar por estado
    estados = {}
    for emp in empresas.get('data', []):
        estado = emp.get('estado', 'inactivo')
        estados[estado] = estados.get(estado, 0) + 1
    
    return {
        'success': True,
        'datos': estados
    }


@estadisticas_router.get("/certificados")
async def obtener_certificados():
    """Obtiene estadísticas de certificados con información de vencimientos"""
    # Obtener estadísticas generales
    resultado_general = stats_service.obtener_estadisticas_generales()
    if not resultado_general['success']:
        raise HTTPException(status_code=500, detail=resultado_general.get('error'))
    
    cert_stats = resultado_general.get('data', {}).get('certificados', {})
    
    # Obtener estadísticas de vencimientos basadas en fechas
    resultado_vencimientos = stats_service.obtener_estadisticas_vencimientos_certificados()
    if not resultado_vencimientos['success']:
        raise HTTPException(status_code=500, detail=resultado_vencimientos.get('error'))
    
    vencimientos = resultado_vencimientos.get('data', {})
    
    return {
        'success': True,
        'datos': {
            **cert_stats,
            'vencidos': vencimientos.get('vencidos', 0),
            'por_vencer': vencimientos.get('por_vencer', 0),
            'vigentes': vencimientos.get('vigentes', 0)
        }
    }


@estadisticas_router.get("/resoluciones")
async def obtener_resoluciones():
    """Obtiene estadísticas de resoluciones con información de vencimientos"""
    # Obtener estadísticas generales
    resultado_general = stats_service.obtener_estadisticas_generales()
    if not resultado_general['success']:
        raise HTTPException(status_code=500, detail=resultado_general.get('error'))
    
    res_stats = resultado_general.get('data', {}).get('resoluciones', {})
    
    # Obtener estadísticas de vencimientos basadas en fechas
    resultado_vencimientos = stats_service.obtener_estadisticas_vencimientos_resoluciones()
    if not resultado_vencimientos['success']:
        raise HTTPException(status_code=500, detail=resultado_vencimientos.get('error'))
    
    vencimientos = resultado_vencimientos.get('data', {})
    
    return {
        'success': True,
        'datos': {
            **res_stats,
            'vencidos': vencimientos.get('vencidos', 0),
            'por_vencer': vencimientos.get('por_vencer', 0),
            'vigentes': vencimientos.get('vigentes', 0)
        }
    }


@estadisticas_router.get("/documentos")
async def obtener_documentos():
    """Obtiene estadísticas de documentos con información de vencimientos"""
    # Obtener estadísticas generales
    resultado_general = stats_service.obtener_estadisticas_generales()
    if not resultado_general['success']:
        raise HTTPException(status_code=500, detail=resultado_general.get('error'))
    
    doc_stats = resultado_general.get('data', {}).get('documentos', {})
    
    # Obtener estadísticas de vencimientos basadas en fechas
    resultado_vencimientos = stats_service.obtener_estadisticas_vencimientos_documentos()
    if not resultado_vencimientos['success']:
        raise HTTPException(status_code=500, detail=resultado_vencimientos.get('error'))
    
    vencimientos = resultado_vencimientos.get('data', {})
    
    return {
        'success': True,
        'datos': {
            **doc_stats,
            'vencidos': vencimientos.get('vencidos', 0),
            'por_vencer': vencimientos.get('por_vencer', 0),
            'vigentes': vencimientos.get('vigentes', 0)
        }
    }


@estadisticas_router.get("/pendientes")
async def obtener_pendientes():
    """Obtiene empresas con pendientes de renovación o facturación"""
    resultado = stats_service.obtener_empresas_pendientes()
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    return resultado


# ========================================
# RUTAS DE NOTIFICACIONES
# ========================================

@notificaciones_router.get("/vencimientos")
async def obtener_vencimientos(
    dias: int = Query(30, ge=1, le=365, description="Días de anticipación")
):
    """Obtiene notificaciones de vencimientos próximos"""
    resultado = notif_service.obtener_notificaciones_pendientes(dias)
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    return normalize_response(resultado)


@notificaciones_router.get("/criticas")
async def obtener_criticas():
    """Obtiene notificaciones críticas (próximas a vencer en 7 días)"""
    resultado = notif_service.obtener_notificaciones_pendientes(7)
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    return normalize_response(resultado)


@notificaciones_router.get("/conteo")
async def obtener_conteo():
    """Obtiene el conteo de notificaciones por prioridad"""
    resultado = notif_service.obtener_notificaciones_pendientes(30)
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    
    # Aplanar alertas para contar por prioridad
    datos = resultado.get('data', [])
    alertas_flat = []
    for notif in datos:
        for alerta in notif.get('alertas', []):
            alertas_flat.append(alerta)
    
    conteo = {
        'CRITICA': sum(1 for a in alertas_flat if a.get('prioridad') == 'CRITICA'),
        'ALTA': sum(1 for a in alertas_flat if a.get('prioridad') == 'ALTA'),
        'MEDIA': sum(1 for a in alertas_flat if a.get('prioridad') == 'MEDIA'),
        'total': len(alertas_flat)
    }
    
    return {
        'success': True,
        'datos': conteo
    }


@notificaciones_router.get("/mes-actual")
async def obtener_vencimientos_mes():
    """Obtiene vencimientos del mes actual"""
    resultado = notif_service.obtener_vencimientos_mes_actual()
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    return normalize_response(resultado)


# ========================================
# RUTAS DE EMAIL
# ========================================

@email_router.post("/enviar-notificaciones")
async def enviar_notificaciones_email(
    destinatarios: list[str] = Body(..., description="Lista de emails destino")
):
    """
    Envía las notificaciones pendientes por email
    
    Args:
        destinatarios: Lista de direcciones de email
        
    Returns:
        Resultado del envío
    """
    if not email_service:
        raise HTTPException(
            status_code=503, 
            detail="Servicio de email no disponible"
        )
    
    # Obtener notificaciones pendientes
    resultado_notif = notif_service.obtener_notificaciones_pendientes()
    if not resultado_notif['success']:
        raise HTTPException(
            status_code=500, 
            detail=resultado_notif.get('error')
        )
    
    notificaciones = resultado_notif.get('data', [])
    
    # Enviar email
    resultado = email_service.enviar_notificaciones_vencimientos(
        destinatarios, 
        notificaciones
    )
    
    if not resultado['success']:
        raise HTTPException(
            status_code=500, 
            detail=resultado.get('error')
        )
    
    return {
        'success': True,
        'datos': resultado
    }


@email_router.post("/enviar-simple")
async def enviar_email_simple(
    destinatario: str = Body(..., description="Email destino"),
    asunto: str = Body(..., description="Asunto del email"),
    mensaje: str = Body(..., description="Contenido del mensaje")
):
    """
    Envía un email simple
    
    Args:
        destinatario: Email destino
        asunto: Asunto del email
        mensaje: Contenido del mensaje
        
    Returns:
        Resultado del envío
    """
    if not email_service:
        raise HTTPException(
            status_code=503, 
            detail="Servicio de email no disponible"
        )
    
    resultado = email_service.enviar_email_simple(
        destinatario, 
        asunto, 
        mensaje
    )
    
    if not resultado['success']:
        raise HTTPException(
            status_code=500, 
            detail=resultado.get('error')
        )
    
    return {
        'success': True,
        'datos': resultado
    }


@email_router.get("/configurado")
async def verificar_configuracion():
    """
    Verifica si el servicio de email está configurado
    
    Returns:
        Estado de la configuración
    """
    if not email_service:
        return {
            'success': False,
            'configurado': False,
            'mensaje': 'Servicio no inicializado'
        }
    
    configurado = bool(email_service.smtp_user and email_service.smtp_password)
    
    return {
        'success': True,
        'configurado': configurado,
        'smtp_user': email_service.smtp_user if configurado else None,
        'mensaje': 'Configurado correctamente' if configurado else 'Faltan credenciales SMTP'
    }


# ========================================
# RUTAS DE TRIGGERS
# ========================================

@triggers_router.get("")
async def obtener_triggers():
    """
    Obtiene todos los triggers configurados
    
    Returns:
        Lista de triggers
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.obtener_triggers()
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    
    return normalize_response(resultado)


@triggers_router.get("/{trigger_id}")
async def obtener_trigger(trigger_id: int):
    """
    Obtiene un trigger por ID
    
    Args:
        trigger_id: ID del trigger
        
    Returns:
        Trigger encontrado
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.obtener_trigger(trigger_id)
    if not resultado['success']:
        raise HTTPException(status_code=404, detail=resultado.get('error'))
    
    return normalize_response(resultado)


@triggers_router.post("")
async def crear_trigger(datos: Dict[str, Any] = Body(...)):
    """
    Crea un nuevo trigger
    
    Args:
        datos: Datos del trigger
        
    Returns:
        Trigger creado
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.crear_trigger(datos)
    if not resultado['success']:
        raise HTTPException(status_code=400, detail=resultado.get('error'))
    
    # Recargar scheduler con el nuevo trigger
    try:
        from app.services.scheduler_service import get_scheduler
        get_scheduler().reload_triggers()
    except Exception as e:
        print(f"Advertencia: No se pudo recargar scheduler: {e}")
    
    return normalize_response(resultado)


@triggers_router.put("/{trigger_id}")
async def actualizar_trigger(trigger_id: int, datos: Dict[str, Any] = Body(...)):
    """
    Actualiza un trigger existente
    
    Args:
        trigger_id: ID del trigger
        datos: Datos a actualizar
        
    Returns:
        Trigger actualizado
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.actualizar_trigger(trigger_id, datos)
    if not resultado['success']:
        raise HTTPException(status_code=400, detail=resultado.get('error'))
    
    # Recargar scheduler con los cambios
    try:
        from app.services.scheduler_service import get_scheduler
        get_scheduler().reload_triggers()
    except Exception as e:
        print(f"Advertencia: No se pudo recargar scheduler: {e}")
    
    return normalize_response(resultado)


@triggers_router.delete("/{trigger_id}")
async def eliminar_trigger(trigger_id: int):
    """
    Elimina un trigger
    
    Args:
        trigger_id: ID del trigger
        
    Returns:
        Resultado de la eliminación
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.eliminar_trigger(trigger_id)
    if not resultado['success']:
        raise HTTPException(status_code=404, detail=resultado.get('error'))
    
    # Recargar scheduler después de eliminar
    try:
        from app.services.scheduler_service import get_scheduler
        get_scheduler().reload_triggers()
    except Exception as e:
        print(f"Advertencia: No se pudo recargar scheduler: {e}")
    
    return normalize_response(resultado)


@triggers_router.patch("/{trigger_id}/estado")
async def cambiar_estado_trigger(
    trigger_id: int,
    activo: bool = Body(..., embed=True)
):
    """
    Activa o desactiva un trigger
    
    Args:
        trigger_id: ID del trigger
        activo: Nuevo estado (true/false)
        
    Returns:
        Trigger actualizado
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.cambiar_estado(trigger_id, activo)
    if not resultado['success']:
        raise HTTPException(status_code=400, detail=resultado.get('error'))
    
    # Recargar scheduler al cambiar estado
    try:
        from app.services.scheduler_service import get_scheduler
        get_scheduler().reload_triggers()
    except Exception as e:
        print(f"Advertencia: No se pudo recargar scheduler: {e}")
    
    return normalize_response(resultado)


@triggers_router.get("/pendientes/ejecutar")
async def obtener_triggers_pendientes():
    """
    Obtiene triggers que deben ejecutarse ahora
    
    Returns:
        Lista de triggers pendientes
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.obtener_triggers_pendientes()
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    
    return normalize_response(resultado)


# ========================================
# RUTAS DE HISTORIAL DE EJECUCIONES
# ========================================

@triggers_router.get("/ejecuciones")
async def obtener_todas_ejecuciones(
    limit: int = Query(default=100, ge=1, le=500, description="Número máximo de registros")
):
    """
    Obtiene todas las ejecuciones de todos los triggers
    
    Args:
        limit: Número máximo de registros a retornar (default: 100, max: 500)
        
    Returns:
        Lista de ejecuciones ordenadas por fecha descendente
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.obtener_todas_ejecuciones(limit)
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    
    return normalize_response(resultado)


@triggers_router.get("/{trigger_id}/ejecuciones")
async def obtener_historial_trigger(
    trigger_id: int = Path(..., description="ID del trigger"),
    limit: int = Query(default=50, ge=1, le=200, description="Número máximo de registros")
):
    """
    Obtiene el historial de ejecuciones de un trigger específico
    
    Args:
        trigger_id: ID del trigger
        limit: Número máximo de registros a retornar (default: 50, max: 200)
        
    Returns:
        Lista de ejecuciones del trigger ordenadas por fecha descendente
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.obtener_historial_trigger(trigger_id, limit)
    if not resultado['success']:
        raise HTTPException(status_code=500, detail=resultado.get('error'))
    
    return normalize_response(resultado)


@triggers_router.get("/{trigger_id}/estadisticas")
async def obtener_estadisticas_trigger(
    trigger_id: int = Path(..., description="ID del trigger")
):
    """
    Obtiene estadísticas de ejecución de un trigger
    
    Args:
        trigger_id: ID del trigger
        
    Returns:
        Estadísticas del trigger (total ejecuciones, tasa de éxito, etc.)
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.obtener_estadisticas_trigger(trigger_id)
    if not resultado['success']:
        raise HTTPException(status_code=404, detail=resultado.get('error'))
    
    return normalize_response(resultado)


@triggers_router.post("/ejecuciones")
async def registrar_ejecucion(datos: Dict[str, Any] = Body(...)):
    """
    Registra una nueva ejecución de un trigger
    
    Args:
        datos: Información de la ejecución:
            - trigger_id: ID del trigger (requerido)
            - estado: 'exitoso' o 'fallido' (default: 'exitoso')
            - notificaciones_enviadas: Número de notificaciones enviadas
            - empresas_procesadas: Número de empresas procesadas
            - error_mensaje: Mensaje de error (si aplica)
            - detalles: Información adicional en JSON
            
    Returns:
        Ejecución registrada
    """
    if not trigger_service:
        raise HTTPException(
            status_code=503,
            detail="Servicio de triggers no disponible"
        )
    
    resultado = trigger_service.registrar_ejecucion(datos)
    if not resultado['success']:
        raise HTTPException(status_code=400, detail=resultado.get('error'))
    
    return normalize_response(resultado)


# ========================================
# RUTAS DE CONTROL DEL SCHEDULER
# ========================================

@triggers_router.get("/scheduler/status")
async def obtener_estado_scheduler():
    """
    Obtiene el estado del scheduler automático
    
    Returns:
        Estado del scheduler y lista de jobs programados
    """
    try:
        from app.services.scheduler_service import get_scheduler
        scheduler = get_scheduler()
        status = scheduler.get_status()
        
        return {
            'success': True,
            'datos': status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@triggers_router.post("/scheduler/reload")
async def recargar_scheduler():
    """
    Recarga todos los triggers en el scheduler
    Útil después de crear, actualizar o eliminar triggers
    
    Returns:
        Confirmación de recarga
    """
    try:
        from app.services.scheduler_service import get_scheduler
        scheduler = get_scheduler()
        scheduler.reload_triggers()
        
        return {
            'success': True,
            'message': 'Scheduler recargado exitosamente',
            'datos': scheduler.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


 
