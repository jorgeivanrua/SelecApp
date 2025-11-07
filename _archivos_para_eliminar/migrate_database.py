#!/usr/bin/env python3
"""
Script para migrar la base de datos existente al nuevo esquema
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

def migrate_database():
    """Migrar base de datos existente al nuevo esquema"""
    
    print("🔄 Migrando base de datos al nuevo esquema...")
    
    # Hacer backup de la base de datos actual
    if os.path.exists('caqueta_electoral.db'):
        backup_name = f'caqueta_electoral_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        os.system(f'copy caqueta_electoral.db {backup_name}')
        print(f"✅ Backup creado: {backup_name}")
    
    # Conectar a la base de datos
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Obtener datos existentes de usuarios
        cursor.execute("SELECT username, cedula, nombre_completo, email, password_hash, rol, activo FROM users")
        existing_users = cursor.fetchall()
        print(f"📋 Encontrados {len(existing_users)} usuarios existentes")
        
        # Eliminar tabla users existente
        cursor.execute("DROP TABLE IF EXISTS users")
        print("✅ Tabla users anterior eliminada")
        
    except sqlite3.OperationalError:
        existing_users = []
        print("📋 No se encontraron usuarios existentes")
    
    # Crear todas las tablas del nuevo esquema
    create_new_schema(cursor)
    
    # Restaurar usuarios existentes con nuevos campos
    if existing_users:
        print("🔄 Restaurando usuarios existentes...")
        for i, user in enumerate(existing_users):
            try:
                cursor.execute("""
                    INSERT INTO users 
                    (username, cedula, nombre_completo, email, password_hash, rol, activo, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, user)
            except sqlite3.IntegrityError as e:
                # Si hay conflicto, usar INSERT OR IGNORE o actualizar email
                username, cedula, nombre_completo, email, password_hash, rol, activo = user
                if email:
                    email = f"{email.split('@')[0]}_{i}@{email.split('@')[1]}" if '@' in email else f"{email}_{i}"
                cursor.execute("""
                    INSERT OR IGNORE INTO users 
                    (username, cedula, nombre_completo, email, password_hash, rol, activo, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (username, cedula, nombre_completo, email, password_hash, rol, activo))
        print(f"✅ {len(existing_users)} usuarios procesados")
    
    # Insertar datos básicos
    insertar_datos_basicos(cursor)
    
    # Confirmar cambios
    conn.commit()
    conn.close()
    
    print("✅ Migración completada exitosamente")

def create_new_schema(cursor):
    """Crear el nuevo esquema de base de datos"""
    
    print("🔄 Creando nuevo esquema...")
    
    # Crear tabla de municipios
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
    
    # Crear tabla de usuarios con campos extendidos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
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
    
    # Crear tabla de observaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observaciones (
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
        "CREATE INDEX IF NOT EXISTS idx_users_cedula ON users(cedula)",
        "CREATE INDEX IF NOT EXISTS idx_users_rol ON users(rol)",
        "CREATE INDEX IF NOT EXISTS idx_users_municipio ON users(municipio_id)",
        "CREATE INDEX IF NOT EXISTS idx_observaciones_testigo ON observaciones(testigo_id)",
        "CREATE INDEX IF NOT EXISTS idx_observaciones_fecha ON observaciones(fecha_hora)",
        "CREATE INDEX IF NOT EXISTS idx_incidencias_reportado ON incidencias(reportado_por)",
        "CREATE INDEX IF NOT EXISTS idx_incidencias_estado ON incidencias(estado)",
        "CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON notificaciones(usuario_id)"
    ]
    
    for indice in indices:
        cursor.execute(indice)
    
    print("✅ Nuevo esquema creado")

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
    
    # Actualizar usuarios demo existentes con nuevos campos
    usuarios_demo_updates = [
        ('12345678', 1, None, None, 'Partido Independiente', '3001234567'),
        ('87654321', 1, None, None, None, '3007654321'),
        ('11111111', 1, None, None, None, '3001111111'),
        ('22222222', 1, 1, None, None, '3002222222'),
        ('33333333', 1, 1, None, 'Partido Democrático', '3003333333'),
        ('44444444', 1, 1, 1, 'Partido Liberal', '3004444444')
    ]
    
    for cedula, municipio_id, puesto_id, mesa_id, partido, telefono in usuarios_demo_updates:
        cursor.execute("""
            UPDATE users 
            SET municipio_id = ?, puesto_id = ?, mesa_id = ?, partido_politico = ?, telefono = ?
            WHERE cedula = ?
        """, (municipio_id, puesto_id, mesa_id, partido, telefono, cedula))
    
    print("✅ Datos básicos insertados")

if __name__ == "__main__":
    try:
        migrate_database()
        print("🎉 Migración completada exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()