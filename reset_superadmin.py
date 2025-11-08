#!/usr/bin/env python3
"""Script para resetear la contraseña del super admin"""

import sqlite3
from werkzeug.security import generate_password_hash

def reset_superadmin():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Nueva contraseña
    new_password = "admin123"
    password_hash = generate_password_hash(new_password)
    
    print("=" * 80)
    print("RESETEAR CONTRASEÑA DE SUPER ADMIN")
    print("=" * 80)
    
    # Verificar si existe el usuario
    cursor.execute("SELECT id, username, nombre_completo FROM users WHERE rol='super_admin'")
    user = cursor.fetchone()
    
    if user:
        user_id, username, nombre = user
        print(f"\n✅ Usuario encontrado:")
        print(f"   ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Nombre: {nombre}")
        
        # Actualizar contraseña
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        """, (password_hash, user_id))
        
        conn.commit()
        
        print(f"\n✅ Contraseña actualizada exitosamente")
        print(f"\n📋 CREDENCIALES:")
        print(f"   Username: {username}")
        print(f"   Password: {new_password}")
        print(f"\n🌐 URL de acceso:")
        print(f"   http://127.0.0.1:5000/login")
        
    else:
        print("\n❌ No se encontró usuario con rol 'super_admin'")
        print("   Creando nuevo usuario...")
        
        # Crear nuevo super admin
        cursor.execute("""
            INSERT INTO users (
                username, cedula, nombre_completo, email, telefono,
                password_hash, rol, activo, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            'superadmin',
            '1000000000',
            'Super Administrador',
            'superadmin@caqueta.gov.co',
            '3001234567',
            password_hash,
            'super_admin',
            1
        ))
        
        conn.commit()
        
        print(f"\n✅ Usuario super admin creado exitosamente")
        print(f"\n📋 CREDENCIALES:")
        print(f"   Username: superadmin")
        print(f"   Password: {new_password}")
        print(f"\n🌐 URL de acceso:")
        print(f"   http://127.0.0.1:5000/login")
    
    print("=" * 80)
    conn.close()

if __name__ == "__main__":
    reset_superadmin()
