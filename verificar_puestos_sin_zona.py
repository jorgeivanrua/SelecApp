import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT pv.id, m.nombre as municipio, pv.nombre
    FROM puestos_votacion pv
    JOIN municipios m ON pv.municipio_id = m.id
    WHERE pv.zona_id IS NULL AND pv.activo = 1
''')

print("Puestos sin zona:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, {row[1]} - {row[2]}")

conn.close()
