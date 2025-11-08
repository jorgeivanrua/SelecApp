import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

# Verificar qué puestos tienen zona_id = 84 (Zona 90)
cursor.execute('''
    SELECT id, nombre, zona_id
    FROM puestos_votacion
    WHERE municipio_id = 7 AND activo = 1
    ORDER BY zona_id, nombre
''')

print("Puestos de Florencia por zona:")
print("-" * 70)

zona_actual = None
for row in cursor.fetchall():
    puesto_id, nombre, zona_id = row
    
    if zona_id != zona_actual:
        cursor.execute('SELECT codigo_zz, nombre FROM zonas WHERE id = ?', (zona_id,))
        zona_info = cursor.fetchone()
        if zona_info:
            print(f"\nZona {zona_info[0]} - {zona_info[1]}:")
        zona_actual = zona_id
    
    print(f"  {puesto_id:3} - {nombre[:60]}")

# Verificar específicamente la zona 90
print("\n" + "=" * 70)
cursor.execute('''
    SELECT COUNT(*) FROM puestos_votacion
    WHERE zona_id = 84 AND activo = 1
''')
count = cursor.fetchone()[0]
print(f"Puestos en Zona 90 (ID: 84): {count}")

# Buscar el puesto que debería estar en zona 90
cursor.execute('''
    SELECT id, nombre, zona_id
    FROM puestos_votacion
    WHERE nombre LIKE '%UNIVERSIDAD DE LA AMAZONIA%' AND municipio_id = 7
''')

print("\nPuestos con 'UNIVERSIDAD DE LA AMAZONIA':")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Nombre: {row[1]}, Zona_ID: {row[2]}")

conn.close()
