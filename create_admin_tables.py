#!/usr/bin/env python3
"""
Script para crear tablas administrativas del Sistema Electoral ERP
Candidatos, Partidos, Coaliciones, etc.
"""

import sqlite3
from datetime import datetime

def create_admin_tables():
    """Crear tablas administrativas"""
    
    print("🔄 Creando tablas administrativas...")
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Habilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Tabla de partidos políticos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidos_politicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            sigla TEXT NOT NULL UNIQUE,
            color_principal TEXT DEFAULT '#007bff',
            logo_url TEXT,
            representante_legal TEXT,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            activo INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla de coaliciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coaliciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            fecha_conformacion DATE,
            activa INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla de partidos en coaliciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coalicion_partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coalicion_id INTEGER NOT NULL,
            partido_id INTEGER NOT NULL,
            fecha_adhesion DATE DEFAULT CURRENT_DATE,
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (coalicion_id) REFERENCES coaliciones(id),
            FOREIGN KEY (partido_id) REFERENCES partidos_politicos(id),
            UNIQUE(coalicion_id, partido_id)
        )
    """)
    
    # Tabla de cargos electorales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cargos_electorales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            nivel TEXT NOT NULL, -- 'nacional', 'departamental', 'municipal'
            municipio_id INTEGER,
            activo INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (municipio_id) REFERENCES municipios(id)
        )
    """)
    
    # Tabla de candidatos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula TEXT NOT NULL UNIQUE,
            nombre_completo TEXT NOT NULL,
            fecha_nacimiento DATE,
            lugar_nacimiento TEXT,
            profesion TEXT,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            foto_url TEXT,
            hoja_vida_url TEXT,
            partido_id INTEGER,
            coalicion_id INTEGER,
            cargo_id INTEGER NOT NULL,
            municipio_id INTEGER,
            numero_lista INTEGER,
            estado TEXT DEFAULT 'inscrito', -- 'inscrito', 'aprobado', 'rechazado', 'retirado'
            fecha_inscripcion DATE DEFAULT CURRENT_DATE,
            observaciones TEXT,
            activo INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (partido_id) REFERENCES partidos_politicos(id),
            FOREIGN KEY (coalicion_id) REFERENCES coaliciones(id),
            FOREIGN KEY (cargo_id) REFERENCES cargos_electorales(id),
            FOREIGN KEY (municipio_id) REFERENCES municipios(id)
        )
    """)
    
    # Tabla de procesos electorales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS procesos_electorales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            tipo TEXT NOT NULL, -- 'presidencial', 'congreso', 'departamental', 'municipal'
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE NOT NULL,
            fecha_eleccion DATE NOT NULL,
            estado TEXT DEFAULT 'configuracion', -- 'configuracion', 'activo', 'votacion', 'escrutinio', 'finalizado'
            municipio_id INTEGER,
            activo INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (municipio_id) REFERENCES municipios(id)
        )
    """)
    
    # Tabla de asignaciones de testigos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asignaciones_testigos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            testigo_id INTEGER NOT NULL,
            partido_id INTEGER,
            coalicion_id INTEGER,
            puesto_id INTEGER NOT NULL,
            mesa_id INTEGER,
            proceso_electoral_id INTEGER NOT NULL,
            tipo_testigo TEXT DEFAULT 'mesa', -- 'mesa', 'puesto', 'general'
            fecha_asignacion DATE DEFAULT CURRENT_DATE,
            asignado_por INTEGER NOT NULL,
            estado TEXT DEFAULT 'asignado', -- 'asignado', 'confirmado', 'presente', 'ausente'
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (testigo_id) REFERENCES users(id),
            FOREIGN KEY (partido_id) REFERENCES partidos_politicos(id),
            FOREIGN KEY (coalicion_id) REFERENCES coaliciones(id),
            FOREIGN KEY (puesto_id) REFERENCES puestos_votacion(id),
            FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id),
            FOREIGN KEY (proceso_electoral_id) REFERENCES procesos_electorales(id),
            FOREIGN KEY (asignado_por) REFERENCES users(id)
        )
    """)
    
    # Tabla de configuración del sistema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clave TEXT NOT NULL UNIQUE,
            valor TEXT NOT NULL,
            descripcion TEXT,
            tipo TEXT DEFAULT 'string', -- 'string', 'number', 'boolean', 'json'
            categoria TEXT DEFAULT 'general',
            modificado_por INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (modificado_por) REFERENCES users(id)
        )
    """)
    
    # Crear índices
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_candidatos_cedula ON candidatos(cedula)",
        "CREATE INDEX IF NOT EXISTS idx_candidatos_partido ON candidatos(partido_id)",
        "CREATE INDEX IF NOT EXISTS idx_candidatos_cargo ON candidatos(cargo_id)",
        "CREATE INDEX IF NOT EXISTS idx_asignaciones_testigo ON asignaciones_testigos(testigo_id)",
        "CREATE INDEX IF NOT EXISTS idx_asignaciones_puesto ON asignaciones_testigos(puesto_id)",
        "CREATE INDEX IF NOT EXISTS idx_asignaciones_mesa ON asignaciones_testigos(mesa_id)",
        "CREATE INDEX IF NOT EXISTS idx_procesos_fecha ON procesos_electorales(fecha_eleccion)",
        "CREATE INDEX IF NOT EXISTS idx_config_clave ON configuracion_sistema(clave)"
    ]
    
    for indice in indices:
        cursor.execute(indice)
    
    print("✅ Tablas administrativas creadas")
    
    # Insertar datos iniciales
    insertar_datos_administrativos(cursor)
    
    conn.commit()
    conn.close()
    
    print("✅ Sistema administrativo inicializado")

def insertar_datos_administrativos(cursor):
    """Insertar datos administrativos iniciales"""
    
    print("🔄 Insertando datos administrativos iniciales...")
    
    # Partidos políticos principales de Colombia
    partidos = [
        ('Partido Liberal Colombiano', 'PLC', '#FF0000', 'Partido Liberal'),
        ('Partido Conservador Colombiano', 'PCC', '#0000FF', 'Partido Conservador'),
        ('Centro Democrático', 'CD', '#FF8C00', 'Centro Democrático'),
        ('Cambio Radical', 'CR', '#FFD700', 'Cambio Radical'),
        ('Partido de la U', 'U', '#008000', 'Partido Social de Unidad Nacional'),
        ('Polo Democrático Alternativo', 'PDA', '#800080', 'Polo Democrático'),
        ('Alianza Verde', 'AV', '#00FF00', 'Partido Verde'),
        ('MAIS', 'MAIS', '#FFA500', 'Movimiento Alternativo Indígena y Social'),
        ('ASI', 'ASI', '#FF69B4', 'Alianza Social Independiente'),
        ('AICO', 'AICO', '#8B4513', 'Autoridades Indígenas de Colombia')
    ]
    
    for nombre, sigla, color, descripcion in partidos:
        cursor.execute("""
            INSERT OR IGNORE INTO partidos_politicos (nombre, sigla, color_principal, representante_legal)
            VALUES (?, ?, ?, ?)
        """, (nombre, sigla, color, descripcion))
    
    # Cargos electorales
    cargos = [
        ('Alcalde Municipal', 'Alcalde del municipio', 'municipal'),
        ('Concejal Municipal', 'Miembro del Concejo Municipal', 'municipal'),
        ('Gobernador Departamental', 'Gobernador del Departamento', 'departamental'),
        ('Diputado Departamental', 'Miembro de la Asamblea Departamental', 'departamental'),
        ('Senador', 'Miembro del Senado de la República', 'nacional'),
        ('Representante a la Cámara', 'Miembro de la Cámara de Representantes', 'nacional'),
        ('Presidente de la República', 'Presidente de Colombia', 'nacional'),
        ('Vicepresidente de la República', 'Vicepresidente de Colombia', 'nacional')
    ]
    
    for nombre, descripcion, nivel in cargos:
        cursor.execute("""
            INSERT OR IGNORE INTO cargos_electorales (nombre, descripcion, nivel)
            VALUES (?, ?, ?)
        """, (nombre, descripcion, nivel))
    
    # Proceso electoral actual
    cursor.execute("""
        INSERT OR IGNORE INTO procesos_electorales 
        (nombre, descripcion, tipo, fecha_inicio, fecha_fin, fecha_eleccion, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        'Elecciones Municipales 2024',
        'Elecciones para Alcalde y Concejo Municipal',
        'municipal',
        '2024-10-01',
        '2024-12-31',
        '2024-11-15',
        'activo'
    ))
    
    # Configuraciones del sistema
    configuraciones = [
        ('sistema_nombre', 'Sistema Electoral ERP - Caquetá', 'Nombre del sistema', 'string', 'general'),
        ('sistema_version', '1.0.0', 'Versión del sistema', 'string', 'general'),
        ('eleccion_activa', 'true', 'Si hay una elección activa', 'boolean', 'electoral'),
        ('permitir_e14_duplicados', 'false', 'Permitir E14 duplicados por mesa', 'boolean', 'electoral'),
        ('tiempo_sesion_minutos', '480', 'Tiempo de sesión en minutos', 'number', 'seguridad'),
        ('max_intentos_login', '3', 'Máximo intentos de login', 'number', 'seguridad'),
        ('departamento', 'Caquetá', 'Departamento del sistema', 'string', 'ubicacion'),
        ('zona_horaria', 'America/Bogota', 'Zona horaria del sistema', 'string', 'general')
    ]
    
    for clave, valor, descripcion, tipo, categoria in configuraciones:
        cursor.execute("""
            INSERT OR IGNORE INTO configuracion_sistema (clave, valor, descripcion, tipo, categoria)
            VALUES (?, ?, ?, ?, ?)
        """, (clave, valor, descripcion, tipo, categoria))
    
    print("✅ Datos administrativos insertados")

if __name__ == "__main__":
    try:
        create_admin_tables()
        print("🎉 Sistema administrativo creado exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()