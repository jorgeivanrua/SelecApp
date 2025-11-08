#!/usr/bin/env python3
"""
Script para corregir las zonas de nombres descriptivos a números
Cambia: Zona Urbana, Zona Rural, Cárceles, Censo
A: Zona 01, Zona 02, Zona 03, etc.
"""

import sqlite3

def fix_zonas():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=== CORRIGIENDO ZONAS A FORMATO NUMÉRICO ===\n")
    
    # Obtener todos los municipios
    cursor.execute('SELECT id, nombre FROM municipios ORDER BY id')
    municipios = cursor.fetchall()
    
    for mun_id, mun_nombre in municipios:
        print(f"\n📍 Municipio: {mun_nombre} (ID: {mun_id})")
        
        # Obtener zonas actuales del municipio
        cursor.execute('''
            SELECT id, codigo_zz, nombre, tipo_zona 
            FROM zonas 
            WHERE municipio_id = ? 
            ORDER BY 
                CASE tipo_zona
                    WHEN 'urbana' THEN 1
                    WHEN 'rural' THEN 2
                    WHEN 'carcel' THEN 3
                    WHEN 'censo' THEN 4
                    ELSE 5
                END,
                codigo_zz
        ''', (mun_id,))
        
        zonas = cursor.fetchall()
        
        if not zonas:
            print("  ⚠️  No tiene zonas")
            continue
        
        # Renumerar zonas
        for idx, (zona_id, codigo_zz, nombre_actual, tipo_zona) in enumerate(zonas, start=1):
            nuevo_codigo = f"{idx:02d}"  # 01, 02, 03, etc.
            nuevo_nombre = f"Zona {idx:02d}"
            
            # Mantener descripción del tipo en el campo descripcion
            descripcion_tipo = {
                'urbana': 'Zona Urbana',
                'rural': 'Zona Rural',
                'carcel': 'Cárceles',
                'censo': 'Puesto de Censo'
            }.get(tipo_zona, 'Zona')
            
            print(f"  ✏️  Zona {zona_id}: '{nombre_actual}' → '{nuevo_nombre}' (código: {nuevo_codigo})")
            
            # Actualizar zona
            cursor.execute('''
                UPDATE zonas 
                SET codigo_zz = ?,
                    nombre = ?,
                    descripcion = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (nuevo_codigo, nuevo_nombre, descripcion_tipo, zona_id))
    
    # Commit cambios
    conn.commit()
    
    print("\n" + "="*60)
    print("✅ ZONAS ACTUALIZADAS CORRECTAMENTE")
    print("="*60)
    
    # Mostrar resultado
    print("\n=== ZONAS DESPUÉS DE LA CORRECCIÓN ===\n")
    cursor.execute('''
        SELECT z.id, z.codigo_zz, z.nombre, z.descripcion, m.nombre as municipio
        FROM zonas z
        JOIN municipios m ON z.municipio_id = m.id
        ORDER BY m.nombre, z.codigo_zz
        LIMIT 30
    ''')
    
    rows = cursor.fetchall()
    print(f"{'ID':<5} {'Código':<8} {'Nombre':<15} {'Descripción':<20} {'Municipio':<25}")
    print("-" * 85)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<8} {row[2]:<15} {row[3]:<20} {row[4]:<25}")
    
    conn.close()
    print(f"\n✅ Total de zonas actualizadas: {len(rows)}")

if __name__ == '__main__':
    try:
        fix_zonas()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
