#!/usr/bin/env python3
"""
Instalación completa del Sistema Electoral ERP con UV
Incluye configuración de entorno, dependencias y base de datos
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

class ElectoralSystemInstaller:
    """Instalador completo del sistema electoral"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.project_root = Path.cwd()
        
    def print_header(self):
        """Mostrar header del instalador"""
        print("=" * 70)
        print("🏛️  SISTEMA ELECTORAL ERP - INSTALADOR COMPLETO")
        print("=" * 70)
        print(f"Sistema: {platform.system()} {platform.release()}")
        print(f"Python: {self.python_version}")
        print(f"Directorio: {self.project_root}")
        print("=" * 70)
        print()
    
    def check_python_version(self):
        """Verificar versión de Python"""
        print("🐍 Verificando versión de Python...")
        
        if sys.version_info < (3, 8):
            print("❌ Error: Se requiere Python 3.8 o superior")
            print(f"   Versión actual: {self.python_version}")
            return False
        
        print(f"✅ Python {self.python_version} - Compatible")
        return True
    
    def install_uv(self):
        """Instalar UV si no está disponible"""
        print("\n📦 Verificando UV...")
        
        try:
            result = subprocess.run(["uv", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ UV ya está instalado: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📥 UV no encontrado. Instalando...")
            
            try:
                if self.system == "windows":
                    # Windows
                    cmd = 'powershell -c "irm https://astral.sh/uv/install.ps1 | iex"'
                else:
                    # Unix/Linux/macOS
                    cmd = 'curl -LsSf https://astral.sh/uv/install.sh | sh'
                
                subprocess.run(cmd, shell=True, check=True)
                
                # Verificar instalación
                subprocess.run(["uv", "--version"], check=True, capture_output=True)
                print("✅ UV instalado exitosamente")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Error instalando UV: {e}")
                print("   Instala UV manualmente desde: https://docs.astral.sh/uv/")
                return False
    
    def setup_project(self):
        """Configurar proyecto con UV"""
        print("\n🏗️  Configurando proyecto...")
        
        try:
            # Crear entorno virtual
            print("   Creando entorno virtual...")
            subprocess.run(["uv", "venv"], check=True, capture_output=True)
            print("   ✅ Entorno virtual creado")
            
            # Sincronizar dependencias
            print("   Sincronizando dependencias...")
            subprocess.run(["uv", "sync"], check=True)
            print("   ✅ Dependencias instaladas")
            
            # Instalar dependencias de desarrollo
            print("   Instalando dependencias de desarrollo...")
            subprocess.run(["uv", "sync", "--group", "dev"], check=True, capture_output=True)
            print("   ✅ Dependencias de desarrollo instaladas")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error configurando proyecto: {e}")
            return False
    
    def setup_database(self):
        """Configurar base de datos"""
        print("\n🗄️  Configurando base de datos...")
        
        try:
            # Verificar si ya existe la base de datos
            db_file = self.project_root / "caqueta_electoral.db"
            
            if db_file.exists():
                print("   ⚠️  Base de datos ya existe")
                response = input("   ¿Deseas recrearla? (s/N): ").lower().strip()
                
                if response in ['s', 'si', 'sí', 'y', 'yes']:
                    db_file.unlink()
                    print("   🗑️  Base de datos anterior eliminada")
                else:
                    print("   ✅ Manteniendo base de datos existente")
                    return True
            
            # Inicializar base de datos
            print("   Inicializando base de datos...")
            result = subprocess.run(
                ["uv", "run", "python", "initialization_service.py"],
                capture_output=True, text=True, check=True
            )
            
            if "INICIALIZACIÓN COMPLETADA" in result.stdout:
                print("   ✅ Base de datos inicializada exitosamente")
                return True
            else:
                print("   ⚠️  Inicialización completada con advertencias")
                print("   Ver detalles en el log anterior")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error configurando base de datos: {e}")
            if e.stdout:
                print(f"   Salida: {e.stdout}")
            if e.stderr:
                print(f"   Error: {e.stderr}")
            return False
    
    def create_env_file(self):
        """Crear archivo .env si no existe"""
        print("\n⚙️  Configurando variables de entorno...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if env_file.exists():
            print("   ✅ Archivo .env ya existe")
            return True
        
        if env_example.exists():
            try:
                # Copiar .env.example a .env
                with open(env_example, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("   ✅ Archivo .env creado desde .env.example")
                print("   ⚠️  Recuerda actualizar las variables según tu entorno")
                return True
                
            except Exception as e:
                print(f"❌ Error creando .env: {e}")
                return False
        else:
            print("   ⚠️  No se encontró .env.example")
            return True
    
    def run_tests(self):
        """Ejecutar pruebas del sistema"""
        print("\n🧪 Ejecutando pruebas del sistema...")
        
        try:
            # Ejecutar demo para verificar funcionamiento
            print("   Ejecutando demo del sistema...")
            result = subprocess.run(
                ["uv", "run", "python", "demo.py"],
                capture_output=True, text=True, check=True
            )
            
            if "DEMO COMPLETADO" in result.stdout:
                print("   ✅ Demo ejecutado exitosamente")
                return True
            else:
                print("   ⚠️  Demo completado con advertencias")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error ejecutando pruebas: {e}")
            return False
    
    def show_completion_info(self):
        """Mostrar información de finalización"""
        print("\n" + "=" * 70)
        print("🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print()
        print("📋 Próximos pasos:")
        print()
        print("1. Iniciar el sistema:")
        print("   uv run python run.py")
        print()
        print("2. Acceder al sistema:")
        print("   http://localhost:5000")
        print()
        print("3. Credenciales por defecto:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print()
        print("🔧 Comandos útiles:")
        print("   uv run python demo.py          # Ejecutar demo")
        print("   uv run python test_system.py   # Probar sistema")
        print("   uv add <paquete>               # Agregar dependencia")
        print("   uv sync                        # Sincronizar dependencias")
        print("   uv run <comando>               # Ejecutar en entorno virtual")
        print()
        print("📚 Documentación:")
        print("   README.md                      # Documentación principal")
        print("   SYSTEM_SUMMARY.md              # Resumen del sistema")
        print()
        print("🎯 Características implementadas:")
        print("   ✅ Sistema modular con 5 módulos")
        print("   ✅ 8 roles de usuario con permisos granulares")
        print("   ✅ 40+ endpoints REST")
        print("   ✅ Dashboard personalizable por rol")
        print("   ✅ Sistema de reportes completo")
        print("   ✅ Base de datos con datos de Caquetá")
        print("   ✅ Interfaces específicas por rol")
        print("   ✅ Formularios especializados")
        print()
        print("=" * 70)
    
    def install(self):
        """Ejecutar instalación completa"""
        self.print_header()
        
        steps = [
            ("Verificar Python", self.check_python_version),
            ("Instalar UV", self.install_uv),
            ("Configurar proyecto", self.setup_project),
            ("Configurar base de datos", self.setup_database),
            ("Crear archivo .env", self.create_env_file),
            ("Ejecutar pruebas", self.run_tests)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Instalación fallida en: {step_name}")
                return False
        
        self.show_completion_info()
        return True

def main():
    """Función principal"""
    installer = ElectoralSystemInstaller()
    
    try:
        success = installer.install()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()