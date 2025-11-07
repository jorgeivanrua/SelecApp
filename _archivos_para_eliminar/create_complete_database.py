#!/usr/bin/env python3
"""
Script para crear esquema completo de base de datos del Sistema Electoral ERP
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

def create_complete_database():
    """Crear esquema completo de base de datos"""
    
    print("🔄 Creando esquema completo de base de datos...")
    
    # Conectar a la base de datos
    db_path = 'caqueta_electoral.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Crear tabla de municipios (base)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS municipios (
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
    
    # Crear tabla de puestos de votación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS puestos_votacion (
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
    
    # Crear tabla de mesas de votación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mesas_votacion (
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
    
    # Actualizar tabla de usuarios con campos adicionales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_new (
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
    
    # Migrar datos existentes si la tabla users existe
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            cursor.execute("""
                INSERT INTO users_new (username, cedula, nombre_completo, email, password_hash, rol, activo, created_at)
                SELECT username, cedula, nombre_completo, email, password_hash, rol, activo, created_at
                FROM users
            """)
            cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
    except:
        cursor.execute("ALTER TABLE users_new RENAME TO users")
    
    # Crear tabla de observaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            testigo_id INTEGER NOT NULL,
            mesa_id INTEGER,
            puesto_id INTEGER,
            tipo_observacion TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            evidencia_fotos TEXT, -- JSON array de rutas
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
    
    # Crear tabla de incidencias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reportado_por INTEGER NOT NULL,
            mesa_id INTEGER,
            puesto_id INTEGER,
            tipo_incidencia TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            severidad TEXT NOT NULL,
            estado TEXT DEFAULT 'abierta',
            evidencia_fotos TEXT, -- JSON array de rutas
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
    
    # Crear tabla de asignaciones de personal
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asignaciones_personal (
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
    
    # Crear tabla de inventario de materiales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_materiales (
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
    
    # Crear tabla de notificaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            datos_adicionales TEXT, -- JSON con datos extra
            leida INTEGER DEFAULT 0,
            urgente INTEGER DEFAULT 0,
            accion_requerida INTEGER DEFAULT 0,
            fecha_expiracion TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leida_at TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES users(id)
        )
    """)
    
    # Crear tabla de comunicaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comunicaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente_id INTEGER NOT NULL,
            destinatario_id INTEGER,
            tipo_destinatario TEXT, -- 'usuario', 'rol', 'puesto', 'municipio'
            destinatario_referencia TEXT, -- ID o nombre del destinatario
            asunto TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            tipo_comunicacion TEXT DEFAULT 'mensaje',
            prioridad TEXT DEFAULT 'normal',
            estado TEXT DEFAULT 'enviado',
            fecha_lectura TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (remitente_id) REFERENCES users(id),
            FOREIGN KEY (destinatario_id) REFERENCES users(id)
        )
    """)
    
    # Crear tabla de reportes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generado_por INTEGER NOT NULL,
            tipo_reporte TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            parametros TEXT, -- JSON con parámetros del reporte
            archivo_path TEXT,
            formato TEXT DEFAULT 'pdf',
            estado TEXT DEFAULT 'generando',
            fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_completado TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (generado_por) REFERENCES users(id)
        )
    """)
    
    # Crear tabla de logs de auditoría
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            accion TEXT NOT NULL,
            tabla_afectada TEXT,
            registro_id INTEGER,
            datos_anteriores TEXT, -- JSON con datos antes del cambio
            datos_nuevos TEXT, -- JSON con datos después del cambio
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES users(id)
        )
    """)
    
    # Crear índices para optimización
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_users_cedula ON users(cedula)",
        "CREATE INDEX IF NOT EXISTS idx_users_rol ON users(rol)",
        "CREATE INDEX IF NOT EXISTS idx_users_municipio ON users(municipio_id)",
        "CREATE INDEX IF NOT EXISTS idx_observaciones_testigo ON observaciones(testigo_id)",
        "CREATE INDEX IF NOT EXISTS idx_observaciones_mesa ON observaciones(mesa_id)",
        "CREATE INDEX IF NOT EXISTS idx_observaciones_fecha ON observaciones(fecha_hora)",
        "CREATE INDEX IF NOT EXISTS idx_incidencias_reportado ON incidencias(reportado_por)",
        "CREATE INDEX IF NOT EXISTS idx_incidencias_estado ON incidencias(estado)",
        "CREATE INDEX IF NOT EXISTS idx_asignaciones_usuario ON asignaciones_personal(usuario_id)",
        "CREATE INDEX IF NOT EXISTS idx_asignaciones_puesto ON asignaciones_personal(puesto_id)",
        "CREATE INDEX IF NOT EXISTS idx_inventario_puesto ON inventario_materiales(puesto_id)",
        "CREATE INDEX IF NOT EXISTS idx_inventario_estado ON inventario_materiales(estado)",
        "CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON notificaciones(usuario_id)",
        "CREATE INDEX IF NOT EXISTS idx_notificaciones_leida ON notificaciones(leida)",
        "CREATE INDEX IF NOT EXISTS idx_comunicaciones_destinatario ON comunicaciones(destinatario_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_usuario ON audit_logs(usuario_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)"
    ]
    
    for indice in indices:
        cursor.execute(indice)
    
    print("✅ Esquema de base de datos creado exitosamente")
    
    # Insertar datos básicos
    insertar_datos_basicos(cursor)
    
    # Confirmar cambios
    conn.commit()
    conn.close()
    
    print("✅ Base de datos completa inicializada")

def insertar_datos_basicos(cursor):
    """Insertar datos básicos necesarios"""
    
    print("🔄 Insertando datos básicos...")
    
    # Insertar municipios del Caquetá
    municipios = [
        ('18001', 'Florencia', 185000),
        ('18029', 'San Vicente del Caguán', 61000),
        ('18592', 'Puerto Rico', 38000),
        ('18479', 'El Paujil', 21000),
        ('18410', 'La Montañita', 19000),
        ('18205', 'Curillo', 13000),
        ('18247', 'El Doncello', 23000),
        ('18256', 'Belén de los Andaquíes', 12000),
        ('18150', 'Cartagena del Chairá', 35000),
        ('18460', 'Morelia', 8000),
        ('18753', 'San José del Fragua', 15000),
        ('18610', 'Albania', 7000),
        ('18785', 'Solano', 25000),
        ('18550', 'Milán', 9000),
        ('18756', 'Solita', 6000),
        ('18685', 'Valparaíso', 4000)
    ]
    
    for codigo, nombre, poblacion in municipios:
        cursor.execute("""
            INSERT OR IGNORE INTO municipios (codigo, nombre, poblacion)
            VALUES (?, ?, ?)
        """, (codigo, nombre, poblacion))
    
    # Insertar puestos de votación de ejemplo para Florencia
    puestos_florencia = [
        ('Escuela Central', 'Carrera 11 # 15-20, Centro', 1, 1.6143, -75.6062, 2800),
        ('Colegio San José', 'Calle 18 # 8-45, Barrio San José', 1, 1.6156, -75.6089, 2400),
        ('Universidad de la Amazonia', 'Calle 17 Diagonal 17 con Carrera 3F', 1, 1.6234, -75.6067, 3200),
        ('Centro Comercial Florencia Plaza', 'Carrera 15 # 8-120', 1, 1.6178, -75.6045, 1800),
        ('Polideportivo Municipal', 'Carrera 7 # 25-30', 1, 1.6089, -75.6123, 2200)
    ]
    
    for nombre, direccion, municipio_id, lat, lng, capacidad in puestos_florencia:
        cursor.execute("""
            INSERT OR IGNORE INTO puestos_votacion 
            (nombre, direccion, municipio_id, coordenadas_lat, coordenadas_lng, capacidad_votantes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, direccion, municipio_id, lat, lng, capacidad))
    
    # Insertar mesas de votación de ejemplo
    cursor.execute("SELECT id FROM puestos_votacion LIMIT 3")
    puestos = cursor.fetchall()
    
    mesa_counter = 1
    for puesto_id, in puestos:
        for i in range(1, 9):  # 8 mesas por puesto
            numero_mesa = f"{mesa_counter:03d}-{chr(64+i)}"
            cursor.execute("""
                INSERT OR IGNORE INTO mesas_votacion 
                (numero, puesto_id, municipio_id, votantes_habilitados)
                VALUES (?, ?, 1, ?)
            """, (numero_mesa, puesto_id, 350))
        mesa_counter += 1
    
    # Recrear usuarios demo con nuevos campos
    usuarios_demo = [
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
    
    for user in usuarios_demo:
        password_hash = generate_password_hash(user['password'])
        cursor.execute("""
            INSERT OR REPLACE INTO users 
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
        create_complete_database()
        print("🎉 Base de datos completa creada exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()