"""
Script para migrar datos de SQLite a PostgreSQL
Ejecutar este script para transferir todos los datos existentes
"""
import sqlite3
import psycopg2
import os
from datetime import datetime
from typing import Optional


class MigracionSQLiteAPostgreSQL:
    """Clase para manejar la migración de datos de SQLite a PostgreSQL"""
    
    def __init__(self, 
                 sqlite_path: str,
                 pg_host: str,
                 pg_port: int,
                 pg_database: str,
                 pg_user: str,
                 pg_password: str):
        """
        Inicializa el migrador
        
        Args:
            sqlite_path: Ruta al archivo SQLite
            pg_host: Host de PostgreSQL
            pg_port: Puerto de PostgreSQL
            pg_database: Nombre de la base de datos PostgreSQL
            pg_user: Usuario de PostgreSQL
            pg_password: Contraseña de PostgreSQL
        """
        self.sqlite_path = sqlite_path
        self.pg_params = {
            'host': pg_host,
            'port': pg_port,
            'database': pg_database,
            'user': pg_user,
            'password': pg_password
        }
    
    def verificar_sqlite_existe(self) -> bool:
        """Verifica si existe el archivo SQLite"""
        if not os.path.exists(self.sqlite_path):
            print(f"❌ No se encontró el archivo SQLite en: {self.sqlite_path}")
            return False
        print(f"✓ Archivo SQLite encontrado: {self.sqlite_path}")
        return True
    
    def conectar_postgresql(self):
        """Conecta a PostgreSQL y verifica la conexión"""
        try:
            conn = psycopg2.connect(**self.pg_params)
            print(f"✓ Conexión exitosa a PostgreSQL: {self.pg_params['database']}")
            return conn
        except Exception as e:
            print(f"❌ Error al conectar a PostgreSQL: {e}")
            return None
    
    def crear_tabla_postgresql(self, pg_conn):
        """Crea la tabla empresas en PostgreSQL si no existe"""
        cursor = pg_conn.cursor()
        
        print("Creando tabla 'empresas' en PostgreSQL...")
        
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
        
        # Crear índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nit ON empresas(nit)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_estado ON empresas(estado)')
        
        pg_conn.commit()
        print("✓ Tabla 'empresas' creada/verificada en PostgreSQL")
    
    def limpiar_tabla_postgresql(self, pg_conn):
        """Limpia la tabla empresas en PostgreSQL (opcional)"""
        cursor = pg_conn.cursor()
        cursor.execute('DELETE FROM empresas')
        pg_conn.commit()
        print("✓ Tabla 'empresas' limpiada en PostgreSQL")
    
    def convertir_fecha(self, fecha_str: Optional[str]):
        """Convierte una fecha de formato ISO string a datetime o None"""
        if not fecha_str:
            return None
        try:
            return datetime.fromisoformat(fecha_str)
        except:
            return None
    
    def migrar_datos(self, limpiar_destino: bool = False):
        """
        Ejecuta la migración de datos
        
        Args:
            limpiar_destino: Si True, limpia la tabla PostgreSQL antes de migrar
        """
        print("\n" + "="*60)
        print("MIGRACIÓN DE SQLITE A POSTGRESQL")
        print("="*60 + "\n")
        
        # Verificar SQLite
        if not self.verificar_sqlite_existe():
            return False
        
        # Conectar a PostgreSQL
        pg_conn = self.conectar_postgresql()
        if not pg_conn:
            return False
        
        try:
            # Crear tabla en PostgreSQL
            self.crear_tabla_postgresql(pg_conn)
            
            # Limpiar tabla si se solicita
            if limpiar_destino:
                respuesta = input("\n⚠️  ¿Estás seguro de querer limpiar la tabla PostgreSQL? (s/n): ")
                if respuesta.lower() == 's':
                    self.limpiar_tabla_postgresql(pg_conn)
                else:
                    print("Migración cancelada por el usuario")
                    return False
            
            # Conectar a SQLite
            print(f"\nLeyendo datos de SQLite...")
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row
            sqlite_cursor = sqlite_conn.cursor()
            
            # Leer todas las empresas
            sqlite_cursor.execute('SELECT * FROM empresas')
            empresas = sqlite_cursor.fetchall()
            
            if not empresas:
                print("⚠️  No hay datos para migrar en SQLite")
                sqlite_conn.close()
                pg_conn.close()
                return True
            
            print(f"✓ Se encontraron {len(empresas)} empresas en SQLite")
            
            # Migrar cada empresa
            pg_cursor = pg_conn.cursor()
            migradas = 0
            errores = 0
            
            print("\nMigrando empresas...")
            for row in empresas:
                try:
                    # Convertir fechas
                    cert_fecha_inicio = self.convertir_fecha(row['cert_fecha_inicio'])
                    cert_fecha_final = self.convertir_fecha(row['cert_fecha_final'])
                    resol_fecha_inicio = self.convertir_fecha(row['resol_fecha_inicio'])
                    resol_fecha_final = self.convertir_fecha(row['resol_fecha_final'])
                    doc_fecha_inicio = self.convertir_fecha(row['doc_fecha_inicio'])
                    doc_fecha_final = self.convertir_fecha(row['doc_fecha_final'])
                    fecha_creacion = self.convertir_fecha(row['fecha_creacion'])
                    fecha_actualizacion = self.convertir_fecha(row['fecha_actualizacion'])
                    
                    # Insertar en PostgreSQL
                    pg_cursor.execute('''
                        INSERT INTO empresas (
                            nit, nombre, tipo, estado,
                            cert_activo, cert_fecha_inicio, cert_fecha_final, cert_notificacion,
                            cert_renovado, cert_facturado, cert_comentarios,
                            resol_activo, resol_fecha_inicio, resol_fecha_final, resol_notificacion,
                            resol_renovado, resol_facturado, resol_comentarios,
                            doc_activo, doc_fecha_inicio, doc_fecha_final, doc_notificacion,
                            doc_renovado, doc_facturado, doc_comentarios,
                            fecha_creacion, fecha_actualizacion
                        ) VALUES (
                            %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s
                        )
                        ON CONFLICT (nit) DO UPDATE SET
                            nombre = EXCLUDED.nombre,
                            tipo = EXCLUDED.tipo,
                            estado = EXCLUDED.estado,
                            cert_activo = EXCLUDED.cert_activo,
                            cert_fecha_inicio = EXCLUDED.cert_fecha_inicio,
                            cert_fecha_final = EXCLUDED.cert_fecha_final,
                            cert_notificacion = EXCLUDED.cert_notificacion,
                            cert_renovado = EXCLUDED.cert_renovado,
                            cert_facturado = EXCLUDED.cert_facturado,
                            cert_comentarios = EXCLUDED.cert_comentarios,
                            resol_activo = EXCLUDED.resol_activo,
                            resol_fecha_inicio = EXCLUDED.resol_fecha_inicio,
                            resol_fecha_final = EXCLUDED.resol_fecha_final,
                            resol_notificacion = EXCLUDED.resol_notificacion,
                            resol_renovado = EXCLUDED.resol_renovado,
                            resol_facturado = EXCLUDED.resol_facturado,
                            resol_comentarios = EXCLUDED.resol_comentarios,
                            doc_activo = EXCLUDED.doc_activo,
                            doc_fecha_inicio = EXCLUDED.doc_fecha_inicio,
                            doc_fecha_final = EXCLUDED.doc_fecha_final,
                            doc_notificacion = EXCLUDED.doc_notificacion,
                            doc_renovado = EXCLUDED.doc_renovado,
                            doc_facturado = EXCLUDED.doc_facturado,
                            doc_comentarios = EXCLUDED.doc_comentarios,
                            fecha_actualizacion = EXCLUDED.fecha_actualizacion
                    ''', (
                        row['nit'], row['nombre'], row['tipo'], row['estado'],
                        row['cert_activo'], cert_fecha_inicio, cert_fecha_final, row['cert_notificacion'],
                        row['cert_renovado'], row['cert_facturado'], row['cert_comentarios'],
                        row['resol_activo'], resol_fecha_inicio, resol_fecha_final, row['resol_notificacion'],
                        row['resol_renovado'], row['resol_facturado'], row['resol_comentarios'],
                        row['doc_activo'], doc_fecha_inicio, doc_fecha_final, row['doc_notificacion'],
                        row['doc_renovado'], row['doc_facturado'], row['doc_comentarios'],
                        fecha_creacion, fecha_actualizacion
                    ))
                    
                    migradas += 1
                    print(f"  ✓ {row['nombre']} (NIT: {row['nit']})")
                    
                except Exception as e:
                    errores += 1
                    print(f"  ❌ Error al migrar {row['nombre']}: {e}")
            
            # Commit de todos los cambios
            pg_conn.commit()
            
            # Cerrar conexiones
            sqlite_conn.close()
            pg_conn.close()
            
            # Resumen
            print("\n" + "="*60)
            print("RESUMEN DE MIGRACIÓN")
            print("="*60)
            print(f"Total de empresas: {len(empresas)}")
            print(f"Migradas exitosamente: {migradas}")
            print(f"Errores: {errores}")
            print("="*60 + "\n")
            
            if errores == 0:
                print("✅ Migración completada exitosamente!")
                return True
            else:
                print("⚠️  Migración completada con algunos errores")
                return False
                
        except Exception as e:
            print(f"\n❌ Error durante la migración: {e}")
            if pg_conn:
                pg_conn.close()
            return False


def main():
    """Función principal para ejecutar la migración"""
    print("\n" + "="*60)
    print("CONFIGURACIÓN DE MIGRACIÓN")
    print("="*60 + "\n")
    
    # Configuración de SQLite
    sqlite_path = input("Ruta al archivo SQLite [data/facturacion.db]: ").strip()
    if not sqlite_path:
        sqlite_path = "data/facturacion.db"
    
    print("\nConfiguración de PostgreSQL:")
    pg_host = input("  Host [localhost]: ").strip() or "localhost"
    pg_port = input("  Puerto [5432]: ").strip() or "5432"
    pg_database = input("  Base de datos [facturacion]: ").strip() or "facturacion"
    pg_user = input("  Usuario [postgres]: ").strip() or "postgres"
    pg_password = input("  Contraseña: ").strip()
    
    if not pg_password:
        print("\n❌ La contraseña de PostgreSQL es requerida")
        return
    
    # Preguntar si limpiar la tabla de destino
    limpiar = input("\n¿Limpiar tabla PostgreSQL antes de migrar? (s/n) [n]: ").strip().lower() == 's'
    
    # Crear instancia del migrador
    migrador = MigracionSQLiteAPostgreSQL(
        sqlite_path=sqlite_path,
        pg_host=pg_host,
        pg_port=int(pg_port),
        pg_database=pg_database,
        pg_user=pg_user,
        pg_password=pg_password
    )
    
    # Ejecutar migración
    exito = migrador.migrar_datos(limpiar_destino=limpiar)
    
    if exito:
        print("\n✅ Ahora puedes actualizar tu archivo .env con:")
        print(f"   DB_TYPE=postgresql")
        print(f"   DB_HOST={pg_host}")
        print(f"   DB_PORT={pg_port}")
        print(f"   DB_NAME={pg_database}")
        print(f"   DB_USER={pg_user}")
        print(f"   DB_PASSWORD=tu_password")
    else:
        print("\n⚠️  Revisa los errores arriba antes de cambiar a PostgreSQL")


if __name__ == "__main__":
    main()
