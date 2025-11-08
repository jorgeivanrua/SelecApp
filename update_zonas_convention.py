#!/usr/bin/env python3
"""
Script para actualizar las zonas según la convención oficial DIVIPOLA
zz: 01-89 = Zonas urbanas
zz: 90 = Puesto censo
zz: 98 = Cárceles
zz: 99 = Zona rural
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

def update_zonas_convention():
    """Actualizar zonas según convención oficial"""
    
    backup_file = backup_database()
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("ACTUALIZANDO ZONAS SEGÚN CONVENCIÓN DIVIPOLA")
    print("="*80)
    print("\nConvención oficial:")
    print("  01-89: Zonas urbanas")
    print("  90:    Puesto censo")
    print("  98:    Cárceles")
    print("  99:    Zona rural")
    
    try:
        # 1. Agregar columna tipo_zona
        print("\n📝 1. Agregando columna tipo_zona...")
        
        cursor.execute("PRAGMA table_info(zonas)")
        columns = {col[1] for col in cursor.fetchall()}
        
        if 'tipo_zona' not in columns:
            cursor.execute("ALTER TABLE zonas ADD COLUMN tipo_zona TEXT")
            print("   ✅ Columna tipo_zona agregada")
        
        # 2. Actualizar zona existente
        print("\n📝 2. Actualizando zona existente...")
        
        cursor.execute("UPDATE zonas SET tipo_zona = 'urbana' WHERE codigo_zz = '01'")
        print("   ✅ Zona 01 marcada como 'urbana'")
        
        # 3. Crear zonas especiales para cada municipio
        print("\n📝 3. Creando zonas especiales...")
        
        cursor.execute("SELECT id, codigo, nombre, codigo_dd, codigo_mm FROM municipios WHERE activo = 1")
        municipios = cursor.fetchall()
        
        for mun in municipios:
            mun_id, codigo, nombre, dd, mm = mun
            
            # Zona 99: Rural
            cursor.execute("""
                INSERT OR IGNORE INTO zonas (codigo_zz, nombre, municipio_id, codigo_completo, tipo_zona)
                VALUES ('99', ?, ?, ?, 'rural')
            """, (f'Zona Rural {nombre}', mun_id, f'{codigo}99', ))
            
            # Zona 90: Puesto censo
            cursor.execute("""
                INSERT OR IGNORE INTO zonas (codigo_zz, nombre, municipio_id, codigo_completo, tipo_zona)
                VALUES ('90', ?, ?, ?, 'censo')
            """, (f'Puesto Censo {nombre}', mun_id, f'{codigo}90', ))
            
            # Zona 98: Cárceles
            cursor.execute("""
                INSERT OR IGNORE INTO zonas (codigo_zz, nombre, municipio_id, codigo_completo, tipo_zona)
                VALUES ('98', ?, ?, ?, 'carcel')
            """, (f'Cárceles {nombre}', mun_id, f'{codigo}98', ))
            
            print(f"   ✅ Zonas especiales creadas para {nombre}")
        
        # 4. Crear constraint para validar códigos
        print("\n📝 4. Documentando convención...")
        
        # Crear tabla de referencia para tipos de zona
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tipos_zona (
                codigo_zz TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                rango_inicio INTEGER,
                rango_fin INTEGER
            )
        """)
        
        # Insertar convención
        cursor.execute("DELETE FROM tipos_zona")  # Limpiar primero
        
        tipos = [
            ('01-89', 'urbana', 'Zonas urbanas numeradas secuencialmente', 1, 89),
            ('90', 'censo', 'Puesto censo', 90, 90),
            ('98', 'carcel', 'Establecimientos carcelarios', 98, 98),
            ('99', 'rural', 'Zona rural', 99, 99)
        ]
        
        cursor.executemany("""
            INSERT INTO tipos_zona (codigo_zz, tipo, descripcion, rango_inicio, rango_fin)
            VALUES (?, ?, ?, ?, ?)
        """, tipos)
        
        print("   ✅ Tabla tipos_zona creada con convención oficial")
        
        # Commit cambios
        conn.commit()
        
        # Verificar resultado
        print("\n" + "="*80)
        print("VERIFICACIÓN DE RESULTADOS")
        print("="*80)
        
        cursor.execute("""
            SELECT z.codigo_zz, z.tipo_zona, z.nombre, m.nombre as municipio
            FROM zonas z
            JOIN municipios m ON z.municipio_id = m.id
            ORDER BY m.nombre, z.codigo_zz
        """)
        
        print("\n📍 Zonas creadas por municipio:")
        current_mun = None
        for row in cursor.fetchall():
            codigo_zz, tipo, nombre, municipio = row
            if municipio != current_mun:
                print(f"\n  {municipio}:")
                current_mun = municipio
            print(f"    {codigo_zz} ({tipo:8}) - {nombre}")
        
        cursor.execute("SELECT COUNT(*) FROM zonas")
        total_zonas = cursor.fetchone()[0]
        
        print(f"\n✅ Total de zonas: {total_zonas}")
        
        # Mostrar convención
        print("\n📋 Convención DIVIPOLA:")
        cursor.execute("SELECT * FROM tipos_zona ORDER BY rango_inicio")
        for row in cursor.fetchall():
            print(f"  {row[0]:<8} {row[1]:<10} {row[2]}")
        
        print("\n" + "="*80)
        print("✅ Zonas actualizadas según convención DIVIPOLA")
        print(f"📁 Backup guardado en: {backup_file}")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        print(f"⚠️  Restaurar desde backup: {backup_file}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("⚠️  ADVERTENCIA: Este script modificará las zonas en la base de datos")
    print("   Se creará un backup automáticamente")
    
    response = input("\n¿Deseas continuar? (s/n): ")
    
    if response.lower() == 's':
        update_zonas_convention()
    else:
        print("❌ Operación cancelada")
