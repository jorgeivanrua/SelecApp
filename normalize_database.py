#!/usr/bin/env python3
"""
Script para normalizar la base de datos siguiendo buenas prácticas
"""

import sqlite3
import shutil
from datetime import datetime

def backup_database():
    """Crear backup de la base de datos"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'caqueta_electoral_backup_{timestamp}.db'
    shutil.copy2('caqueta_electoral.db', backup_file)
    print(f"✅ Backup creado: {backup_file}")
    return backup_file

def normalize_database():
    """Normalizar la base de datos"""
    
    # Crear backup primero
    backup_file = backup_database()
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("NORMALIZANDO BASE DE DATOS")
    print("="*80)
    
    changes = []
    
    # 1. Estandarizar columna de estado activo a 'activo' (INTEGER)
    print("\n📝 1. Estandarizando columnas de estado...")
    
    tables_with_activa = [
        'coaliciones',
        'configuracion_prioridades',
        'mesas_votacion'
    ]
    
    for table in tables_with_activa:
        try:
            # Verificar si la columna existe
            cursor.execute(f"PRAGMA table_info({table})")
            columns = {col[1]: col for col in cursor.fetchall()}
            
            if 'activa' in columns:
                print(f"   Cambiando 'activa' a 'activo' en {table}...")
                
                # SQLite no permite renombrar columnas directamente en versiones antiguas
                # Necesitamos recrear la tabla
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                create_sql = cursor.fetchone()[0]
                
                # Reemplazar 'activa' por 'activo' en el CREATE TABLE
                new_create_sql = create_sql.replace(' activa ', ' activo ')
                
                # Crear tabla temporal
                cursor.execute(f"ALTER TABLE {table} RENAME TO {table}_old")
                cursor.execute(new_create_sql)
                
                # Copiar datos
                cursor.execute(f"SELECT * FROM {table}_old")
                rows = cursor.fetchall()
                
                if rows:
                    placeholders = ','.join(['?' for _ in range(len(rows[0]))])
                    cursor.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
                
                # Eliminar tabla antigua
                cursor.execute(f"DROP TABLE {table}_old")
                
                changes.append(f"✅ {table}: 'activa' -> 'activo'")
                
        except Exception as e:
            print(f"   ⚠️  Error en {table}: {e}")
    
    # 2. Agregar timestamps faltantes
    print("\n📝 2. Agregando timestamps faltantes...")
    
    tables_missing_timestamps = {
        'alertas_prioridad': ['created_at', 'updated_at'],
        'capturas_e14': ['created_at', 'updated_at'],
        'coalicion_partidos': ['created_at', 'updated_at'],
        'datos_ocr_e14': ['created_at', 'updated_at'],
        'discrepancias_e24': ['updated_at'],
        'estadisticas_coordinacion': ['updated_at'],
        'estructura_e14': ['created_at', 'updated_at'],
        'incidencias_testigo': ['created_at', 'updated_at'],
        'log_coordinacion_municipal': ['created_at', 'updated_at'],
        'notificaciones': ['updated_at'],
        'notificaciones_coordinacion': ['created_at', 'updated_at'],
        'observaciones_testigo': ['created_at', 'updated_at']
    }
    
    for table, missing_cols in tables_missing_timestamps.items():
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            existing_cols = {col[1] for col in cursor.fetchall()}
            
            for col in missing_cols:
                if col not in existing_cols:
                    print(f"   Agregando {col} a {table}...")
                    cursor.execute(f"""
                        ALTER TABLE {table} 
                        ADD COLUMN {col} TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    """)
                    changes.append(f"✅ {table}: agregado {col}")
                    
        except Exception as e:
            print(f"   ⚠️  Error en {table}: {e}")
    
    # 3. Eliminar columna duplicada puesto_votacion_id de mesas_votacion
    print("\n📝 3. Eliminando columnas duplicadas...")
    
    try:
        cursor.execute("PRAGMA table_info(mesas_votacion)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        if 'puesto_votacion_id' in columns:
            print("   Eliminando puesto_votacion_id de mesas_votacion...")
            
            # Obtener CREATE TABLE original
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='mesas_votacion'")
            create_sql = cursor.fetchone()[0]
            
            # Crear nueva tabla sin puesto_votacion_id
            cursor.execute("ALTER TABLE mesas_votacion RENAME TO mesas_votacion_old")
            
            # Crear nueva tabla
            cursor.execute("""
                CREATE TABLE mesas_votacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT NOT NULL,
                    puesto_id INTEGER NOT NULL,
                    municipio_id INTEGER NOT NULL,
                    votantes_habilitados INTEGER,
                    estado TEXT,
                    ubicacion_especifica TEXT,
                    activo INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    coordenadas_lat REAL,
                    coordenadas_lng REAL,
                    FOREIGN KEY (municipio_id) REFERENCES municipios(id),
                    FOREIGN KEY (puesto_id) REFERENCES puestos_votacion(id)
                )
            """)
            
            # Copiar datos (sin puesto_votacion_id y total_votantes)
            cursor.execute("""
                INSERT INTO mesas_votacion (
                    id, numero, puesto_id, municipio_id, votantes_habilitados,
                    estado, ubicacion_especifica, activo, created_at, updated_at,
                    coordenadas_lat, coordenadas_lng
                )
                SELECT 
                    id, numero, puesto_id, municipio_id, votantes_habilitados,
                    estado, ubicacion_especifica, activa, created_at, updated_at,
                    coordenadas_lat, coordenadas_lng
                FROM mesas_votacion_old
            """)
            
            # Eliminar tabla antigua
            cursor.execute("DROP TABLE mesas_votacion_old")
            
            # Recrear índices
            cursor.execute("CREATE INDEX idx_mesas_puesto ON mesas_votacion(puesto_id)")
            cursor.execute("CREATE INDEX idx_mesas_municipio ON mesas_votacion(municipio_id)")
            
            changes.append("✅ mesas_votacion: eliminado puesto_votacion_id y total_votantes")
            changes.append("✅ mesas_votacion: 'activa' -> 'activo'")
            
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    # Commit cambios
    conn.commit()
    conn.close()
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE CAMBIOS")
    print("="*80)
    
    if changes:
        for change in changes:
            print(change)
    else:
        print("⚠️  No se realizaron cambios")
    
    print("\n" + "="*80)
    print(f"✅ Normalización completada")
    print(f"📁 Backup guardado en: {backup_file}")
    print("="*80)

if __name__ == "__main__":
    print("⚠️  ADVERTENCIA: Este script modificará la base de datos")
    print("   Se creará un backup automáticamente")
    
    response = input("\n¿Deseas continuar? (s/n): ")
    
    if response.lower() == 's':
        normalize_database()
    else:
        print("❌ Operación cancelada")
