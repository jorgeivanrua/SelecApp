#!/usr/bin/env python3
"""
Script para actualizar la zona_id de los puestos basándose en los datos de DIVIPOLA.
"""

import sqlite3
import csv

def actualizar_zonas_puestos():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("ACTUALIZAR ZONAS DE PUESTOS DESDE DIVIPOLA")
    print("=" * 70)
    
    # Leer DIVIPOLA y crear un mapa de puesto -> zona
    puesto_zona_map = {}
    
    with open('divipola.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['departamento'] == 'CAQUETA':
                municipio = row['municipio']
                puesto = row['puesto']
                zona_codigo = row['zz'].replace('.0', '')
                
                key = f"{municipio}|{puesto}"
                puesto_zona_map[key] = zona_codigo
    
    print(f"\n📊 Puestos en DIVIPOLA: {len(puesto_zona_map)}")
    
    # Obtener todos los puestos de la BD
    cursor.execute('''
        SELECT pv.id, pv.nombre, m.nombre as municipio, pv.zona_id
        FROM puestos_votacion pv
        JOIN municipios m ON pv.municipio_id = m.id
        WHERE pv.activo = 1
        ORDER BY m.nombre, pv.nombre
    ''')
    
    puestos = cursor.fetchall()
    total_actualizados = 0
    total_sin_zona = 0
    
    print(f"\n🔄 Actualizando {len(puestos)} puestos...\n")
    
    for puesto_id, puesto_nombre, municipio_nombre, zona_id_actual in puestos:
        municipio_upper = municipio_nombre.upper()
        key = f"{municipio_upper}|{puesto_nombre}"
        
        if key in puesto_zona_map:
            zona_codigo = puesto_zona_map[key]
            
            # Convertir zona "0" a "00" para cabecera municipal
            if zona_codigo == '0':
                zona_codigo = '00'
            
            # Buscar el ID de la zona
            cursor.execute('''
                SELECT id FROM zonas 
                WHERE municipio_id = (SELECT id FROM municipios WHERE nombre = ?)
                  AND codigo_zz = ?
            ''', (municipio_nombre, zona_codigo))
            
            result = cursor.fetchone()
            
            if result:
                nueva_zona_id = result[0]
                
                if zona_id_actual != nueva_zona_id:
                    # Actualizar
                    cursor.execute('''
                        UPDATE puestos_votacion
                        SET zona_id = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (nueva_zona_id, puesto_id))
                    
                    print(f"✅ {municipio_nombre} - {puesto_nombre[:50]}: Zona {zona_codigo}")
                    total_actualizados += 1
            else:
                print(f"⚠️  {municipio_nombre} - {puesto_nombre[:50]}: Zona {zona_codigo} no encontrada en BD")
                total_sin_zona += 1
        else:
            print(f"⚠️  {municipio_nombre} - {puesto_nombre[:50]}: No encontrado en DIVIPOLA")
            total_sin_zona += 1
    
    conn.commit()
    
    print("\n" + "=" * 70)
    print(f"✅ ACTUALIZACIÓN COMPLETADA")
    print(f"   Puestos actualizados: {total_actualizados}")
    print(f"   Puestos sin zona: {total_sin_zona}")
    print("=" * 70)
    
    # Verificar distribución de puestos por zona
    print("\n📊 DISTRIBUCIÓN DE PUESTOS POR ZONA:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT 
            m.nombre as municipio,
            z.codigo_zz,
            z.nombre as zona,
            COUNT(pv.id) as num_puestos
        FROM municipios m
        LEFT JOIN zonas z ON m.id = z.municipio_id AND z.activo = 1
        LEFT JOIN puestos_votacion pv ON z.id = pv.zona_id AND pv.activo = 1
        WHERE m.activo = 1
        GROUP BY m.id, z.id
        HAVING num_puestos > 0
        ORDER BY m.nombre, z.codigo_zz
    ''')
    
    for row in cursor.fetchall():
        municipio, codigo, zona, num_puestos = row
        print(f"{municipio:25} | Zona {codigo:2} - {zona:20} | {num_puestos:2} puestos")
    
    conn.close()

if __name__ == '__main__':
    actualizar_zonas_puestos()
