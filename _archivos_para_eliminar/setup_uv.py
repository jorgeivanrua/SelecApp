#!/usr/bin/env python3
"""
Script de configuración con UV para Sistema Electoral ERP
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Ejecutar comando y manejar errores"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Error: {e.stderr}")
        return False

def check_uv_installed():
    """Verificar si UV está instalado"""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ UV está instalado")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ UV no está instalado")
        return False

def install_uv():
    """Instalar UV"""
    print("📦 Instalando UV...")
    
    # Detectar sistema operativo
    if os.name == 'nt':  # Windows
        command = 'powershell -c "irm https://astral.sh/uv/install.ps1 | iex"'
    else:  # Unix/Linux/macOS
        command = 'curl -LsSf https://astral.sh/uv/install.sh | sh'
    
    return run_command(command, "Instalando UV")

def setup_project():
    """Configurar proyecto con UV"""
    print("🏗️  Configurando proyecto con UV...")
    
    commands = [
        ("uv sync", "Sincronizando dependencias"),
        ("uv add --dev pytest pytest-flask pytest-cov", "Agregando dependencias de desarrollo"),
        ("uv add --optional production gunicorn psycopg2-binary", "Agregando dependencias de producción"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def create_virtual_env():
    """Crear entorno virtual con UV"""
    return run_command("uv venv", "Creando entorno virtual")

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN DEL SISTEMA ELECTORAL ERP CON UV")
    print("=" * 60)
    
    # Verificar si UV está instalado
    if not check_uv_installed():
        print("📥 UV no encontrado. Instalando...")
        if not install_uv():
            print("❌ Error instalando UV. Instálalo manualmente desde: https://docs.astral.sh/uv/")
            return False
        
        # Verificar instalación
        if not check_uv_installed():
            print("❌ UV no se instaló correctamente")
            return False
    
    # Crear entorno virtual
    if not create_virtual_env():
        print("⚠️  Error creando entorno virtual, continuando...")
    
    # Configurar proyecto
    if not setup_project():
        print("❌ Error configurando proyecto")
        return False
    
    print("\n✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print("\n📋 Próximos pasos:")
    print("1. uv run python initialization_service.py  # Inicializar BD")
    print("2. uv run python run.py                     # Ejecutar sistema")
    print("3. uv run python demo.py                    # Ver demo")
    print("4. uv run pytest                            # Ejecutar tests")
    
    print("\n🔧 Comandos útiles con UV:")
    print("• uv add <package>           # Agregar dependencia")
    print("• uv remove <package>        # Remover dependencia")
    print("• uv sync                    # Sincronizar dependencias")
    print("• uv run <command>           # Ejecutar comando en venv")
    print("• uv shell                   # Activar shell del venv")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)