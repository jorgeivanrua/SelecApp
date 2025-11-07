#!/usr/bin/env python3
"""
Verificar hash de contraseñas
"""

import sqlite3
import hashlib

def verify_hash():
    conn = sqlite3.connect('electoral_system_prod.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, password_hash FROM users WHERE username = 'admin'")
    user = cursor.fetchone()
    
    if user:
        username, stored_hash = user
        test_password = "demo123"
        calculated_hash = hashlib.sha256(test_password.encode()).hexdigest()
        
        print(f"Usuario: {username}")
        print(f"Hash almacenado: {stored_hash}")
        print(f"Hash calculado:  {calculated_hash}")
        print(f"¿Coinciden? {stored_hash == calculated_hash}")
    else:
        print("Usuario no encontrado")
    
    conn.close()

if __name__ == "__main__":
    verify_hash()
