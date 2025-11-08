import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

print("Estructura de mesas_votacion:")
cursor.execute('PRAGMA table_info(mesas_votacion)')
for col in cursor.fetchall():
    print(f'  {col[1]} ({col[2]})')

print("\nDatos de ejemplo:")
cursor.execute('SELECT * FROM mesas_votacion WHERE puesto_id = 2 LIMIT 3')
for row in cursor.fetchall():
    print(row)

conn.close()
