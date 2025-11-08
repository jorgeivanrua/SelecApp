import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT id, cedula, nombre_completo, rol, municipio_id, puesto_id, mesa_id 
    FROM users 
    WHERE rol = "testigo_mesa" 
    LIMIT 5
''')

print('Usuarios testigo:')
for row in cursor.fetchall():
    print(f'  ID={row[0]}, Cedula={row[1]}, Nombre={row[2]}, Mun={row[4]}, Puesto={row[5]}, Mesa={row[6]}')

conn.close()
