#!/usr/bin/env python3
"""
Redistribuir mesas para cumplir con la regla de la Registraduría:
Máximo 400 votantes por mesa (excepto zona 90 que puede tener más)
"""

import sqlite3

def redistribuir_mesas():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("REDISTRIBUCIÓN DE MESAS - MÁXIMO 400 VOTANTES")
    print("=" * 70)
    
    # Eliminar todas las mesas actuales
    print("\n🗑️  Eliminando mesas actuales...")
    cursor.execute('DELETE FROM mesas_votacion')
    conn.commit()
    print("✅ Mesas eliminadas")
    
    # Obtener todos los puestos
    cursor.execute('''
        SELECT 
            pv.id,
            pv.nombre,
            pv.capacidad_votantes,
            pv.municipio_id,
            m.nombre as municipio,
            z.codigo_zz as zona_codigo
        FROM puestos_votacion pv
        JOIN municipios m ON pv.municipio_id = m.id
        LEFT JOIN zonas z ON pv.zona_id = z.id
        WHERE pv.activo = 1
        ORDER BY m.nombre, pv.nombre
    ''')
    
    puestos = cursor.fetchall()
    total_puestos = len(puestos)
    total_mesas_creadas = 0
    
    print(f"\n📊 Procesando {total_puestos} puestos...")
    print()
    
    for puesto_id, puesto_nombre, total_votantes, municipio_id, municipio, zona_codigo in puestos:
        # Determinar el límite de votantes por mesa
        # Zona 90 puede tener más de 400
        if zona_codigo == '90':
            max_votantes_por_mesa = 600  # Límite más alto para zona 90
        else:
            max_votantes_por_mesa = 400
        
        # Calcular número de mesas necesarias
        if total_votantes == 0:
            num_mesas = 1  # Al menos una mesa
        else:
            num_mesas = (total_votantes + max_votantes_por_mesa - 1) // max_votantes_por_mesa
        
        # Calcular votantes por mesa
        votantes_por_mesa = total_votantes // num_mesas
        votantes_restantes = total_votantes % num_mesas
        
        # Crear las mesas
        for i in range(num_mesas):
            numero_mesa = str(i + 1).zfill(3)  # 001, 002, 003...
            votantes_mesa = votantes_por_mesa + (1 if i < votantes_restantes else 0)
            
            cursor.execute('''
                INSERT INTO mesas_votacion (
                    numero, puesto_id, municipio_id,
                    votantes_habilitados, total_votantes,
                    estado, activa,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'configurada', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (
                numero_mesa,
                puesto_id,
                municipio_id,
                votantes_mesa,
                votantes_mesa
            ))
            
            total_mesas_creadas += 1
        
        zona_str = f"Zona {zona_codigo}" if zona_codigo else "Sin zona"
        print(f"✅ {municipio} - {puesto_nombre[:45]:45} | {zona_str}")
        print(f"   Total: {total_votantes:5} votantes → {num_mesas:3} mesas (máx {max(votantes_por_mesa, votantes_por_mesa + 1)} votantes/mesa)")
    
    conn.commit()
    
    print("\n" + "=" * 70)
    print(f"✅ REDISTRIBUCIÓN COMPLETADA")
    print(f"   Puestos procesados: {total_puestos}")
    print(f"   Mesas creadas: {total_mesas_creadas}")
    print("=" * 70)
    
    # Verificar que no haya mesas con más de 400 votantes (excepto zona 90)
    print("\n📊 VERIFICACIÓN FINAL:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            MIN(votantes_habilitados) as min,
            MAX(votantes_habilitados) as max,
            AVG(votantes_habilitados) as avg
        FROM mesas_votacion
    ''')
    
    row = cursor.fetchone()
    print(f"Total mesas: {row[0]}")
    print(f"Mínimo votantes/mesa: {row[1]}")
    print(f"Máximo votantes/mesa: {row[2]}")
    print(f"Promedio votantes/mesa: {row[3]:.0f}")
    
    # Verificar mesas que exceden 400 (deben ser solo zona 90)
    cursor.execute('''
        SELECT 
            mv.numero,
            mv.votantes_habilitados,
            pv.nombre,
            m.nombre,
            z.codigo_zz
        FROM mesas_votacion mv
        JOIN puestos_votacion pv ON mv.puesto_id = pv.id
        JOIN municipios m ON mv.municipio_id = m.id
        LEFT JOIN zonas z ON pv.zona_id = z.id
        WHERE mv.votantes_habilitados > 400
        ORDER BY mv.votantes_habilitados DESC
    ''')
    
    mesas_excedidas = cursor.fetchall()
    if mesas_excedidas:
        print(f"\n⚠️  Mesas con más de 400 votantes: {len(mesas_excedidas)}")
        for row in mesas_excedidas[:10]:
            mesa, votantes, puesto, municipio, zona = row
            zona_str = f"Zona {zona}" if zona else "Sin zona"
            print(f"   Mesa {mesa}: {votantes} votantes | {municipio} - {puesto[:30]} | {zona_str}")
    else:
        print(f"\n✅ Todas las mesas tienen 400 votantes o menos")
    
    # Resumen por municipio
    print("\n📊 RESUMEN POR MUNICIPIO:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT 
            m.nombre as municipio,
            COUNT(DISTINCT pv.id) as num_puestos,
            COUNT(DISTINCT mv.id) as num_mesas,
            SUM(pv.capacidad_votantes) as total_votantes,
            AVG(mv.votantes_habilitados) as promedio_por_mesa
        FROM municipios m
        LEFT JOIN puestos_votacion pv ON m.id = pv.municipio_id
        LEFT JOIN mesas_votacion mv ON pv.id = mv.puesto_id
        WHERE m.activo = 1 AND pv.id IS NOT NULL
        GROUP BY m.id, m.nombre
        ORDER BY m.nombre
    ''')
    
    for row in cursor.fetchall():
        municipio, num_puestos, num_mesas, total_votantes, promedio = row
        total_votantes = total_votantes or 0
        promedio = promedio or 0
        print(f"{municipio:30} | Puestos: {num_puestos:3} | Mesas: {num_mesas:4} | Votantes: {total_votantes:7} | Prom/mesa: {promedio:3.0f}")
    
    conn.close()

if __name__ == '__main__':
    redistribuir_mesas()
