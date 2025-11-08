#!/usr/bin/env python3
"""Script para corregir la tabla mesas_votacion"""

import sqlite3

def fix_mesas_votacion():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("="*80)
    print("CORRIGIENDO TABLA mesas_votacion")
    print("="*80)
    
    try:
        # Verificar estructura actual
        cursor.execute("PRAGMA table_info(mesas_votacion)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        print("\nColumnas actuales:")
        for col_name in columns.keys():
            print(f"  - {col_name}")
        
        # Renombrar tabla actual
        print("\n1. Renombrando tabla actual...")
        cursor.execute("ALTER TABLE mesas_votacion RENAME TO mesas_votacion_old")
        
        # Crear nueva tabla normalizada
        print("2. Creando nueva tabla normalizada...")
        cursor.execute("""
            CREATE TABLE mesas_votacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                puesto_id INTEGER NOT NULL,
                municipio_id INTEGER NOT NULL,
                votantes_habilitados INTEGER DEFAULT 0,
                estado TEXT DEFAULT 'configurada',
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
        
        # Copiar datos
        print("3. Copiando datos...")
        
        # Determinar qué columna usar para activo
        activo_col = 'activa' if 'activa' in columns else 'activo'
        
        cursor.execute(f"""
            INSERT INTO mesas_votacion (
                id, numero, puesto_id, municipio_id, votantes_habilitados,
                estado, ubicacion_especifica, activo, created_at, updated_at,
                coordenadas_lat, coordenadas_lng
            )
            SELECT 
                id, numero, puesto_id, municipio_id, votantes_habilitados,
                estado, ubicacion_especifica, {activo_col}, created_at, updated_at,
                coordenadas_lat, coordenadas_lng
            FROM mesas_votacion_old
        """)
        
        rows_copied = cursor.rowcount
        print(f"   ✅ {rows_copied} filas copiadas")
        
        # Eliminar tabla antigua
        print("4. Eliminando tabla antigua...")
        cursor.execute("DROP TABLE mesas_votacion_old")
        
        # Recrear índices
        print("5. Recreando índices...")
        cursor.execute("CREATE INDEX idx_mesas_puesto ON mesas_votacion(puesto_id)")
        cursor.execute("CREATE INDEX idx_mesas_municipio ON mesas_votacion(municipio_id)")
        cursor.execute("CREATE INDEX idx_mesas_activo ON mesas_votacion(activo)")
        
        # Commit
        conn.commit()
        
        # Verificar resultado
        print("\n6. Verificando resultado...")
        cursor.execute("PRAGMA table_info(mesas_votacion)")
        new_columns = cursor.fetchall()
        
        print("\nNuevas columnas:")
        for col in new_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute("SELECT COUNT(*) FROM mesas_votacion")
        count = cursor.fetchone()[0]
        print(f"\nTotal de registros: {count}")
        
        print("\n" + "="*80)
        print("✅ Tabla mesas_votacion corregida exitosamente")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_mesas_votacion()
