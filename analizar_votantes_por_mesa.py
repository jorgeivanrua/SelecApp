#!/usr/bin/env python3
"""
Analizar la distribución de votantes por mesa según la Registraduría.
Regla: Máximo 400 votantes por mesa (excepto zona 90 que puede tener más)
"""

import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

print("=" * 70)
print("ANÁLISIS DE VOTANTES POR MESA")
print("=" * 70)

# Estadísticas generales
cursor.execute('''
    SELECT 
        MIN(votantes_habilitados) as min, 
        MAX(votantes_habilitados) as max, 
        AVG(votantes_habilitados) as avg,
        COUNT(*) as total_mesas
    FROM mesas_votacion
''')
row = cursor.fetchone()
print(f'\n📊 ESTADÍSTICAS GENERALES:')
print(f'   Total de mesas: {row[3]}')
print(f'   Mínimo votantes: {row[0]}')
print(f'   Máximo votantes: {row[1]}')
print(f'   Promedio votantes: {row[2]:.0f}')

# Mesas con más de 400 votantes
cursor.execute('''
    SELECT 
        mv.numero,
        mv.votantes_habilitados,
        pv.nombre as puesto,
        m.nombre as municipio,
        z.codigo_zz as zona
    FROM mesas_votacion mv
    JOIN puestos_votacion pv ON mv.puesto_id = pv.id
    JOIN municipios m ON mv.municipio_id = m.id
    LEFT JOIN zonas z ON pv.zona_id = z.id
    WHERE mv.votantes_habilitados > 400
    ORDER BY mv.votantes_habilitados DESC
''')

mesas_excedidas = cursor.fetchall()
print(f'\n⚠️  MESAS CON MÁS DE 400 VOTANTES: {len(mesas_excedidas)}')
print('-' * 70)
for row in mesas_excedidas[:20]:  # Mostrar primeras 20
    mesa, votantes, puesto, municipio, zona = row
    zona_str = f"Zona {zona}" if zona else "Sin zona"
    print(f'Mesa {mesa}: {votantes:4} votantes | {municipio} - {puesto[:40]} | {zona_str}')

# Verificar si hay zona 90
cursor.execute('''
    SELECT COUNT(*) FROM zonas WHERE codigo_zz = '90'
''')
tiene_zona_90 = cursor.fetchone()[0] > 0
print(f'\n📍 ¿Existe Zona 90 en la BD?: {"SÍ" if tiene_zona_90 else "NO"}')

# Distribución por rangos
print(f'\n📊 DISTRIBUCIÓN POR RANGOS:')
print('-' * 70)

rangos = [
    (0, 100, '0-100'),
    (101, 200, '101-200'),
    (201, 300, '201-300'),
    (301, 400, '301-400'),
    (401, 500, '401-500'),
    (501, 1000, '501-1000'),
    (1001, 2000, '1001-2000'),
    (2001, 5000, '2001-5000')
]

for min_v, max_v, label in rangos:
    cursor.execute('''
        SELECT COUNT(*) 
        FROM mesas_votacion 
        WHERE votantes_habilitados BETWEEN ? AND ?
    ''', (min_v, max_v))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f'   {label:12} votantes: {count:3} mesas')

# Puestos que necesitan más mesas
print(f'\n🔧 PUESTOS QUE NECESITAN REDISTRIBUCIÓN (>400 votantes/mesa):')
print('-' * 70)

cursor.execute('''
    SELECT 
        pv.nombre as puesto,
        m.nombre as municipio,
        pv.capacidad_votantes,
        COUNT(mv.id) as num_mesas,
        AVG(mv.votantes_habilitados) as promedio_por_mesa,
        MAX(mv.votantes_habilitados) as max_por_mesa
    FROM puestos_votacion pv
    JOIN municipios m ON pv.municipio_id = m.id
    JOIN mesas_votacion mv ON pv.id = mv.puesto_id
    GROUP BY pv.id
    HAVING max_por_mesa > 400
    ORDER BY max_por_mesa DESC
''')

puestos_problema = cursor.fetchall()
print(f'   Total de puestos: {len(puestos_problema)}')
print()
for row in puestos_problema[:15]:  # Mostrar primeros 15
    puesto, municipio, total, num_mesas, promedio, max_mesa = row
    mesas_necesarias = (total + 399) // 400  # Redondear hacia arriba
    print(f'{municipio} - {puesto[:35]:35}')
    print(f'   Total: {total:5} votantes | Mesas actuales: {num_mesas} | Máx/mesa: {int(max_mesa):4}')
    print(f'   Mesas recomendadas: {mesas_necesarias} (para max 400 votantes/mesa)')
    print()

conn.close()

print("=" * 70)
print("RECOMENDACIÓN:")
print("Según la Registraduría, cada mesa debe tener máximo 400 votantes")
print("(excepto zona 90 que puede tener más).")
print("Se debe redistribuir las mesas en los puestos que exceden este límite.")
print("=" * 70)
