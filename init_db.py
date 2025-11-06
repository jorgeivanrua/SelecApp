#!/usr/bin/env python3
"""
Script de inicialización de base de datos para Sistema Electoral ERP
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializar base de datos con datos básicos"""
    
    print("🔄 Inicializando base de datos del Sistema Electoral ERP...")
    
    # Aquí se crearían las tablas y datos iniciales
    # Por ahora, creamos un archivo SQL básico
    
    sql_content = """
-- Sistema Electoral ERP - Inicialización de Base de Datos
-- Departamento del Caquetá

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de municipios
CREATE TABLE IF NOT EXISTS municipios (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    departamento VARCHAR(50) DEFAULT 'Caquetá',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de mesas de votación
CREATE TABLE IF NOT EXISTS mesas_votacion (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(10) NOT NULL,
    municipio_id INTEGER REFERENCES municipios(id),
    puesto_votacion VARCHAR(200),
    direccion TEXT,
    votantes_habilitados INTEGER DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'configurada',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de candidatos
CREATE TABLE IF NOT EXISTS candidatos (
    id SERIAL PRIMARY KEY,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    partido VARCHAR(100),
    cargo VARCHAR(100),
    municipio_id INTEGER REFERENCES municipios(id),
    estado VARCHAR(20) DEFAULT 'registrado',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de votos
CREATE TABLE IF NOT EXISTS votos (
    id SERIAL PRIMARY KEY,
    mesa_id INTEGER REFERENCES mesas_votacion(id),
    candidato_id INTEGER REFERENCES candidatos(id),
    cantidad INTEGER NOT NULL,
    tipo_voto VARCHAR(20) DEFAULT 'valido', -- valido, blanco, nulo
    registrado_por INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de incidencias
CREATE TABLE IF NOT EXISTS incidencias (
    id SERIAL PRIMARY KEY,
    mesa_id INTEGER REFERENCES mesas_votacion(id),
    tipo VARCHAR(50) NOT NULL,
    descripcion TEXT NOT NULL,
    reportado_por INTEGER REFERENCES users(id),
    estado VARCHAR(20) DEFAULT 'abierta',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar municipios del Caquetá
INSERT INTO municipios (codigo, nombre) VALUES
('18001', 'Florencia'),
('18029', 'San Vicente del Caguán'),
('18592', 'Puerto Rico'),
('18479', 'El Paujil'),
('18410', 'La Montañita'),
('18205', 'Curillo'),
('18247', 'El Doncello'),
('18256', 'Belén de los Andaquíes'),
('18150', 'Cartagena del Chairá'),
('18460', 'Morelia'),
('18753', 'San José del Fragua'),
('18610', 'Albania'),
('18785', 'Solano'),
('18550', 'Milán'),
('18756', 'Solita'),
('18685', 'Valparaíso')
ON CONFLICT (codigo) DO NOTHING;

-- Crear usuario administrador por defecto
INSERT INTO users (username, cedula, nombre_completo, email, password_hash, rol) VALUES
('admin', '12345678', 'Administrador del Sistema', 'admin@caqueta.gov.co', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5u', 'super_admin')
ON CONFLICT (username) DO NOTHING;

-- Crear índices para optimización
CREATE INDEX IF NOT EXISTS idx_users_cedula ON users(cedula);
CREATE INDEX IF NOT EXISTS idx_users_rol ON users(rol);
CREATE INDEX IF NOT EXISTS idx_mesas_municipio ON mesas_votacion(municipio_id);
CREATE INDEX IF NOT EXISTS idx_votos_mesa ON votos(mesa_id);
CREATE INDEX IF NOT EXISTS idx_votos_candidato ON votos(candidato_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_mesa ON incidencias(mesa_id);

-- Crear vistas útiles
CREATE OR REPLACE VIEW vista_resultados_mesa AS
SELECT 
    m.numero as mesa,
    mu.nombre as municipio,
    c.nombre_completo as candidato,
    c.partido,
    SUM(v.cantidad) as total_votos
FROM mesas_votacion m
JOIN municipios mu ON m.municipio_id = mu.id
LEFT JOIN votos v ON m.id = v.mesa_id
LEFT JOIN candidatos c ON v.candidato_id = c.id
WHERE v.tipo_voto = 'valido'
GROUP BY m.numero, mu.nombre, c.nombre_completo, c.partido
ORDER BY m.numero, total_votos DESC;

COMMIT;
"""
    
    # Guardar script SQL
    with open('init_database.sql', 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print("✅ Script de inicialización creado: init_database.sql")
    print("📝 Para ejecutar: psql -U electoral_user -d caqueta_electoral -f init_database.sql")
    
    return True

if __name__ == "__main__":
    try:
        init_database()
        print("🎉 Inicialización completada exitosamente!")
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        sys.exit(1)