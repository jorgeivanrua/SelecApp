import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

# Verificar estructura de puestos_votacion
print("=== ESTRUCTURA TABLA PUESTOS ===")
cursor.execute("PRAGMA table_info(puestos_votacion)")
columns = cursor.fetchall()
for col in columns:
    print(f"{col[1]} ({col[2]})")

print("\n=== DATOS PUESTOS (primeros 5) ===")
cursor.execute("SELECT * FROM puestos_votacion LIMIT 5")
for row in cursor.fetchall():
    print(row)

# Verificar estructura de mesas_votacion
print("\n=== ESTRUCTURA TABLA MESAS ===")
cursor.execute("PRAGMA table_info(mesas_votacion)")
columns = cursor.fetchall()
for col in columns:
    print(f"{col[1]} ({col[2]})")

print("\n=== DATOS MESAS (primeros 5) ===")
cursor.execute("SELECT * FROM mesas_votacion LIMIT 5")
for row in cursor.fetchall():
    print(row)

# Verificar zonas
print("\n=== DATOS ZONAS (primeros 5) ===")
cursor.execute("SELECT * FROM zonas LIMIT 5")
for row in cursor.fetchall():
    print(row)

conn.close()
