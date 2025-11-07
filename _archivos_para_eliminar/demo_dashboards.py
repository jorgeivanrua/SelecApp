#!/usr/bin/env python3
"""
Script de demostración para mostrar los dashboards específicos por rol
"""

import webbrowser
import time
import sys

def demo_dashboards():
    """Demostración interactiva de dashboards por rol"""
    
    base_url = "http://localhost:5000"
    
    print("🚀 DEMOSTRACIÓN DE DASHBOARDS ESPECÍFICOS POR ROL")
    print("=" * 60)
    print("Sistema Electoral ERP - Departamento del Caquetá")
    print("=" * 60)
    print()
    
    # Roles disponibles con descripciones
    roles = {
        '1': {
            'name': 'super_admin',
            'display': 'Super Administrador',
            'description': 'Control total del sistema, gestión de usuarios y configuración'
        },
        '2': {
            'name': 'admin_departamental',
            'display': 'Administrador Departamental',
            'description': 'Gestión de municipios y procesos electorales departamentales'
        },
        '3': {
            'name': 'admin_municipal',
            'display': 'Administrador Municipal',
            'description': 'Gestión de mesas de votación y candidatos locales'
        },
        '4': {
            'name': 'coordinador_electoral',
            'display': 'Coordinador Electoral',
            'description': 'Coordinación de procesos electorales y cronogramas'
        },
        '5': {
            'name': 'jurado_votacion',
            'display': 'Jurado de Votación',
            'description': 'Registro de votos y generación de actas'
        },
        '6': {
            'name': 'testigo_mesa',
            'display': 'Testigo de Mesa',
            'description': 'Observación y verificación del proceso de votación'
        },
        '7': {
            'name': 'auditor_electoral',
            'display': 'Auditor Electoral',
            'description': 'Auditoría y supervisión de procesos electorales'
        },
        '8': {
            'name': 'observador_internacional',
            'display': 'Observador Internacional',
            'description': 'Monitoreo según estándares internacionales'
        }
    }
    
    while True:
        print("\n📋 ROLES DISPONIBLES:")
        print("-" * 40)
        
        for key, role in roles.items():
            print(f"{key}. {role['display']}")
            print(f"   {role['description']}")
            print()
        
        print("9. Ver todas las funcionalidades adicionales")
        print("0. Salir")
        print()
        
        choice = input("Selecciona un rol para ver su dashboard (0-9): ").strip()
        
        if choice == '0':
            print("\n👋 ¡Gracias por usar la demostración!")
            break
        elif choice == '9':
            show_additional_features(base_url)
        elif choice in roles:
            role = roles[choice]
            show_role_dashboard(base_url, role)
        else:
            print("❌ Opción inválida. Por favor selecciona un número del 0 al 9.")

def show_role_dashboard(base_url, role):
    """Mostrar dashboard específico de un rol"""
    print(f"\n🎯 Abriendo dashboard para: {role['display']}")
    print(f"📝 Descripción: {role['description']}")
    print(f"🌐 URL: {base_url}/dashboard/{role['name']}")
    
    try:
        webbrowser.open(f"{base_url}/dashboard/{role['name']}")
        print("✅ Dashboard abierto en el navegador")
    except Exception as e:
        print(f"❌ Error al abrir el navegador: {e}")
        print(f"   Puedes abrir manualmente: {base_url}/dashboard/{role['name']}")
    
    input("\nPresiona Enter para continuar...")

def show_additional_features(base_url):
    """Mostrar funcionalidades adicionales"""
    print("\n🔧 FUNCIONALIDADES ADICIONALES")
    print("=" * 40)
    
    features = {
        '1': {
            'name': 'Formulario de Auditoría',
            'url': '/audit/start',
            'description': 'Crear nueva auditoría electoral'
        },
        '2': {
            'name': 'Observación Internacional',
            'url': '/observation/new',
            'description': 'Registrar observación internacional'
        },
        '3': {
            'name': 'Gestión de Usuarios',
            'url': '/users',
            'description': 'Administrar usuarios del sistema'
        },
        '4': {
            'name': 'Gestión de Municipios',
            'url': '/municipalities',
            'description': 'Administrar municipios del departamento'
        },
        '5': {
            'name': 'Gestión de Mesas',
            'url': '/tables',
            'description': 'Configurar mesas de votación'
        },
        '6': {
            'name': 'Registro de Votos',
            'url': '/voting/register',
            'description': 'Sistema de registro de votos'
        },
        '7': {
            'name': 'Dashboard Principal',
            'url': '/dashboard',
            'description': 'Dashboard general del sistema'
        }
    }
    
    while True:
        print("\n📋 FUNCIONALIDADES:")
        print("-" * 30)
        
        for key, feature in features.items():
            print(f"{key}. {feature['name']}")
            print(f"   {feature['description']}")
            print()
        
        print("0. Volver al menú principal")
        print()
        
        choice = input("Selecciona una funcionalidad (0-7): ").strip()
        
        if choice == '0':
            break
        elif choice in features:
            feature = features[choice]
            print(f"\n🎯 Abriendo: {feature['name']}")
            print(f"🌐 URL: {base_url}{feature['url']}")
            
            try:
                webbrowser.open(f"{base_url}{feature['url']}")
                print("✅ Funcionalidad abierta en el navegador")
            except Exception as e:
                print(f"❌ Error al abrir el navegador: {e}")
                print(f"   Puedes abrir manualmente: {base_url}{feature['url']}")
            
            input("\nPresiona Enter para continuar...")
        else:
            print("❌ Opción inválida. Por favor selecciona un número del 0 al 7.")

def check_server():
    """Verificar que el servidor esté ejecutándose"""
    try:
        import requests
        response = requests.get("http://localhost:5000", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔍 Verificando servidor...")
    
    if not check_server():
        print("❌ El servidor no está ejecutándose en http://localhost:5000")
        print("   Por favor ejecuta 'python app.py' en otra terminal")
        sys.exit(1)
    
    print("✅ Servidor disponible")
    demo_dashboards()