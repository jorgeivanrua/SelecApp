#!/usr/bin/env python3
"""
Verificar diferencias entre nombres de municipios en BD y DIVIPOLA
"""

import sqlite3
import csv

# Obtener municipios de la BD
conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()
cursor.execute('SELECT nombre FROM municipios WHERE activo = 1 ORDER BY nombre')
municipios_bd = set([row[0].upper() for row in cursor.fetchall()])
conn.close()

# Obtener municipios de DIVIPOLA
municipios_divipola = set()
with open('divipola.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['departamento'] == 'CAQUETA':
            municipios_divipola.add(row['municipio'])

print("=" * 80)
print("COMPARACIÓN DE NOMBRES DE MUNICIPIOS")
print("=" * 80)

print("\nMunicipios en BD:")
for m in sorted(municipios_bd):
    print(f"  - {m}")

print("\nMunicipios en DIVIPOLA:")
for m in sorted(municipios_divipola):
    print(f"  - {m}")

print("\nMunicipios en BD pero NO en DIVIPOLA:")
diferencia_bd = municipios_bd - municipios_divipola
if diferencia_bd:
    for m in sorted(diferencia_bd):
        print(f"  ⚠️  {m}")
else:
    print("  ✅ Ninguno")

print("\nMunicipios en DIVIPOLA pero NO en BD:")
diferencia_divipola = municipios_divipola - municipios_bd
if diferencia_divipola:
    for m in sorted(diferencia_divipola):
        print(f"  ⚠️  {m}")
else:
    print("  ✅ Ninguno")

# Buscar similitudes
print("\nPosibles coincidencias (nombres similares):")
for bd_name in sorted(diferencia_bd):
    for div_name in sorted(diferencia_divipola):
        # Comparar primeras palabras
        bd_first = bd_name.split()[0]
        div_first = div_name.split()[0]
        if bd_first == div_first or bd_name in div_name or div_name in bd_name:
            print(f"  {bd_name:35} <-> {div_name}")
