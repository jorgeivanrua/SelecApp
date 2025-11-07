#!/usr/bin/env python3
"""
Script para crear tablas de coordinación municipal del Sistema Electoral ERP
Consolidación de E-14 a E-24, verificación y generación de informes
"""

import sqlite3
from datetime import datetime

def create_municipal_coordination_tables():
    """Crear tablas de coordinación municipal"""
    
    print("🔄 Creando tablas de coordinación municipal...")
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Tabla de consolidaciones municipales E-24
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consolidaciones_e24 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            municipio_id INTEGER NOT NULL,
            proceso_electoral_id INTEGER NOT NULL,
            tipo_eleccion TEXT NOT NULL, -- 'alcalde', 'concejo', 'senado', etc.
            estado TEXT DEFAULT 'pendiente', -- 'pendiente', 'consolidando', 'completado', 'verificado'
            total_mesas INTEGER DEFAULT 0,
            mesas_procesadas INTEGER DEFAULT 0,
            total_votos_validos INTEGER DEFAULT 0,
            total_votos_blancos INTEGER DEFAULT 0,
            total_votos_nulos INTEGER DEFAULT 0,
            total_votos_no_marcados INTEGER DEFAULT 0,
            total_tarjetones INTEGER DEFAULT 0,
            fecha_consolidacion TIMESTAMP,
            consolidado_por INTEGER,
            observaciones TEXT,
            imagen_e24_generado TEXT, -- Path de la imagen E-24 generada
            imagen_e24_oficial TEXT, -- Path de la imagen E-24 oficial de Registraduría
            discrepancias_detectadas INTEGER DEFAULT 0,
            estado_verificacion TEXT DEFAULT 'pendiente', -- 'pendiente', 'verificado', 'con_discrepancias'
            verificado_por INTEGER,
            fecha_verificacion TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (municipio_id) REFERENCES municipios(id),
            FOREIGN KEY (proceso_electoral_id) REFERENCES procesos_electorales(id),
            FOREIGN KEY (consolidado_por) REFERENCES users(id),
            FOREIGN KEY (verificado_por) REFERENCES users(id),
            UNIQUE(municipio_id, proceso_electoral_id, tipo_eleccion)
        )
    """)
    
    # Tabla de resultados consolidados por candidato
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados_candidatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consolidacion_id INTEGER NOT NULL,
            candidato_id INTEGER NOT NULL,
            votos_obtenidos INTEGER DEFAULT 0,
            porcentaje_votos REAL DEFAULT 0.0,
            posicion_ranking INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consolidacion_id) REFERENCES consolidaciones_e24(id),
            FOREIGN KEY (candidato_id) REFERENCES candidatos(id),
            UNIQUE(consolidacion_id, candidato_id)
        )
    """)
    
    # Tabla de resultados consolidados por partido
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados_partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consolidacion_id INTEGER NOT NULL,
            partido_id INTEGER NOT NULL,
            total_votos INTEGER DEFAULT 0,
            porcentaje_votos REAL DEFAULT 0.0,
            total_candidatos INTEGER DEFAULT 0,
            candidatos_electos INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consolidacion_id) REFERENCES consolidaciones_e24(id),
            FOREIGN KEY (partido_id) REFERENCES partidos_politicos(id),
            UNIQUE(consolidacion_id, partido_id)
        )
    """)
    
    # Tabla de discrepancias E-24
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discrepancias_e24 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consolidacion_id INTEGER NOT NULL,
            tipo_discrepancia TEXT NOT NULL, -- 'total_votos', 'candidato_votos', 'suma_incorrecta', 'dato_faltante'
            campo_afectado TEXT NOT NULL,
            valor_generado TEXT,
            valor_oficial TEXT,
            diferencia INTEGER DEFAULT 0,
            severidad TEXT DEFAULT 'media', -- 'baja', 'media', 'alta', 'critica'
            descripcion TEXT,
            estado TEXT DEFAULT 'pendiente', -- 'pendiente', 'revisado', 'resuelto', 'aceptado'
            revisado_por INTEGER,
            fecha_revision TIMESTAMP,
            observaciones_revision TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consolidacion_id) REFERENCES consolidaciones_e24(id),
            FOREIGN KEY (revisado_por) REFERENCES users(id)
        )
    """)
    
    # Tabla de reclamaciones generadas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reclamaciones_e24 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consolidacion_id INTEGER NOT NULL,
            numero_reclamacion TEXT UNIQUE,
            tipo_reclamacion TEXT NOT NULL, -- 'discrepancia_totales', 'error_candidato', 'suma_incorrecta'
            descripcion TEXT NOT NULL,
            evidencia_generada TEXT, -- Path del archivo de evidencia
            evidencia_oficial TEXT, -- Path del E-24 oficial
            estado TEXT DEFAULT 'generada', -- 'generada', 'enviada', 'en_revision', 'resuelta', 'rechazada'
            fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            generada_por INTEGER NOT NULL,
            enviada_a TEXT, -- Entidad a la que se envía la reclamación
            fecha_envio TIMESTAMP,
            respuesta_recibida TEXT,
            fecha_respuesta TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consolidacion_id) REFERENCES consolidaciones_e24(id),
            FOREIGN KEY (generada_por) REFERENCES users(id)
        )
    """)
    
    # Tabla de informes PDF municipales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS informes_pdf_municipales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            municipio_id INTEGER NOT NULL,
            proceso_electoral_id INTEGER,
            tipo_informe TEXT NOT NULL, -- 'consolidado_general', 'por_tipo_eleccion', 'comparativo_puestos'
            tipo_eleccion TEXT, -- Específico si es por tipo de elección
            nombre_archivo TEXT NOT NULL,
            ruta_archivo TEXT NOT NULL,
            tamaño_archivo INTEGER,
            hash_integridad TEXT,
            estado TEXT DEFAULT 'generando', -- 'generando', 'completado', 'error', 'descargado'
            fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            generado_por INTEGER NOT NULL,
            parametros_generacion TEXT, -- JSON con parámetros usados
            estadisticas_incluidas TEXT, -- JSON con estadísticas incluidas
            total_paginas INTEGER,
            fecha_descarga TIMESTAMP,
            descargas_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (municipio_id) REFERENCES municipios(id),
            FOREIGN KEY (proceso_electoral_id) REFERENCES procesos_electorales(id),
            FOREIGN KEY (generado_por) REFERENCES users(id)
        )
    """)
    
    # Tabla de estadísticas de consolidación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estadisticas_consolidacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consolidacion_id INTEGER NOT NULL,
            total_electores_habilitados INTEGER DEFAULT 0,
            total_votos_depositados INTEGER DEFAULT 0,
            porcentaje_participacion REAL DEFAULT 0.0,
            total_mesas_instaladas INTEGER DEFAULT 0,
            mesas_con_novedad INTEGER DEFAULT 0,
            tiempo_promedio_consolidacion INTEGER, -- En minutos
            anomalias_detectadas INTEGER DEFAULT 0,
            calidad_datos TEXT DEFAULT 'buena', -- 'excelente', 'buena', 'regular', 'deficiente'
            observaciones_estadisticas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consolidacion_id) REFERENCES consolidaciones_e24(id),
            UNIQUE(consolidacion_id)
        )
    """)
    
    # Tabla de log de acciones de coordinación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_coordinacion_municipal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            municipio_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            accion TEXT NOT NULL, -- 'iniciar_consolidacion', 'completar_consolidacion', 'verificar_e24', 'generar_reclamacion', 'generar_informe'
            entidad_tipo TEXT, -- 'consolidacion', 'discrepancia', 'reclamacion', 'informe'
            entidad_id INTEGER,
            descripcion TEXT,
            datos_adicionales TEXT, -- JSON con datos adicionales
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (municipio_id) REFERENCES municipios(id),
            FOREIGN KEY (usuario_id) REFERENCES users(id)
        )
    """)
    
    # Crear índices para optimizar consultas
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_consolidaciones_municipio ON consolidaciones_e24(municipio_id)",
        "CREATE INDEX IF NOT EXISTS idx_consolidaciones_proceso ON consolidaciones_e24(proceso_electoral_id)",
        "CREATE INDEX IF NOT EXISTS idx_consolidaciones_estado ON consolidaciones_e24(estado)",
        "CREATE INDEX IF NOT EXISTS idx_consolidaciones_tipo ON consolidaciones_e24(tipo_eleccion)",
        "CREATE INDEX IF NOT EXISTS idx_resultados_candidatos_consolidacion ON resultados_candidatos(consolidacion_id)",
        "CREATE INDEX IF NOT EXISTS idx_resultados_candidatos_candidato ON resultados_candidatos(candidato_id)",
        "CREATE INDEX IF NOT EXISTS idx_resultados_partidos_consolidacion ON resultados_partidos(consolidacion_id)",
        "CREATE INDEX IF NOT EXISTS idx_resultados_partidos_partido ON resultados_partidos(partido_id)",
        "CREATE INDEX IF NOT EXISTS idx_discrepancias_consolidacion ON discrepancias_e24(consolidacion_id)",
        "CREATE INDEX IF NOT EXISTS idx_discrepancias_severidad ON discrepancias_e24(severidad)",
        "CREATE INDEX IF NOT EXISTS idx_reclamaciones_consolidacion ON reclamaciones_e24(consolidacion_id)",
        "CREATE INDEX IF NOT EXISTS idx_reclamaciones_estado ON reclamaciones_e24(estado)",
        "CREATE INDEX IF NOT EXISTS idx_informes_municipio ON informes_pdf_municipales(municipio_id)",
        "CREATE INDEX IF NOT EXISTS idx_informes_tipo ON informes_pdf_municipales(tipo_informe)",
        "CREATE INDEX IF NOT EXISTS idx_log_municipio ON log_coordinacion_municipal(municipio_id)",
        "CREATE INDEX IF NOT EXISTS idx_log_usuario ON log_coordinacion_municipal(usuario_id)",
        "CREATE INDEX IF NOT EXISTS idx_log_accion ON log_coordinacion_municipal(accion)",
        "CREATE INDEX IF NOT EXISTS idx_log_timestamp ON log_coordinacion_municipal(timestamp)"
    ]
    
    for indice in indices:
        cursor.execute(indice)
    
    print("✅ Tablas de coordinación municipal creadas")
    
    # Insertar datos de ejemplo
    insertar_datos_ejemplo(cursor)
    
    conn.commit()
    conn.close()
    
    print("✅ Sistema de coordinación municipal inicializado")

def insertar_datos_ejemplo(cursor):
    """Insertar datos de ejemplo para coordinación municipal"""
    
    print("🔄 Insertando datos de ejemplo...")
    
    # Obtener municipio de Florencia
    cursor.execute("SELECT id FROM municipios WHERE nombre = 'Florencia'")
    florencia = cursor.fetchone()
    
    if florencia:
        municipio_id = florencia[0]
        
        # Obtener proceso electoral activo
        cursor.execute("SELECT id FROM procesos_electorales WHERE estado = 'activo' LIMIT 1")
        proceso = cursor.fetchone()
        
        if proceso:
            proceso_id = proceso[0]
            
            # Crear consolidación de ejemplo para Alcalde
            cursor.execute("""
                INSERT OR IGNORE INTO consolidaciones_e24 
                (municipio_id, proceso_electoral_id, tipo_eleccion, estado, total_mesas, mesas_procesadas,
                 total_votos_validos, total_votos_blancos, total_votos_nulos, consolidado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (municipio_id, proceso_id, 'alcalde', 'consolidando', 25, 18, 12450, 234, 156, 1))
            
            # Crear consolidación de ejemplo para Concejo
            cursor.execute("""
                INSERT OR IGNORE INTO consolidaciones_e24 
                (municipio_id, proceso_electoral_id, tipo_eleccion, estado, total_mesas, mesas_procesadas,
                 total_votos_validos, total_votos_blancos, total_votos_nulos, consolidado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (municipio_id, proceso_id, 'concejo', 'pendiente', 25, 12, 11890, 198, 142, 1))
            
            # Obtener ID de la consolidación de alcalde
            cursor.execute("""
                SELECT id FROM consolidaciones_e24 
                WHERE municipio_id = ? AND tipo_eleccion = 'alcalde'
            """, (municipio_id,))
            consolidacion = cursor.fetchone()
            
            if consolidacion:
                consolidacion_id = consolidacion[0]
                
                # Crear estadísticas de ejemplo
                cursor.execute("""
                    INSERT OR IGNORE INTO estadisticas_consolidacion 
                    (consolidacion_id, total_electores_habilitados, total_votos_depositados, 
                     porcentaje_participacion, total_mesas_instaladas, tiempo_promedio_consolidacion)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (consolidacion_id, 18500, 12840, 69.4, 25, 45))
                
                # Crear algunas discrepancias de ejemplo
                cursor.execute("""
                    INSERT OR IGNORE INTO discrepancias_e24 
                    (consolidacion_id, tipo_discrepancia, campo_afectado, valor_generado, 
                     valor_oficial, diferencia, severidad, descripcion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (consolidacion_id, 'total_votos', 'total_votos_validos', '12450', '12448', 2, 'baja', 
                      'Diferencia menor en total de votos válidos'))
    
    print("✅ Datos de ejemplo insertados")

if __name__ == "__main__":
    try:
        create_municipal_coordination_tables()
        print("🎉 Sistema de coordinación municipal creado exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()