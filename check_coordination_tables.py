#!/usr/bin/env python3
"""
Script para verificar las tablas de coordinación municipal
"""

import sqlite3

def check_tables():
    """Verificar qué tablas existen en la base de datos"""
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    print("📋 TODAS LAS TABLAS EN LA BASE DE DATOS:")
    for table in all_tables:
        print(f"   - {table}")
    
    # Buscar tablas relacionadas con coordinación
    coordination_tables = [table for table in all_tables if 'coordinador' in table.lower() or 'testigo' in table.lower() or 'asignacion' in table.lower()]
    
    print(f"\n🎯 TABLAS DE COORDINACIÓN ENCONTRADAS ({len(coordination_tables)}):")
    for table in coordination_tables:
        print(f"   - {table}")
        
        # Mostrar estructura de la tabla
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"     Columnas: {len(columns)}")
        
        # Contar registros
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"     Registros: {count}")
    
    conn.close()

if __name__ == "__main__":
    check_tables()