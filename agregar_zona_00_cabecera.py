#!/usr/bin/env python3
"""
Script para agregar la zona 00 (Cabecera Municipal) a los municipios que la necesitan
y corregir las zonas 1-4 de Florencia.
"""

import sqlite3
import csv
from collections import defaultdict

def agregar_zona_cabecera():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("AGREGAR ZONA 00 (CABECERA MUNICIPAL) Y CORREGIR ZONAS URBANAS")
    print("=" * 70)
    
    # Leer DIVIPOLA para ver qué municipios tienen zona 0
    municipios_con_zona_0 = set()
    
    with open('divipola.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['departamento'] == 'CAQUETA' and row['zz'] == '0.0':
                municipios_con_zona_0.add(row['municipio'])
    
    print(f"\n📊 Municipios con zona 0 en DIVIPOLA: {len(municipios_con_zona_0)}")
    
    total_agregadas = 0
    
    # Obtener todos los municipios
    cursor.execute('SELECT id, nombre FROM municipios WHERE activo = 1 ORDER BY nombre')
    municipios = cursor.fetchall()
    
    for municipio_id, municipio_nombre in municipios:
        municipio_upper = municipio_nombre.upper()
        
        if municipio_upper in municipios_con_zona_0:
            # Verificar si ya existe zona 00
            cursor.execute('''
                SELECT id FROM zonas 
                WHERE municipio_id = ? AND codigo_zz = '00'
            ''', (municipio_id,))
            
            if cursor.fetchone():
                print(f"   ⚠️  {municipio_nombre}: Zona 00 ya existe")
            else:
                # Agregar zona 00
                cursor.execute('''
                    INSERT INTO zonas (
                        codigo_zz, nombre, municipio_id, descripcion, 
                        activo, tipo_zona, created_at, updated_at
                    ) VALUES ('00', 'Zona 00', ?, 'Cabecera Municipal', 1, 'urbana', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (municipio_id,))
                
                print(f"   ✅ {municipio_nombre}: Agregada Zona 00 - Cabecera Municipal")
                total_agregadas += 1
    
    # Caso especial: Florencia tiene zonas 1, 2, 3, 4 que son comunas urbanas
    print(f"\n📍 Verificando zonas urbanas de Florencia...")
    
    cursor.execute("SELECT id FROM municipios WHERE nombre = 'Florencia'")
    florencia_id = cursor.fetchone()[0]
    
    zonas_florencia = {
        '1': {'nombre': 'Comuna 1', 'descripcion': 'Comuna 1 Occidental', 'tipo': 'urbana'},
        '2': {'nombre': 'Comuna 2', 'descripcion': 'Comuna 2 Sur', 'tipo': 'urbana'},
        '3': {'nombre': 'Comuna 3', 'descripcion': 'Comuna 3 Norte', 'tipo': 'urbana'},
        '4': {'nombre': 'Comuna 4', 'descripcion': 'Comuna 4 Oriental', 'tipo': 'urbana'}
    }
    
    for codigo, info in zonas_florencia.items():
        cursor.execute('''
            SELECT id FROM zonas 
            WHERE municipio_id = ? AND codigo_zz = ?
        ''', (florencia_id, codigo))
        
        if cursor.fetchone():
            print(f"   ⚠️  Florencia: Zona {codigo} ya existe")
        else:
            cursor.execute('''
                INSERT INTO zonas (
                    codigo_zz, nombre, municipio_id, descripcion, 
                    activo, tipo_zona, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (codigo, info['nombre'], florencia_id, info['descripcion'], info['tipo']))
            
            print(f"   ✅ Florencia: Agregada Zona {codigo} - {info['nombre']}")
            total_agregadas += 1
    
    conn.commit()
    
    print("\n" + "=" * 70)
    print(f"✅ PROCESO COMPLETADO")
    print(f"   Zonas agregadas: {total_agregadas}")
    print("=" * 70)
    
    # Verificar zonas de Florencia
    print("\n📊 ZONAS DE FLORENCIA:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT codigo_zz, nombre, descripcion, tipo_zona
        FROM zonas
        WHERE municipio_id = ? AND activo = 1
        ORDER BY CAST(codigo_zz AS INTEGER)
    ''', (florencia_id,))
    
    for row in cursor.fetchall():
        codigo, nombre, descripcion, tipo = row
        print(f"Zona {codigo:2} - {nombre:15} | {descripcion:30} | Tipo: {tipo}")
    
    conn.close()

if __name__ == '__main__':
    agregar_zona_cabecera()
