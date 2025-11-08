#!/usr/bin/env python3
"""
Script para crear usuarios demo siguiendo el flujo de registro real
"""

import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime
import random

def get_db_connection():
    conn = sqlite3.connect('caqueta_electoral.db')
    conn.row_factory = sqlite3.Row
    return conn

def crear_usuarios_demo():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener algunos municipios, puestos y mesas reales
    cursor.execute("""
        SELECT m.id, m.nombre, m.codigo
        FROM municipios m
        WHERE m.activo = 1
        ORDER BY m.nombre
        LIMIT 10
    """)
    municipios = cursor.fetchall()
    
    print("=" * 70)
    print("CREANDO USUARIOS DEMO")
    print("=" * 70)
    
    usuarios_demo = []
    
    # Crear usuarios para diferentes roles
    roles_config = [
        {
            'rol': 'testigo_mesa',
            'cantidad': 15,
            'prefijo': 'Testigo'
        },
        {
            'rol': 'coordinador_puesto',
            'cantidad': 8,
            'prefijo': 'Coordinador Puesto'
        },
        {
            'rol': 'coordinador_municipal',
            'cantidad': 5,
            'prefijo': 'Coordinador Municipal'
        }
    ]
    
    cedula_base = 1000000000
    
    for config in roles_config:
        print(f"\nCreando {config['cantidad']} usuarios con rol: {config['rol']}")
        
        for i in range(config['cantidad']):
            # Seleccionar municipio aleatorio
            municipio = random.choice(municipios)
            
            # Obtener un puesto del municipio
            cursor.execute("""
                SELECT id, nombre
                FROM puestos_votacion
                WHERE municipio_id = ? AND activo = 1
                LIMIT 1
            """, (municipio['id'],))
            puesto = cursor.fetchone()
            
            if not puesto:
                continue
            
            # Obtener una mesa del puesto (solo para testigos)
            mesa_id = None
            if config['rol'] == 'testigo_mesa':
                cursor.execute("""
                    SELECT id, numero
                    FROM mesas_votacion
                    WHERE puesto_id = ? AND activa = 1
                    LIMIT 1
                """, (puesto['id'],))
                mesa = cursor.fetchone()
                if mesa:
                    mesa_id = mesa['id']
            
            # Generar datos del usuario
            cedula = str(cedula_base + len(usuarios_demo) + 1)
            nombre = f"{config['prefijo']} {municipio['nombre']} {i+1}"
            email = f"demo_{config['rol']}_{cedula}@electoral.gov.co"
            telefono = f"310{random.randint(1000000, 9999999)}"
            username = f"user_{cedula}"
            password = "Demo2024!"  # Contraseña demo
            password_hash = generate_password_hash(password)
            
            # Verificar si ya existe
            cursor.execute("SELECT id FROM users WHERE cedula = ?", (cedula,))
            if cursor.fetchone():
                print(f"  ⚠️  Usuario con cédula {cedula} ya existe, saltando...")
                continue
            
            # Insertar usuario
            try:
                cursor.execute("""
                    INSERT INTO users (
                        username, cedula, nombre_completo, email, telefono,
                        password_hash, rol, municipio_id, puesto_id, mesa_id,
                        activo, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    username,
                    cedula,
                    nombre,
                    email,
                    telefono,
                    password_hash,
                    config['rol'],
                    municipio['id'],
                    puesto['id'],
                    mesa_id,
                    1,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                
                usuarios_demo.append({
                    'cedula': cedula,
                    'nombre': nombre,
                    'email': email,
                    'telefono': telefono,
                    'username': username,
                    'password': password,
                    'rol': config['rol'],
                    'municipio': municipio['nombre'],
                    'puesto': puesto['nombre'],
                    'mesa': mesa_id
                })
                
                print(f"  ✅ Creado: {nombre} (Cédula: {cedula})")
                
            except Exception as e:
                print(f"  ❌ Error creando usuario {nombre}: {e}")
    
    conn.commit()
    
    # Mostrar resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE USUARIOS DEMO CREADOS")
    print("=" * 70)
    print(f"\nTotal usuarios creados: {len(usuarios_demo)}")
    
    print("\n" + "-" * 70)
    print("CREDENCIALES DE ACCESO")
    print("-" * 70)
    print(f"{'Rol':<25} {'Cédula':<15} {'Password':<15} {'Municipio':<20}")
    print("-" * 70)
    
    for usuario in usuarios_demo[:10]:  # Mostrar solo los primeros 10
        print(f"{usuario['rol']:<25} {usuario['cedula']:<15} {usuario['password']:<15} {usuario['municipio']:<20}")
    
    if len(usuarios_demo) > 10:
        print(f"\n... y {len(usuarios_demo) - 10} usuarios más")
    
    print("\n" + "=" * 70)
    print("NOTA: Todos los usuarios demo tienen la contraseña: Demo2024!")
    print("=" * 70)
    
    # Guardar credenciales en archivo
    with open('USUARIOS_DEMO.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("USUARIOS DEMO - SISTEMA ELECTORAL CAQUETÁ\n")
        f.write("=" * 70 + "\n\n")
        f.write("Contraseña para todos: Demo2024!\n\n")
        
        for config in roles_config:
            f.write(f"\n{config['rol'].upper()}\n")
            f.write("-" * 70 + "\n")
            usuarios_rol = [u for u in usuarios_demo if u['rol'] == config['rol']]
            for usuario in usuarios_rol:
                f.write(f"Cédula: {usuario['cedula']}\n")
                f.write(f"Nombre: {usuario['nombre']}\n")
                f.write(f"Email: {usuario['email']}\n")
                f.write(f"Municipio: {usuario['municipio']}\n")
                f.write(f"Puesto: {usuario['puesto']}\n")
                if usuario['mesa']:
                    f.write(f"Mesa: {usuario['mesa']}\n")
                f.write("\n")
    
    print("\n✅ Credenciales guardadas en: USUARIOS_DEMO.txt")
    
    conn.close()

if __name__ == '__main__':
    crear_usuarios_demo()
