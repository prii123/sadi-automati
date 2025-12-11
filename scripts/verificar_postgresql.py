"""
Script para verificar la conexión a PostgreSQL
y configurar el archivo .env
"""
import psycopg2
import os


def verificar_conexion_postgresql(host: str, port: int, database: str, user: str, password: str) -> bool:
    """
    Verifica la conexión a PostgreSQL
    
    Args:
        host: Host del servidor PostgreSQL
        port: Puerto del servidor PostgreSQL
        database: Nombre de la base de datos
        user: Usuario de PostgreSQL
        password: Contraseña de PostgreSQL
    
    Returns:
        True si la conexión es exitosa, False en caso contrario
    """
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        # Probar la conexión
        cursor = conn.cursor()
        cursor.execute('SELECT version()')
        version = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print(f"✅ Conexión exitosa a PostgreSQL!")
        print(f"   Versión: {version[0][:50]}...")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión a PostgreSQL:")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado:")
        print(f"   {e}")
        return False


def crear_archivo_env(host: str, port: int, database: str, user: str, password: str):
    """
    Crea un archivo .env con la configuración de PostgreSQL
    """
    env_content = f"""# Variables de entorno para PostgreSQL
# Generado automáticamente

# Tipo de base de datos
DB_TYPE=postgresql

# PostgreSQL - Configuración
DB_HOST={host}
DB_PORT={port}
DB_NAME={database}
DB_USER={user}
DB_PASSWORD={password}

# API
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=True
API_BASE_URL=http://localhost:5000/api

# CORS - Orígenes permitidos
CORS_ORIGINS=*

# Email (Gmail)
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_password_de_aplicacion
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Destinatarios de notificaciones
EMAIL_DESTINATARIOS=destinatario1@example.com,destinatario2@example.com

# Notificaciones
NOTIFICACION_DIAS_ANTICIPACION=30

# Seguridad
SECRET_KEY=change-this-to-a-random-secret-key-in-production
"""
    
    # Verificar si ya existe .env
    if os.path.exists('.env'):
        respuesta = input("\n⚠️  El archivo .env ya existe. ¿Quieres sobrescribirlo? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Operación cancelada. No se modificó el archivo .env")
            return False
    
    # Crear archivo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ Archivo .env creado exitosamente!")
    print(f"   Ubicación: {os.path.abspath('.env')}")
    return True


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE CONEXIÓN A POSTGRESQL")
    print("="*60 + "\n")
    
    print("Ingresa los datos de tu servidor PostgreSQL:\n")
    
    # Solicitar datos de conexión
    host = input("  Host [localhost]: ").strip() or "localhost"
    port = input("  Puerto [5432]: ").strip() or "5432"
    database = input("  Base de datos [facturacion]: ").strip() or "facturacion"
    user = input("  Usuario [postgres]: ").strip() or "postgres"
    password = input("  Contraseña: ").strip()
    
    if not password:
        print("\n❌ La contraseña es requerida")
        return
    
    print("\n" + "-"*60)
    print("Verificando conexión...")
    print("-"*60 + "\n")
    
    # Verificar conexión
    exito = verificar_conexion_postgresql(
        host=host,
        port=int(port),
        database=database,
        user=user,
        password=password
    )
    
    if exito:
        # Preguntar si quiere crear el archivo .env
        respuesta = input("\n¿Quieres crear/actualizar el archivo .env con esta configuración? (s/n): ")
        if respuesta.lower() == 's':
            crear_archivo_env(host, int(port), database, user, password)
            print("\n✅ Ahora puedes ejecutar la aplicación con:")
            print("   python servidor.py")
            print("\n   O migrar los datos desde SQLite con:")
            print("   python scripts/migrar_sqlite_a_postgresql.py")
    else:
        print("\n⚠️  No se pudo conectar a PostgreSQL.")
        print("   Verifica los datos de conexión e intenta de nuevo.")
        print("\n   Posibles problemas:")
        print("   - PostgreSQL no está ejecutándose")
        print("   - El puerto está bloqueado por firewall")
        print("   - Las credenciales son incorrectas")
        print("   - La base de datos no existe")


if __name__ == "__main__":
    main()
