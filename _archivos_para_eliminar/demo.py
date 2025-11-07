#!/usr/bin/env python3
"""
Demo del Sistema Electoral ERP
Muestra las funcionalidades principales sin necesidad de servidor web
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager
from core.auth import AuthManager
from core.permissions import PermissionManager
from modules.electoral.services import ElectoralService
from modules.candidates.services import CandidateService
from modules.users.services import UserService
from modules.reports.services import ReportService
from modules.dashboard.services import DashboardService

class SystemDemo:
    """Demo del sistema electoral"""
    
    def __init__(self):
        # Inicializar componentes
        self.db = DatabaseManager('sqlite:///caqueta_electoral.db')
        self.auth = AuthManager(self.db)
        self.permissions = PermissionManager(self.db)
        
        # Servicios
        self.electoral_service = ElectoralService(self.db)
        self.candidate_service = CandidateService(self.db)
        self.user_service = UserService(self.db)
        self.report_service = ReportService(self.db)
        self.dashboard_service = DashboardService(self.db)
    
    def show_system_overview(self):
        """Mostrar vista general del sistema"""
        print("🏛️  SISTEMA ELECTORAL ERP - CAQUETÁ")
        print("=" * 60)
        
        try:
            # Verificar conexión a base de datos
            if self.db.health_check():
                print("✅ Base de datos: Conectada")
            else:
                print("❌ Base de datos: Error de conexión")
                return
            
            # Obtener estadísticas generales
            tables = self.db.get_all_tables()
            print(f"📊 Tablas en base de datos: {len(tables)}")
            
            # Mostrar tablas principales
            main_tables = [
                'users', 'candidates', 'political_parties', 'coalitions',
                'mesas_electorales', 'electoral_processes', 'locations'
            ]
            
            print("\n📋 DATOS PRINCIPALES:")
            for table in main_tables:
                if table in tables:
                    try:
                        count_result = self.db.execute_query(f"SELECT COUNT(*) FROM {table}")
                        count = count_result[0][0] if count_result else 0
                        print(f"   • {table.replace('_', ' ').title()}: {count} registros")
                    except:
                        print(f"   • {table.replace('_', ' ').title()}: Error al contar")
            
        except Exception as e:
            print(f"❌ Error en vista general: {e}")
    
    def demo_authentication(self):
        """Demo de autenticación"""
        print("\n🔐 DEMO: AUTENTICACIÓN")
        print("-" * 40)
        
        try:
            # Obtener usuarios disponibles
            users_query = "SELECT username, rol FROM users WHERE activo = 1 LIMIT 5"
            users = self.db.execute_query(users_query)
            
            print("👥 Usuarios disponibles:")
            for user in users:
                print(f"   • {user[0]} ({user[1]})")
            
            # Obtener roles y permisos
            roles = self.permissions.get_all_roles()
            print(f"\n🎭 Roles del sistema: {len(roles)} disponibles")
            for role in roles[:5]:  # Mostrar solo los primeros 5
                print(f"   • {role['name']}: {len(role['permissions'])} permisos")
            
        except Exception as e:
            print(f"❌ Error en demo de autenticación: {e}")
    
    def demo_electoral_module(self):
        """Demo del módulo electoral"""
        print("\n🗳️  DEMO: MÓDULO ELECTORAL")
        print("-" * 40)
        
        try:
            # Obtener procesos electorales
            processes = self.electoral_service.get_electoral_processes(page=1, per_page=5)
            print(f"📊 Procesos electorales: {processes['pagination']['total']} total")
            
            for process in processes['data'][:3]:  # Mostrar solo los primeros 3
                print(f"   • {process['nombre']} ({process['estado']})")
            
            # Obtener tipos de elección
            election_types = self.electoral_service.get_election_types()
            print(f"\n🏛️  Tipos de elección: {len(election_types)} disponibles")
            for et in election_types:
                print(f"   • {et['nombre']} ({et['codigo']})")
            
            # Obtener estadísticas de mesas
            mesas = self.electoral_service.get_electoral_mesas(page=1, per_page=1)
            print(f"\n📋 Mesas electorales: {mesas['pagination']['total']} total")
            
        except Exception as e:
            print(f"❌ Error en demo electoral: {e}")
    
    def demo_candidates_module(self):
        """Demo del módulo de candidatos"""
        print("\n👥 DEMO: MÓDULO CANDIDATOS")
        print("-" * 40)
        
        try:
            # Obtener candidatos
            candidates = self.candidate_service.get_candidates(page=1, per_page=5)
            print(f"🏃 Candidatos: {candidates['pagination']['total']} total")
            
            for candidate in candidates['data']:
                party = candidate['partido_siglas'] or 'Independiente'
                print(f"   • {candidate['nombre_completo']} ({party}) - {candidate['cargo_aspirado']}")
            
            # Obtener partidos políticos
            parties = self.candidate_service.get_political_parties()
            print(f"\n🏛️  Partidos políticos: {len(parties)} registrados")
            for party in parties[:5]:  # Mostrar solo los primeros 5
                print(f"   • {party['siglas']}: {party['nombre_oficial']}")
            
            # Obtener coaliciones
            coalitions = self.candidate_service.get_coalitions()
            print(f"\n🤝 Coaliciones: {len(coalitions)} registradas")
            for coalition in coalitions:
                parties_str = ', '.join(coalition['partidos_siglas'])
                print(f"   • {coalition['nombre_coalicion']} ({parties_str})")
            
        except Exception as e:
            print(f"❌ Error en demo de candidatos: {e}")
    
    def demo_reports_module(self):
        """Demo del módulo de reportes"""
        print("\n📊 DEMO: MÓDULO REPORTES")
        print("-" * 40)
        
        try:
            # Generar resumen electoral
            summary = self.report_service.generate_electoral_summary()
            
            print("📈 Resumen electoral generado:")
            general_stats = summary.get('general_stats', {})
            print(f"   • Total candidatos: {general_stats.get('total_candidates', 0)}")
            print(f"   • Total partidos: {general_stats.get('total_parties', 0)}")
            print(f"   • Total mesas: {general_stats.get('total_mesas', 0)}")
            
            # Progreso de recolección
            progress = summary.get('collection_progress', {})
            total = progress.get('total', 0)
            if total > 0:
                print(f"\n📊 Progreso de recolección:")
                for estado, count in progress.items():
                    if not estado.endswith('_percentage') and estado != 'total':
                        percentage = progress.get(f"{estado}_percentage", 0)
                        print(f"   • {estado.title()}: {count} ({percentage}%)")
            
            # Plantillas disponibles
            templates = self.report_service.get_report_templates()
            print(f"\n📋 Plantillas de reportes: {len(templates)} disponibles")
            for template in templates[:3]:  # Mostrar solo las primeras 3
                print(f"   • {template['name']}: {template['description']}")
            
        except Exception as e:
            print(f"❌ Error en demo de reportes: {e}")
    
    def demo_dashboard_module(self):
        """Demo del módulo de dashboard"""
        print("\n📈 DEMO: MÓDULO DASHBOARD")
        print("-" * 40)
        
        try:
            # Simular usuario admin
            admin_user_id = 1
            
            # Obtener vista general del dashboard
            overview = self.dashboard_service.get_dashboard_overview(admin_user_id)
            
            print("🎛️  Dashboard overview generado:")
            print(f"   • Rol de usuario: {overview.get('user_role', 'N/A')}")
            
            quick_stats = overview.get('quick_stats', {})
            print(f"   • Candidatos totales: {quick_stats.get('total_candidates', 0)}")
            print(f"   • Mesas totales: {quick_stats.get('total_mesas', 0)}")
            print(f"   • Usuarios activos: {quick_stats.get('active_users', 0)}")
            
            # Widget de progreso electoral
            progress_widget = self.dashboard_service.get_electoral_progress_widget()
            print(f"\n📊 Widget de progreso electoral:")
            print(f"   • Total mesas: {progress_widget.get('total_mesas', 0)}")
            
            progress_percentages = progress_widget.get('progress_percentages', {})
            for estado, percentage in progress_percentages.items():
                print(f"   • {estado.title()}: {percentage}%")
            
            # Widget de ranking de candidatos
            ranking_widget = self.dashboard_service.get_candidate_ranking_widget(limit=3)
            candidates = ranking_widget.get('candidates', [])
            
            if candidates:
                print(f"\n🏆 Top candidatos:")
                for i, candidate in enumerate(candidates, 1):
                    party = candidate.get('partido_siglas', 'IND')
                    votes = candidate.get('total_votos', 0)
                    print(f"   {i}. {candidate['nombre']} ({party}) - {votes} votos")
            
        except Exception as e:
            print(f"❌ Error en demo de dashboard: {e}")
    
    def run_full_demo(self):
        """Ejecutar demo completo"""
        print("🚀 DEMO COMPLETO DEL SISTEMA ELECTORAL ERP")
        print("=" * 60)
        
        demos = [
            ("Vista General", self.show_system_overview),
            ("Autenticación", self.demo_authentication),
            ("Módulo Electoral", self.demo_electoral_module),
            ("Módulo Candidatos", self.demo_candidates_module),
            ("Módulo Reportes", self.demo_reports_module),
            ("Módulo Dashboard", self.demo_dashboard_module)
        ]
        
        for demo_name, demo_func in demos:
            try:
                demo_func()
            except Exception as e:
                print(f"\n❌ Error en {demo_name}: {e}")
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETADO")
        print("=" * 60)
        print("\n📋 Para usar el sistema completo:")
        print("1. python run.py                 # Iniciar servidor web")
        print("2. Abrir http://localhost:5000   # Acceder al sistema")
        print("3. Login: admin / admin123       # Credenciales por defecto")
        print("\n🔗 Endpoints principales:")
        print("• GET  /api/system/info          # Información del sistema")
        print("• POST /api/auth/login           # Autenticación")
        print("• GET  /api/electoral/processes  # Procesos electorales")
        print("• GET  /api/candidates/candidates # Candidatos")
        print("• GET  /api/dashboard/overview   # Dashboard principal")

def main():
    """Función principal"""
    try:
        demo = SystemDemo()
        demo.run_full_demo()
    except Exception as e:
        print(f"❌ Error ejecutando demo: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)