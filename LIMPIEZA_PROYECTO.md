# Limpieza del Proyecto - Sistema Electoral Caquetá

## Fecha: 7 de noviembre de 2025

## Resumen de Limpieza

Se realizó una limpieza exhaustiva del proyecto, moviendo **aproximadamente 140 archivos innecesarios** a la carpeta `_archivos_para_eliminar/`.

## Archivos Movidos por Categoría

### 1. Bases de Datos de Backup (7 archivos)
Backups antiguos de la base de datos que ya no son necesarios.

### 2. Configuraciones Duplicadas (4 archivos)
Archivos de configuración alternativos que duplicaban funcionalidad.

### 3. Scripts de Prueba (27 archivos)
Scripts de testing antiguos y duplicados.

### 4. Scripts de Creación de Tablas (10 archivos)
Scripts ya ejecutados para crear tablas en la base de datos.

### 5. Scripts de Verificación (10 archivos)
Scripts de verificación antiguos ya no necesarios.

### 6. Documentación Temporal (38 archivos)
Documentos de progreso y estado que ya fueron consolidados.

### 7. Scripts de Demo (7 archivos)
Scripts de demostración antiguos.

### 8. Scripts de Instalación (5 archivos)
Scripts de instalación duplicados.

### 9. Scripts de Migración (5 archivos)
Scripts de migración y fixes ya aplicados.

### 10. Archivos de Inicio Duplicados (3 archivos)
Scripts de inicio alternativos.

### 11. Configuración Docker (7 archivos)
Archivos de Docker no utilizados actualmente.

### 12. Documentación Duplicada (4 archivos)
Documentos de diseño y tareas duplicados.

### 13. Archivos de Ejemplo (8 archivos)
Imágenes y archivos de prueba antiguos.

### 14. Modelos Duplicados (2 archivos)
Archivos de modelos que duplicaban funcionalidad.

### 15. README Duplicados (3 archivos)
Documentación README alternativa.

## Estructura Limpia del Proyecto

```
sistema-electoral/
├── .kiro/                          # Especificaciones y configuración Kiro
│   └── specs/                      # Specs del proyecto
├── api/                            # APIs REST
├── config/                         # Configuraciones
├── core/                           # Funcionalidades core
├── modules/                        # Módulos del sistema
│   ├── admin/                      # Módulo de administración
│   ├── candidates/                 # Módulo de candidatos
│   ├── coordination/               # Módulo de coordinación
│   ├── dashboard/                  # Módulo de dashboard
│   ├── electoral/                  # Módulo electoral
│   ├── reports/                    # Módulo de reportes
│   ├── testigo/                    # Módulo testigo electoral
│   └── users/                      # Módulo de usuarios
├── scripts/                        # Scripts de utilidad
├── services/                       # Servicios del sistema
├── static/                         # Archivos estáticos (CSS, JS, imágenes)
├── templates/                      # Plantillas HTML
├── tests/                          # Tests organizados
├── uploads/                        # Archivos subidos
├── _archivos_para_eliminar/        # Archivos movidos para eliminar
├── app.py                          # Aplicación principal
├── config.py                       # Configuración principal
├── caqueta_electoral.db            # Base de datos principal
├── create_excel_template.py        # Crear plantilla Excel
├── divipola_corregido.csv          # Datos DIVIPOLA
├── download_tesseract.ps1          # Descargador Tesseract
├── install_tesseract_simple.ps1    # Instalador Tesseract
├── plantilla_datos_electorales.xlsx # Plantilla Excel
├── README.md                       # Documentación principal
├── REQUERIMIENTOS_SISTEMA_COMPLETO.md # Requerimientos consolidados
├── requirements.txt                # Dependencias Python
├── requirements_ocr.txt            # Dependencias OCR
├── run.py                          # Script de inicio
├── setup_demo_users.py             # Crear usuarios demo
├── start_admin.py                  # Iniciar aplicación
├── test_all_roles.py               # Pruebas de roles
├── test_ocr.py                     # Pruebas OCR
└── wsgi.py                         # WSGI para producción
```

## Archivos Principales Mantenidos

### Aplicación
- `app.py` - Aplicación Flask principal
- `config.py` - Configuración del sistema
- `wsgi.py` - WSGI para producción
- `run.py` - Script de inicio

### Base de Datos
- `caqueta_electoral.db` - Base de datos SQLite principal

### Scripts Útiles
- `setup_demo_users.py` - Crear usuarios de demostración
- `start_admin.py` - Iniciar aplicación
- `test_all_roles.py` - Pruebas de todos los roles
- `test_ocr.py` - Pruebas del sistema OCR
- `create_excel_template.py` - Crear plantilla Excel

### Instalación OCR
- `install_tesseract_simple.ps1` - Instalador automatizado de Tesseract
- `download_tesseract.ps1` - Descargador de Tesseract

### Documentación
- `README.md` - Documentación principal del proyecto
- `REQUERIMIENTOS_SISTEMA_COMPLETO.md` - Requerimientos consolidados
- `.kiro/specs/` - Especificaciones detalladas

### Configuración
- `.env.example` - Ejemplo de variables de entorno
- `.env.production` - Variables de entorno para producción
- `requirements.txt` - Dependencias Python
- `requirements_ocr.txt` - Dependencias OCR específicas

### Datos
- `divipola_corregido.csv` - Datos DIVIPOLA de Colombia
- `plantilla_datos_electorales.xlsx` - Plantilla para importar datos

## Beneficios de la Limpieza

1. **Claridad**: Estructura de proyecto más clara y fácil de navegar
2. **Mantenibilidad**: Menos archivos duplicados = menos confusión
3. **Rendimiento**: Menos archivos para indexar y buscar
4. **Profesionalismo**: Proyecto más organizado y profesional
5. **Git**: Historial más limpio y commits más relevantes

## Próximos Pasos

### Para Eliminar Definitivamente
Si estás seguro de que no necesitas los archivos movidos:

```powershell
Remove-Item -Recurse -Force _archivos_para_eliminar
```

### Para Recuperar Archivos
Si necesitas recuperar algún archivo, puedes:

1. Moverlo de vuelta desde `_archivos_para_eliminar/`
2. Recuperarlo del historial de Git (si ya fue eliminado)

## Recomendación

**Mantén la carpeta `_archivos_para_eliminar/` por 1-2 semanas** para asegurarte de que no necesitas ningún archivo. Después de ese período, puedes eliminarla de forma segura.

## Verificación

Para verificar que el sistema sigue funcionando correctamente después de la limpieza:

```powershell
# Iniciar el servidor
python start_admin.py

# En otra terminal, ejecutar pruebas
python test_all_roles.py
python test_ocr.py
```

## Notas

- Todos los archivos movidos están documentados en `_archivos_para_eliminar/README_ARCHIVOS_MOVIDOS.md`
- El historial de Git mantiene todos los archivos por si necesitas recuperar algo
- La funcionalidad del sistema NO se ve afectada por esta limpieza
