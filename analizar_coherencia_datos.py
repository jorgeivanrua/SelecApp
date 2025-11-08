#!/usr/bin/env python3
"""
Script para analizar la coherencia de los datos en la base de datos
"""

import sqlite3

def analizar_coherencia():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("ANÁLISIS DE COHERENCIA DE DATOS")
    print("=" * 80)
    
    # 1. Verificar municipios
    print("\n1. MUNICIPIOS")
    print("-" * 80)
    cursor.execute('SELECT COUNT(*) FROM municipios WHERE activo = 1')
    print(f"Total municipios activos: {cursor.fetchone()[0]}")
    
    # 2. Verificar zonas
    print("\n2. ZONAS")
    print("-" * 80)
    cursor.execute('''
        SELECT m.nombre, COUNT(z.id) as num_zonas
        FROM municipios m
        LEFT JOIN zonas z ON m.id = z.municipio_id AND z.activo = 1
        WHERE m.activo = 1
        GROUP BY m.id
        ORDER BY m.nombre
    ''')
    
    for row in cursor.fetchall():
        municipio, num_zonas = row
        print(f"{municipio:30} | {num_zonas:2} zonas")
    
    # 3. Verificar puestos
    print("\n3. PUESTOS DE VOTACIÓN")
    print("-" * 80)
    cursor.execute('''
        SELECT m.nombre, COUNT(pv.id) as num_puestos
        FROM municipios m
        LEFT JOIN puestos_votacion pv ON m.id = pv.municipio_id AND pv.activo = 1
        WHERE m.activo = 1
        GROUP BY m.id
        ORDER BY m.nombre
    ''')
    
    total_puestos = 0
    for row in cursor.fetchall():
        municipio, num_puestos = row
        total_puestos += num_puestos
        print(f"{municipio:30} | {num_puestos:3} puestos")
    
    print(f"\nTotal puestos: {total_puestos}")
    
    # 4. Verificar puestos sin zona
    print("\n4. PUESTOS SIN ZONA ASIGNADA")
    print("-" * 80)
    cursor.execute('''
        SELECT m.nombre, pv.nombre
        FROM puestos_votacion pv
        JOIN municipios m ON pv.municipio_id = m.id
        WHERE pv.zona_id IS NULL AND pv.activo = 1
        ORDER BY m.nombre, pv.nombre
    ''')
    
    puestos_sin_zona = cursor.fetchall()
    if puestos_sin_zona:
        for municipio, puesto in puestos_sin_zona:
            print(f"⚠️  {municipio} - {puesto}")
    else:
        print("✅ Todos los puestos tienen zona asignada")
    
    # 5. Verificar mesas
    print("\n5. MESAS DE VOTACIÓN")
    print("-" * 80)
    cursor.execute('''
        SELECT m.nombre, COUNT(mv.id) as num_mesas, SUM(mv.votantes_habilitados) as total_votantes
        FROM municipios m
        LEFT JOIN mesas_votacion mv ON m.id = mv.municipio_id AND mv.activa = 1
        WHERE m.activo = 1
        GROUP BY m.id
        ORDER BY m.nombre
    ''')
    
    total_mesas = 0
    total_votantes = 0
    for row in cursor.fetchall():
        municipio, num_mesas, votantes = row
        total_mesas += num_mesas or 0
        total_votantes += votantes or 0
        print(f"{municipio:30} | {num_mesas or 0:3} mesas | {votantes or 0:7} votantes")
    
    print(f"\nTotal mesas: {total_mesas}")
    print(f"Total votantes: {total_votantes}")
    
    # 6. Verificar mesas sin puesto
    print("\n6. MESAS SIN PUESTO ASIGNADO")
    print("-" * 80)
    cursor.execute('''
        SELECT COUNT(*) FROM mesas_votacion
        WHERE puesto_id IS NULL AND activa = 1
    ''')
    
    mesas_sin_puesto = cursor.fetchone()[0]
    if mesas_sin_puesto > 0:
        print(f"⚠️  {mesas_sin_puesto} mesas sin puesto asignado")
    else:
        print("✅ Todas las mesas tienen puesto asignado")
    
    # 7. Verificar coherencia puesto-mesa
    print("\n7. COHERENCIA PUESTOS-MESAS")
    print("-" * 80)
    cursor.execute('''
        SELECT 
            m.nombre as municipio,
            pv.nombre as puesto,
            pv.capacidad_votantes as votantes_puesto,
            COUNT(mv.id) as num_mesas,
            SUM(mv.votantes_habilitados) as votantes_mesas
        FROM puestos_votacion pv
        JOIN municipios m ON pv.municipio_id = m.id
        LEFT JOIN mesas_votacion mv ON pv.id = mv.puesto_id AND mv.activa = 1
        WHERE pv.activo = 1
        GROUP BY pv.id
        HAVING votantes_puesto != COALESCE(votantes_mesas, 0)
        ORDER BY m.nombre, pv.nombre
        LIMIT 20
    ''')
    
    incoherencias = cursor.fetchall()
    if incoherencias:
        print("⚠️  Puestos con incoherencia entre votantes del puesto y suma de mesas:")
        for municipio, puesto, vot_puesto, num_mesas, vot_mesas in incoherencias:
            print(f"  {municipio} - {puesto[:50]}")
            print(f"    Puesto: {vot_puesto} votantes | Mesas: {num_mesas} mesas con {vot_mesas or 0} votantes")
    else:
        print("✅ Coherencia correcta entre puestos y mesas")
    
    # 8. Verificar zonas duplicadas
    print("\n8. ZONAS DUPLICADAS")
    print("-" * 80)
    cursor.execute('''
        SELECT m.nombre, z.codigo_zz, COUNT(*) as duplicados
        FROM zonas z
        JOIN municipios m ON z.municipio_id = m.id
        WHERE z.activo = 1
        GROUP BY z.municipio_id, z.codigo_zz
        HAVING COUNT(*) > 1
        ORDER BY m.nombre, z.codigo_zz
    ''')
    
    duplicados = cursor.fetchall()
    if duplicados:
        print("⚠️  Zonas duplicadas encontradas:")
        for municipio, codigo, count in duplicados:
            print(f"  {municipio} - Zona {codigo}: {count} registros")
    else:
        print("✅ No hay zonas duplicadas")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("ANÁLISIS COMPLETADO")
    print("=" * 80)

if __name__ == '__main__':
    analizar_coherencia()
