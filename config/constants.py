"""
Constantes del sistema electoral
"""

# Roles del sistema
ROLES = {
    'SUPER_ADMIN': 'super_admin',
    'ADMIN_DEPARTAMENTAL': 'admin_departamental',
    'ADMIN_MUNICIPAL': 'admin_municipal',
    'COORDINADOR_ELECTORAL': 'coordinador_electoral',
    'COORDINADOR_MUNICIPAL': 'coordinador_municipal',
    'COORDINADOR_PUESTO': 'coordinador_puesto',
    'TESTIGO_ELECTORAL': 'testigo_electoral',
    'JURADO_VOTACION': 'jurado_votacion',
    'TESTIGO_MESA': 'testigo_mesa',
    'AUDITOR_ELECTORAL': 'auditor_electoral',
    'OBSERVADOR_INTERNACIONAL': 'observador_internacional'
}

# Estados de recolección
ESTADOS_RECOLECCION = {
    'PENDIENTE': 'pendiente',
    'IMAGEN_CAPTURADA': 'imagen_capturada',
    'PROCESANDO_OCR': 'procesando_ocr',
    'DATOS_RECONOCIDOS': 'datos_reconocidos',
    'VALIDANDO_MANUAL': 'validando_manual',
    'CAPTURADO': 'capturado',
    'EN_REVISION': 'en_revision',
    'VALIDADO': 'validado',
    'RECHAZADO': 'rechazado',
    'CONSOLIDADO': 'consolidado',
    'CERRADO': 'cerrado'
}

# Tipos de elección
TIPOS_ELECCION = {
    'CONCEJOS_JUVENTUDES': 'concejos_juventudes',
    'SENADO': 'senado',
    'CAMARA': 'camara',
    'CITREP': 'citrep',
    'PRESIDENCIALES': 'presidenciales',
    'GOBERNACION': 'gobernacion',
    'ASAMBLEA': 'asamblea',
    'ALCALDIA': 'alcaldia',
    'CONCEJO': 'concejo',
    'EDILES': 'ediles'
}

# Configuración de base de datos
DEFAULT_DB_PATH = 'electoral_system.db'
BACKUP_DB_PATH = 'backups/'

# Configuración de archivos
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB