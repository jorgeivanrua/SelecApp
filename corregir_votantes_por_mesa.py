#!/usr/bin/env python3
"""
Script para corregir la distribución de votantes por mesa.
El total de DIVIPOLA es por PUESTO, no por mesa.
Debemos dividir el total del puesto entre sus mesas.
"""

import sqlite3

def corregir_votantes_por_mesa():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("CORRECCIÓN DE VOTANTES POR MESA")
    print("=" * 70)
    
    # Obtener todos los puestos con sus totales de votantes
    cursor.execute('''
        SELECT id, nombre, municipio_id, capacidad_votantes
        FROM puestos_votacion
        WHERE activo = 1
        ORDER BY municipio_id, nombre
    ''')
    
    puestos = cursor.fetchall()
    total_puestos = len(puestos)
    total_mesas_actualizadas = 0
    
    print(f"\nProcesando {total_puestos} puestos de votación...\n")
    
    for puesto in puestos:
        puesto_id, puesto_nombre, municipio_id, total_votantes_puesto = puesto
        
        # Obtener el nombre del municipio
        cursor.execute('SELECT nombre FROM municipios WHERE id = ?', (municipio_id,))
        municipio_nombre = cursor.fetchone()[0]
        
        # Contar cuántas mesas tiene este puesto
        cursor.execute('''
            SELECT COUNT(*) FROM mesas_votacion 
            WHERE puesto_id = ? AND activa = 1
        ''', (puesto_id,))
        
        num_mesas = cursor.fetchone()[0]
        
        if num_mesas == 0:
            print(f"⚠️  {municipio_nombre} - {puesto_nombre}: Sin mesas")
            continue
        
        # Calcular votantes por mesa (distribución equitativa)
        votantes_por_mesa = total_votantes_puesto // num_mesas
        votantes_restantes = total_votantes_puesto % num_mesas
        
        print(f"📍 {municipio_nombre} - {puesto_nombre}")
        print(f"   Total votantes puesto: {total_votantes_puesto}")
        print(f"   Número de mesas: {num_mesas}")
        print(f"   Votantes por mesa: {votantes_por_mesa}")
        if votantes_restantes > 0:
            print(f"   Votantes extra (primeras mesas): {votantes_restantes}")
        
        # Obtener todas las mesas del puesto
        cursor.execute('''
            SELECT id, numero FROM mesas_votacion 
            WHERE puesto_id = ? AND activa = 1
            ORDER BY numero
        ''', (puesto_id,))
        
        mesas = cursor.fetchall()
        
        # Actualizar cada mesa
        for idx, (mesa_id, mesa_numero) in enumerate(mesas):
            # Las primeras mesas reciben un votante extra si hay resto
            votantes_mesa = votantes_por_mesa + (1 if idx < votantes_restantes else 0)
            
            cursor.execute('''
                UPDATE mesas_votacion 
                SET votantes_habilitados = ?,
                    total_votantes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (votantes_mesa, votantes_mesa, mesa_id))
            
            total_mesas_actualizadas += 1
        
        print(f"   ✅ {num_mesas} mesas actualizadas\n")
    
    conn.commit()
    
    print("=" * 70)
    print(f"✅ CORRECCIÓN COMPLETADA")
    print(f"   Puestos procesados: {total_puestos}")
    print(f"   Mesas actualizadas: {total_mesas_actualizadas}")
    print("=" * 70)
    
    # Verificar algunos ejemplos
    print("\n📊 VERIFICACIÓN - Ejemplos de mesas actualizadas:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT 
            m.nombre as municipio,
            pv.nombre as puesto,
            mv.numero as mesa,
            mv.votantes_habilitados,
            pv.capacidad_votantes as total_puesto
        FROM mesas_votacion mv
        JOIN puestos_votacion pv ON mv.puesto_id = pv.id
        JOIN municipios m ON pv.municipio_id = m.id
        WHERE mv.activa = 1
        ORDER BY m.nombre, pv.nombre, mv.numero
        LIMIT 20
    ''')
    
    for row in cursor.fetchall():
        municipio, puesto, mesa, votantes, total_puesto = row
        print(f"{municipio} - {puesto} - Mesa {mesa}: {votantes} votantes (Puesto: {total_puesto})")
    
    conn.close()

if __name__ == '__main__':
    corregir_votantes_por_mesa()
