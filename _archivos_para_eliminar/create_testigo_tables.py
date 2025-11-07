#!/usr/bin/env python3
"""
Script para crear las tablas faltantes del módulo de testigo
Sistema Electoral Caquetá
"""

import sqlite3
from datetime import datetime

def create_testigo_tables():
    """Crear todas las tablas necesarias para el módulo de testigo"""
    
    print("=" * 80)
    print("🔧 CREACIÓN DE TABLAS DEL MÓDULO TESTIGO")
    print("=" * 80)
    print()
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('caqueta_electoral.db')
        cursor = conn.cursor()
        
        print("✅ Conexión a base de datos establecida")
        print()
        
        # 1. Tabla capturas_e14
        print("1️⃣ Creando tabla capturas_e14...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS capturas_e14 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mesa_id INTEGER NOT NULL,
                testigo_id INTEGER NOT NULL,
                ruta_foto VARCHAR(255) NOT NULL,
                datos_json TEXT NOT NULL,
                total_votos INTEGER,
                observaciones TEXT,
                estado VARCHAR(50) DEFAULT 'pendiente',
                procesado_ocr BOOLEAN DEFAULT FALSE,
                confianza_ocr FLOAT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id),
                FOREIGN KEY (testigo_id) REFERENCES users(id)
            )
        """)
        print("   ✅ Tabla capturas_e14 creada")
        
        # 2. Tabla observaciones_testigo
        print("2️⃣ Creando tabla observaciones_testigo...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observaciones_testigo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                testigo_id INTEGER NOT NULL,
                mesa_id INTEGER NOT NULL,
                tipo VARCHAR(50),
                descripcion TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (testigo_id) REFERENCES users(id),
                FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id)
            )
        """)
        print("   ✅ Tabla observaciones_testigo creada")
        
        # 3. Tabla incidencias_testigo
        print("3️⃣ Creando tabla incidencias_testigo...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidencias_testigo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                testigo_id INTEGER NOT NULL,
                mesa_id INTEGER NOT NULL,
                tipo VARCHAR(50),
                gravedad VARCHAR(20),
                descripcion TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (testigo_id) REFERENCES users(id),
                FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id)
            )
        """)
        print("   ✅ Tabla incidencias_testigo creada")
        
        # 4. Tabla estructura_e14 (para OCR)
        print("4️⃣ Creando tabla estructura_e14...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estructura_e14 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_eleccion_id INTEGER,
                posicion INTEGER,
                tipo VARCHAR(50),
                candidato_id INTEGER,
                partido_id INTEGER,
                zona_ocr_x INTEGER,
                zona_ocr_y INTEGER,
                zona_ocr_width INTEGER,
                zona_ocr_height INTEGER
            )
        """)
        print("   ✅ Tabla estructura_e14 creada")
        
        # 5. Tabla datos_ocr_e14
        print("5️⃣ Creando tabla datos_ocr_e14...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datos_ocr_e14 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                captura_e14_id INTEGER NOT NULL,
                posicion INTEGER,
                candidato_id INTEGER,
                votos_detectados INTEGER,
                votos_confirmados INTEGER,
                confianza FLOAT,
                editado BOOLEAN DEFAULT FALSE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (captura_e14_id) REFERENCES capturas_e14(id),
                FOREIGN KEY (candidato_id) REFERENCES candidatos(id)
            )
        """)
        print("   ✅ Tabla datos_ocr_e14 creada")
        
        # Commit de cambios
        conn.commit()
        print()
        print("=" * 80)
        print("✅ TODAS LAS TABLAS CREADAS EXITOSAMENTE")
        print("=" * 80)
        print()
        
        # Verificar tablas creadas
        print("📊 Verificando tablas creadas...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE '%testigo%' OR name LIKE '%e14%'
            ORDER BY name
        """)
        
        tablas = cursor.fetchall()
        print()
        print("Tablas del módulo testigo:")
        for tabla in tablas:
            print(f"   ✅ {tabla[0]}")
        
        print()
        print("=" * 80)
        print("🎉 PROCESO COMPLETADO")
        print("=" * 80)
        print()
        print("Próximos pasos:")
        print("1. Implementar APIs del testigo")
        print("2. Conectar frontend con backend")
        print("3. Probar flujo completo de captura E14")
        print()
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = create_testigo_tables()
    exit(0 if success else 1)
