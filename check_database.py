#!/usr/bin/env python3
"""
Script para verificar estructura de la base de datos
"""

import sqlite3

def check_database():
    conn = sqlite3.connect('electoral_system_prod.db')
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("📊 TABLAS EN LA BASE DE DATOS:")
    print("=" * 50)
    
    for table in tables:
        table_name = table[0]
        print(f"\n🔹 Tabla: {table_name}")
        
        # Obtener estructura de la tabla
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        if columns:
            print("   Columnas:")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
        else:
            print("   (Sin columnas)")
    
    conn.close()

if __name__ == "__main__":
    check_database()
