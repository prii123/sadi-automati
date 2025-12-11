"""
Repositorio PostgreSQL para la entidad Empresa
Implementación concreta usando PostgreSQL
"""
import psycopg2
import psycopg2.extras
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.empresa import Empresa, ModuloEmpresa
from app.repositories.base_repository import IRepository


class PostgreSQLEmpresaRepository(IRepository):
    """
    Repositorio para gestionar empresas en PostgreSQL.
    Esta clase es compatible con IRepository y puede reemplazar a EmpresaRepository.
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
        self._init_tables()

    def _get_connection(self):
        """Crea una conexión a la base de datos PostgreSQL"""
        return psycopg2.connect(**self.connection_params)

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
                id SERIAL PRIMARY KEY,
                nit TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'activo',
                
                -- Certificado de Facturación Electrónica
                cert_activo INTEGER DEFAULT 0,
                cert_fecha_inicio TIMESTAMP,
                cert_fecha_final TIMESTAMP,
                cert_notificacion TEXT,
                cert_renovado INTEGER DEFAULT 0,
                cert_facturado INTEGER DEFAULT 0,
                cert_comentarios TEXT,
                
                -- Resolución de Facturación
                resol_activo INTEGER DEFAULT 0,
                resol_fecha_inicio TIMESTAMP,
                resol_fecha_final TIMESTAMP,
                resol_notificacion TEXT,
                resol_renovado INTEGER DEFAULT 0,
                resol_facturado INTEGER DEFAULT 0,
                resol_comentarios TEXT,
                
                -- Resolución Documentos Soporte
                doc_activo INTEGER DEFAULT 0,
                doc_fecha_inicio TIMESTAMP,
                doc_fecha_final TIMESTAMP,
                doc_notificacion TEXT,
                doc_renovado INTEGER DEFAULT 0,
                doc_facturado INTEGER DEFAULT 0,
                doc_comentarios TEXT,
                
                -- Metadatos
                fecha_creacion TIMESTAMP NOT NULL,
                fecha_actualizacion TIMESTAMP NOT NULL
            )
        ''')
        
        # Índices para mejorar el rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nit ON empresas(nit)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_estado ON empresas(estado)')
        
        conn.commit()
        cursor.close()
        conn.close()

    def _row_to_empresa(self, row: tuple) -> Empresa:
        """Convierte una fila de base de datos a un objeto Empresa"""
        def parse_date(date_value) -> Optional[datetime]:
            if date_value:
                if isinstance(date_value, datetime):
                    return date_value
                try:
                    return datetime.fromisoformat(str(date_value))
                except ValueError:
                    return None
            return None

        certificado = ModuloEmpresa(
            activo=row[5],  # cert_activo
            fecha_inicio=parse_date(row[6]),  # cert_fecha_inicio
            fecha_final=parse_date(row[7]),  # cert_fecha_final
            notificacion=row[8],  # cert_notificacion
            renovado=row[9],  # cert_renovado
            facturado=row[10],  # cert_facturado
            comentarios=row[11]  # cert_comentarios
        )

        resolucion = ModuloEmpresa(
            activo=row[12],  # resol_activo
            fecha_inicio=parse_date(row[13]),  # resol_fecha_inicio
            fecha_final=parse_date(row[14]),  # resol_fecha_final
            notificacion=row[15],  # resol_notificacion
            renovado=row[16],  # resol_renovado
            facturado=row[17],  # resol_facturado
            comentarios=row[18]  # resol_comentarios
        )

        documento = ModuloEmpresa(
            activo=row[19],  # doc_activo
            fecha_inicio=parse_date(row[20]),  # doc_fecha_inicio
            fecha_final=parse_date(row[21]),  # doc_fecha_final
            notificacion=row[22],  # doc_notificacion
            renovado=row[23],  # doc_renovado
            facturado=row[24],  # doc_facturado
            comentarios=row[25]  # doc_comentarios
        )

        return Empresa(
            id=row[0],
            nit=row[1],
            nombre=row[2],
            tipo=row[3],
            estado=row[4],
            certificado=certificado,
            resolucion=resolucion,
            documento=documento,
            fecha_creacion=parse_date(row[26]),
            fecha_actualizacion=parse_date(row[27])
        )

    def create(self, empresa: Empresa) -> Empresa:
        """Crea una nueva empresa en la base de datos"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        empresa.fecha_creacion = now
        empresa.fecha_actualizacion = now
        
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
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            empresa.nit, empresa.nombre, empresa.tipo, empresa.estado,
            empresa.certificado.activo,
            empresa.certificado.fecha_inicio,
            empresa.certificado.fecha_final,
            empresa.certificado.notificacion,
            empresa.certificado.renovado, empresa.certificado.facturado, empresa.certificado.comentarios,
            empresa.resolucion.activo,
            empresa.resolucion.fecha_inicio,
            empresa.resolucion.fecha_final,
            empresa.resolucion.notificacion,
            empresa.resolucion.renovado, empresa.resolucion.facturado, empresa.resolucion.comentarios,
            empresa.documento.activo,
            empresa.documento.fecha_inicio,
            empresa.documento.fecha_final,
            empresa.documento.notificacion,
            empresa.documento.renovado, empresa.documento.facturado, empresa.documento.comentarios,
            now, now
        ))
        
        empresa.id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return empresa

    def get_by_id(self, entity_id: int) -> Optional[Empresa]:
        """Obtiene una empresa por su ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM empresas WHERE id = %s', (entity_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return self._row_to_empresa(row) if row else None

    def get_by_nit(self, nit: str) -> Optional[Empresa]:
        """Obtiene una empresa por su NIT"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM empresas WHERE nit = %s', (nit,))
        row = cursor.fetchone()
        cursor.close()
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
                query += ' AND estado = %s'
                params.append(filters['estado'])
            
            if 'activos_solamente' in filters and filters['activos_solamente']:
                query += ' AND (cert_activo = 1 OR resol_activo = 1 OR doc_activo = 1)'
        
        query += ' ORDER BY nombre'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
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
                nombre = %s, tipo = %s, estado = %s,
                cert_activo = %s, cert_fecha_inicio = %s, cert_fecha_final = %s,
                cert_notificacion = %s, cert_renovado = %s, cert_facturado = %s,
                cert_comentarios = %s,
                resol_activo = %s, resol_fecha_inicio = %s, resol_fecha_final = %s,
                resol_notificacion = %s, resol_renovado = %s, resol_facturado = %s,
                resol_comentarios = %s,
                doc_activo = %s, doc_fecha_inicio = %s, doc_fecha_final = %s,
                doc_notificacion = %s, doc_renovado = %s, doc_facturado = %s,
                doc_comentarios = %s,
                fecha_actualizacion = %s
            WHERE id = %s
        ''', (
            empresa.nombre, empresa.tipo, empresa.estado,
            cert.activo,
            cert.fecha_inicio,
            cert.fecha_final,
            cert.notificacion,
            cert.renovado, cert.facturado, cert.comentarios,
            resol.activo,
            resol.fecha_inicio,
            resol.fecha_final,
            resol.notificacion,
            resol.renovado, resol.facturado, resol.comentarios,
            doc.activo,
            doc.fecha_inicio,
            doc.fecha_final,
            doc.notificacion,
            doc.renovado, doc.facturado, doc.comentarios,
            empresa.fecha_actualizacion,
            empresa.id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
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
        
        now = datetime.now()
        query = f'UPDATE empresas SET {columna} = %s, fecha_actualizacion = %s WHERE nit = %s'
        
        cursor.execute(query, (valor, now, nit))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success

    def delete(self, entity_id: int) -> bool:
        """Elimina una empresa por su ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM empresas WHERE id = %s', (entity_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success

    def exists(self, entity_id: int) -> bool:
        """Verifica si existe una empresa con el ID dado"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM empresas WHERE id = %s LIMIT 1', (entity_id,))
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        return exists

    def exists_by_nit(self, nit: str) -> bool:
        """Verifica si existe una empresa con el NIT dado"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM empresas WHERE nit = %s LIMIT 1', (nit,))
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        return exists
