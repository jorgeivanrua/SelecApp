#!/usr/bin/env python3
"""Script para analizar la estructura de la base de datos"""

import sqlite3

def analyze_database():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("="*80)
    print("ANÁLISIS DE BASE DE DATOS - BUENAS PRÁCTICAS")
    print("="*80)
    
    issues = []
    
    for table in tables:
        if table == 'sqlite_sequence':
            continue
            
        print(f"\n📋 Tabla: {table}")
        print("-"*80)
        
        # Obtener estructura
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        # Verificar problemas comunes
        has_id = False
        has_created_at = False
        has_updated_at = False
        inconsistent_naming = []
        
        for col in columns:
            col_id, col_name, col_type, not_null, default, pk = col
            
            # Verificar ID
            if col_name == 'id' and pk == 1:
                has_id = True
            
            # Verificar timestamps
            if col_name in ['created_at', 'fecha_creacion', 'creado_en']:
                has_created_at = True
            if col_name in ['updated_at', 'fecha_actualizacion', 'actualizado_en']:
                has_updated_at = True
            
            # Verificar inconsistencias en nombres
            if '_' in col_name and any(c.isupper() for c in col_name):
                inconsistent_naming.append(col_name)
            
            # Mostrar columna
            pk_mark = " 🔑 PK" if pk else ""
            nn_mark = " ⚠️ NOT NULL" if not_null else ""
            print(f"  {col_name:<30} {col_type:<15}{pk_mark}{nn_mark}")
        
        # Reportar problemas
        if not has_id:
            issues.append(f"❌ {table}: No tiene columna 'id' como PRIMARY KEY")
        
        if not has_created_at:
            issues.append(f"⚠️  {table}: No tiene columna 'created_at'")
        
        if not has_updated_at:
            issues.append(f"⚠️  {table}: No tiene columna 'updated_at'")
        
        if inconsistent_naming:
            issues.append(f"⚠️  {table}: Nombres inconsistentes: {', '.join(inconsistent_naming)}")
        
        # Verificar foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        fks = cursor.fetchall()
        if fks:
            print("\n  🔗 Foreign Keys:")
            for fk in fks:
                print(f"    {fk[3]} -> {fk[2]}.{fk[4]}")
        
        # Verificar índices
        cursor.execute(f"PRAGMA index_list({table})")
        indexes = cursor.fetchall()
        if indexes:
            print("\n  📊 Índices:")
            for idx in indexes:
                print(f"    {idx[1]} (unique: {idx[2]})")
    
    # Resumen de problemas
    print("\n" + "="*80)
    print("RESUMEN DE PROBLEMAS ENCONTRADOS")
    print("="*80)
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✅ No se encontraron problemas críticos")
    
    # Verificar inconsistencias específicas
    print("\n" + "="*80)
    print("VERIFICACIÓN DE CONSISTENCIA")
    print("="*80)
    
    # Verificar columnas activo/activa
    print("\n🔍 Columnas de estado activo:")
    for table in tables:
        if table == 'sqlite_sequence':
            continue
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            if col[1] in ['activo', 'activa', 'active']:
                print(f"  {table}: {col[1]} ({col[2]})")
    
    # Verificar columnas de capacidad
    print("\n🔍 Columnas de capacidad/votantes:")
    for table in tables:
        if table == 'sqlite_sequence':
            continue
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            if 'votant' in col[1].lower() or 'capacidad' in col[1].lower():
                print(f"  {table}: {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    analyze_database()
