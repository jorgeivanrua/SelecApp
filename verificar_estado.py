import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

print("=" * 60)
print("VERIFICACION DEL SISTEMA ELECTORAL DEL CAQUETA")
print("=" * 60)

# Estadísticas generales
cursor.execute('SELECT COUNT(*) FROM municipios WHERE activo = 1')
municipios = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM puestos_votacion WHERE activo = 1')
puestos = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM mesas_votacion WHERE activa = 1')
mesas = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM puestos_votacion WHERE zona_id IS NULL AND activo = 1')
puestos_sin_zona = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM mesas_votacion WHERE votantes_habilitados = 0 AND activa = 1')
mesas_sin_votantes = cursor.fetchone()[0]

print(f"\nEstadisticas Generales:")
print(f"  Municipios activos: {municipios}")
print(f"  Puestos de votacion: {puestos}")
print(f"  Mesas de votacion: {mesas}")
print(f"  Puestos sin zona: {puestos_sin_zona}")
print(f"  Mesas sin votantes: {mesas_sin_votantes}")

# Distribución por municipio
print(f"\nDistribucion de puestos por municipio:")
cursor.execute('''
    SELECT m.nombre, COUNT(p.id) as puestos 
    FROM municipios m 
    LEFT JOIN puestos_votacion p ON m.id = p.municipio_id AND p.activo = 1 
    WHERE m.activo = 1 
    GROUP BY m.id 
    ORDER BY m.nombre
''')

for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} puestos")

# Verificar zonas
print(f"\nDistribucion de zonas:")
cursor.execute('''
    SELECT z.codigo, z.nombre, COUNT(p.id) as puestos
    FROM zonas z
    LEFT JOIN puestos_votacion p ON z.id = p.zona_id AND p.activo = 1
    GROUP BY z.id
    ORDER BY z.codigo
''')

for row in cursor.fetchall():
    print(f"  Zona {row[0]} - {row[1]}: {row[2]} puestos")

print("\n" + "=" * 60)
if puestos_sin_zona == 0 and mesas_sin_votantes == 0:
    print("ESTADO: SISTEMA CORRECTO Y LISTO PARA USAR")
else:
    print("ESTADO: SE REQUIEREN CORRECCIONES")
print("=" * 60)

conn.close()
