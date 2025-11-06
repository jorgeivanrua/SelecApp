#!/usr/bin/env python3
"""
Script de inicio como Administrador
Sistema Electoral ERP - Departamento del Caquetá
"""

import webbrowser
import time
import requests
import sys

def print_banner():
    """Mostrar banner de administrador"""
    print("=" * 70)
    print("👑 SISTEMA ELECTORAL ERP - MODO ADMINISTRADOR")
    print("=" * 70)
    print("🏛️  Departamento del Caquetá")
    print("🔧 Acceso de Super Administrador")
    print("📅 Noviembre 2024")
    print("=" * 70)
    print()

def check_server():
    """Verificar que el servidor esté ejecutándose"""
    print("🔍 Verificando servidor...")
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor disponible en http://localhost:5000")
            return True
        else:
            print(f"⚠️  Servidor responde con código {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Servidor no disponible")
        return False

def show_admin_info():
    """Mostrar información de administrador"""
    print("👑 INFORMACIÓN DE ADMINISTRADOR")
    print("-" * 40)
    print("🔑 Usuario: admin")
    print("🆔 Cédula: 12345678")
    print("📧 Email: admin@caqueta.gov.co")
    print("🎯 Rol: Super Administrador")
    print("🔒 Contraseña: demo123 (cambiar en producción)")
    print()

def show_admin_urls():
    """Mostrar URLs de administrador"""
    print("🌐 URLS DE ADMINISTRADOR")
    print("-" * 40)
    
    admin_urls = {
        'Dashboard Principal': 'http://localhost:5000/dashboard/super_admin',
        'Gestión de Usuarios': 'http://localhost:5000/users',
        'Procesos Electorales': 'http://localhost:5000/electoral',
        'Reportes del Sistema': 'http://localhost:5000/reports',
        'Configuración': 'http://localhost:5000/settings',
        'API Health Check': 'http://localhost:5000/api/health',
        'Información del Sistema': 'http://localhost:5000/api/system/info'
    }
    
    for name, url in admin_urls.items():
        print(f"📍 {name}: {url}")
    
    print()

def open_admin_dashboard():
    """Abrir dashboard de administrador"""
    print("🚀 Abriendo Dashboard de Super Administrador...")
    
    dashboard_url = "http://localhost:5000/dashboard/super_admin"
    
    try:
        webbrowser.open(dashboard_url)
        print(f"✅ Dashboard abierto en: {dashboard_url}")
        return True
    except Exception as e:
        print(f"❌ Error al abrir navegador: {e}")
        print(f"   Abre manualmente: {dashboard_url}")
        return False

def show_admin_menu():
    """Mostrar menú de administrador"""
    while True:
        print("\n👑 MENÚ DE ADMINISTRADOR")
        print("-" * 30)
        print("1. 🏠 Dashboard Principal")
        print("2. 👥 Gestión de Usuarios")
        print("3. 🗳️  Procesos Electorales")
        print("4. 📊 Reportes del Sistema")
        print("5. ⚙️  Configuración")
        print("6. 🔍 Health Check")
        print("7. 📋 Información del Sistema")
        print("8. 🌐 Ver todas las URLs")
        print("0. 🚪 Salir")
        print()
        
        choice = input("Selecciona una opción (0-8): ").strip()
        
        if choice == '0':
            print("\n👋 Cerrando sesión de administrador...")
            break
        elif choice == '1':
            webbrowser.open("http://localhost:5000/dashboard/super_admin")
            print("✅ Dashboard abierto")
        elif choice == '2':
            webbrowser.open("http://localhost:5000/users")
            print("✅ Gestión de usuarios abierta")
        elif choice == '3':
            webbrowser.open("http://localhost:5000/electoral")
            print("✅ Procesos electorales abierto")
        elif choice == '4':
            webbrowser.open("http://localhost:5000/reports")
            print("✅ Reportes abiertos")
        elif choice == '5':
            webbrowser.open("http://localhost:5000/settings")
            print("✅ Configuración abierta")
        elif choice == '6':
            try:
                response = requests.get("http://localhost:5000/api/health")
                print(f"✅ Health Check: {response.json()}")
            except Exception as e:
                print(f"❌ Error en Health Check: {e}")
        elif choice == '7':
            try:
                response = requests.get("http://localhost:5000/api/system/info")
                info = response.json()
                print("📋 INFORMACIÓN DEL SISTEMA:")
                for key, value in info.items():
                    print(f"   {key}: {value}")
            except Exception as e:
                print(f"❌ Error obteniendo información: {e}")
        elif choice == '8':
            show_admin_urls()
        else:
            print("❌ Opción inválida")

def main():
    """Función principal"""
    print_banner()
    
    # Verificar servidor
    if not check_server():
        print("❌ El servidor no está disponible.")
        print("   Por favor ejecuta 'python app.py' primero")
        sys.exit(1)
    
    # Mostrar información
    show_admin_info()
    show_admin_urls()
    
    # Abrir dashboard automáticamente
    open_admin_dashboard()
    
    # Mostrar menú interactivo
    show_admin_menu()

if __name__ == "__main__":
    main()