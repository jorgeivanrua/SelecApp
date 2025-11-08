#!/usr/bin/env python3
"""
Script para cargar los datos reales de votantes desde el archivo DIVIPOLA
y actualizar los puestos de votación con el total correcto de votantes.
"""

import sqlite3
import csv

def cargar_votantes_desde_divipola():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("CARGA DE VOTANTES DESDE DIVIPOLA")
    print("=" * 70)
    
    # Leer el archivo DIVIPOLA
    puestos_divipola = {}
    
    with open('divipola.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Filtrar solo Caquetá
            if row['departamento'] == 'CAQUETA':
                municipio = row['municipio']
                puesto = row['puesto']
                total_votantes = int(row['total'])
                
                key = f"{municipio}|{puesto}"
                puestos_divipola[key] = total_votantes
    
    print(f"\n📊 Puestos encontrados en DIVIPOLA: {len(puestos_divipola)}")
    
    # Actualizar puestos en la base de datos
    total_actualizados = 0
    total_no_encontrados = 0
    
    # Obtener todos los puestos de la BD
    cursor.execute('''
        SELECT pv.id, pv.nombre, m.nombre as municipio
        FROM puestos_votacion pv
        JOIN municipios m ON pv.municipio_id = m.id
        WHERE pv.activo = 1
        ORDER BY m.nombre, pv.nombre
    ''')
    
    puestos_bd = cursor.fetchall()
    
    print(f"\n🔄 Actualizando {len(puestos_bd)} puestos...\n")
    
    for puesto_id, puesto_nombre, municipio_nombre in puestos_bd:
        # Normalizar nombres para buscar coincidencias
        municipio_upper = municipio_nombre.upper()
        
        # Buscar en DIVIPOLA
        key = f"{municipio_upper}|{puesto_nombre}"
        
        if key in puestos_divipola:
            total_votantes = puestos_divipola[key]
            
            # Actualizar en la BD
            cursor.execute('''
                UPDATE puestos_votacion
                SET capacidad_votantes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (total_votantes, puesto_id))
            
            print(f"✅ {municipio_nombre} - {puesto_nombre}: {total_votantes} votantes")
            total_actualizados += 1
        else:
            print(f"⚠️  {municipio_nombre} - {puesto_nombre}: NO ENCONTRADO en DIVIPOLA")
            total_no_encontrados += 1
    
    conn.commit()
    
    print("\n" + "=" * 70)
    print(f"✅ ACTUALIZACIÓN COMPLETADA")
    print(f"   Puestos actualizados: {total_actualizados}")
    print(f"   Puestos no encontrados: {total_no_encontrados}")
    print("=" * 70)
    
    # Verificar algunos ejemplos
    print("\n📊 VERIFICACIÓN - Ejemplos de puestos actualizados:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT 
            m.nombre as municipio,
            pv.nombre as puesto,
            pv.capacidad_votantes
        FROM puestos_votacion pv
        JOIN municipios m ON pv.municipio_id = m.id
        WHERE pv.activo = 1 AND pv.capacidad_votantes > 0
        ORDER BY m.nombre, pv.nombre
        LIMIT 20
    ''')
    
    for row in cursor.fetchall():
        municipio, puesto, votantes = row
        print(f"{municipio} - {puesto}: {votantes} votantes")
    
    conn.close()

if __name__ == '__main__':
    cargar_votantes_desde_divipola()
