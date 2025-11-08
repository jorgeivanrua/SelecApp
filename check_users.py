#!/usr/bin/env python3
"""Script para verificar los usuarios existentes"""

import sqlite3

def check_users():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, nombre_completo, rol, activo, created_at
        FROM users
        ORDER BY id
    """)
    
    users = cursor.fetchall()
    
    print("=" * 80)
    print("USUARIOS EN EL SISTEMA")
    print("=" * 80)
    
    if users:
        print(f"{'ID':<5} {'Username':<20} {'Nombre':<25} {'Rol':<25} {'Activo':<8}")
        print("-" * 80)
        for user in users:
            user_id, username, nombre, rol, activo, created = user
            activo_str = "✅ Sí" if activo else "❌ No"
            print(f"{user_id:<5} {username:<20} {nombre:<25} {rol:<25} {activo_str:<8}")
    else:
        print("⚠️  No hay usuarios en el sistema")
    
    print("=" * 80)
    
    # Verificar si existe super_admin
    cursor.execute("SELECT * FROM users WHERE rol='super_admin'")
    super_admin = cursor.fetchone()
    
    if super_admin:
        print("\n✅ Usuario Super Admin encontrado:")
        print(f"   Username: {super_admin[1]}")
        print(f"   Nombre: {super_admin[3]}")
        print(f"   Email: {super_admin[4]}")
        print(f"   Activo: {'Sí' if super_admin[12] else 'No'}")
    else:
        print("\n❌ No hay usuario con rol 'super_admin'")
    
    conn.close()

if __name__ == "__main__":
    check_users()
