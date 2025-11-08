#!/usr/bin/env python3
"""
Análisis completo de la coherencia de datos
"""

import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

print("=" * 80)
print("ANALISIS COMPLETO DE DATOS")
print("=" * 80)

# 1. Verificar Zona 02 de Florencia
print("\n1. ZONA 02 DE FLORENCIA")
print("-" * 80)

cursor.execute('''
    SELECT id, codigo_zz, nombre, descripcion
    FROM zonas
    WHERE municipio_id = 7 AND codigo_zz = '02'
''')

zona_02 = cursor.fetchone()
if zona_02:
    zona_id = zona_02[0]
    print(f"Zona encontrada: ID={zona_id}, Codigo={zona_02[1]}, Nombre={zona_02[2]}")
    
    # Buscar puestos de esta zona
    cursor.execute('''
        SELECT id, nombre, zona_id
        FROM puestos_votacion
        WHERE zona_id = ? AND activo = 1
    ''', (zona_id,))
    
    puestos = cursor.fetchall()
    print(f"\nPuestos en Zona 02: {len(puestos)}")
    for puesto in puestos:
        print(f"  - ID: {puesto[0]}, Nombre: {puesto[1][:60]}")
else:
    print("⚠️ Zona 02 NO encontrada")

# 2. Verificar todas las zonas de Florencia con puestos
print("\n2. TODAS LAS ZONAS DE FLORENCIA CON PUESTOS")
print("-" * 80)

cursor.execute('''
    SELECT z.codigo_zz, z.nombre, COUNT(pv.id) as num_puestos
    FROM zonas z
    LEFT JOIN puestos_votacion pv ON z.id = pv.zona_id AND pv.activo = 1
    WHERE z.municipio_id = 7 AND z.activo = 1
    GROUP BY z.id
    ORDER BY z.codigo_zz
''')

for row in cursor.fetchall():
    codigo, nombre, num_puestos = row
    print(f"Zona {codigo:3} - {nombre:30} | {num_puestos:2} puestos")

# 3. Verificar puestos sin zona
print("\n3. PUESTOS SIN ZONA ASIGNADA")
print("-" * 80)

cursor.execute('''
    SELECT m.nombre, pv.id, pv.nombre
    FROM puestos_votacion pv
    JOIN municipios m ON pv.municipio_id = m.id
    WHERE pv.zona_id IS NULL AND pv.activo = 1
    ORDER BY m.nombre
''')

puestos_sin_zona = cursor.fetchall()
if puestos_sin_zona:
    print(f"Total: {len(puestos_sin_zona)} puestos sin zona")
    for municipio, puesto_id, puesto_nombre in puestos_sin_zona[:20]:
        print(f"  {municipio:30} | ID:{puesto_id:3} | {puesto_nombre[:40]}")
else:
    print("✅ Todos los puestos tienen zona asignada")

# 4. Verificar mesas sin votantes
print("\n4. MESAS SIN VOTANTES")
print("-" * 80)

cursor.execute('''
    SELECT COUNT(*) FROM mesas_votacion
    WHERE votantes_habilitados = 0 AND activa = 1
''')

mesas_sin_votantes = cursor.fetchone()[0]
if mesas_sin_votantes > 0:
    print(f"⚠️ {mesas_sin_votantes} mesas sin votantes asignados")
    
    cursor.execute('''
        SELECT m.nombre, pv.nombre, mv.numero
        FROM mesas_votacion mv
        JOIN puestos_votacion pv ON mv.puesto_id = pv.id
        JOIN municipios m ON mv.municipio_id = m.id
        WHERE mv.votantes_habilitados = 0 AND mv.activa = 1
        LIMIT 10
    ''')
    
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1][:40]} - Mesa {row[2]}")
else:
    print("✅ Todas las mesas tienen votantes asignados")

# 5. Resumen por municipio
print("\n5. RESUMEN POR MUNICIPIO")
print("-" * 80)

cursor.execute('''
    SELECT 
        m.nombre,
        COUNT(DISTINCT z.id) as zonas,
        COUNT(DISTINCT pv.id) as puestos,
        COUNT(DISTINCT mv.id) as mesas,
        SUM(mv.votantes_habilitados) as votantes
    FROM municipios m
    LEFT JOIN zonas z ON m.id = z.municipio_id AND z.activo = 1
    LEFT JOIN puestos_votacion pv ON m.id = pv.municipio_id AND pv.activo = 1
    LEFT JOIN mesas_votacion mv ON m.id = mv.municipio_id AND mv.activa = 1
    WHERE m.activo = 1
    GROUP BY m.id
    ORDER BY m.nombre
''')

print(f"{'Municipio':<30} | Zonas | Puestos | Mesas | Votantes")
print("-" * 80)
for row in cursor.fetchall():
    municipio, zonas, puestos, mesas, votantes = row
    print(f"{municipio:<30} | {zonas:5} | {puestos:7} | {mesas:5} | {votantes or 0:8}")

conn.close()

print("\n" + "=" * 80)
print("ANALISIS COMPLETADO")
print("=" * 80)
