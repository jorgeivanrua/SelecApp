#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

print("=== VERIFICANDO DATOS EN BD ===\n")

print("📍 MUNICIPIOS:")
cursor.execute('SELECT id, codigo, nombre FROM municipios ORDER BY nombre LIMIT 10')
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Código: {row[1]}, Nombre: {row[2]}")

print(f"\n📍 ZONAS (Florencia - ID 7):")
cursor.execute('SELECT id, codigo_zz, nombre, descripcion FROM zonas WHERE municipio_id = 7 ORDER BY codigo_zz')
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Código: {row[1]}, Nombre: {row[2]}, Desc: {row[3]}")

print(f"\n📍 PUESTOS (Zona 01 Florencia - ID 20):")
cursor.execute('SELECT id, nombre, direccion FROM puestos_votacion WHERE zona_id = 20')
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Nombre: {row[1]}")

print(f"\n📍 MESAS (Puesto 1):")
cursor.execute('SELECT id, numero, votantes_habilitados FROM mesas_votacion WHERE puesto_id = 1 LIMIT 5')
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Número: {row[1]}, Votantes: {row[2]}")

conn.close()
