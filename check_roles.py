#!/usr/bin/env python3
"""
Script para verificar roles en la base de datos
"""

import sqlite3

def check_roles():
    """Verificar roles en la base de datos"""
    
    print("🔍 Verificando roles en la base de datos...")
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Verificar usuarios demo
    cursor.execute("""
        SELECT cedula, nombre_completo, rol, username 
        FROM users 
        WHERE cedula IN ('12345678', '87654321', '11111111', '22222222', '33333333', '44444444')
        ORDER BY cedula
    """)
    
    users = cursor.fetchall()
    
    print(f"\n👥 Usuarios demo encontrados:")
    for user in users:
        print(f"  • Cédula: {user[0]} | Nombre: {user[1]} | Rol: {user[2]} | Username: {user[3]}")
    
    # Verificar todos los roles únicos
    cursor.execute("SELECT DISTINCT rol FROM users ORDER BY rol")
    roles = cursor.fetchall()
    
    print(f"\n🏷️  Roles únicos en la BD:")
    for role in roles:
        print(f"  • {role[0]}")
    
    conn.close()
    
    return [user[2] for user in users]  # Retornar lista de roles

if __name__ == "__main__":
    check_roles()