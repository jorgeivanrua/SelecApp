import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

print("Estructura de la tabla zonas:")
cursor.execute('PRAGMA table_info(zonas)')
for col in cursor.fetchall():
    print(f'  {col[1]} ({col[2]})')

print("\nContenido de la tabla zonas:")
cursor.execute('SELECT * FROM zonas')
for row in cursor.fetchall():
    print(f'  {row}')

print("\nMunicipios sin puestos:")
cursor.execute('''
    SELECT m.nombre 
    FROM municipios m 
    LEFT JOIN puestos_votacion p ON m.id = p.municipio_id AND p.activo = 1
    WHERE m.activo = 1
    GROUP BY m.id
    HAVING COUNT(p.id) = 0
''')
for row in cursor.fetchall():
    print(f'  {row[0]}')

conn.close()
