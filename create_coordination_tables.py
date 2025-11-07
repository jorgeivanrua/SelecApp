#!/usr/bin/env python3
"""
Script para crear tablas de coordinación municipal del Sistema Electoral ERP
Herramientas para coordinadores municipales: asignación de testigos, gestión de mesas, supervisión
"""

import sqlite3
from datetime import datetime, date

def create_coordination_tables():
    """Crear tablas de coordinación municipal"""
    
    print("🔄 Creando tablas de coordinación municipal...")
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Tabla de coordinadores municipales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coordinadores_municipales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            municipio_id INTEGER NOT NULL,
            nombre_completo TEXT NOT NULL,
            cedula TEXT NOT NULL UNIQUE,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            fecha_asignacion DATE DEFAULT CURRENT_DATE,
            estado TEXT DEFAULT 'activo', -- activo, inactivo, suspendido
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (municipio_id) REFERENCES municipios(id)
        )
    """)
    
    # Tabla de testigos electorales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS testigos_electorales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            coordinador_id INTEGER NOT NULL,
            municipio_id INTEGER NOT NULL,
            nombre_completo TEXT NOT NULL,
            cedula TEXT NOT NULL UNIQUE,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            fecha_nacimiento DATE,
            profesion TEXT,
            experiencia_electoral TEXT,
            partido_id INTEGER,
            tipo_testigo TEXT DEFAULT 'principal', -- principal, suplente
            estado TEXT DEFAULT 'disponible', -- disponible, asignado, inactivo
            fecha_registro DATE DEFAULT CURRENT_DATE,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (coordinador_id) REFERENCES coordinadores_municipales(id),
            FOREIGN KEY (municipio_id) REFERENCES municipios(id),
            FOREIGN KEY (partido_id) REFERENCES partidos_politicos(id)
        )
    """)
    
    # Actualizar tabla de mesas de votación si no tiene las columnas necesarias
    cursor.execute("PRAGMA table_info(mesas_votacion)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'puesto_votacion_id' not in columns:
        cursor.execute("ALTER TABLE mesas_votacion ADD COLUMN puesto_votacion_id INTEGER")
    if 'coordenadas_lat' not in columns:
        cursor.execute("ALTER TABLE mesas_votacion ADD COLUMN coordenadas_lat REAL")
    if 'coordenadas_lng' not in columns:
        cursor.execute("ALTER TABLE mesas_votacion ADD COLUMN coordenadas_lng REAL")
    if 'total_votantes' not in columns:
        cursor.execute("ALTER TABLE mesas_votacion ADD COLUMN total_votantes INTEGER DEFAULT 0")
    if 'estado' not in columns:
        cursor.execute("ALTER TABLE mesas_votacion ADD COLUMN estado TEXT DEFAULT 'activa'")
    
    # Actualizar tabla de puestos de votación si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS puestos_votacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            codigo TEXT UNIQUE,
            municipio_id INTEGER NOT NULL,
            direccion TEXT NOT NULL,
            barrio_vereda TEXT,
            coordenadas_lat REAL,
            coordenadas_lng REAL,
            responsable_nombre TEXT,
            responsable_telefono TEXT,
            capacidad_mesas INTEGER DEFAULT 1,
            estado TEXT DEFAULT 'activo', -- activo, inactivo
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (municipio_id) REFERENCES municipios(id)
        )
    """)
    
    # Actualizar tabla de asignaciones de testigos
    cursor.execute("DROP TABLE IF EXISTS asignaciones_testigos")
    cursor.execute("""
        CREATE TABLE asignaciones_testigos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            testigo_id INTEGER NOT NULL,
            mesa_id INTEGER NOT NULL,
            coordinador_id INTEGER NOT NULL,
            proceso_electoral_id INTEGER NOT NULL,
            tipo_asignacion TEXT DEFAULT 'principal', -- principal, suplente
            fecha_asignacion DATE DEFAULT CURRENT_DATE,
            hora_inicio TIME,
            hora_fin TIME,
            estado TEXT DEFAULT 'asignado', -- asignado, confirmado, presente, ausente, reemplazado
            observaciones TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (testigo_id) REFERENCES testigos_electorales(id),
            FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id),
            FOREIGN KEY (coordinador_id) REFERENCES coordinadores_municipales(id),
            FOREIGN KEY (proceso_electoral_id) REFERENCES procesos_electorales(id),
            FOREIGN KEY (created_by) REFERENCES users(id),
            UNIQUE(testigo_id, mesa_id, proceso_electoral_id)
        )
    """)
    
    # Tabla de reportes de coordinación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reportes_coordinacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinador_id INTEGER NOT NULL,
            municipio_id INTEGER NOT NULL,
            proceso_electoral_id INTEGER,
            tipo_reporte TEXT NOT NULL, -- cobertura, incidencias, progreso, resumen
            titulo TEXT NOT NULL,
            contenido TEXT NOT NULL,
            datos_json TEXT, -- Datos estructurados en JSON
            fecha_reporte DATE DEFAULT CURRENT_DATE,
            estado TEXT DEFAULT 'borrador', -- borrador, enviado, revisado
            destinatario_id INTEGER,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coordinador_id) REFERENCES coordinadores_municipales(id),
            FOREIGN KEY (municipio_id) REFERENCES municipios(id),
            FOREIGN KEY (proceso_electoral_id) REFERENCES procesos_electorales(id),
            FOREIGN KEY (destinatario_id) REFERENCES users(id)
        )
    """)
    
    # Tabla de notificaciones para coordinadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones_coordinacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinador_id INTEGER NOT NULL,
            tipo_notificacion TEXT NOT NULL, -- asignacion, alerta, recordatorio, mensaje
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            datos_json TEXT,
            prioridad INTEGER DEFAULT 2, -- 1=Alta, 2=Media, 3=Baja
            leida INTEGER DEFAULT 0,
            fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_lectura TIMESTAMP,
            remitente_id INTEGER,
            FOREIGN KEY (coordinador_id) REFERENCES coordinadores_municipales(id),
            FOREIGN KEY (remitente_id) REFERENCES users(id)
        )
    """)
    
    # Tabla de tareas de coordinación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas_coordinacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinador_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            tipo_tarea TEXT NOT NULL, -- asignacion, verificacion, reporte, seguimiento
            prioridad INTEGER DEFAULT 2, -- 1=Alta, 2=Media, 3=Baja
            fecha_limite DATE,
            estado TEXT DEFAULT 'pendiente', -- pendiente, en_progreso, completada, cancelada
            progreso INTEGER DEFAULT 0, -- Porcentaje de avance
            asignada_por INTEGER,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coordinador_id) REFERENCES coordinadores_municipales(id),
            FOREIGN KEY (asignada_por) REFERENCES users(id)
        )
    """)
    
    # Tabla de estadísticas de coordinación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estadisticas_coordinacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinador_id INTEGER NOT NULL,
            municipio_id INTEGER NOT NULL,
            fecha_estadistica DATE DEFAULT CURRENT_DATE,
            total_testigos INTEGER DEFAULT 0,
            testigos_asignados INTEGER DEFAULT 0,
            testigos_disponibles INTEGER DEFAULT 0,
            total_mesas INTEGER DEFAULT 0,
            mesas_cubiertas INTEGER DEFAULT 0,
            mesas_sin_cobertura INTEGER DEFAULT 0,
            porcentaje_cobertura REAL DEFAULT 0.0,
            reportes_enviados INTEGER DEFAULT 0,
            incidencias_reportadas INTEGER DEFAULT 0,
            datos_json TEXT, -- Estadísticas adicionales
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coordinador_id) REFERENCES coordinadores_municipales(id),
            FOREIGN KEY (municipio_id) REFERENCES municipios(id)
        )
    """)
    
    # Crear índices para optimizar consultas
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_coordinadores_municipio ON coordinadores_municipales(municipio_id)",
        "CREATE INDEX IF NOT EXISTS idx_coordinadores_estado ON coordinadores_municipales(estado)",
        "CREATE INDEX IF NOT EXISTS idx_testigos_coordinador ON testigos_electorales(coordinador_id)",
        "CREATE INDEX IF NOT EXISTS idx_testigos_municipio ON testigos_electorales(municipio_id)",
        "CREATE INDEX IF NOT EXISTS idx_testigos_estado ON testigos_electorales(estado)",
        "CREATE INDEX IF NOT EXISTS idx_testigos_partido ON testigos_electorales(partido_id)",
        "CREATE INDEX IF NOT EXISTS idx_mesas_municipio ON mesas_votacion(municipio_id)",
        "CREATE INDEX IF NOT EXISTS idx_mesas_puesto ON mesas_votacion(puesto_votacion_id)",
        "CREATE INDEX IF NOT EXISTS idx_asignaciones_testigo ON asignaciones_testigos(testigo_id)",
        "CREATE INDEX IF NOT EXISTS idx_asignaciones_mesa ON asignaciones_testigos(mesa_id)",
        "CREATE INDEX IF NOT EXISTS idx_asignaciones_coordinador ON asignaciones_testigos(coordinador_id)",
        "CREATE INDEX IF NOT EXISTS idx_asignaciones_proceso ON asignaciones_testigos(proceso_electoral_id)",
        "CREATE INDEX IF NOT EXISTS idx_asignaciones_estado ON asignaciones_testigos(estado)",
        "CREATE INDEX IF NOT EXISTS idx_reportes_coordinador ON reportes_coordinacion(coordinador_id)",
        "CREATE INDEX IF NOT EXISTS idx_reportes_municipio ON reportes_coordinacion(municipio_id)",
        "CREATE INDEX IF NOT EXISTS idx_reportes_tipo ON reportes_coordinacion(tipo_reporte)",
        "CREATE INDEX IF NOT EXISTS idx_notificaciones_coordinador ON notificaciones_coordinacion(coordinador_id)",
        "CREATE INDEX IF NOT EXISTS idx_notificaciones_leida ON notificaciones_coordinacion(leida)",
        "CREATE INDEX IF NOT EXISTS idx_tareas_coordinador ON tareas_coordinacion(coordinador_id)",
        "CREATE INDEX IF NOT EXISTS idx_tareas_estado ON tareas_coordinacion(estado)",
        "CREATE INDEX IF NOT EXISTS idx_estadisticas_coordinador ON estadisticas_coordinacion(coordinador_id, fecha_estadistica)"
    ]
    
    for indice in indices:
        cursor.execute(indice)
    
    print("✅ Tablas de coordinación municipal creadas")
    
    # Insertar datos de ejemplo
    insertar_datos_coordinacion(cursor)
    
    conn.commit()
    conn.close()
    
    print("✅ Sistema de coordinación municipal inicializado")

def insertar_datos_coordinacion(cursor):
    """Insertar datos de ejemplo para coordinación municipal"""
    
    print("🔄 Insertando datos de coordinación municipal...")
    
    # Insertar puestos de votación de ejemplo
    puestos_votacion = [
        ('Institución Educativa Central', 'PV001', 1, 'Carrera 10 # 15-20, Centro', 'Centro', 1.6143, -75.6066, 'María González', '3001234567', 5),
        ('Colegio San José', 'PV002', 1, 'Calle 8 # 12-15, La Esperanza', 'La Esperanza', 1.6150, -75.6070, 'Carlos Rodríguez', '3009876543', 3),
        ('Escuela Rural El Progreso', 'PV003', 1, 'Vereda El Progreso Km 5', 'El Progreso', 1.6200, -75.6100, 'Ana Martínez', '3005555555', 2),
        ('Centro Comunitario Norte', 'PV004', 1, 'Barrio Norte Calle 20 # 8-10', 'Norte', 1.6180, -75.6050, 'Luis Castro', '3007777777', 4)
    ]
    
    for puesto in puestos_votacion:
        cursor.execute("""
            INSERT OR IGNORE INTO puestos_votacion 
            (nombre, codigo, municipio_id, direccion, barrio_vereda, coordenadas_lat, 
             coordenadas_lng, responsable_nombre, responsable_telefono, capacidad_mesas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, puesto)
    
    # Actualizar mesas de votación existentes con puesto_votacion_id
    cursor.execute("SELECT id FROM puestos_votacion LIMIT 4")
    puestos_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM mesas_votacion LIMIT 8")
    mesas_ids = [row[0] for row in cursor.fetchall()]
    
    # Asignar mesas a puestos
    for i, mesa_id in enumerate(mesas_ids):
        puesto_id = puestos_ids[i % len(puestos_ids)]
        cursor.execute("""
            UPDATE mesas_votacion 
            SET puesto_votacion_id = ?, total_votantes = ?, estado = 'activa'
            WHERE id = ?
        """, (puesto_id, 300 + (i * 20), mesa_id))
    
    # Insertar coordinador municipal de ejemplo
    cursor.execute("""
        INSERT OR IGNORE INTO coordinadores_municipales 
        (user_id, municipio_id, nombre_completo, cedula, telefono, email, direccion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (2, 1, 'Roberto Coordinador Municipal', '98765432', '3001111111', 'coordinador@florencia.gov.co', 'Alcaldía Municipal Florencia'))
    
    # Obtener ID del coordinador
    cursor.execute("SELECT id FROM coordinadores_municipales WHERE user_id = 2")
    coordinador_result = cursor.fetchone()
    if coordinador_result:
        coordinador_id = coordinador_result[0]
        
        # Insertar testigos electorales de ejemplo
        testigos = [
            (coordinador_id, 1, 'Juan Carlos Testigo Uno', '11111111', '3002222222', 'testigo1@email.com', 'Barrio Centro', '1985-03-15', 'Contador', 'Primera vez', 1, 'principal'),
            (coordinador_id, 1, 'María Elena Testigo Dos', '22222222', '3003333333', 'testigo2@email.com', 'Barrio La Esperanza', '1990-07-20', 'Abogada', '2 procesos anteriores', 2, 'principal'),
            (coordinador_id, 1, 'Carlos Alberto Testigo Tres', '33333333', '3004444444', 'testigo3@email.com', 'Vereda El Progreso', '1988-11-10', 'Ingeniero', 'Experiencia local', 1, 'suplente'),
            (coordinador_id, 1, 'Ana Lucía Testigo Cuatro', '44444444', '3005555555', 'testigo4@email.com', 'Barrio Norte', '1992-01-25', 'Docente', 'Primera vez', 3, 'principal'),
            (coordinador_id, 1, 'Luis Fernando Testigo Cinco', '55555555', '3006666666', 'testigo5@email.com', 'Centro', '1987-09-05', 'Comerciante', '3 procesos anteriores', 2, 'suplente')
        ]
        
        for testigo in testigos:
            cursor.execute("""
                INSERT OR IGNORE INTO testigos_electorales 
                (coordinador_id, municipio_id, nombre_completo, cedula, telefono, email, 
                 direccion, fecha_nacimiento, profesion, experiencia_electoral, partido_id, tipo_testigo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, testigo)
        
        # Insertar algunas asignaciones de ejemplo
        cursor.execute("SELECT id FROM testigos_electorales LIMIT 4")
        testigos_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM mesas_votacion LIMIT 4")
        mesas_ids = [row[0] for row in cursor.fetchall()]
        
        for i, (testigo_id, mesa_id) in enumerate(zip(testigos_ids, mesas_ids)):
            cursor.execute("""
                INSERT OR IGNORE INTO asignaciones_testigos 
                (testigo_id, mesa_id, coordinador_id, proceso_electoral_id, tipo_asignacion, 
                 hora_inicio, hora_fin, estado, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (testigo_id, mesa_id, coordinador_id, 1, 'principal', '06:00', '18:00', 'asignado', 1))
        
        # Insertar tareas de ejemplo
        tareas = [
            (coordinador_id, 'Verificar asignación de testigos', 'Revisar que todas las mesas tengan testigos asignados', 'verificacion', 1, '2024-11-15'),
            (coordinador_id, 'Generar reporte de cobertura', 'Crear reporte semanal de cobertura de mesas', 'reporte', 2, '2024-11-10'),
            (coordinador_id, 'Contactar testigos faltantes', 'Llamar a testigos que no han confirmado asistencia', 'seguimiento', 1, '2024-11-08')
        ]
        
        for tarea in tareas:
            cursor.execute("""
                INSERT OR IGNORE INTO tareas_coordinacion 
                (coordinador_id, titulo, descripcion, tipo_tarea, prioridad, fecha_limite, asignada_por)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, tarea)
    
    print("✅ Datos de coordinación municipal insertados")

if __name__ == "__main__":
    try:
        create_coordination_tables()
        print("🎉 Sistema de coordinación municipal creado exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()