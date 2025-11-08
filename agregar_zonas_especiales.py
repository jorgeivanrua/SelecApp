#!/usr/bin/env python3
"""
Script para agregar las zonas especiales 90, 98, 99 a todos los municipios del Caquetá
basándose en los datos de DIVIPOLA.
"""

import sqlite3
import csv
from collections import defaultdict

def agregar_zonas_especiales():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("AGREGAR ZONAS ESPECIALES (90, 98, 99)")
    print("=" * 70)
    
    # Leer DIVIPOLA para ver qué municipios tienen zonas especiales
    zonas_por_municipio = defaultdict(set)
    
    with open('divipola.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['departamento'] == 'CAQUETA':
                municipio = row['municipio']
                zona_codigo = row['zz']
                zonas_por_municipio[municipio].add(zona_codigo)
    
    print(f"\n📊 Analizando zonas en DIVIPOLA...")
    
    # Definir las zonas especiales
    zonas_especiales = {
        '90.0': {'nombre': 'Zona 90', 'descripcion': 'Resguardos Indígenas', 'tipo': 'indigena'},
        '98.0': {'nombre': 'Zona 98', 'descripcion': 'Corregimientos', 'tipo': 'corregimiento'},
        '99.0': {'nombre': 'Zona 99', 'descripcion': 'Zona Rural', 'tipo': 'rural'}
    }
    
    total_agregadas = 0
    
    # Obtener todos los municipios
    cursor.execute('SELECT id, nombre FROM municipios WHERE activo = 1 ORDER BY nombre')
    municipios = cursor.fetchall()
    
    for municipio_id, municipio_nombre in municipios:
        municipio_upper = municipio_nombre.upper()
        
        if municipio_upper not in zonas_por_municipio:
            continue
        
        zonas_municipio = zonas_por_municipio[municipio_upper]
        
        print(f"\n📍 {municipio_nombre}")
        print(f"   Zonas en DIVIPOLA: {sorted(zonas_municipio)}")
        
        # Verificar qué zonas especiales tiene este municipio
        for zona_codigo, zona_info in zonas_especiales.items():
            if zona_codigo in zonas_municipio:
                # Verificar si ya existe
                cursor.execute('''
                    SELECT id FROM zonas 
                    WHERE municipio_id = ? AND codigo_zz = ?
                ''', (municipio_id, zona_codigo.replace('.0', '')))
                
                if cursor.fetchone():
                    print(f"   ⚠️  Zona {zona_codigo} ya existe")
                else:
                    # Agregar la zona
                    cursor.execute('''
                        INSERT INTO zonas (
                            codigo_zz, nombre, municipio_id, descripcion, 
                            activo, tipo_zona, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ''', (
                        zona_codigo.replace('.0', ''),
                        zona_info['nombre'],
                        municipio_id,
                        zona_info['descripcion'],
                        zona_info['tipo']
                    ))
                    
                    print(f"   ✅ Agregada: {zona_info['nombre']} - {zona_info['descripcion']}")
                    total_agregadas += 1
    
    conn.commit()
    
    print("\n" + "=" * 70)
    print(f"✅ PROCESO COMPLETADO")
    print(f"   Zonas especiales agregadas: {total_agregadas}")
    print("=" * 70)
    
    # Verificar resumen de zonas por municipio
    print("\n📊 RESUMEN DE ZONAS POR MUNICIPIO:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT 
            m.nombre as municipio,
            GROUP_CONCAT(z.codigo_zz || ':' || z.nombre, ', ') as zonas
        FROM municipios m
        LEFT JOIN zonas z ON m.id = z.municipio_id AND z.activo = 1
        WHERE m.activo = 1
        GROUP BY m.id, m.nombre
        ORDER BY m.nombre
    ''')
    
    for row in cursor.fetchall():
        municipio, zonas = row
        print(f"{municipio:30} | {zonas}")
    
    conn.close()

if __name__ == '__main__':
    agregar_zonas_especiales()
