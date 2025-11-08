import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

# Ejecutar exactamente la misma query que la API
zona_id = 84
cursor.execute('''
    SELECT id, nombre, direccion
    FROM puestos_votacion
    WHERE zona_id = ? AND activo = 1
    ORDER BY nombre
''', (zona_id,))

print(f"Query: SELECT id, nombre, direccion FROM puestos_votacion WHERE zona_id = {zona_id} AND activo = 1")
print("\nResultados:")

rows = cursor.fetchall()
print(f"Total filas: {len(rows)}")

for row in rows:
    print(f"  ID: {row[0]}, Nombre: {row[1]}, Dirección: {row[2]}")

conn.close()
