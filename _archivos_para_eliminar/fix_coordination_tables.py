#!/usr/bin/env python3
"""
Script para corregir y completar las tablas de coordinación municipal
"""

import sqlite3

def fix_coordination_tables():
    """Corregir tablas de coordinación municipal"""
    
    print("🔧 Corrigiendo tablas de coordinación municipal...")
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Verificar y agregar columnas faltantes a puestos_votacion
    cursor.execute("PRAGMA table_info(puestos_votacion)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'codigo' not in columns:
        cursor.execute("ALTER TABLE puestos_votacion ADD COLUMN codigo TEXT")
    if 'barrio_vereda' not in columns:
        cursor.execute("ALTER TABLE puestos_votacion ADD COLUMN barrio_vereda TEXT")
    if 'responsable_nombre' not in columns:
        cursor.execute("ALTER TABLE puestos_votacion ADD COLUMN responsable_nombre TEXT")
    if 'responsable_telefono' not in columns:
        cursor.execute("ALTER TABLE puestos_votacion ADD COLUMN responsable_telefono TEXT")
    if 'capacidad_mesas' not in columns:
        cursor.execute("ALTER TABLE puestos_votacion ADD COLUMN capacidad_mesas INTEGER DEFAULT 1")
    if 'observaciones' not in columns:
        cursor.execute("ALTER TABLE puestos_votacion ADD COLUMN observaciones TEXT")
    
    # Crear tabla de coordinadores municipales
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
            estado TEXT DEFAULT 'activo',
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (municipio_id) REFERENCES municipios(id)
        )
    """)
    
    # Crear tabla de testigos electorales
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
            tipo_testigo TEXT DEFAULT 'principal',
            estado TEXT DEFAULT 'disponible',
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
    
    # Recrear tabla de asignaciones de testigos
    cursor.execute("DROP TABLE IF EXISTS asignaciones_testigos")
    cursor.execute("""
        CREATE TABLE asignaciones_testigos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            testigo_id INTEGER NOT NULL,
            mesa_id INTEGER NOT NULL,
            coordinador_id INTEGER NOT NULL,
            proceso_electoral_id INTEGER NOT NULL,
            tipo_asignacion TEXT DEFAULT 'principal',
            fecha_asignacion DATE DEFAULT CURRENT_DATE,
            hora_inicio TIME,
            hora_fin TIME,
            estado TEXT DEFAULT 'asignado',
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
    
    # Crear otras tablas necesarias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas_coordinacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinador_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            tipo_tarea TEXT NOT NULL,
            prioridad INTEGER DEFAULT 2,
            fecha_limite DATE,
            estado TEXT DEFAULT 'pendiente',
            progreso INTEGER DEFAULT 0,
            asignada_por INTEGER,
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coordinador_id) REFERENCES coordinadores_municipales(id),
            FOREIGN KEY (asignada_por) REFERENCES users(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones_coordinacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinador_id INTEGER NOT NULL,
            tipo_notificacion TEXT NOT NULL,
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            datos_json TEXT,
            prioridad INTEGER DEFAULT 2,
            leida INTEGER DEFAULT 0,
            fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_lectura TIMESTAMP,
            remitente_id INTEGER,
            FOREIGN KEY (coordinador_id) REFERENCES coordinadores_municipales(id),
            FOREIGN KEY (remitente_id) REFERENCES users(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reportes_coordinacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinador_id INTEGER NOT NULL,
            municipio_id INTEGER NOT NULL,
            proceso_electoral_id INTEGER,
            tipo_reporte TEXT NOT NULL,
            titulo TEXT NOT NULL,
            contenido TEXT NOT NULL,
            datos_json TEXT,
            fecha_reporte DATE DEFAULT CURRENT_DATE,
            estado TEXT DEFAULT 'borrador',
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
            datos_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coordinador_id) REFERENCES coordinadores_municipales(id),
            FOREIGN KEY (municipio_id) REFERENCES municipios(id)
        )
    """)
    
    print("✅ Tablas corregidas")
    
    # Insertar datos de ejemplo
    insertar_datos_ejemplo(cursor)
    
    conn.commit()
    conn.close()
    
    print("✅ Sistema de coordinación municipal corregido")

def insertar_datos_ejemplo(cursor):
    """Insertar datos de ejemplo"""
    
    print("🔄 Insertando datos de ejemplo...")
    
    # Actualizar puestos de votación existentes
    cursor.execute("SELECT id FROM puestos_votacion LIMIT 4")
    puestos = cursor.fetchall()
    
    codigos = ['PV001', 'PV002', 'PV003', 'PV004']
    nombres_responsables = ['María González', 'Carlos Rodríguez', 'Ana Martínez', 'Luis Castro']
    telefonos = ['3001234567', '3009876543', '3005555555', '3007777777']
    
    for i, puesto in enumerate(puestos):
        cursor.execute("""
            UPDATE puestos_votacion 
            SET codigo = ?, responsable_nombre = ?, responsable_telefono = ?, capacidad_mesas = ?
            WHERE id = ?
        """, (codigos[i], nombres_responsables[i], telefonos[i], 3 + i, puesto[0]))
    
    # Insertar coordinador municipal
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
        
        # Insertar testigos electorales
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
        
        # Insertar tareas de ejemplo
        tareas = [
            (coordinador_id, 'Verificar asignación de testigos', 'Revisar que todas las mesas tengan testigos asignados', 'verificacion', 1, '2024-11-15', 1),
            (coordinador_id, 'Generar reporte de cobertura', 'Crear reporte semanal de cobertura de mesas', 'reporte', 2, '2024-11-10', 1),
            (coordinador_id, 'Contactar testigos faltantes', 'Llamar a testigos que no han confirmado asistencia', 'seguimiento', 1, '2024-11-08', 1)
        ]
        
        for tarea in tareas:
            cursor.execute("""
                INSERT OR IGNORE INTO tareas_coordinacion 
                (coordinador_id, titulo, descripcion, tipo_tarea, prioridad, fecha_limite, asignada_por)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, tarea)
    
    print("✅ Datos de ejemplo insertados")

if __name__ == "__main__":
    try:
        fix_coordination_tables()
        print("🎉 Sistema de coordinación municipal corregido exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()