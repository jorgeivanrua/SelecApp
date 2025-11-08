import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

print("=" * 70)
print("VERIFICACION FINAL DEL SISTEMA ELECTORAL DEL CAQUETA")
print("=" * 70)

# Estadísticas generales
cursor.execute('SELECT COUNT(*) FROM municipios WHERE activo = 1')
municipios = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM puestos_votacion WHERE activo = 1')
puestos = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM mesas_votacion WHERE activa = 1')
mesas = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM users WHERE activo = 1')
usuarios = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM puestos_votacion WHERE zona_id IS NULL AND activo = 1')
puestos_sin_zona = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM mesas_votacion WHERE votantes_habilitados = 0 AND activa = 1')
mesas_sin_votantes = cursor.fetchone()[0]

print(f"\nEstadisticas Generales:")
print(f"  Municipios activos: {municipios}")
print(f"  Puestos de votacion: {puestos}")
print(f"  Mesas de votacion: {mesas}")
print(f"  Usuarios registrados: {usuarios}")
print(f"  Puestos sin zona: {puestos_sin_zona}")
print(f"  Mesas sin votantes: {mesas_sin_votantes}")

# Usuarios por rol
print(f"\nUsuarios por rol:")
cursor.execute('SELECT rol, COUNT(*) FROM users WHERE activo = 1 GROUP BY rol ORDER BY rol')
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Municipios sin puestos
print(f"\nMunicipios sin puestos:")
cursor.execute("""
    SELECT m.nombre 
    FROM municipios m 
    LEFT JOIN puestos_votacion p ON m.id = p.municipio_id AND p.activo = 1
    WHERE m.activo = 1
    GROUP BY m.id
    HAVING COUNT(p.id) = 0
""")
municipios_sin_puestos = cursor.fetchall()
if municipios_sin_puestos:
    for row in municipios_sin_puestos:
        print(f"  - {row[0]}")
else:
    print("  ✅ Todos los municipios tienen puestos asignados")

print("\n" + "=" * 70)
if puestos_sin_zona == 0 and mesas_sin_votantes == 0 and not municipios_sin_puestos:
    print("✅ SISTEMA CORRECTO Y LISTO PARA USAR")
else:
    print("⚠️  SE REQUIEREN CORRECCIONES")
print("=" * 70)

conn.close()
