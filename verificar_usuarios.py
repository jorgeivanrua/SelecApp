import sqlite3

conn = sqlite3.connect('caqueta_electoral.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM users')
total = cursor.fetchone()[0]

cursor.execute('SELECT rol, COUNT(*) FROM users GROUP BY rol')
print(f'Total usuarios en la BD: {total}')
print('\nUsuarios por rol:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

print('\nÚltimos 5 usuarios creados:')
cursor.execute("""
    SELECT cedula, nombre_completo, rol, email
    FROM users
    ORDER BY created_at DESC
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f'  {row[0]} - {row[1]} ({row[2]})')

conn.close()
