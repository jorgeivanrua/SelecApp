#!/usr/bin/env python3
"""
Verificar que los datos en la BD coincidan con DIVIPOLA oficial
"""

import sqlite3

# Datos oficiales DIVIPOLA del Caquetá
MUNICIPIOS_DIVIPOLA = {
    '18001': 'Florencia',
    '18029': 'Albania',
    '18094': 'Belén de los Andaquíes',
    '18150': 'Cartagena del Chairá',
    '18205': 'Curillo',
    '18247': 'El Doncello',
    '18256': 'El Paujil',
    '18410': 'La Montañita',
    '18460': 'Milán',
    '18479': 'Morelia',
    '18592': 'Puerto Rico',
    '18610': 'San José del Fragua',
    '18753': 'San Vicente del Caguán',
    '18756': 'Solano',
    '18785': 'Solita',
    '18860': 'Valparaíso'
}

def verificar_bd():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("="*80)
    print("VERIFICACIÓN DE DATOS DIVIPOLA EN BASE DE DATOS")
    print("="*80)
    
    # Verificar municipios
    print("\n📍 VERIFICANDO MUNICIPIOS\n")
    cursor.execute('SELECT codigo, nombre FROM municipios ORDER BY codigo')
    municipios_bd = cursor.fetchall()
    
    print(f"Total en DIVIPOLA oficial: {len(MUNICIPIOS_DIVIPOLA)}")
    print(f"Total en BD: {len(municipios_bd)}")
    
    if len(municipios_bd) != len(MUNICIPIOS_DIVIPOLA):
        print("⚠️  ADVERTENCIA: El número de municipios no coincide!")
    else:
        print("✅ Número de municipios correcto")
    
    print("\nComparación detallada:")
    print(f"{'Código':<10} {'DIVIPOLA':<35} {'Base de Datos':<35} {'Estado':<10}")
    print("-"*95)
    
    municipios_bd_dict = {codigo: nombre for codigo, nombre in municipios_bd}
    
    errores = 0
    for codigo, nombre_divipola in sorted(MUNICIPIOS_DIVIPOLA.items()):
        nombre_bd = municipios_bd_dict.get(codigo, 'NO ENCONTRADO')
        
        if nombre_bd == nombre_divipola:
            estado = "✅ OK"
        elif nombre_bd == 'NO ENCONTRADO':
            estado = "❌ FALTA"
            errores += 1
        else:
            estado = "⚠️  DIFIERE"
            errores += 1
        
        print(f"{codigo:<10} {nombre_divipola:<35} {nombre_bd:<35} {estado:<10}")
    
    # Verificar si hay municipios extra en la BD
    for codigo, nombre in municipios_bd:
        if codigo not in MUNICIPIOS_DIVIPOLA:
            print(f"{codigo:<10} {'(no en DIVIPOLA)':<35} {nombre:<35} {'❌ EXTRA':<10}")
            errores += 1
    
    print("\n" + "="*80)
    if errores == 0:
        print("✅ TODOS LOS MUNICIPIOS COINCIDEN CON DIVIPOLA")
    else:
        print(f"❌ SE ENCONTRARON {errores} ERRORES")
    print("="*80)
    
    # Verificar estructura de códigos
    print("\n📍 VERIFICANDO ESTRUCTURA DE CÓDIGOS\n")
    cursor.execute('SELECT codigo, codigo_dd, codigo_mm FROM municipios LIMIT 5')
    print(f"{'Código Completo':<20} {'Código DD':<15} {'Código MM':<15}")
    print("-"*50)
    for row in cursor.fetchall():
        print(f"{row[0]:<20} {row[1]:<15} {row[2]:<15}")
    
    # Verificar zonas
    print("\n📍 VERIFICANDO ZONAS\n")
    cursor.execute('''
        SELECT m.nombre, COUNT(z.id) as num_zonas
        FROM municipios m
        LEFT JOIN zonas z ON m.id = z.municipio_id
        GROUP BY m.id, m.nombre
        ORDER BY m.nombre
    ''')
    
    print(f"{'Municipio':<35} {'Zonas':<10}")
    print("-"*45)
    total_zonas = 0
    for row in cursor.fetchall():
        print(f"{row[0]:<35} {row[1]:<10}")
        total_zonas += row[1]
    
    print(f"\n{'TOTAL':<35} {total_zonas:<10}")
    
    # Verificar puestos y mesas
    print("\n📍 VERIFICANDO PUESTOS Y MESAS\n")
    cursor.execute('SELECT COUNT(*) FROM puestos_votacion')
    total_puestos = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM mesas_votacion')
    total_mesas = cursor.fetchone()[0]
    
    print(f"Total puestos de votación: {total_puestos}")
    print(f"Total mesas de votación: {total_mesas}")
    
    # Detalle de puestos por municipio
    print("\n📍 PUESTOS POR MUNICIPIO\n")
    cursor.execute('''
        SELECT m.nombre, COUNT(DISTINCT p.id) as num_puestos, COUNT(mv.id) as num_mesas
        FROM municipios m
        LEFT JOIN puestos_votacion p ON m.id = p.municipio_id
        LEFT JOIN mesas_votacion mv ON p.id = mv.puesto_id
        GROUP BY m.id, m.nombre
        HAVING num_puestos > 0
        ORDER BY m.nombre
    ''')
    
    print(f"{'Municipio':<35} {'Puestos':<10} {'Mesas':<10}")
    print("-"*55)
    for row in cursor.fetchall():
        print(f"{row[0]:<35} {row[1]:<10} {row[2]:<10}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("VERIFICACIÓN COMPLETADA")
    print("="*80)

if __name__ == '__main__':
    verificar_bd()
