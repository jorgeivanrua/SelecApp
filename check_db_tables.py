#!/usr/bin/env python3
"""Script para verificar las tablas en la base de datos"""

import sqlite3

def check_tables():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("=" * 60)
    print("TABLAS EN LA BASE DE DATOS")
    print("=" * 60)
    
    if tables:
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {table_name:<40} ({count} registros)")
    else:
        print("  ⚠️  No se encontraron tablas")
    
    print("=" * 60)
    
    # Verificar si existe la tabla users
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_table = cursor.fetchone()
    
    if users_table:
        print("\n✅ Tabla 'users' existe")
        cursor.execute("SELECT * FROM users LIMIT 1")
        print(f"   Columnas: {[desc[0] for desc in cursor.description]}")
    else:
        print("\n❌ Tabla 'users' NO existe")
        print("   Se necesita crear la tabla de usuarios")
    
    conn.close()

if __name__ == "__main__":
    check_tables()
