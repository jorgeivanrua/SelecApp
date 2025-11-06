#!/usr/bin/env python3
"""
Script para corregir referencias problemáticas en templates de roles
"""

import os
import re
from pathlib import Path

def fix_template_urls():
    """Corregir todas las referencias problemáticas a url_for en templates"""
    
    templates_dir = Path("templates/roles")
    
    # Mapeo de correcciones comunes
    url_fixes = {
        # Super Admin
        r"url_for\('super_admin\.dashboard'\)": "url_for('dashboard_role', role='super_admin')",
        r"url_for\('super_admin\.users'\)": "'/users'",
        r"url_for\('super_admin\.roles'\)": "'/users/roles'",
        r"url_for\('super_admin\.system'\)": "'/settings'",
        r"url_for\('super_admin\.processes'\)": "'/electoral'",
        r"url_for\('super_admin\.candidates'\)": "'/candidates'",
        r"url_for\('super_admin\.parties'\)": "'/parties'",
        r"url_for\('super_admin\.reports'\)": "'/reports'",
        r"url_for\('super_admin\.create_user'\)": "'/users/new'",
        r"url_for\('super_admin\.create_process'\)": "'/electoral/new'",
        r"url_for\('super_admin\.system_backup'\)": "'/system/backup'",
        r"url_for\('super_admin\.audit_logs'\)": "'/audit/logs'",
        r"url_for\('super_admin\.system_settings'\)": "'/settings'",
        
        # Admin Departamental
        r"url_for\('admin_dept\.dashboard'\)": "url_for('dashboard_role', role='admin_departamental')",
        r"url_for\('admin_dept\.municipalities'\)": "'/municipalities'",
        r"url_for\('admin_dept\.electoral_posts'\)": "'/electoral-posts'",
        r"url_for\('admin_dept\.mesas'\)": "'/tables'",
        r"url_for\('admin_dept\.coordinators'\)": "'/coordinators'",
        r"url_for\('admin_dept\.witnesses'\)": "'/witnesses'",
        r"url_for\('admin_dept\.candidates'\)": "'/candidates'",
        r"url_for\('admin_dept\.reports'\)": "'/reports'",
        r"url_for\('admin_dept\.assign_personnel'\)": "'/personnel/assign'",
        r"url_for\('admin_dept\.create_process'\)": "'/electoral/new'",
        
        # Admin Municipal
        r"url_for\('admin_mun\.dashboard'\)": "url_for('dashboard_role', role='admin_municipal')",
        r"url_for\('admin_mun\.puestos'\)": "'/voting-stations'",
        r"url_for\('admin_mun\.mesas'\)": "'/tables'",
        r"url_for\('admin_mun\.assign_witnesses'\)": "'/witnesses/assign'",
        r"url_for\('admin_mun\.candidates'\)": "'/candidates/local'",
        r"url_for\('admin_mun\.reports'\)": "'/reports/municipal'",
        r"url_for\('admin_mun\.export_municipal_data'\)": "'/reports/export'",
        
        # Coordinador Electoral
        r"url_for\('electoral\.create'\)": "'/electoral/new'",
        r"url_for\('candidates\.create'\)": "'/candidates/new'",
        r"url_for\('reports\.generate'\)": "'/reports/generate'",
        r"url_for\('electoral\.monitor'\)": "'/electoral/monitor'",
        
        # Jurado de Votación
        r"url_for\('electoral\.my_table'\)": "'/voting/my-table'",
        r"url_for\('electoral\.voting'\)": "'/voting/register'",
        
        # Testigo de Mesa
        r"url_for\('testigo\.dashboard'\)": "url_for('dashboard_role', role='testigo_mesa')",
        r"url_for\('testigo\.capture'\)": "'/voting/capture'",
        r"url_for\('testigo\.results'\)": "'/voting/results'",
        r"url_for\('testigo\.help'\)": "'/help'",
        r"url_for\('testigo\.certificate'\)": "'/voting/certificate'",
        r"url_for\('testigo\.manual'\)": "'/help/manual'",
        r"url_for\('testigo\.faq'\)": "'/help/faq'",
    }
    
    fixed_files = []
    
    for role_dir in templates_dir.iterdir():
        if role_dir.is_dir():
            dashboard_file = role_dir / "dashboard.html"
            if dashboard_file.exists():
                print(f"Procesando: {dashboard_file}")
                
                # Leer contenido
                with open(dashboard_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Aplicar correcciones
                for pattern, replacement in url_fixes.items():
                    content = re.sub(pattern, replacement, content)
                
                # Solo escribir si hubo cambios
                if content != original_content:
                    with open(dashboard_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_files.append(str(dashboard_file))
                    print(f"  ✅ Corregido")
                else:
                    print(f"  ℹ️  Sin cambios necesarios")
    
    return fixed_files

def add_missing_routes_to_app():
    """Agregar rutas faltantes al app.py"""
    
    additional_routes = '''
    # Rutas adicionales para dashboards específicos
    @app.route('/coordination')
    def coordination():
        """Coordinación de procesos electorales"""
        return render_template('dashboard_generic.html',
                             user_role='coordinador_electoral',
                             role_name='Coordinación de Procesos',
                             stats={'active_processes': 2, 'pending_tasks': 5, 'completion': 78},
                             quick_actions=[
                                 {'name': 'Nuevo Proceso', 'url': '/electoral/new', 'icon': 'fas fa-plus'},
                                 {'name': 'Cronograma', 'url': '/schedule', 'icon': 'fas fa-calendar'},
                                 {'name': 'Monitorear', 'url': '/monitor', 'icon': 'fas fa-eye'}
                             ])
    
    @app.route('/schedule')
    def schedule():
        """Cronograma electoral"""
        return render_template('dashboard_generic.html',
                             user_role='coordinador_electoral',
                             role_name='Cronograma Electoral',
                             stats={'scheduled_events': 12, 'completed': 8, 'pending': 4},
                             quick_actions=[
                                 {'name': 'Nuevo Evento', 'url': '/schedule/new', 'icon': 'fas fa-plus'},
                                 {'name': 'Ver Calendario', 'url': '/calendar', 'icon': 'fas fa-calendar-alt'},
                                 {'name': 'Recordatorios', 'url': '/reminders', 'icon': 'fas fa-bell'}
                             ])
    
    @app.route('/progress')
    def progress():
        """Supervisar avance"""
        return render_template('dashboard_generic.html',
                             user_role='coordinador_electoral',
                             role_name='Supervisión de Avance',
                             stats={'overall_progress': 78, 'on_track': 85, 'delayed': 15},
                             quick_actions=[
                                 {'name': 'Ver Detalles', 'url': '/progress/details', 'icon': 'fas fa-chart-line'},
                                 {'name': 'Generar Reporte', 'url': '/reports/progress', 'icon': 'fas fa-file-alt'},
                                 {'name': 'Alertas', 'url': '/alerts', 'icon': 'fas fa-exclamation-triangle'}
                             ])
    
    @app.route('/electoral')
    def electoral():
        """Procesos electorales"""
        return render_template('dashboard_generic.html',
                             user_role='admin',
                             role_name='Procesos Electorales',
                             stats={'active_processes': 3, 'total_processes': 15, 'completion': 85},
                             quick_actions=[
                                 {'name': 'Nuevo Proceso', 'url': '/electoral/new', 'icon': 'fas fa-plus'},
                                 {'name': 'Ver Todos', 'url': '/electoral/list', 'icon': 'fas fa-list'},
                                 {'name': 'Configurar', 'url': '/electoral/config', 'icon': 'fas fa-cogs'}
                             ])
    
    @app.route('/candidates')
    def candidates():
        """Gestión de candidatos"""
        return render_template('dashboard_generic.html',
                             user_role='admin',
                             role_name='Gestión de Candidatos',
                             stats={'total_candidates': 45, 'approved': 42, 'pending': 3},
                             quick_actions=[
                                 {'name': 'Nuevo Candidato', 'url': '/candidates/new', 'icon': 'fas fa-user-plus'},
                                 {'name': 'Aprobar Pendientes', 'url': '/candidates/approve', 'icon': 'fas fa-check'},
                                 {'name': 'Ver Lista', 'url': '/candidates/list', 'icon': 'fas fa-list'}
                             ])
    
    @app.route('/reports')
    def reports():
        """Reportes del sistema"""
        return render_template('dashboard_generic.html',
                             user_role='admin',
                             role_name='Reportes del Sistema',
                             stats={'generated_reports': 25, 'scheduled': 8, 'pending': 3},
                             quick_actions=[
                                 {'name': 'Nuevo Reporte', 'url': '/reports/new', 'icon': 'fas fa-plus'},
                                 {'name': 'Programar', 'url': '/reports/schedule', 'icon': 'fas fa-clock'},
                                 {'name': 'Exportar', 'url': '/reports/export', 'icon': 'fas fa-download'}
                             ])
'''
    
    # Leer app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar donde insertar las rutas
    insert_point = content.find("@app.route('/logout')")
    
    if insert_point != -1:
        # Insertar antes de logout
        new_content = content[:insert_point] + additional_routes + "\n    " + content[insert_point:]
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Rutas adicionales agregadas a app.py")
    else:
        print("❌ No se pudo encontrar el punto de inserción en app.py")

if __name__ == "__main__":
    print("🔧 Corrigiendo templates de roles...")
    fixed_files = fix_template_urls()
    
    if fixed_files:
        print(f"\n✅ Se corrigieron {len(fixed_files)} archivos:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("\nℹ️  No se encontraron archivos que necesiten corrección")
    
    print("\n🔧 Agregando rutas faltantes...")
    add_missing_routes_to_app()
    
    print("\n✅ Correcciones completadas!")