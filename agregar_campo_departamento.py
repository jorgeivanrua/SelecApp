#!/usr/bin/env python3
"""
Agregar campo departamento a la tabla users
"""

import sqlite3

def agregar_campo_departamento():
    """Agregar campo departamento a users"""
    try:
        conn = sqlite3.connect('caqueta_electoral.db')
        cursor = conn.cursor()
        
        # Verificar si el campo ya existe
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'departamento' not in columns:
            print("Agregando campo departamento...")
            cursor.execute("ALTER TABLE users ADD COLUMN departamento TEXT DEFAULT 'Caquetá'")
            conn.commit()
            print("✅ Campo departamento agregado exitosamente")
        else:
            print("✅ El campo departamento ya existe")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    agregar_campo_departamento()
