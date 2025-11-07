#!/usr/bin/env python3
"""
Script para crear las tablas de candidatos, partidos políticos y coaliciones
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import os
from datetime import datetime

def create_candidate_tables():
    """Crear todas las tablas relacionadas con candidatos, partidos y coaliciones"""
    
    # Conectar a la base de datos
    db_path = 'electoral_system.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🗳️  Creando tablas de candidatos, partidos y coaliciones...")
        
        # 1. Tabla de partidos políticos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS political_parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_oficial VARCHAR(200) NOT NULL,
            siglas VARCHAR(20) UNIQUE NOT NULL,
            color_representativo VARCHAR(7),
            logo_url VARCHAR(500),
            descripcion TEXT,
            fundacion_year INTEGER,
            ideologia VARCHAR(100),
            activo BOOLEAN DEFAULT 1,
            reconocido_oficialmente BOOLEAN DEFAULT 1,
            creado_por INTEGER,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creado_por) REFERENCES users(id)
        )
        ''')
        
        # Crear índices para partidos políticos
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_parties_nombre ON political_parties(nombre_oficial)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_parties_siglas ON political_parties(siglas)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_parties_activo ON political_parties(activo)')
        
        # 2. Tabla de coaliciones
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coalitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_coalicion VARCHAR(200) NOT NULL,
            descripcion TEXT,
            fecha_formacion DATETIME,
            fecha_disolucion DATETIME,
            activo BOOLEAN DEFAULT 1,
            creado_por INTEGER,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creado_por) REFERENCES users(id)
        )
        ''')
        
        # Crear índices para coaliciones
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coalitions_nombre ON coalitions(nombre_coalicion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coalitions_activo ON coalitions(activo)')
        
        # 3. Tabla de relación coalición-partido
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coalition_parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coalition_id INTEGER NOT NULL,
            party_id INTEGER NOT NULL,
            fecha_adhesion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_retiro DATETIME,
            es_partido_principal BOOLEAN DEFAULT 0,
            porcentaje_participacion REAL,
            FOREIGN KEY (coalition_id) REFERENCES coalitions(id),
            FOREIGN KEY (party_id) REFERENCES political_parties(id),
            UNIQUE(coalition_id, party_id)
        )
        ''')
        
        # Crear índices para coalition_parties
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coalition_parties_coalition ON coalition_parties(coalition_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coalition_parties_party ON coalition_parties(party_id)')
        
        # 4. Tabla de candidatos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo VARCHAR(200) NOT NULL,
            cedula VARCHAR(20) UNIQUE NOT NULL,
            numero_tarjeton INTEGER NOT NULL,
            cargo_aspirado VARCHAR(100) NOT NULL,
            election_type_id INTEGER NOT NULL,
            circunscripcion VARCHAR(100) NOT NULL,
            party_id INTEGER,
            coalition_id INTEGER,
            es_independiente BOOLEAN DEFAULT 0,
            foto_url VARCHAR(500),
            biografia TEXT,
            propuestas TEXT,
            experiencia TEXT,
            activo BOOLEAN DEFAULT 1,
            habilitado_oficialmente BOOLEAN DEFAULT 1,
            creado_por INTEGER,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (election_type_id) REFERENCES election_types(id),
            FOREIGN KEY (party_id) REFERENCES political_parties(id),
            FOREIGN KEY (coalition_id) REFERENCES coalitions(id),
            FOREIGN KEY (creado_por) REFERENCES users(id),
            CHECK ((party_id IS NOT NULL AND coalition_id IS NULL AND es_independiente = 0) OR
                   (party_id IS NULL AND coalition_id IS NOT NULL AND es_independiente = 0) OR
                   (party_id IS NULL AND coalition_id IS NULL AND es_independiente = 1))
        )
        ''')
        
        # Crear índices para candidatos
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_nombre ON candidates(nombre_completo)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_cedula ON candidates(cedula)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_tarjeton ON candidates(numero_tarjeton)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_cargo ON candidates(cargo_aspirado)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_election_type ON candidates(election_type_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_party ON candidates(party_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_coalition ON candidates(coalition_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_activo ON candidates(activo)')
        
        # 5. Tabla de resultados por candidato
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidate_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            election_type_id INTEGER NOT NULL,
            total_votos INTEGER DEFAULT 0,
            porcentaje_votacion REAL DEFAULT 0.0,
            posicion_ranking INTEGER,
            votos_por_municipio TEXT,
            votos_por_puesto TEXT,
            mejor_municipio VARCHAR(100),
            peor_municipio VARCHAR(100),
            promedio_votos_por_mesa REAL,
            desviacion_estandar REAL,
            coeficiente_variacion REAL,
            fecha_calculo DATETIME DEFAULT CURRENT_TIMESTAMP,
            calculado_por INTEGER,
            total_mesas_incluidas INTEGER DEFAULT 0,
            total_votos_validos_contexto INTEGER DEFAULT 0,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id),
            FOREIGN KEY (election_type_id) REFERENCES election_types(id),
            FOREIGN KEY (calculado_por) REFERENCES users(id)
        )
        ''')
        
        # Crear índices para candidate_results
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidate_results_candidate ON candidate_results(candidate_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidate_results_election_type ON candidate_results(election_type_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidate_results_ranking ON candidate_results(posicion_ranking)')
        
        # 6. Tabla de resultados por partido
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS party_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_id INTEGER NOT NULL,
            election_type_id INTEGER NOT NULL,
            total_votos_partido INTEGER DEFAULT 0,
            porcentaje_votacion_partido REAL DEFAULT 0.0,
            posicion_ranking_partido INTEGER,
            total_candidatos INTEGER DEFAULT 0,
            candidatos_resultados TEXT,
            mejor_candidato_id INTEGER,
            peor_candidato_id INTEGER,
            votos_por_municipio TEXT,
            mejor_municipio_partido VARCHAR(100),
            fecha_calculo DATETIME DEFAULT CURRENT_TIMESTAMP,
            calculado_por INTEGER,
            FOREIGN KEY (party_id) REFERENCES political_parties(id),
            FOREIGN KEY (election_type_id) REFERENCES election_types(id),
            FOREIGN KEY (mejor_candidato_id) REFERENCES candidates(id),
            FOREIGN KEY (peor_candidato_id) REFERENCES candidates(id),
            FOREIGN KEY (calculado_por) REFERENCES users(id)
        )
        ''')
        
        # Crear índices para party_results
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_party_results_party ON party_results(party_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_party_results_election_type ON party_results(election_type_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_party_results_ranking ON party_results(posicion_ranking_partido)')
        
        # 7. Tabla de resultados por coalición
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coalition_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coalition_id INTEGER NOT NULL,
            election_type_id INTEGER NOT NULL,
            total_votos_coalicion INTEGER DEFAULT 0,
            porcentaje_votacion_coalicion REAL DEFAULT 0.0,
            posicion_ranking_coalicion INTEGER,
            partidos_resultados TEXT,
            mejor_partido_id INTEGER,
            total_candidatos_coalicion INTEGER DEFAULT 0,
            mejor_candidato_coalicion_id INTEGER,
            fecha_calculo DATETIME DEFAULT CURRENT_TIMESTAMP,
            calculado_por INTEGER,
            FOREIGN KEY (coalition_id) REFERENCES coalitions(id),
            FOREIGN KEY (election_type_id) REFERENCES election_types(id),
            FOREIGN KEY (mejor_partido_id) REFERENCES political_parties(id),
            FOREIGN KEY (mejor_candidato_coalicion_id) REFERENCES candidates(id),
            FOREIGN KEY (calculado_por) REFERENCES users(id)
        )
        ''')
        
        # Crear índices para coalition_results
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coalition_results_coalition ON coalition_results(coalition_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coalition_results_election_type ON coalition_results(election_type_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coalition_results_ranking ON coalition_results(posicion_ranking_coalicion)')
        
        # 8. Insertar algunos partidos políticos de ejemplo para Colombia
        partidos_ejemplo = [
            ('Partido Conservador Colombiano', 'PCC', '#0066CC', 'Conservador'),
            ('Partido Liberal Colombiano', 'PLC', '#FF0000', 'Liberal'),
            ('Centro Democrático', 'CD', '#FF6600', 'Centro-derecha'),
            ('Cambio Radical', 'CR', '#FFFF00', 'Centro'),
            ('Partido de la U', 'U', '#00CC00', 'Centro'),
            ('Polo Democrático Alternativo', 'PDA', '#FFFF00', 'Izquierda'),
            ('Alianza Verde', 'AV', '#00AA00', 'Verde'),
            ('MAIS', 'MAIS', '#800080', 'Alternativo'),
            ('ASI', 'ASI', '#FF69B4', 'Alternativo'),
            ('AICO', 'AICO', '#8B4513', 'Indígena'),
            ('Comunes', 'COMUNES', '#FF4500', 'Izquierda'),
            ('Nuevo Liberalismo', 'NL', '#DC143C', 'Liberal'),
            ('Pacto Histórico', 'PH', '#4B0082', 'Izquierda'),
            ('Equipo por Colombia', 'EPC', '#1E90FF', 'Centro-derecha'),
            ('Liga de Gobernantes Anticorrupción', 'LIGA', '#32CD32', 'Anticorrupción')
        ]
        
        for nombre, siglas, color, ideologia in partidos_ejemplo:
            cursor.execute('''
            INSERT OR IGNORE INTO political_parties 
            (nombre_oficial, siglas, color_representativo, ideologia, activo, reconocido_oficialmente)
            VALUES (?, ?, ?, ?, 1, 1)
            ''', (nombre, siglas, color, ideologia))
        
        # 9. Insertar algunos tipos de elecciones de ejemplo
        tipos_eleccion_ejemplo = [
            ('Concejos de Juventudes', 'Elección de representantes juveniles', 'CJ', 
             '{"campos_votos": ["votos_candidato"], "permite_tarjeton": true, "tipo_votacion": "candidatos"}'),
            ('Senado de la República', 'Elección de senadores', 'SEN',
             '{"campos_votos": ["votos_lista", "votos_preferentes"], "permite_tarjeton": true, "tipo_votacion": "listas_candidatos"}'),
            ('Cámara de Representantes', 'Elección de representantes a la cámara', 'CAM',
             '{"campos_votos": ["votos_lista", "votos_preferentes"], "permite_tarjeton": true, "tipo_votacion": "listas_candidatos"}'),
            ('Presidencia de la República', 'Elección presidencial', 'PRES',
             '{"campos_votos": ["votos_candidato"], "permite_tarjeton": true, "tipo_votacion": "candidatos"}'),
            ('Gobernación', 'Elección de gobernador', 'GOB',
             '{"campos_votos": ["votos_candidato"], "permite_tarjeton": true, "tipo_votacion": "candidatos"}'),
            ('Alcaldía', 'Elección de alcalde', 'ALC',
             '{"campos_votos": ["votos_candidato"], "permite_tarjeton": true, "tipo_votacion": "candidatos"}'),
            ('Concejo Municipal', 'Elección de concejales', 'CON',
             '{"campos_votos": ["votos_lista", "votos_preferentes"], "permite_tarjeton": true, "tipo_votacion": "listas_candidatos"}'),
            ('Asamblea Departamental', 'Elección de diputados', 'ASA',
             '{"campos_votos": ["votos_lista", "votos_preferentes"], "permite_tarjeton": true, "tipo_votacion": "listas_candidatos"}')
        ]
        
        for nombre, descripcion, codigo, plantilla in tipos_eleccion_ejemplo:
            cursor.execute('''
            INSERT OR IGNORE INTO election_types 
            (nombre, descripcion, codigo, plantilla_e14, activo)
            VALUES (?, ?, ?, ?, 1)
            ''', (nombre, descripcion, codigo, plantilla))
        
        # Confirmar cambios
        conn.commit()
        
        # Verificar creación de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%candidate%' OR name LIKE '%part%' OR name LIKE '%coalition%'")
        tablas_creadas = cursor.fetchall()
        
        print("✅ Tablas creadas exitosamente:")
        for tabla in tablas_creadas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {tabla[0]}: {count} registros")
        
        print(f"\n📊 Resumen de creación:")
        print(f"   - Base de datos: {db_path}")
        print(f"   - Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - Tablas principales: political_parties, coalitions, candidates")
        print(f"   - Tablas de resultados: candidate_results, party_results, coalition_results")
        print(f"   - Tablas de relación: coalition_parties")
        print(f"   - Partidos políticos insertados: {len(partidos_ejemplo)}")
        print(f"   - Tipos de elección insertados: {len(tipos_eleccion_ejemplo)}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error creando tablas: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🗳️  Sistema de Recolección Inicial de Votaciones - Caquetá")
    print("=" * 60)
    print("Creando tablas de candidatos, partidos políticos y coaliciones...")
    print()
    
    success = create_candidate_tables()
    
    if success:
        print("\n🎉 ¡Tablas de candidatos creadas exitosamente!")
        print("Ya puedes usar el sistema de gestión de candidatos, partidos y coaliciones.")
    else:
        print("\n💥 Error en la creación de tablas. Revisa los logs para más detalles.")