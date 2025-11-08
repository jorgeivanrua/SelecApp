#!/usr/bin/env python3
"""
Script para agregar estructura DIVIPOLA completa a la base de datos
dd: departamento (2 dígitos)
mm: municipio (3 dígitos)
zz: zona (2 dígitos)
pp: puesto (2 dígitos)
"""

import sqlite3
import shutil
from datetime import datetime

def backup_database():
    """Crear backup de la base de datos"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'caqueta_electoral_backup_{timestamp}.db'
    shutil.copy2('caqueta_electoral.db', backup_file)
    print(f"✅ Backup creado: {backup_file}")
    return backup_file

def add_divipola_structure():
    """Agregar estructura DIVIPOLA a las tablas"""
    
    backup_file = backup_database()
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("AGREGANDO ESTRUCTURA DIVIPOLA")
    print("="*80)
    
    try:
        # 1. Agregar columnas DIVIPOLA a municipios
        print("\n📝 1. Actualizando tabla municipios...")
        
        cursor.execute("PRAGMA table_info(municipios)")
        columns = {col[1] for col in cursor.fetchall()}
        
        if 'codigo_dd' not in columns:
            cursor.execute("ALTER TABLE municipios ADD COLUMN codigo_dd TEXT")
            print("   ✅ Agregada columna codigo_dd")
        
        if 'codigo_mm' not in columns:
            cursor.execute("ALTER TABLE municipios ADD COLUMN codigo_mm TEXT")
            print("   ✅ Agregada columna codigo_mm")
        
        # Extraer dd y mm del código existente
        cursor.execute("SELECT id, codigo FROM municipios")
        for row in cursor.fetchall():
            mun_id, codigo = row
            if len(codigo) == 5:
                dd = codigo[:2]
                mm = codigo[2:5]
                cursor.execute("""
                    UPDATE municipios 
                    SET codigo_dd = ?, codigo_mm = ?
                    WHERE id = ?
                """, (dd, mm, mun_id))
        
        print("   ✅ Códigos dd y mm extraídos del código existente")
        
        # 2. Crear tabla de zonas si no existe
        print("\n📝 2. Creando tabla zonas...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS zonas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_zz TEXT NOT NULL,
                nombre TEXT NOT NULL,
                municipio_id INTEGER NOT NULL,
                codigo_completo TEXT,
                descripcion TEXT,
                activo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (municipio_id) REFERENCES municipios(id),
                UNIQUE(municipio_id, codigo_zz)
            )
        """)
        print("   ✅ Tabla zonas creada")
        
        # 3. Agregar columnas DIVIPOLA a puestos_votacion
        print("\n📝 3. Actualizando tabla puestos_votacion...")
        
        cursor.execute("PRAGMA table_info(puestos_votacion)")
        columns = {col[1] for col in cursor.fetchall()}
        
        if 'zona_id' not in columns:
            cursor.execute("ALTER TABLE puestos_votacion ADD COLUMN zona_id INTEGER REFERENCES zonas(id)")
            print("   ✅ Agregada columna zona_id")
        
        if 'codigo_pp' not in columns:
            cursor.execute("ALTER TABLE puestos_votacion ADD COLUMN codigo_pp TEXT")
            print("   ✅ Agregada columna codigo_pp")
        
        if 'codigo_divipola' not in columns:
            cursor.execute("ALTER TABLE puestos_votacion ADD COLUMN codigo_divipola TEXT")
            print("   ✅ Agregada columna codigo_divipola (ddmmzzpp)")
        
        # 4. Crear zonas por defecto para los puestos existentes
        print("\n📝 4. Creando zonas por defecto...")
        
        cursor.execute("""
            SELECT DISTINCT municipio_id, m.codigo, m.nombre
            FROM puestos_votacion p
            JOIN municipios m ON p.municipio_id = m.id
        """)
        
        for row in cursor.fetchall():
            municipio_id, codigo_mun, nombre_mun = row
            
            # Crear zona 01 por defecto para cada municipio
            cursor.execute("""
                INSERT OR IGNORE INTO zonas (codigo_zz, nombre, municipio_id, codigo_completo)
                VALUES ('01', ?, ?, ?)
            """, (f'Zona Urbana {nombre_mun}', municipio_id, f'{codigo_mun}01'))
            
            print(f"   ✅ Zona 01 creada para {nombre_mun}")
        
        # 5. Asignar zonas a puestos existentes
        print("\n📝 5. Asignando zonas a puestos existentes...")
        
        cursor.execute("""
            SELECT p.id, p.municipio_id, z.id as zona_id
            FROM puestos_votacion p
            JOIN zonas z ON p.municipio_id = z.municipio_id AND z.codigo_zz = '01'
            WHERE p.zona_id IS NULL
        """)
        
        for row in cursor.fetchall():
            puesto_id, municipio_id, zona_id = row
            cursor.execute("UPDATE puestos_votacion SET zona_id = ? WHERE id = ?", (zona_id, puesto_id))
        
        print("   ✅ Puestos asignados a zonas")
        
        # 6. Generar códigos DIVIPOLA para puestos
        print("\n📝 6. Generando códigos DIVIPOLA para puestos...")
        
        cursor.execute("""
            SELECT p.id, m.codigo_dd, m.codigo_mm, z.codigo_zz, p.codigo
            FROM puestos_votacion p
            JOIN municipios m ON p.municipio_id = m.id
            JOIN zonas z ON p.zona_id = z.id
        """)
        
        puesto_counter = {}
        for row in cursor.fetchall():
            puesto_id, dd, mm, zz, codigo_actual = row
            
            # Generar código pp secuencial por zona
            key = f"{dd}{mm}{zz}"
            if key not in puesto_counter:
                puesto_counter[key] = 1
            else:
                puesto_counter[key] += 1
            
            pp = f"{puesto_counter[key]:02d}"
            codigo_divipola = f"{dd}{mm}{zz}{pp}"
            
            cursor.execute("""
                UPDATE puestos_votacion 
                SET codigo_pp = ?, codigo_divipola = ?
                WHERE id = ?
            """, (pp, codigo_divipola, puesto_id))
            
            print(f"   ✅ Puesto {puesto_id}: {codigo_divipola} (dd:{dd} mm:{mm} zz:{zz} pp:{pp})")
        
        # 7. Crear índices
        print("\n📝 7. Creando índices...")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_zonas_municipio ON zonas(municipio_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_puestos_zona ON puestos_votacion(zona_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_puestos_divipola ON puestos_votacion(codigo_divipola)")
        
        print("   ✅ Índices creados")
        
        # Commit cambios
        conn.commit()
        
        # Verificar resultado
        print("\n" + "="*80)
        print("VERIFICACIÓN DE RESULTADOS")
        print("="*80)
        
        cursor.execute("SELECT COUNT(*) FROM zonas")
        print(f"\n✅ Zonas creadas: {cursor.fetchone()[0]}")
        
        cursor.execute("""
            SELECT p.id, p.nombre, p.codigo_divipola, m.nombre as municipio
            FROM puestos_votacion p
            JOIN municipios m ON p.municipio_id = m.id
            ORDER BY p.codigo_divipola
        """)
        
        print("\n📍 Puestos con códigos DIVIPOLA:")
        for row in cursor.fetchall():
            print(f"  {row[2]}: {row[1]} ({row[3]})")
        
        print("\n" + "="*80)
        print("✅ Estructura DIVIPOLA agregada exitosamente")
        print(f"📁 Backup guardado en: {backup_file}")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        print(f"⚠️  Restaurar desde backup: {backup_file}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("⚠️  ADVERTENCIA: Este script modificará la estructura de la base de datos")
    print("   Se creará un backup automáticamente")
    
    response = input("\n¿Deseas continuar? (s/n): ")
    
    if response.lower() == 's':
        add_divipola_structure()
    else:
        print("❌ Operación cancelada")
