#!/usr/bin/env python3
"""
Script de instalación completa del Sistema Electoral ERP usando UV
Instala todas las dependencias y configura el entorno de desarrollo
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description="", check=True):
    """Ejecutar comando del sistema con manejo de errores"""
    print(f"\n🔄 {description}")
    print(f"Ejecutando: {command}")
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(f"✅ {result.stdout}")
        if result.stderr and check:
            print(f"⚠️  {result.stderr}")
        
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando: {command}")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_uv_installed():
    """Verificar si UV está instalado"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ UV ya está instalado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ UV no está instalado")
    return False

def install_uv():
    """Instalar UV package manager"""
    print("\n📦 Instalando UV package manager...")
    
    system = platform.system()
    
    if system == "Windows":
        # Para Windows, usar PowerShell
        command = 'powershell -c "irm https://astral.sh/uv/install.ps1 | iex"'
        run_command(command, "Instalando UV en Windows")
    elif system == "Darwin":  # macOS
        # Para macOS, usar curl
        command = 'curl -LsSf https://astral.sh/uv/install.sh | sh'
        run_command(command, "Instalando UV en macOS")
    else:  # Linux
        # Para Linux, usar curl
        command = 'curl -LsSf https://astral.sh/uv/install.sh | sh'
        run_command(command, "Instalando UV en Linux")
    
    # Verificar instalación
    if not check_uv_installed():
        print("❌ Error: UV no se pudo instalar correctamente")
        print("Por favor instale UV manualmente desde: https://docs.astral.sh/uv/getting-started/installation/")
        sys.exit(1)

def setup_project():
    """Configurar el proyecto con UV"""
    print("\n🏗️  Configurando proyecto con UV...")
    
    # Inicializar proyecto si no existe pyproject.toml
    if not Path("pyproject.toml").exists():
        print("❌ No se encontró pyproject.toml")
        sys.exit(1)
    
    # Sincronizar dependencias
    run_command("uv sync", "Sincronizando dependencias del proyecto")
    
    # Instalar dependencias de desarrollo
    run_command("uv sync --extra dev", "Instalando dependencias de desarrollo")

def setup_database():
    """Configurar base de datos"""
    print("\n🗄️  Configurando base de datos...")
    
    # Ejecutar inicialización de base de datos
    if Path("initialization_service.py").exists():
        run_command("uv run python initialization_service.py", "Inicializando base de datos")
    else:
        print("⚠️  No se encontró initialization_service.py")

def run_tests():
    """Ejecutar tests del sistema"""
    print("\n🧪 Ejecutando tests del sistema...")
    
    if Path("test_system.py").exists():
        run_command("uv run python test_system.py", "Ejecutando tests del sistema", check=False)
    else:
        print("⚠️  No se encontró test_system.py")

def create_env_file():
    """Crear archivo .env si no existe"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("\n📝 Creando archivo .env...")
        env_file.write_text(env_example.read_text())
        print("✅ Archivo .env creado desde .env.example")
    elif not env_file.exists():
        print("\n📝 Creando archivo .env básico...")
        env_content = """# Configuración del Sistema Electoral ERP
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///caqueta_electoral.db
JWT_SECRET_KEY=jwt-secret-key-change-in-production

# Configuración de correo (opcional)
MAIL_SERVER=localhost
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=

# Configuración de Redis (opcional)
REDIS_URL=redis://localhost:6379/0
"""
        env_file.write_text(env_content)
        print("✅ Archivo .env básico creado")

def show_completion_message():
    """Mostrar mensaje de finalización"""
    print("\n" + "="*60)
    print("🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print("\n📋 PRÓXIMOS PASOS:")
    print("\n1. Para iniciar el servidor de desarrollo:")
    print("   uv run python app.py")
    print("\n2. Para ejecutar el demo:")
    print("   uv run python demo.py")
    print("\n3. Para ejecutar tests:")
    print("   uv run python test_system.py")
    print("\n4. Para acceder al sistema:")
    print("   http://localhost:5000")
    print("\n5. Usuarios de prueba:")
    print("   - Super Admin: 12345678 / admin123")
    print("   - Admin Depto: 87654321 / admin123")
    print("   - Admin Municipal: 11111111 / admin123")
    print("   - Testigo Mesa: 22222222 / testigo123")
    print("\n📚 DOCUMENTACIÓN:")
    print("   - README.md: Información general")
    print("   - SYSTEM_SUMMARY.md: Resumen técnico")
    print("   - .kiro/specs/: Especificaciones del proyecto")
    print("\n🔧 COMANDOS ÚTILES:")
    print("   - uv add <package>: Agregar dependencia")
    print("   - uv remove <package>: Remover dependencia")
    print("   - uv sync: Sincronizar dependencias")
    print("   - uv run <command>: Ejecutar comando en el entorno")
    print("\n" + "="*60)

def main():
    """Función principal de instalación"""
    print("🚀 INSTALADOR DEL SISTEMA ELECTORAL ERP")
    print("="*50)
    print("Este script instalará todas las dependencias necesarias")
    print("para el Sistema Electoral ERP usando UV package manager.")
    print("="*50)
    
    # Verificar Python
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"Versión actual: {python_version.major}.{python_version.minor}")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detectado")
    
    # Verificar directorio del proyecto
    if not Path("pyproject.toml").exists():
        print("❌ Error: No se encontró pyproject.toml")
        print("Asegúrese de ejecutar este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    try:
        # Paso 1: Verificar/Instalar UV
        if not check_uv_installed():
            install_uv()
        
        # Paso 2: Configurar proyecto
        setup_project()
        
        # Paso 3: Crear archivo .env
        create_env_file()
        
        # Paso 4: Configurar base de datos
        setup_database()
        
        # Paso 5: Ejecutar tests (opcional)
        run_tests()
        
        # Paso 6: Mostrar mensaje de finalización
        show_completion_message()
        
    except KeyboardInterrupt:
        print("\n\n❌ Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error durante la instalación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()