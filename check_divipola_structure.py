#!/usr/bin/env python3
"""Script para verificar la estructura DIVIPOLA en la BD"""

import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

print("="*80)
print("ESTRUCTURA ACTUAL DE CÓDIGOS DIVIPOLA")
print("="*80)

print("\n📍 MUNICIPIOS:")
cursor.execute("SELECT id, codigo, nombre FROM municipios ORDER BY codigo")
for row in cursor.fetchall():
    print(f"  ID: {row[0]:<3} Código: {row[1]:<10} Nombre: {row[2]}")

print("\n📍 PUESTOS DE VOTACIÓN:")
cursor.execute("""
    SELECT p.id, p.codigo, p.nombre, m.nombre as municipio
    FROM puestos_votacion p
    LEFT JOIN municipios m ON p.municipio_id = m.id
    ORDER BY p.id
""")
for row in cursor.fetchall():
    print(f"  ID: {row[0]:<3} Código: {row[1] or 'NULL':<10} Puesto: {row[2]:<40} Municipio: {row[3]}")

print("\n📍 MESAS DE VOTACIÓN:")
cursor.execute("""
    SELECT m.id, m.numero, p.nombre as puesto, mu.nombre as municipio
    FROM mesas_votacion m
    LEFT JOIN puestos_votacion p ON m.puesto_id = p.id
    LEFT JOIN municipios mu ON m.municipio_id = mu.id
    ORDER BY m.id
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"  ID: {row[0]:<3} Número: {row[1]:<10} Puesto: {row[2]:<40} Municipio: {row[3]}")

print("\n" + "="*80)
print("ANÁLISIS DE CÓDIGOS")
print("="*80)

# Verificar si los códigos siguen el formato DIVIPOLA
print("\n🔍 Formato de códigos de municipios:")
cursor.execute("SELECT codigo FROM municipios")
for row in cursor.fetchall():
    codigo = row[0]
    if len(codigo) == 5:
        dd = codigo[:2]
        mm = codigo[2:5]
        print(f"  {codigo} -> dd:{dd} mm:{mm}")
    else:
        print(f"  {codigo} -> ⚠️ Formato no estándar")

print("\n🔍 Códigos de puestos:")
cursor.execute("SELECT codigo FROM puestos_votacion WHERE codigo IS NOT NULL")
puestos_codes = cursor.fetchall()
if puestos_codes:
    for row in puestos_codes:
        print(f"  {row[0]}")
else:
    print("  ⚠️ No hay códigos en puestos_votacion")

conn.close()
