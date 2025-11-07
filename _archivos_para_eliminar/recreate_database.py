#!/usr/bin/env python3
"""
Script para recrear completamente la base de datos
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

def recreate_database():
    """Recrear completamente la base de datos"""
    
    print("🔄 Recreando base de datos desde cero...")
    
    # Eliminar base de datos existente
    if os.path.exists('caqueta_electoral.db'):
        backup_name = f'caqueta_electoral_old_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        os.rename('caqueta_electoral.db', backup_name)
        print(f"✅ Base de datos anterior respaldada como: {backup_name}")
    
    # Crear nueva base de datos
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Crear todas las tablas
    create_all_tables(cursor)
    
    # Insertar datos básicos
    insert_basic_data(cursor)
    
    # Confirmar cambios
    conn.commit()
    conn.close()
    
    print("✅ Base de datos recreada exitosamente")

def create_all_tables(cursor):
    """Crear todas las tablas del esquema"""
    
    print("🔄 Creando tablas...")
    
    # Tabla de municipios
    cursor.execute("""
        CREATE TABLE municipios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            departamento TEXT DEFAULT 'Caquetá',
            poblacion INTEGER DEFAULT 0,
            activo INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla de puestos de votación
    cursor.execute("""
        CREATE TABLE puestos_votacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT NOT NULL,
            municipio_id INTEGER NOT NULL,
            coordenadas_lat REAL,
            coordenadas_lng REAL,
            capacidad_votantes INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'configurado',
            activo INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (municipio_id) REFERENCES municipios(id)
        )
    """)
    
    # Tabla de mesas de votación
    cursor.execute("""
        CREATE TABLE mesas_votacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            puesto_id INTEGER NOT NULL,
            municipio_id INTEGER NOT NULL,
            votantes_habilitados INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'configurada',
            ubicacion_especifica TEXT,
            activa INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (puesto_id) REFERENCES puestos_votacion(id),
            FOREIGN KEY (municipio_id) REFERENCES municipios(id)
        )
    """)
    
    # Tabla de usuarios
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            nombre_completo TEXT NOT NULL,
            email TEXT UNIQUE,
            telefono TEXT,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL,
            municipio_id INTEGER,
            puesto_id INTEGER,
            mesa_id INTEGER,
            partido_politico TEXT,
            activo INTEGER DEFAULT 1,
            ultimo_acceso TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (municipio_id) REFERENCES municipios(id),
            FOREIGN KEY (puesto_id) REFERENCES puestos_votacion(id),
            FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id)
        )
    """)
    
    # Tabla de observaciones
    cursor.execute("""
        CREATE TABLE observaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            testigo_id INTEGER NOT NULL,
            mesa_id INTEGER,
            puesto_id INTEGER,
            tipo_observacion TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            evidencia_fotos TEXT,
            ubicacion_gps_lat REAL,
            ubicacion_gps_lng REAL,
            fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado TEXT DEFAULT 'registrada',
            severidad TEXT DEFAULT 'normal',
            calificacion_proceso TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (testigo_id) REFERENCES users(id),
            FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id),
            FOREIGN KEY (puesto_id) REFERENCES puestos_votacion(id)
        )
    """)
    
    # Tabla de incidencias
    cursor.execute("""
        CREATE TABLE incidencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reportado_por INTEGER NOT NULL,
            mesa_id INTEGER,
            puesto_id INTEGER,
            tipo_incidencia TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            severidad TEXT NOT NULL,
            estado TEXT DEFAULT 'abierta',
            evidencia_fotos TEXT,
            ubicacion_gps_lat REAL,
            ubicacion_gps_lng REAL,
            fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resuelto_por INTEGER,
            fecha_resolucion TIMESTAMP,
            notas_resolucion TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reportado_por) REFERENCES users(id),
            FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id),
            FOREIGN KEY (puesto_id) REFERENCES puestos_votacion(id),
            FOREIGN KEY (resuelto_por) REFERENCES users(id)
        )
    """)
    
    # Tabla de asignaciones de personal
    cursor.execute("""
        CREATE TABLE asignaciones_personal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            puesto_id INTEGER,
            mesa_id INTEGER,
            rol_asignado TEXT NOT NULL,
            fecha_asignacion DATE NOT NULL,
            turno TEXT DEFAULT 'completo',
            estado TEXT DEFAULT 'asignado',
            asignado_por INTEGER NOT NULL,
            notas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES users(id),
            FOREIGN KEY (puesto_id) REFERENCES puestos_votacion(id),
            FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id),
            FOREIGN KEY (asignado_por) REFERENCES users(id)
        )
    """)
    
    # Tabla de inventario de materiales
    cursor.execute("""
        CREATE TABLE inventario_materiales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            puesto_id INTEGER NOT NULL,
            tipo_material TEXT NOT NULL,
            descripcion TEXT,
            cantidad_requerida INTEGER NOT NULL,
            cantidad_disponible INTEGER DEFAULT 0,
            cantidad_entregada INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'pendiente',
            prioridad TEXT DEFAULT 'normal',
            solicitado_por INTEGER NOT NULL,
            fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_entrega TIMESTAMP,
            entregado_por INTEGER,
            notas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (puesto_id) REFERENCES puestos_votacion(id),
            FOREIGN KEY (solicitado_por) REFERENCES users(id),
            FOREIGN KEY (entregado_por) REFERENCES users(id)
        )
    """)
    
    # Tabla de notificaciones
    cursor.execute("""
        CREATE TABLE notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            datos_adicionales TEXT,
            leida INTEGER DEFAULT 0,
            urgente INTEGER DEFAULT 0,
            accion_requerida INTEGER DEFAULT 0,
            fecha_expiracion TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leida_at TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES users(id)
        )
    """)
    
    # Crear índices
    indices = [
        "CREATE INDEX idx_users_cedula ON users(cedula)",
        "CREATE INDEX idx_users_rol ON users(rol)",
        "CREATE INDEX idx_users_municipio ON users(municipio_id)",
        "CREATE INDEX idx_observaciones_testigo ON observaciones(testigo_id)",
        "CREATE INDEX idx_observaciones_fecha ON observaciones(fecha_hora)",
        "CREATE INDEX idx_incidencias_reportado ON incidencias(reportado_por)",
        "CREATE INDEX idx_incidencias_estado ON incidencias(estado)",
        "CREATE INDEX idx_notificaciones_usuario ON notificaciones(usuario_id)"
    ]
    
    for indice in indices:
        cursor.execute(indice)
    
    print("✅ Todas las tablas creadas")

def insert_basic_data(cursor):
    """Insertar datos básicos"""
    
    print("🔄 Insertando datos básicos...")
    
    # Municipios del Caquetá
    municipios = [
        ('18001', 'Florencia', 185000),
        ('18029', 'San Vicente del Caguán', 61000),
        ('18592', 'Puerto Rico', 38000),
        ('18479', 'El Paujil', 21000),
        ('18410', 'La Montañita', 19000),
        ('18205', 'Curillo', 13000)
    ]
    
    for codigo, nombre, poblacion in municipios:
        cursor.execute("""
            INSERT INTO municipios (codigo, nombre, poblacion)
            VALUES (?, ?, ?)
        """, (codigo, nombre, poblacion))
    
    # Puestos de votación para Florencia
    puestos = [
        ('Escuela Central', 'Carrera 11 # 15-20, Centro', 1, 1.6143, -75.6062, 2800),
        ('Colegio San José', 'Calle 18 # 8-45, Barrio San José', 1, 1.6156, -75.6089, 2400),
        ('Universidad de la Amazonia', 'Calle 17 Diagonal 17 con Carrera 3F', 1, 1.6234, -75.6067, 3200)
    ]
    
    for nombre, direccion, municipio_id, lat, lng, capacidad in puestos:
        cursor.execute("""
            INSERT INTO puestos_votacion 
            (nombre, direccion, municipio_id, coordenadas_lat, coordenadas_lng, capacidad_votantes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, direccion, municipio_id, lat, lng, capacidad))
    
    # Mesas de votación
    for puesto_id in range(1, 4):  # 3 puestos
        for i in range(1, 6):  # 5 mesas por puesto
            numero_mesa = f"{puesto_id:03d}-{chr(64+i)}"
            cursor.execute("""
                INSERT INTO mesas_votacion 
                (numero, puesto_id, municipio_id, votantes_habilitados)
                VALUES (?, ?, 1, 350)
            """, (numero_mesa, puesto_id))
    
    # Usuarios demo
    usuarios = [
        {
            'username': 'superadmin',
            'cedula': '12345678',
            'nombre_completo': 'Super Administrador',
            'email': 'superadmin@caqueta.gov.co',
            'telefono': '3001234567',
            'password': 'demo123',
            'rol': 'super_admin',
            'municipio_id': 1
        },
        {
            'username': 'coord_dept',
            'cedula': '87654321',
            'nombre_completo': 'Carlos Mendoza - Coordinador Departamental',
            'email': 'coord.dept@caqueta.gov.co',
            'telefono': '3007654321',
            'password': 'demo123',
            'rol': 'coordinador_departamental',
            'municipio_id': 1
        },
        {
            'username': 'coord_mun',
            'cedula': '11111111',
            'nombre_completo': 'Ana Patricia Ruiz - Coordinadora Municipal',
            'email': 'coord.mun@florencia.gov.co',
            'telefono': '3001111111',
            'password': 'demo123',
            'rol': 'coordinador_municipal',
            'municipio_id': 1
        },
        {
            'username': 'coord_puesto',
            'cedula': '22222222',
            'nombre_completo': 'Miguel Torres - Coordinador de Puesto',
            'email': 'coord.puesto@florencia.gov.co',
            'telefono': '3002222222',
            'password': 'demo123',
            'rol': 'coordinador_puesto',
            'municipio_id': 1,
            'puesto_id': 1
        },
        {
            'username': 'testigo_electoral',
            'cedula': '33333333',
            'nombre_completo': 'Laura González - Testigo Electoral',
            'email': 'testigo.electoral@partido.com',
            'telefono': '3003333333',
            'password': 'demo123',
            'rol': 'testigo_electoral',
            'municipio_id': 1,
            'puesto_id': 1,
            'partido_politico': 'Partido Democrático'
        },
        {
            'username': 'testigo_mesa',
            'cedula': '44444444',
            'nombre_completo': 'Juan Pérez - Testigo de Mesa',
            'email': 'testigo.mesa@partido.com',
            'telefono': '3004444444',
            'password': 'demo123',
            'rol': 'testigo_mesa',
            'municipio_id': 1,
            'puesto_id': 1,
            'mesa_id': 1,
            'partido_politico': 'Partido Liberal'
        }
    ]
    
    for user in usuarios:
        password_hash = generate_password_hash(user['password'])
        cursor.execute("""
            INSERT INTO users 
            (username, cedula, nombre_completo, email, telefono, password_hash, rol, 
             municipio_id, puesto_id, mesa_id, partido_politico, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            user['username'], user['cedula'], user['nombre_completo'], 
            user['email'], user.get('telefono'), password_hash, user['rol'],
            user.get('municipio_id'), user.get('puesto_id'), user.get('mesa_id'),
            user.get('partido_politico')
        ))
    
    print("✅ Datos básicos insertados")

if __name__ == "__main__":
    try:
        recreate_database()
        print("🎉 Base de datos recreada exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()