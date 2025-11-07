#!/usr/bin/env python3
"""
Script para crear tablas de priorización del Sistema Electoral ERP
Permite al administrador configurar prioridades para la recolección de datos
"""

import sqlite3
from datetime import datetime

def create_priority_tables():
    """Crear tablas de priorización"""
    
    print("🔄 Creando tablas de priorización...")
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Tabla de configuración de prioridades
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion_prioridades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            activa INTEGER DEFAULT 1,
            fecha_inicio DATE,
            fecha_fin DATE,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)
    
    # Tabla de prioridades de partidos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prioridades_partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            configuracion_id INTEGER NOT NULL,
            partido_id INTEGER NOT NULL,
            prioridad INTEGER NOT NULL DEFAULT 1, -- 1=Alta, 2=Media, 3=Baja
            activo INTEGER DEFAULT 1,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (configuracion_id) REFERENCES configuracion_prioridades(id),
            FOREIGN KEY (partido_id) REFERENCES partidos_politicos(id),
            UNIQUE(configuracion_id, partido_id)
        )
    """)
    
    # Tabla de prioridades de coaliciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prioridades_coaliciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            configuracion_id INTEGER NOT NULL,
            coalicion_id INTEGER NOT NULL,
            prioridad INTEGER NOT NULL DEFAULT 1, -- 1=Alta, 2=Media, 3=Baja
            activo INTEGER DEFAULT 1,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (configuracion_id) REFERENCES configuracion_prioridades(id),
            FOREIGN KEY (coalicion_id) REFERENCES coaliciones(id),
            UNIQUE(configuracion_id, coalicion_id)
        )
    """)
    
    # Tabla de prioridades de candidatos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prioridades_candidatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            configuracion_id INTEGER NOT NULL,
            candidato_id INTEGER NOT NULL,
            prioridad INTEGER NOT NULL DEFAULT 1, -- 1=Alta, 2=Media, 3=Baja
            activo INTEGER DEFAULT 1,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (configuracion_id) REFERENCES configuracion_prioridades(id),
            FOREIGN KEY (candidato_id) REFERENCES candidatos(id),
            UNIQUE(configuracion_id, candidato_id)
        )
    """)
    
    # Tabla de prioridades de procesos electorales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prioridades_procesos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            configuracion_id INTEGER NOT NULL,
            proceso_id INTEGER NOT NULL,
            prioridad INTEGER NOT NULL DEFAULT 1, -- 1=Alta, 2=Media, 3=Baja
            activo INTEGER DEFAULT 1,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (configuracion_id) REFERENCES configuracion_prioridades(id),
            FOREIGN KEY (proceso_id) REFERENCES procesos_electorales(id),
            UNIQUE(configuracion_id, proceso_id)
        )
    """)
    
    # Tabla de prioridades de municipios (para enfocar recolección geográfica)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prioridades_municipios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            configuracion_id INTEGER NOT NULL,
            municipio_id INTEGER NOT NULL,
            prioridad INTEGER NOT NULL DEFAULT 1, -- 1=Alta, 2=Media, 3=Baja
            activo INTEGER DEFAULT 1,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (configuracion_id) REFERENCES configuracion_prioridades(id),
            FOREIGN KEY (municipio_id) REFERENCES municipios(id),
            UNIQUE(configuracion_id, municipio_id)
        )
    """)
    
    # Tabla de metas de recolección por prioridad
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas_recoleccion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            configuracion_id INTEGER NOT NULL,
            tipo_entidad TEXT NOT NULL, -- 'partido', 'coalicion', 'candidato', 'proceso', 'municipio'
            entidad_id INTEGER NOT NULL,
            meta_porcentaje INTEGER DEFAULT 100, -- Porcentaje de mesas objetivo
            meta_cantidad INTEGER, -- Cantidad específica de mesas
            progreso_actual INTEGER DEFAULT 0,
            fecha_limite DATE,
            activo INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (configuracion_id) REFERENCES configuracion_prioridades(id)
        )
    """)
    
    # Tabla de alertas de prioridad
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas_prioridad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            configuracion_id INTEGER NOT NULL,
            tipo_alerta TEXT NOT NULL, -- 'meta_no_cumplida', 'fecha_limite', 'baja_cobertura'
            entidad_tipo TEXT NOT NULL,
            entidad_id INTEGER NOT NULL,
            mensaje TEXT NOT NULL,
            nivel_urgencia INTEGER DEFAULT 2, -- 1=Crítico, 2=Alto, 3=Medio, 4=Bajo
            leida INTEGER DEFAULT 0,
            fecha_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (configuracion_id) REFERENCES configuracion_prioridades(id)
        )
    """)
    
    # Crear índices para optimizar consultas
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_prioridades_partidos_config ON prioridades_partidos(configuracion_id)",
        "CREATE INDEX IF NOT EXISTS idx_prioridades_partidos_prioridad ON prioridades_partidos(prioridad)",
        "CREATE INDEX IF NOT EXISTS idx_prioridades_coaliciones_config ON prioridades_coaliciones(configuracion_id)",
        "CREATE INDEX IF NOT EXISTS idx_prioridades_candidatos_config ON prioridades_candidatos(configuracion_id)",
        "CREATE INDEX IF NOT EXISTS idx_prioridades_candidatos_prioridad ON prioridades_candidatos(prioridad)",
        "CREATE INDEX IF NOT EXISTS idx_prioridades_procesos_config ON prioridades_procesos(configuracion_id)",
        "CREATE INDEX IF NOT EXISTS idx_prioridades_municipios_config ON prioridades_municipios(configuracion_id)",
        "CREATE INDEX IF NOT EXISTS idx_metas_recoleccion_config ON metas_recoleccion(configuracion_id)",
        "CREATE INDEX IF NOT EXISTS idx_metas_recoleccion_tipo ON metas_recoleccion(tipo_entidad, entidad_id)",
        "CREATE INDEX IF NOT EXISTS idx_alertas_prioridad_config ON alertas_prioridad(configuracion_id)",
        "CREATE INDEX IF NOT EXISTS idx_alertas_prioridad_nivel ON alertas_prioridad(nivel_urgencia, leida)"
    ]
    
    for indice in indices:
        cursor.execute(indice)
    
    print("✅ Tablas de priorización creadas")
    
    # Insertar configuración de prioridades por defecto
    insertar_configuracion_default(cursor)
    
    conn.commit()
    conn.close()
    
    print("✅ Sistema de priorización inicializado")

def insertar_configuracion_default(cursor):
    """Insertar configuración de prioridades por defecto"""
    
    print("🔄 Insertando configuración de prioridades por defecto...")
    
    # Configuración principal
    cursor.execute("""
        INSERT OR IGNORE INTO configuracion_prioridades 
        (nombre, descripcion, activa, fecha_inicio, fecha_fin, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'Configuración Principal 2024',
        'Configuración de prioridades para elecciones municipales 2024',
        1,
        '2024-11-01',
        '2024-12-31',
        1  # Super admin
    ))
    
    # Obtener ID de la configuración
    cursor.execute("SELECT id FROM configuracion_prioridades WHERE nombre = ?", 
                  ('Configuración Principal 2024',))
    config_result = cursor.fetchone()
    
    if config_result:
        config_id = config_result[0]
        
        # Prioridades de partidos (algunos ejemplos)
        partidos_prioritarios = [
            (1, 1, 'Partido con mayor representación histórica'),  # PLC - Alta
            (2, 1, 'Partido tradicional importante'),              # PCC - Alta
            (3, 2, 'Partido de oposición relevante'),             # CD - Media
            (4, 2, 'Partido con presencia regional'),             # CR - Media
            (7, 3, 'Partido emergente')                           # AV - Baja
        ]
        
        for partido_id, prioridad, observacion in partidos_prioritarios:
            cursor.execute("""
                INSERT OR IGNORE INTO prioridades_partidos 
                (configuracion_id, partido_id, prioridad, observaciones)
                VALUES (?, ?, ?, ?)
            """, (config_id, partido_id, prioridad, observacion))
        
        # Prioridades de procesos electorales
        cursor.execute("SELECT id FROM procesos_electorales WHERE activo = 1")
        procesos = cursor.fetchall()
        
        for proceso in procesos:
            proceso_id = proceso[0]
            cursor.execute("""
                INSERT OR IGNORE INTO prioridades_procesos 
                (configuracion_id, proceso_id, prioridad, observaciones)
                VALUES (?, ?, ?, ?)
            """, (config_id, proceso_id, 1, 'Proceso electoral activo prioritario'))
        
        # Prioridades de municipios (Florencia como alta prioridad)
        cursor.execute("SELECT id FROM municipios WHERE nombre = 'Florencia'")
        florencia = cursor.fetchone()
        
        if florencia:
            cursor.execute("""
                INSERT OR IGNORE INTO prioridades_municipios 
                (configuracion_id, municipio_id, prioridad, observaciones)
                VALUES (?, ?, ?, ?)
            """, (config_id, florencia[0], 1, 'Capital departamental - máxima prioridad'))
        
        # Metas de recolección por defecto
        cursor.execute("""
            INSERT OR IGNORE INTO metas_recoleccion 
            (configuracion_id, tipo_entidad, entidad_id, meta_porcentaje, fecha_limite)
            VALUES (?, ?, ?, ?, ?)
        """, (config_id, 'partido', 1, 90, '2024-11-30'))  # PLC - 90% de cobertura
        
        cursor.execute("""
            INSERT OR IGNORE INTO metas_recoleccion 
            (configuracion_id, tipo_entidad, entidad_id, meta_porcentaje, fecha_limite)
            VALUES (?, ?, ?, ?, ?)
        """, (config_id, 'partido', 2, 85, '2024-11-30'))  # PCC - 85% de cobertura
    
    print("✅ Configuración de prioridades por defecto insertada")

if __name__ == "__main__":
    try:
        create_priority_tables()
        print("🎉 Sistema de priorización creado exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()