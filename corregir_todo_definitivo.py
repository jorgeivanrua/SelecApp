#!/usr/bin/env python3
"""
Corrección definitiva de todas las zonas, puestos y mesas
"""

import sqlite3
import csv

def corregir_todo():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("CORRECCION DEFINITIVA DE DATOS")
    print("=" * 80)
    
    # 1. Eliminar zonas duplicadas de Florencia (las antiguas 01-06)
    print("\n1. ELIMINANDO ZONAS DUPLICADAS DE FLORENCIA")
    print("-" * 80)
    
    cursor.execute('''
        DELETE FROM zonas
        WHERE municipio_id = 7 
        AND codigo_zz IN ('01', '02', '03', '04', '05', '06')
    ''')
    
    print(f"Eliminadas {cursor.rowcount} zonas antiguas de Florencia")
    
    # 2. Asignar zonas a puestos sin zona usando DIVIPOLA
    print("\n2. ASIGNANDO ZONAS A PUESTOS")
    print("-" * 80)
    
    # Leer DIVIPOLA
    puesto_zona_map = {}
    with open('divipola.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['departamento'] == 'CAQUETA':
                municipio = row['municipio']
                puesto = row['puesto']
                zona_codigo = row['zz'].replace('.0', '')
                if zona_codigo == '0':
                    zona_codigo = '00'
                key = f"{municipio}|{puesto}"
                puesto_zona_map[key] = zona_codigo
    
    # Obtener puestos sin zona
    cursor.execute('''
        SELECT pv.id, pv.nombre, m.nombre as municipio
        FROM puestos_votacion pv
        JOIN municipios m ON pv.municipio_id = m.id
        WHERE pv.zona_id IS NULL AND pv.activo = 1
    ''')
    
    puestos_sin_zona = cursor.fetchall()
    actualizados = 0
    
    for puesto_id, puesto_nombre, municipio_nombre in puestos_sin_zona:
        municipio_upper = municipio_nombre.upper()
        key = f"{municipio_upper}|{puesto_nombre}"
        
        if key in puesto_zona_map:
            zona_codigo = puesto_zona_map[key]
            
            # Buscar zona_id
            cursor.execute('''
                SELECT id FROM zonas
                WHERE municipio_id = (SELECT id FROM municipios WHERE nombre = ?)
                AND codigo_zz = ?
            ''', (municipio_nombre, zona_codigo))
            
            result = cursor.fetchone()
            if result:
                zona_id = result[0]
                cursor.execute('''
                    UPDATE puestos_votacion
                    SET zona_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (zona_id, puesto_id))
                actualizados += 1
                print(f"✅ {municipio_nombre} - {puesto_nombre[:40]} -> Zona {zona_codigo}")
    
    print(f"\nTotal puestos actualizados: {actualizados}")
    
    # 3. Distribuir votantes en mesas
    print("\n3. DISTRIBUYENDO VOTANTES EN MESAS")
    print("-" * 80)
    
    cursor.execute('''
        SELECT id, nombre, capacidad_votantes
        FROM puestos_votacion
        WHERE activo = 1
    ''')
    
    puestos = cursor.fetchall()
    mesas_actualizadas = 0
    
    for puesto_id, puesto_nombre, total_votantes in puestos:
        # Contar mesas del puesto
        cursor.execute('''
            SELECT COUNT(*) FROM mesas_votacion
            WHERE puesto_id = ? AND activa = 1
        ''', (puesto_id,))
        
        num_mesas = cursor.fetchone()[0]
        
        if num_mesas > 0 and total_votantes > 0:
            votantes_por_mesa = total_votantes // num_mesas
            votantes_restantes = total_votantes % num_mesas
            
            # Obtener mesas
            cursor.execute('''
                SELECT id FROM mesas_votacion
                WHERE puesto_id = ? AND activa = 1
                ORDER BY numero
            ''', (puesto_id,))
            
            mesas = cursor.fetchall()
            
            for idx, (mesa_id,) in enumerate(mesas):
                votantes_mesa = votantes_por_mesa + (1 if idx < votantes_restantes else 0)
                
                cursor.execute('''
                    UPDATE mesas_votacion
                    SET votantes_habilitados = ?,
                        total_votantes = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (votantes_mesa, votantes_mesa, mesa_id))
                
                mesas_actualizadas += 1
    
    print(f"Mesas actualizadas: {mesas_actualizadas}")
    
    conn.commit()
    
    # 4. Verificación final
    print("\n4. VERIFICACION FINAL")
    print("-" * 80)
    
    cursor.execute('SELECT COUNT(*) FROM puestos_votacion WHERE zona_id IS NULL AND activo = 1')
    sin_zona = cursor.fetchone()[0]
    print(f"Puestos sin zona: {sin_zona}")
    
    cursor.execute('SELECT COUNT(*) FROM mesas_votacion WHERE votantes_habilitados = 0 AND activa = 1')
    sin_votantes = cursor.fetchone()[0]
    print(f"Mesas sin votantes: {sin_votantes}")
    
    cursor.execute('''
        SELECT COUNT(DISTINCT z.id)
        FROM zonas z
        WHERE z.municipio_id = 7 AND z.activo = 1
    ''')
    zonas_florencia = cursor.fetchone()[0]
    print(f"Zonas de Florencia: {zonas_florencia}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("CORRECCION COMPLETADA")
    print("=" * 80)

if __name__ == '__main__':
    corregir_todo()
