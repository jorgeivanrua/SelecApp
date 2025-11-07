#!/usr/bin/env python3
"""
Script de instalación del Sistema Electoral ERP
"""

import subprocess
import sys
import os

def install_package(package):
    """Instalar paquete con pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Función principal de instalación"""
    print("🚀 Instalando Sistema Electoral ERP")
    print("=" * 50)
    
    # Paquetes esenciales
    essential_packages = [
        "flask==2.3.3",
        "flask-cors==4.0.0", 
        "flask-jwt-extended==4.5.3",
        "sqlalchemy==2.0.23",
        "werkzeug==2.3.7"
    ]
    
    print("📦 Instalando paquetes esenciales...")
    
    for package in essential_packages:
        print(f"   Instalando {package}...")
        if install_package(package):
            print(f"   ✅ {package} instalado")
        else:
            print(f"   ❌ Error instalando {package}")
            return False
    
    print("\n✅ Instalación completada!")
    print("\n📋 Próximos pasos:")
    print("1. python initialization_service.py  # Inicializar base de datos")
    print("2. python run.py                     # Ejecutar sistema")
    print("3. python test_system.py             # Probar sistema")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)