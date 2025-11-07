# Archivos Movidos para Eliminación

Este directorio contiene archivos que ya no son necesarios en el proyecto principal.

## Fecha de Limpieza
7 de noviembre de 2025

## Categorías de Archivos Movidos

### 1. Bases de Datos de Backup (7 archivos)
- `caqueta_electoral_backup_20251106_010840.db`
- `caqueta_electoral_backup_20251106_010901.db`
- `caqueta_electoral_old_20251106_100624.db`
- `caqueta_electoral_old_20251106_145250.db`
- `electoral_system_prod.db`
- `electoral_system.db`
- `electoral_system.log`

**Razón**: Backups antiguos ya no necesarios. La base de datos actual es `caqueta_electoral.db`

### 2. Archivos de Configuración Duplicados (4 archivos)
- `app_modular.py`
- `app_production.py`
- `config_production.py`
- `app_config.py`

**Razón**: El archivo principal `app.py` y `config.py` son suficientes

### 3. Scripts de Prueba Duplicados (27 archivos)
- `test_admin_service.py`
- `test_apis.py`
- `test_candidate_management.py`
- `test_complete_functionality.py`
- `test_completo_sistema.py`
- `test_coordination_system.py`
- `test_correcciones.py`
- `test_create_candidate.py`
- `test_dashboard_functionality.py`
- `test_dashboards_completo.py`
- `test_dashboards.py`
- `test_excel_import.py`
- `test_exhaustive_review.py`
- `test_final_optimizado.py`
- `test_forms_functionality.py`
- `test_login_comprehensive.py`
- `test_login_direct.py`
- `test_login_system.py`
- `test_login.py`
- `test_logout_only.py`
- `test_modular_system.py`
- `test_municipal_coordination.py`
- `test_priority_system.py`
- `test_system.py`
- `test_users_generation.py`
- `test_utf8_production.py`
- `test_web_complete.py`

**Razón**: Scripts de prueba antiguos. Los scripts actuales son `test_all_roles.py` y `test_ocr.py`, más los tests en `/tests/`

### 4. Scripts de Creación de Tablas (10 archivos)
- `create_admin_tables.py`
- `create_candidate_tables.py`
- `create_coordination_tables.py`
- `create_municipal_coordination_tables.py`
- `create_priority_tables.py`
- `create_testigo_tables.py`
- `create_complete_database.py`
- `create_missing_routes.py`
- `add_e14_table.py`
- `fix_coordination_tables.py`

**Razón**: Ya ejecutados. Las tablas están creadas en la base de datos actual

### 5. Scripts de Verificación (10 archivos)
- `check_candidates.py`
- `check_coordination_tables.py`
- `check_database.py`
- `check_roles.py`
- `verify_data.py`
- `verify_hash.py`
- `verify_production.py`
- `verify_users.py`
- `final_system_test.py`
- `final_verification.py`

**Razón**: Scripts de verificación antiguos ya no necesarios

### 6. Documentación Duplicada (38 archivos)
- `ADMIN_ACCESS.md`
- `ARQUITECTURA_MODULAR.md`
- `CANDIDATOS_SISTEMA_COMPLETADO.md`
- `COORDINACION_MUNICIPAL_IMPLEMENTADA.md`
- `DASHBOARD_FUNCTIONALITY_REPORT.md`
- `DASHBOARDS_FUNCIONALIDAD_COMPLETA.md`
- `DASHBOARDS_IMPLEMENTADOS.md`
- `DATOS_CARGADOS.md`
- `ESTADO_FINAL_SISTEMA.md`
- `HTML_REQUIREMENTS_GAP_ANALYSIS.md`
- `INSTALL_OCR.md`
- `MIGRACION_COMPLETADA.md`
- `MODULO_REPORTES_COMPLETADO.md`
- `MODULOS_USUARIOS_ADMIN_COMPLETADOS.md`
- `OCR_IMPLEMENTATION_SUMMARY.md`
- `OCR_INSTALLATION_STATUS.md`
- `OCR_READY.md`
- `REPORTE_REVISION_COMPLETA.md`
- `REQUERIMIENTOS_TESTIGO_CONSOLIDADOS.md`
- `RESUMEN_EJECUTIVO.md`
- `RESUMEN_REVISION_FINAL.md`
- `REVISION_COMPLETA_SISTEMA.md`
- `REVISION_EXHAUSTIVA_FORMULARIOS.md`
- `ROLES_FINAL_CORRECTED.md`
- `ROLES_FUNCTIONALITY_ANALYSIS.md`
- `ROLES_UPDATED_STRUCTURE.md`
- `ROLES_VERIFICATION_COMPLETE.md`
- `SISTEMA_COMPLETO_FUNCIONAL.md`
- `SISTEMA_COMPLETO_UV.md`
- `SISTEMA_ELECTORAL_COMPLETADO.md`
- `SISTEMA_LISTO.md`
- `SISTEMA_LOGIN_CORREGIDO.md`
- `SISTEMA_MODULAR_PROGRESO_FINAL.md`
- `SYSTEM_SUMMARY.md`
- `TEMPLATES_ANALYSIS.md`
- `TEMPLATES_CLEANUP_REPORT.md`
- `TESTIGO_DASHBOARD_REQUIREMENTS.md`
- `TESTIGO_FLUJO_CORRECTO.md`
- `TESTIGO_OCR_WORKFLOW.md`

**Razón**: Documentación de progreso temporal. La documentación actual está en `REQUERIMIENTOS_SISTEMA_COMPLETO.md` y `.kiro/specs/`

### 7. Scripts de Demo y Utilidades (7 archivos)
- `demo_completo.py`
- `demo_dashboards.py`
- `demo.py`
- `quick_demo_test.py`
- `database_summary.py`
- `query_database.py`
- `revision_completa.py`

**Razón**: Scripts de demostración antiguos

### 8. Scripts de Instalación y Setup (5 archivos)
- `install_complete.py`
- `install_uv.py`
- `install.py`
- `setup_uv.py`
- `create_demo_users.py`

**Razón**: El script actual es `setup_demo_users.py`

### 9. Scripts de Migración y Fix (5 archivos)
- `migrate_database.py`
- `recreate_database.py`
- `fix_login_system.py`
- `fix_templates.py`
- `login_fix.py`

**Razón**: Migraciones y fixes ya aplicados

### 10. Archivos de Inicio Duplicados (3 archivos)
- `start_production.py`
- `initialization_service.py`
- `init_db.py`

**Razón**: El script actual es `start_admin.py`

### 11. Configuración Docker (7 archivos)
- `docker-compose.yml`
- `Dockerfile`
- `entrypoint.sh`
- `nginx.conf`
- `gunicorn.conf.py`
- `deploy.sh`
- `init_database.sql`

**Razón**: No se está usando Docker actualmente

### 12. Documentación y Diseño Duplicados (4 archivos)
- `design.md`
- `tasks.md`
- `requirements.md`
- `setup_github.md`

**Razón**: La documentación actual está en `.kiro/specs/`

### 13. Archivos de Ejemplo y Test (8 archivos)
- `E14_basico_001.png`
- `E14_basico_002.png`
- `E14_basico.pdf`
- `E24_basico.pdf`
- `test_ocr_image.png`
- `test_ocr_procesada.png`
- `muestra_mesas_caqueta.json`
- `role_verification_report.json`

**Razón**: Archivos de prueba antiguos

### 14. Modelos y APIs Duplicados (2 archivos)
- `models.py`
- `api_endpoints.py`

**Razón**: Los modelos están en `/modules/` y las APIs en `/api/`

### 15. README Duplicados (3 archivos)
- `README_PRODUCCION.md`
- `README_UV.md`
- `TECHNICAL_DOCUMENTATION.md`

**Razón**: El README principal es suficiente

## Total de Archivos Movidos
**140 archivos aproximadamente**

## Archivos Principales que SE MANTIENEN en el Proyecto

### Archivos de Aplicación
- `app.py` - Aplicación principal
- `config.py` - Configuración
- `wsgi.py` - WSGI para producción
- `run.py` - Script de inicio

### Base de Datos
- `caqueta_electoral.db` - Base de datos principal

### Scripts Útiles
- `setup_demo_users.py` - Crear usuarios de demostración
- `start_admin.py` - Iniciar aplicación
- `test_all_roles.py` - Pruebas de roles
- `test_ocr.py` - Pruebas de OCR
- `create_excel_template.py` - Crear plantilla Excel

### Instalación OCR
- `install_tesseract_simple.ps1` - Instalador de Tesseract
- `download_tesseract.ps1` - Descargador de Tesseract

### Documentación Principal
- `README.md` - Documentación principal
- `REQUERIMIENTOS_SISTEMA_COMPLETO.md` - Requerimientos consolidados
- `.kiro/specs/` - Especificaciones del proyecto

### Directorios de Código
- `/modules/` - Módulos del sistema
- `/api/` - APIs REST
- `/config/` - Configuraciones
- `/core/` - Funcionalidades core
- `/services/` - Servicios
- `/templates/` - Plantillas HTML
- `/static/` - Archivos estáticos
- `/tests/` - Tests organizados

## Recomendación
Estos archivos pueden ser eliminados de forma segura. Si necesitas recuperar alguno, están en el historial de Git.

Para eliminar definitivamente esta carpeta:
```powershell
Remove-Item -Recurse -Force _archivos_para_eliminar
```
