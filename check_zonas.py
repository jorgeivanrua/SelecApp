#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

print("=== ZONAS ACTUALES ===\n")
cursor.execute('SELECT id, codigo_zz, nombre, tipo_zona, municipio_id FROM zonas ORDER BY municipio_id, codigo_zz LIMIT 30')
rows = cursor.fetchall()

print(f"{'ID':<5} {'Codigo':<10} {'Nombre':<30} {'Tipo':<15} {'Mun ID':<8}")
print("-" * 80)
for row in rows:
    print(f"{row[0]:<5} {row[1]:<10} {row[2]:<30} {str(row[3]):<15} {row[4]:<8}")

print(f"\nTotal zonas: {len(rows)}")

conn.close()
