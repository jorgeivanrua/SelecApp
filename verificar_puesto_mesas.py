import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

# Verificar puesto 225
cursor.execute('SELECT id, nombre FROM puestos_votacion WHERE id = 225')
puesto = cursor.fetchone()
print(f"Puesto 225: {puesto}")

# Verificar mesas del puesto 225
cursor.execute('SELECT id, numero, puesto_id, votantes_habilitados FROM mesas_votacion WHERE puesto_id = 225')
print(f"\nMesas del puesto 225:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Numero: {row[1]}, Puesto_ID: {row[2]}, Votantes: {row[3]}")

# Verificar a qué puesto pertenecen las mesas 723 y 724
cursor.execute('SELECT id, numero, puesto_id, votantes_habilitados FROM mesas_votacion WHERE id IN (723, 724)')
print(f"\nMesas 723 y 724:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Numero: {row[1]}, Puesto_ID: {row[2]}, Votantes: {row[3]}")

conn.close()
