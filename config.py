"""
Configuración del Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Base de datos
    DATABASE_URL: str = "sqlite:///caqueta_electoral.db"
    DATABASE_ECHO: bool = True  # Para desarrollo, False en producción
    
    # Aplicación
    APP_NAME: str = "Sistema de Recolección Inicial - Caquetá"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Departamento específico
    DEPARTAMENTO_CODIGO: str = "18"
    DEPARTAMENTO_NOMBRE: str = "CAQUETÁ"
    
    # Archivos de datos
    DIVIPOLA_CSV_PATH: str = "divipola_corregido.csv"
    
    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuración de seguridad
    SECRET_KEY: str = "caqueta-electoral-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración de archivos
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Configuración de mapas
    DEFAULT_MAP_CENTER_LAT: float = 1.6143  # Florencia, Caquetá
    DEFAULT_MAP_CENTER_LNG: float = -75.6061
    DEFAULT_MAP_ZOOM: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

# Configuración específica para Caquetá
CAQUETA_CONFIG = {
    "departamento": {
        "codigo": "18",
        "nombre": "CAQUETÁ",
        "capital": "FLORENCIA"
    },
    "municipios_principales": [
        "FLORENCIA",
        "SAN VICENTE DEL CAGUAN",
        "PUERTO RICO",
        "EL PAUJIL",
        "LA MONTAÑITA",
        "CURILLO",
        "EL DONCELLO",
        "BELEN DE LOS ANDAQUIES",
        "ALBANIA",
        "MORELIA",
        "MILAN",
        "SAN JOSE DEL FRAGUA",
        "VALPARAISO",
        "CARTAGENA DEL CHAIRA",
        "SOLANO",
        "SOLITA"
    ],
    "coordenadas_centro": {
        "latitud": 1.6143,
        "longitud": -75.6061
    },
    "zona_horaria": "America/Bogota"
}

def get_database_url() -> str:
    """Obtiene la URL de la base de datos"""
    return settings.DATABASE_URL

def get_upload_directory() -> str:
    """Obtiene el directorio de uploads y lo crea si no existe"""
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

def is_development() -> bool:
    """Verifica si estamos en modo desarrollo"""
    return settings.DEBUG

def get_caqueta_municipalities() -> list:
    """Obtiene la lista de municipios de Caquetá"""
    return CAQUETA_CONFIG["municipios_principales"]

def get_map_center() -> tuple:
    """Obtiene las coordenadas del centro del mapa para Caquetá"""
    coords = CAQUETA_CONFIG["coordenadas_centro"]
    return (coords["latitud"], coords["longitud"])

if __name__ == "__main__":
    print("=== Configuración del Sistema Electoral - Caquetá ===")
    print(f"Aplicación: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Base de datos: {settings.DATABASE_URL}")
    print(f"Departamento: {CAQUETA_CONFIG['departamento']['nombre']}")
    print(f"Capital: {CAQUETA_CONFIG['departamento']['capital']}")
    print(f"Municipios configurados: {len(CAQUETA_CONFIG['municipios_principales'])}")
    print(f"Centro del mapa: {get_map_center()}")
    print(f"Modo desarrollo: {is_development()}")