"""
Script asistente para migración completa a PostgreSQL
Ejecuta todos los pasos necesarios de forma guiada
"""
import os
import sys
import subprocess


def imprimir_banner(texto: str):
    """Imprime un banner decorado"""
    print("\n" + "="*70)
    print(f"  {texto}")
    print("="*70 + "\n")


def imprimir_paso(numero: int, titulo: str):
    """Imprime un título de paso"""
    print(f"\n{'─'*70}")
    print(f"PASO {numero}: {titulo}")
    print(f"{'─'*70}\n")


def verificar_psycopg2():
    """Verifica si psycopg2 está instalado"""
    try:
        import psycopg2
        print("✓ psycopg2 ya está instalado")
        return True
    except ImportError:
        print("⚠️  psycopg2 no está instalado")
        return False


def instalar_dependencias():
    """Instala las dependencias necesarias"""
    imprimir_paso(1, "Instalación de Dependencias")
    
    if verificar_psycopg2():
        respuesta = input("\n¿Quieres reinstalar las dependencias? (s/n): ")
        if respuesta.lower() != 's':
            return True
    
    print("\nInstalando dependencias desde requirements.txt...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("\n✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Error al instalar dependencias")
        return False


def verificar_conexion():
    """Ejecuta el script de verificación de conexión"""
    imprimir_paso(2, "Verificación de Conexión a PostgreSQL")
    
    print("Vamos a verificar la conexión a tu servidor PostgreSQL...\n")
    
    try:
        resultado = subprocess.run([sys.executable, "scripts/verificar_postgresql.py"])
        return resultado.returncode == 0
    except Exception as e:
        print(f"\n❌ Error al ejecutar verificación: {e}")
        return False


def migrar_datos():
    """Ejecuta el script de migración de datos"""
    imprimir_paso(3, "Migración de Datos desde SQLite")
    
    # Verificar si existe el archivo SQLite
    sqlite_paths = [
        "data/facturacion.db",
        "facturacion.db",
    ]
    
    sqlite_encontrado = None
    for path in sqlite_paths:
        if os.path.exists(path):
            sqlite_encontrado = path
            break
    
    if not sqlite_encontrado:
        print("⚠️  No se encontró base de datos SQLite para migrar")
        respuesta = input("¿Quieres continuar sin migrar datos? (s/n): ")
        return respuesta.lower() == 's'
    
    print(f"✓ Base de datos SQLite encontrada: {sqlite_encontrado}")
    respuesta = input("\n¿Quieres migrar los datos a PostgreSQL? (s/n): ")
    
    if respuesta.lower() != 's':
        print("⏭️  Saltando migración de datos")
        return True
    
    try:
        resultado = subprocess.run([sys.executable, "scripts/migrar_sqlite_a_postgresql.py"])
        return resultado.returncode == 0
    except Exception as e:
        print(f"\n❌ Error al ejecutar migración: {e}")
        return False


def verificar_env():
    """Verifica que exista el archivo .env"""
    if os.path.exists('.env'):
        print("\n✓ Archivo .env encontrado")
        
        # Leer y mostrar configuración (sin contraseña)
        with open('.env', 'r') as f:
            for linea in f:
                if 'DB_TYPE' in linea or 'DB_HOST' in linea or 'DB_NAME' in linea or 'DB_USER' in linea:
                    print(f"  {linea.strip()}")
        return True
    else:
        print("\n⚠️  Archivo .env no encontrado")
        print("   Ejecuta primero: python scripts/verificar_postgresql.py")
        return False


def mostrar_resumen():
    """Muestra el resumen final"""
    imprimir_banner("MIGRACIÓN COMPLETADA")
    
    print("✅ Tu aplicación está lista para usar PostgreSQL\n")
    print("Para iniciar la aplicación, ejecuta:")
    print("   python servidor.py\n")
    print("O con uvicorn:")
    print("   uvicorn servidor:app --host 0.0.0.0 --port 5000\n")
    print("Documentación adicional:")
    print("   - MIGRACION_POSTGRESQL.md - Guía completa")
    print("   - RESUMEN_MIGRACION.md - Resumen de cambios")
    print("\n" + "="*70 + "\n")


def main():
    """Función principal del asistente"""
    imprimir_banner("ASISTENTE DE MIGRACIÓN A POSTGRESQL")
    
    print("Este asistente te guiará a través de los siguientes pasos:")
    print("  1. Instalación de dependencias (psycopg2)")
    print("  2. Verificación de conexión a PostgreSQL")
    print("  3. Migración de datos desde SQLite (opcional)")
    print("  4. Verificación final\n")
    
    respuesta = input("¿Quieres continuar? (s/n): ")
    if respuesta.lower() != 's':
        print("\nMigración cancelada")
        return
    
    # Paso 1: Instalar dependencias
    if not instalar_dependencias():
        print("\n❌ Error en instalación de dependencias. Abortando.")
        return
    
    # Paso 2: Verificar conexión
    verificar_conexion()
    
    # Verificar que se creó el archivo .env
    if not verificar_env():
        print("\n⚠️  Debes configurar el archivo .env antes de continuar")
        return
    
    # Paso 3: Migrar datos (opcional)
    migrar_datos()
    
    # Resumen final
    mostrar_resumen()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
