import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

print("=== ZONAS DE FLORENCIA (municipio_id=7) ===")
cursor.execute('''
    SELECT id, codigo_zz, nombre, descripcion, tipo_zona
    FROM zonas
    WHERE municipio_id = 7
    ORDER BY codigo_zz
''')

for row in cursor.fetchall():
    print(f"ID: {row[0]}")
    print(f"  Codigo: {row[1]}")
    print(f"  Nombre: {row[2]}")
    print(f"  Descripcion: {row[3]}")
    print(f"  Tipo: {row[4]}")
    print()

conn.close()
