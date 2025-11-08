import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

cursor.execute('SELECT id, numero, votantes_habilitados FROM mesas_votacion WHERE id IN (723, 724)')
print('Mesas 723 y 724:')
for row in cursor.fetchall():
    print(f'  ID: {row[0]}, Numero: {row[1]}, Votantes: {row[2]}')

conn.close()
