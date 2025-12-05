"""
Repositorio SQLite para la entidad Empresa
Implementación concreta usando SQLite
"""
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.empresa import Empresa, ModuloEmpresa
from app.repositories.base_repository import IRepository


class EmpresaRepository(IRepository):
    """
    Repositorio para gestionar empresas en SQLite.
    Esta clase puede ser reemplazada por MySQLEmpresaRepository sin cambiar el resto del código.
    """

    def __init__(self, db_path: str):
        """
        Inicializa el repositorio con la ruta de la base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Crea una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
        return conn

    def _calcular_notificacion(self, fecha_vencimiento: Optional[datetime]) -> Optional[str]:
        """Calcula la fecha de notificación (30 días antes del vencimiento)"""
        if not fecha_vencimiento:
            return None
        from datetime import timedelta
        fecha_notif = fecha_vencimiento - timedelta(days=30)
        return fecha_notif.isoformat()

    def _init_tables(self):
        """Crea las tablas si no existen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nit TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'activo',
                
                -- Certificado de Facturación Electrónica
                cert_activo INTEGER DEFAULT 0,
                cert_fecha_inicio TEXT,
                cert_fecha_final TEXT,
                cert_notificacion TEXT,
                cert_renovado INTEGER DEFAULT 0,
                cert_facturado INTEGER DEFAULT 0,
                cert_comentarios TEXT,
                
                -- Resolución de Facturación
                resol_activo INTEGER DEFAULT 0,
                resol_fecha_inicio TEXT,
                resol_fecha_final TEXT,
                resol_notificacion TEXT,
                resol_renovado INTEGER DEFAULT 0,
                resol_facturado INTEGER DEFAULT 0,
                resol_comentarios TEXT,
                
                -- Resolución Documentos Soporte
                doc_activo INTEGER DEFAULT 0,
                doc_fecha_inicio TEXT,
                doc_fecha_final TEXT,
                doc_notificacion TEXT,
                doc_renovado INTEGER DEFAULT 0,
                doc_facturado INTEGER DEFAULT 0,
                doc_comentarios TEXT,
                
                -- Metadatos
                fecha_creacion TEXT NOT NULL,
                fecha_actualizacion TEXT NOT NULL
            )
        ''')
        
        # Índices para mejorar el rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nit ON empresas(nit)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_estado ON empresas(estado)')
        
        conn.commit()
        conn.close()

    def _row_to_empresa(self, row: sqlite3.Row) -> Empresa:
        """Convierte una fila de base de datos a un objeto Empresa"""
        def parse_date(date_str: Optional[str]) -> Optional[datetime]:
            if date_str:
                try:
                    return datetime.fromisoformat(date_str)
                except ValueError:
                    return None
            return None

        certificado = ModuloEmpresa(
            activo=row['cert_activo'],
            fecha_inicio=parse_date(row['cert_fecha_inicio']),
            fecha_final=parse_date(row['cert_fecha_final']),
            notificacion=row['cert_notificacion'],
            renovado=row['cert_renovado'],
            facturado=row['cert_facturado'],
            comentarios=row['cert_comentarios']
        )

        resolucion = ModuloEmpresa(
            activo=row['resol_activo'],
            fecha_inicio=parse_date(row['resol_fecha_inicio']),
            fecha_final=parse_date(row['resol_fecha_final']),
            notificacion=row['resol_notificacion'],
            renovado=row['resol_renovado'],
            facturado=row['resol_facturado'],
            comentarios=row['resol_comentarios']
        )

        documento = ModuloEmpresa(
            activo=row['doc_activo'],
            fecha_inicio=parse_date(row['doc_fecha_inicio']),
            fecha_final=parse_date(row['doc_fecha_final']),
            notificacion=row['doc_notificacion'],
            renovado=row['doc_renovado'],
            facturado=row['doc_facturado'],
            comentarios=row['doc_comentarios']
        )

        return Empresa(
            id=row['id'],
            nit=row['nit'],
            nombre=row['nombre'],
            tipo=row['tipo'],
            estado=row['estado'],
            certificado=certificado,
            resolucion=resolucion,
            documento=documento,
            fecha_creacion=parse_date(row['fecha_creacion']),
            fecha_actualizacion=parse_date(row['fecha_actualizacion'])
        )

    def create(self, empresa: Empresa) -> Empresa:
        """Crea una nueva empresa en la base de datos"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        empresa.fecha_creacion = datetime.fromisoformat(now)
        empresa.fecha_actualizacion = datetime.fromisoformat(now)
        
        # Calcular notificaciones automáticamente (30 días antes)
        if empresa.certificado.fecha_final:
            empresa.certificado.notificacion = self._calcular_notificacion(empresa.certificado.fecha_final)
        if empresa.resolucion.fecha_final:
            empresa.resolucion.notificacion = self._calcular_notificacion(empresa.resolucion.fecha_final)
        if empresa.documento.fecha_final:
            empresa.documento.notificacion = self._calcular_notificacion(empresa.documento.fecha_final)
        
        cursor.execute('''
            INSERT INTO empresas (
                nit, nombre, tipo, estado,
                cert_activo, cert_fecha_inicio, cert_fecha_final, cert_notificacion,
                cert_renovado, cert_facturado, cert_comentarios,
                resol_activo, resol_fecha_inicio, resol_fecha_final, resol_notificacion,
                resol_renovado, resol_facturado, resol_comentarios,
                doc_activo, doc_fecha_inicio, doc_fecha_final, doc_notificacion,
                doc_renovado, doc_facturado, doc_comentarios,
                fecha_creacion, fecha_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            empresa.nit, empresa.nombre, empresa.tipo, empresa.estado,
            empresa.certificado.activo,
            empresa.certificado.fecha_inicio.isoformat() if empresa.certificado.fecha_inicio else None,
            empresa.certificado.fecha_final.isoformat() if empresa.certificado.fecha_final else None,
            empresa.certificado.notificacion,
            empresa.certificado.renovado, empresa.certificado.facturado, empresa.certificado.comentarios,
            empresa.resolucion.activo,
            empresa.resolucion.fecha_inicio.isoformat() if empresa.resolucion.fecha_inicio else None,
            empresa.resolucion.fecha_final.isoformat() if empresa.resolucion.fecha_final else None,
            empresa.resolucion.notificacion,
            empresa.resolucion.renovado, empresa.resolucion.facturado, empresa.resolucion.comentarios,
            empresa.documento.activo,
            empresa.documento.fecha_inicio.isoformat() if empresa.documento.fecha_inicio else None,
            empresa.documento.fecha_final.isoformat() if empresa.documento.fecha_final else None,
            empresa.documento.notificacion,
            empresa.documento.renovado, empresa.documento.facturado, empresa.documento.comentarios,
            now, now
        ))
        
        empresa.id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return empresa

    def get_by_id(self, entity_id: int) -> Optional[Empresa]:
        """Obtiene una empresa por su ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM empresas WHERE id = ?', (entity_id,))
        row = cursor.fetchone()
        conn.close()
        
        return self._row_to_empresa(row) if row else None

    def get_by_nit(self, nit: str) -> Optional[Empresa]:
        """Obtiene una empresa por su NIT"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM empresas WHERE nit = ?', (nit,))
        row = cursor.fetchone()
        conn.close()
        
        return self._row_to_empresa(row) if row else None

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Empresa]:
        """Obtiene todas las empresas con filtros opcionales"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM empresas WHERE 1=1'
        params = []
        
        if filters:
            if 'estado' in filters:
                query += ' AND estado = ?'
                params.append(filters['estado'])
            
            if 'activos_solamente' in filters and filters['activos_solamente']:
                query += ' AND (cert_activo = 1 OR resol_activo = 1 OR doc_activo = 1)'
        
        query += ' ORDER BY nombre'
        
        # print(query)  # Debugging line
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        
        # for row in rows:
        #     print(row)  # Debugging line to check fetched rows
        
        return [self._row_to_empresa(row) for row in rows]

    def update(self, empresa: Empresa) -> bool:
        """Actualiza una empresa existente"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        empresa.fecha_actualizacion = datetime.now()
        
        # Manejar módulos opcionales con valores por defecto
        cert = empresa.certificado if empresa.certificado else ModuloEmpresa()
        resol = empresa.resolucion if empresa.resolucion else ModuloEmpresa()
        doc = empresa.documento if empresa.documento else ModuloEmpresa()
        
        # Calcular notificaciones automáticamente (30 días antes)
        if cert.fecha_final:
            cert.notificacion = self._calcular_notificacion(cert.fecha_final)
        if resol.fecha_final:
            resol.notificacion = self._calcular_notificacion(resol.fecha_final)
        if doc.fecha_final:
            doc.notificacion = self._calcular_notificacion(doc.fecha_final)
        
        cursor.execute('''
            UPDATE empresas SET
                nombre = ?, tipo = ?, estado = ?,
                cert_activo = ?, cert_fecha_inicio = ?, cert_fecha_final = ?,
                cert_notificacion = ?, cert_renovado = ?, cert_facturado = ?,
                cert_comentarios = ?,
                resol_activo = ?, resol_fecha_inicio = ?, resol_fecha_final = ?,
                resol_notificacion = ?, resol_renovado = ?, resol_facturado = ?,
                resol_comentarios = ?,
                doc_activo = ?, doc_fecha_inicio = ?, doc_fecha_final = ?,
                doc_notificacion = ?, doc_renovado = ?, doc_facturado = ?,
                doc_comentarios = ?,
                fecha_actualizacion = ?
            WHERE id = ?
        ''', (
            empresa.nombre, empresa.tipo, empresa.estado,
            cert.activo,
            cert.fecha_inicio.isoformat() if cert.fecha_inicio else None,
            cert.fecha_final.isoformat() if cert.fecha_final else None,
            cert.notificacion,
            cert.renovado, cert.facturado, cert.comentarios,
            resol.activo,
            resol.fecha_inicio.isoformat() if resol.fecha_inicio else None,
            resol.fecha_final.isoformat() if resol.fecha_final else None,
            resol.notificacion,
            resol.renovado, resol.facturado, resol.comentarios,
            doc.activo,
            doc.fecha_inicio.isoformat() if doc.fecha_inicio else None,
            doc.fecha_final.isoformat() if doc.fecha_final else None,
            doc.notificacion,
            doc.renovado, doc.facturado, doc.comentarios,
            empresa.fecha_actualizacion.isoformat(),
            empresa.id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success

    def update_field(self, nit: str, modulo: str, campo: str, valor: Any) -> bool:
        """
        Actualiza un campo específico de un módulo de una empresa
        
        Args:
            nit: NIT de la empresa
            modulo: 'certificado', 'resolucion' o 'documento'
            campo: 'renovado' o 'facturado'
            valor: Nuevo valor (0 o 1)
        """
        prefijos = {
            'certificado': 'cert',
            'resolucion': 'resol',
            'documento': 'doc'
        }
        
        if modulo not in prefijos or campo not in ['renovado', 'facturado', 'activo']:
            return False
        
        prefijo = prefijos[modulo]
        columna = f"{prefijo}_{campo}"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        query = f'UPDATE empresas SET {columna} = ?, fecha_actualizacion = ? WHERE nit = ?'
        
        cursor.execute(query, (valor, now, nit))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success

    def delete(self, entity_id: int) -> bool:
        """Elimina una empresa por su ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM empresas WHERE id = ?', (entity_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success

    def exists(self, entity_id: int) -> bool:
        """Verifica si existe una empresa con el ID dado"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM empresas WHERE id = ? LIMIT 1', (entity_id,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists

    def exists_by_nit(self, nit: str) -> bool:
        """Verifica si existe una empresa con el NIT dado"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM empresas WHERE nit = ? LIMIT 1', (nit,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
