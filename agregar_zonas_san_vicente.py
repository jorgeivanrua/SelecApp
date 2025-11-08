import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

# Obtener ID de San Vicente
cursor.execute("SELECT id FROM municipios WHERE nombre = 'San Vicente Del Caguan'")
san_vicente_id = cursor.fetchone()[0]

print(f"San Vicente del Caguan ID: {san_vicente_id}")

# Agregar zonas 1 y 2
zonas = [
    ('1', 'Zona 1', 'Zona Urbana 1', 'urbana'),
    ('2', 'Zona 2', 'Zona Urbana 2', 'urbana')
]

for codigo, nombre, descripcion, tipo in zonas:
    cursor.execute('''
        SELECT id FROM zonas
        WHERE municipio_id = ? AND codigo_zz = ?
    ''', (san_vicente_id, codigo))
    
    if cursor.fetchone():
        print(f"Zona {codigo} ya existe")
    else:
        cursor.execute('''
            INSERT INTO zonas (codigo_zz, nombre, municipio_id, descripcion, activo, tipo_zona, created_at, updated_at)
            VALUES (?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (codigo, nombre, san_vicente_id, descripcion, tipo))
        print(f"✅ Agregada Zona {codigo} - {nombre}")

conn.commit()

# Ahora asignar los puestos a sus zonas
puestos_zona_1 = [341, 342, 343, 344]  # Zona 1
puestos_zona_2 = [345, 346, 347]  # Zona 2

# Obtener IDs de zonas
cursor.execute("SELECT id FROM zonas WHERE municipio_id = ? AND codigo_zz = '1'", (san_vicente_id,))
zona_1_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM zonas WHERE municipio_id = ? AND codigo_zz = '2'", (san_vicente_id,))
zona_2_id = cursor.fetchone()[0]

# Actualizar puestos
for puesto_id in puestos_zona_1:
    cursor.execute('UPDATE puestos_votacion SET zona_id = ? WHERE id = ?', (zona_1_id, puesto_id))
    print(f"✅ Puesto {puesto_id} -> Zona 1")

for puesto_id in puestos_zona_2:
    cursor.execute('UPDATE puestos_votacion SET zona_id = ? WHERE id = ?', (zona_2_id, puesto_id))
    print(f"✅ Puesto {puesto_id} -> Zona 2")

conn.commit()
conn.close()

print("\n✅ Corrección completada")
