#!/usr/bin/env python3
"""
Script para agregar tabla de capturas E14
"""

import sqlite3

def add_e14_table():
    """Agregar tabla de capturas E14"""
    
    print("🔄 Agregando tabla de capturas E14...")
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Crear tabla de capturas E14
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS e14_capturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mesa_id INTEGER NOT NULL,
            testigo_id INTEGER NOT NULL,
            imagen_e14 TEXT NOT NULL,
            votos_validos INTEGER NOT NULL,
            votos_blanco INTEGER NOT NULL,
            votos_nulos INTEGER NOT NULL,
            observaciones TEXT,
            confirmado INTEGER DEFAULT 1,
            fecha_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id),
            FOREIGN KEY (testigo_id) REFERENCES users(id),
            UNIQUE(mesa_id) -- Evitar duplicados por mesa
        )
    """)
    
    # Crear índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_e14_mesa ON e14_capturas(mesa_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_e14_testigo ON e14_capturas(testigo_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_e14_fecha ON e14_capturas(fecha_captura)")
    
    conn.commit()
    conn.close()
    
    print("✅ Tabla de capturas E14 agregada exitosamente")

if __name__ == "__main__":
    try:
        add_e14_table()
        print("🎉 Tabla E14 creada exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()