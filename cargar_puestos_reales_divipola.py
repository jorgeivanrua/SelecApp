#!/usr/bin/env python3
"""
Script para cargar los puestos y mesas REALES desde el archivo DIVIPOLA del Caquetá.
Esto reemplazará los datos ficticios con los datos oficiales.
"""

import sqlite3
import csv
from collections import defaultdict

def cargar_puestos_reales_divipola():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("CARGA DE PUESTOS Y MESAS REALES DESDE DIVIPOLA")
    print("=" * 70)
    
    # Primero, eliminar puestos y mesas existentes
    print("\n🗑️  Eliminando puestos y mesas ficticios...")
    cursor.execute('DELETE FROM mesas_votacion')
    cursor.execute('DELETE FROM puestos_votacion')
    conn.commit()
    print("✅ Datos ficticios eliminados")
    
    # Leer el archivo DIVIPOLA y agrupar por municipio y puesto
    puestos_por_municipio = defaultdict(list)
    
    with open('divipola.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Filtrar solo Caquetá
            if row['departamento'] == 'CAQUETA':
                municipio = row['municipio']
                puesto_nombre = row['puesto']
                direccion = row['dirección']
                total_votantes = int(row['total'])
                num_mesas = int(row['mesas'])
                zona_codigo = row['zz']
                
                puestos_por_municipio[municipio].append({
                    'nombre': puesto_nombre,
                    'direccion': direccion,
                    'total_votantes': total_votantes,
                    'num_mesas': num_mesas,
                    'zona_codigo': zona_codigo
                })
    
    print(f"\n📊 Municipios encontrados: {len(puestos_por_municipio)}")
    print(f"📊 Total de puestos a cargar: {sum(len(p) for p in puestos_por_municipio.values())}")
    
    # Cargar puestos y mesas por municipio
    total_puestos = 0
    total_mesas = 0
    
    for municipio_nombre, puestos in sorted(puestos_por_municipio.items()):
        # Obtener ID del municipio
        cursor.execute('SELECT id FROM municipios WHERE UPPER(nombre) = ?', (municipio_nombre,))
        result = cursor.fetchone()
        
        if not result:
            print(f"⚠️  Municipio no encontrado en BD: {municipio_nombre}")
            continue
        
        municipio_id = result[0]
        
        print(f"\n📍 {municipio_nombre} ({len(puestos)} puestos)")
        
        for puesto_data in puestos:
            # Buscar la zona correspondiente
            cursor.execute('''
                SELECT id FROM zonas 
                WHERE municipio_id = ? AND codigo_zz = ?
            ''', (municipio_id, puesto_data['zona_codigo']))
            
            zona_result = cursor.fetchone()
            zona_id = zona_result[0] if zona_result else None
            
            # Insertar puesto
            cursor.execute('''
                INSERT INTO puestos_votacion (
                    nombre, direccion, municipio_id, zona_id,
                    capacidad_votantes, estado, activo,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'configurado', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (
                puesto_data['nombre'],
                puesto_data['direccion'],
                municipio_id,
                zona_id,
                puesto_data['total_votantes']
            ))
            
            puesto_id = cursor.lastrowid
            total_puestos += 1
            
            # Calcular votantes por mesa
            num_mesas = puesto_data['num_mesas']
            total_votantes = puesto_data['total_votantes']
            votantes_por_mesa = total_votantes // num_mesas
            votantes_restantes = total_votantes % num_mesas
            
            # Crear mesas
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
                
                total_mesas += 1
            
            print(f"   ✅ {puesto_data['nombre'][:50]}: {total_votantes} votantes, {num_mesas} mesas")
    
    conn.commit()
    
    print("\n" + "=" * 70)
    print(f"✅ CARGA COMPLETADA")
    print(f"   Puestos creados: {total_puestos}")
    print(f"   Mesas creadas: {total_mesas}")
    print("=" * 70)
    
    # Verificar resumen por municipio
    print("\n📊 RESUMEN POR MUNICIPIO:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT 
            m.nombre as municipio,
            COUNT(DISTINCT pv.id) as num_puestos,
            COUNT(DISTINCT mv.id) as num_mesas,
            SUM(pv.capacidad_votantes) as total_votantes
        FROM municipios m
        LEFT JOIN puestos_votacion pv ON m.id = pv.municipio_id
        LEFT JOIN mesas_votacion mv ON pv.id = mv.puesto_id
        WHERE m.activo = 1
        GROUP BY m.id, m.nombre
        ORDER BY m.nombre
    ''')
    
    for row in cursor.fetchall():
        municipio, num_puestos, num_mesas, total_votantes = row
        total_votantes = total_votantes or 0
        print(f"{municipio:30} | Puestos: {num_puestos:3} | Mesas: {num_mesas:4} | Votantes: {total_votantes:7}")
    
    conn.close()

if __name__ == '__main__':
    cargar_puestos_reales_divipola()
