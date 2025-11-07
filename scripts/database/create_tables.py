#!/usr/bin/env python3
"""
Script unificado para crear todas las tablas del sistema electoral
"""

import sqlite3
import os
from datetime import datetime

def create_all_tables(db_path: str = 'electoral_system.db'):
    """Crear todas las tablas del sistema electoral"""
    
    print("🗳️  Creando todas las tablas del sistema electoral...")
    print(f"Base de datos: {db_path}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Habilitar foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 1. Tabla de ubicaciones (DIVIPOLA)
        print("📍 Creando tabla de ubicaciones...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_departamento VARCHAR(2) NOT NULL,
            codigo_municipio VARCHAR(3) NOT NULL,
            codigo_zona VARCHAR(3),
            codigo_puesto VARCHAR(2),
            nombre_departamento VARCHAR(100) NOT NULL,
            nombre_municipio VARCHAR(100) NOT NULL,
            nombre_puesto VARCHAR(200),
            tipo VARCHAR(20) NOT NULL,
            comuna VARCHAR(100),
            direccion VARCHAR(500),
            latitud REAL,
            longitud REAL,
            total_mujeres INTEGER DEFAULT 0,
            total_hombres INTEGER DEFAULT 0,
            total_votantes INTEGER DEFAULT 0,
            total_mesas INTEGER DEFAULT 0,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES locations(id)
        )
        ''')
        
        # 2. Tabla de usuarios
        print("👥 Creando tabla de usuarios...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo VARCHAR(200) NOT NULL,
            cedula VARCHAR(20) UNIQUE NOT NULL,
            telefono VARCHAR(20),
            email VARCHAR(100),
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(50) NOT NULL,
            municipio_id INTEGER,
            puesto_id INTEGER,
            activo BOOLEAN DEFAULT 1,
            ultimo_login DATETIME,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (municipio_id) REFERENCES locations(id),
            FOREIGN KEY (puesto_id) REFERENCES locations(id)
        )
        ''')
        
        # 3. Tabla de tipos de elección
        print("🗳️  Creando tabla de tipos de elección...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS election_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) UNIQUE NOT NULL,
            descripcion TEXT,
            codigo VARCHAR(20) UNIQUE NOT NULL,
            plantilla_e14 TEXT NOT NULL,
            ocr_template_config TEXT,
            validation_rules TEXT,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 4. Tabla de partidos políticos
        print("🏛️  Creando tabla de partidos políticos...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS political_parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_oficial VARCHAR(200) NOT NULL,
            siglas VARCHAR(20) UNIQUE NOT NULL,
            color_representativo VARCHAR(7),
            logo_url VARCHAR(500),
            descripcion TEXT,
            fundacion_year INTEGER,
            ideologia VARCHAR(100),
            activo BOOLEAN DEFAULT 1,
            reconocido_oficialmente BOOLEAN DEFAULT 1,
            creado_por INTEGER,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creado_por) REFERENCES users(id)
        )
        ''')
        
        # 5. Tabla de candidatos
        print("👤 Creando tabla de candidatos...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo VARCHAR(200) NOT NULL,
            cedula VARCHAR(20) UNIQUE NOT NULL,
            numero_tarjeton INTEGER NOT NULL,
            cargo_aspirado VARCHAR(100) NOT NULL,
            election_type_id INTEGER NOT NULL,
            circunscripcion VARCHAR(100) NOT NULL,
            party_id INTEGER,
            coalition_id INTEGER,
            es_independiente BOOLEAN DEFAULT 0,
            foto_url VARCHAR(500),
            biografia TEXT,
            propuestas TEXT,
            experiencia TEXT,
            activo BOOLEAN DEFAULT 1,
            habilitado_oficialmente BOOLEAN DEFAULT 1,
            creado_por INTEGER,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (election_type_id) REFERENCES election_types(id),
            FOREIGN KEY (party_id) REFERENCES political_parties(id),
            FOREIGN KEY (creado_por) REFERENCES users(id)
        )
        ''')
        
        # Crear índices
        print("📊 Creando índices...")
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_locations_tipo ON locations(tipo)",
            "CREATE INDEX IF NOT EXISTS idx_users_rol ON users(rol)",
            "CREATE INDEX IF NOT EXISTS idx_users_cedula ON users(cedula)",
            "CREATE INDEX IF NOT EXISTS idx_candidates_election_type ON candidates(election_type_id)",
            "CREATE INDEX IF NOT EXISTS idx_candidates_party ON candidates(party_id)",
            "CREATE INDEX IF NOT EXISTS idx_candidates_tarjeton ON candidates(numero_tarjeton)",
            "CREATE INDEX IF NOT EXISTS idx_parties_siglas ON political_parties(siglas)"
        ]
        
        for index in indices:
            cursor.execute(index)
        
        conn.commit()
        
        # Verificar tablas creadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n✅ Tablas creadas exitosamente:")
        for table in sorted(tables):
            if not table.startswith('sqlite_'):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   - {table}: {count} registros")
        
        print(f"\n📊 Resumen:")
        print(f"   - Total de tablas: {len([t for t in tables if not t.startswith('sqlite_')])}")
        print(f"   - Base de datos: {db_path}")
        print(f"   - Tamaño: {os.path.getsize(db_path) / 1024:.1f} KB")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error creando tablas: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = create_all_tables()
    if success:
        print("\n🎉 ¡Sistema de base de datos creado exitosamente!")
    else:
        print("\n💥 Error en la creación del sistema de base de datos.")