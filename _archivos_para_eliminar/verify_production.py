#!/usr/bin/env python3
"""
Script de verificación para despliegue en producción
Sistema Electoral ERP - Departamento del Caquetá
"""

import os
import sys
import requests
import time
from datetime import datetime

def print_header():
    """Imprimir header del script"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE PRODUCCIÓN")
    print("Sistema Electoral ERP - Departamento del Caquetá")
    print("=" * 60)
    print()

def check_environment():
    """Verificar configuración del entorno"""
    print("🌍 Verificando configuración del entorno...")
    
    required_files = [
        'docker-compose.yml',
        'Dockerfile',
        'requirements.txt',
        'gunicorn.conf.py',
        'nginx.conf',
        '.env',
        'init_database.sql'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        return False
    
    print("✅ Todos los archivos de configuración están presentes")
    return True

def check_docker_services():
    """Verificar servicios de Docker"""
    print("\n🐳 Verificando servicios de Docker...")
    
    try:
        import subprocess
        
        # Verificar que Docker esté ejecutándose
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker no está ejecutándose")
            return False
        
        # Verificar servicios específicos
        services = [
            'sistema-electoral-app',
            'sistema-electoral-db', 
            'sistema-electoral-redis',
            'sistema-electoral-nginx'
        ]
        
        running_services = []
        for service in services:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={service}', '--format', '{{.Names}}'],
                capture_output=True, text=True
            )
            if service in result.stdout:
                running_services.append(service)
                print(f"✅ {service} está ejecutándose")
            else:
                print(f"❌ {service} no está ejecutándose")
        
        return len(running_services) == len(services)
        
    except Exception as e:
        print(f"❌ Error verificando Docker: {e}")
        return False

def check_application_health():
    """Verificar salud de la aplicación"""
    print("\n🏥 Verificando salud de la aplicación...")
    
    endpoints = [
        ('http://localhost/api/health', 'Health Check'),
        ('http://localhost/api/system/info', 'System Info'),
        ('http://localhost/', 'Página Principal'),
        ('http://localhost/dashboard/super_admin', 'Dashboard Super Admin')
    ]
    
    healthy_endpoints = 0
    
    for url, name in endpoints:
        try:
            response = requests.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                print(f"✅ {name}: OK (200)")
                healthy_endpoints += 1
            else:
                print(f"⚠️  {name}: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: Error de conexión - {e}")
    
    return healthy_endpoints == len(endpoints)

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print("\n🗄️  Verificando conexión a la base de datos...")
    
    try:
        import subprocess
        
        # Intentar conectar a PostgreSQL
        result = subprocess.run([
            'docker', 'exec', 'sistema-electoral-db', 
            'psql', '-U', 'electoral_user', '-d', 'caqueta_electoral', 
            '-c', 'SELECT version();'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Conexión a PostgreSQL exitosa")
            return True
        else:
            print(f"❌ Error conectando a PostgreSQL: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def check_ssl_certificates():
    """Verificar certificados SSL"""
    print("\n🔒 Verificando certificados SSL...")
    
    cert_files = ['ssl/cert.pem', 'ssl/key.pem']
    
    for cert_file in cert_files:
        if os.path.exists(cert_file):
            print(f"✅ {cert_file} existe")
        else:
            print(f"❌ {cert_file} no encontrado")
            return False
    
    # Verificar HTTPS
    try:
        response = requests.get('https://localhost/api/health', timeout=10, verify=False)
        if response.status_code == 200:
            print("✅ HTTPS funcionando correctamente")
            return True
        else:
            print(f"⚠️  HTTPS responde con status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando HTTPS: {e}")
        return False

def check_backup_system():
    """Verificar sistema de backup"""
    print("\n💾 Verificando sistema de backup...")
    
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        print(f"❌ Directorio de backup {backup_dir} no existe")
        return False
    
    print(f"✅ Directorio de backup existe")
    
    # Verificar script de backup
    if os.path.exists('scripts/backup.sh'):
        print("✅ Script de backup existe")
        return True
    else:
        print("❌ Script de backup no encontrado")
        return False

def check_logs():
    """Verificar sistema de logs"""
    print("\n📝 Verificando sistema de logs...")
    
    log_dirs = ['logs']
    
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            print(f"✅ Directorio de logs {log_dir} existe")
        else:
            print(f"❌ Directorio de logs {log_dir} no existe")
            return False
    
    return True

def generate_report():
    """Generar reporte de verificación"""
    print("\n📊 Generando reporte de verificación...")
    
    report = f"""
# REPORTE DE VERIFICACIÓN DE PRODUCCIÓN
## Sistema Electoral ERP - Departamento del Caquetá

**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Versión**: 1.0.0

### Resultados de Verificación

- ✅ Configuración del entorno
- ✅ Servicios de Docker
- ✅ Salud de la aplicación
- ✅ Conexión a base de datos
- ✅ Certificados SSL
- ✅ Sistema de backup
- ✅ Sistema de logs

### URLs de Acceso

- **Principal**: https://localhost
- **API**: https://localhost/api
- **Health Check**: https://localhost/api/health
- **Dashboard Admin**: https://localhost/dashboard/super_admin

### Servicios Activos

- sistema-electoral-app (Puerto 5000)
- sistema-electoral-db (PostgreSQL)
- sistema-electoral-redis (Cache)
- sistema-electoral-nginx (Proxy)

### Próximos Pasos

1. Configurar monitoreo continuo
2. Establecer procedimientos de backup
3. Configurar alertas de sistema
4. Capacitar al equipo de operaciones

---
**Sistema listo para producción** ✅
"""
    
    with open('verification_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ Reporte guardado en: verification_report.md")

def main():
    """Función principal"""
    print_header()
    
    checks = [
        ("Entorno", check_environment),
        ("Docker", check_docker_services),
        ("Aplicación", check_application_health),
        ("Base de Datos", check_database_connection),
        ("SSL", check_ssl_certificates),
        ("Backup", check_backup_system),
        ("Logs", check_logs)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed_checks += 1
        except Exception as e:
            print(f"❌ Error en verificación de {name}: {e}")
    
    print(f"\n📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 40)
    print(f"Verificaciones pasadas: {passed_checks}/{total_checks}")
    print(f"Porcentaje de éxito: {(passed_checks/total_checks)*100:.1f}%")
    
    if passed_checks == total_checks:
        print("\n🎉 ¡SISTEMA LISTO PARA PRODUCCIÓN!")
        print("✅ Todas las verificaciones pasaron exitosamente")
        generate_report()
        return 0
    else:
        print(f"\n⚠️  SISTEMA REQUIERE ATENCIÓN")
        print(f"❌ {total_checks - passed_checks} verificaciones fallaron")
        print("Por favor revisa los errores antes de desplegar en producción")
        return 1

if __name__ == "__main__":
    sys.exit(main())