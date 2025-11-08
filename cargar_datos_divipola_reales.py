#!/usr/bin/env python3
"""
Script para cargar datos reales de DIVIPOLA del departamento de Caquetá
Incluye los 16 municipios oficiales con sus códigos DANE
"""

import sqlite3

def cargar_datos_reales():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=== CARGANDO DATOS REALES DE DIVIPOLA - CAQUETÁ ===\n")
    
    # Limpiar datos existentes
    print("🗑️  Limpiando datos existentes...")
    cursor.execute('DELETE FROM mesas_votacion')
    cursor.execute('DELETE FROM puestos_votacion')
    cursor.execute('DELETE FROM zonas')
    cursor.execute('DELETE FROM municipios')
    
    # Datos reales de los 16 municipios del Caquetá según DIVIPOLA
    municipios_caqueta = [
        # (codigo_dane, nombre, poblacion_aprox)
        ('18001', 'Florencia', 185000),
        ('18029', 'Albania', 6000),
        ('18094', 'Belén de los Andaquíes', 12000),
        ('18150', 'Cartagena del Chairá', 35000),
        ('18205', 'Curillo', 12000),
        ('18247', 'El Doncello', 25000),
        ('18256', 'El Paujil', 22000),
        ('18410', 'La Montañita', 22000),
        ('18460', 'Milán', 12000),
        ('18479', 'Morelia', 4000),
        ('18592', 'Puerto Rico', 38000),
        ('18610', 'San José del Fragua', 14000),
        ('18753', 'San Vicente del Caguán', 65000),
        ('18756', 'Solano', 22000),
        ('18785', 'Solita', 15000),
        ('18860', 'Valparaíso', 16000)
    ]
    
    print(f"📍 Insertando {len(municipios_caqueta)} municipios del Caquetá...\n")
    
    municipios_ids = {}
    
    for codigo, nombre, poblacion in municipios_caqueta:
        # Extraer código departamento (18) y código municipio
        codigo_dd = codigo[:2]  # 18
        codigo_mm = codigo[2:]  # 001, 029, etc.
        
        cursor.execute('''
            INSERT INTO municipios (codigo, nombre, departamento, poblacion, codigo_dd, codigo_mm, activo)
            VALUES (?, ?, 'Caquetá', ?, ?, ?, 1)
        ''', (codigo, nombre, poblacion, codigo_dd, codigo_mm))
        
        mun_id = cursor.lastrowid
        municipios_ids[nombre] = mun_id
        print(f"  ✅ {nombre} (Código: {codigo}) - ID: {mun_id}")
    
    print(f"\n✅ {len(municipios_caqueta)} municipios insertados\n")
    
    # Crear zonas para cada municipio
    print("📍 Creando zonas para cada municipio...\n")
    
    zonas_creadas = 0
    for nombre, mun_id in municipios_ids.items():
        # Determinar número de zonas según tamaño del municipio
        poblacion = next(p for c, n, p in municipios_caqueta if n == nombre)
        
        if poblacion > 50000:  # Municipios grandes
            num_zonas = 6
        elif poblacion > 20000:  # Municipios medianos
            num_zonas = 4
        else:  # Municipios pequeños
            num_zonas = 3
        
        for i in range(1, num_zonas + 1):
            codigo_zona = f"{i:02d}"
            nombre_zona = f"Zona {codigo_zona}"
            
            # Determinar tipo de zona
            if i == 1 and poblacion > 20000:
                tipo = 'urbana'
                desc = 'Zona Urbana'
            elif i == num_zonas - 1:
                tipo = 'carcel'
                desc = 'Cárceles'
            elif i == num_zonas:
                tipo = 'censo'
                desc = 'Puesto de Censo'
            else:
                tipo = 'rural'
                desc = f'Zona Rural {i-1}'
            
            cursor.execute('''
                INSERT INTO zonas (codigo_zz, nombre, municipio_id, descripcion, tipo_zona, activo)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (codigo_zona, nombre_zona, mun_id, desc, tipo))
            
            zonas_creadas += 1
    
    print(f"✅ {zonas_creadas} zonas creadas\n")
    
    # Crear puestos de votación de ejemplo para Florencia
    print("📍 Creando puestos de votación de ejemplo en Florencia...\n")
    
    florencia_id = municipios_ids['Florencia']
    
    # Obtener zonas de Florencia
    cursor.execute('SELECT id, nombre FROM zonas WHERE municipio_id = ? ORDER BY codigo_zz', (florencia_id,))
    zonas_florencia = cursor.fetchall()
    
    puestos_ejemplo = [
        ('Colegio Nacional', 'Calle 15 # 10-25', zonas_florencia[0][0]),
        ('Institución Educativa La Salle', 'Carrera 11 # 8-45', zonas_florencia[0][0]),
        ('Colegio Sagrado Corazón', 'Calle 12 # 14-30', zonas_florencia[0][0]),
        ('Escuela Normal Superior', 'Carrera 9 # 16-20', zonas_florencia[1][0]),
        ('Colegio Técnico Industrial', 'Calle 18 # 7-15', zonas_florencia[1][0]),
    ]
    
    puestos_ids = []
    for nombre, direccion, zona_id in puestos_ejemplo:
        cursor.execute('''
            INSERT INTO puestos_votacion (nombre, direccion, municipio_id, zona_id, activo)
            VALUES (?, ?, ?, ?, 1)
        ''', (nombre, direccion, florencia_id, zona_id))
        
        puesto_id = cursor.lastrowid
        puestos_ids.append(puesto_id)
        print(f"  ✅ {nombre}")
    
    print(f"\n✅ {len(puestos_ejemplo)} puestos de votación creados\n")
    
    # Crear mesas de votación de ejemplo
    print("📍 Creando mesas de votación de ejemplo...\n")
    
    mesas_creadas = 0
    for puesto_id in puestos_ids:
        # Crear 5 mesas por puesto
        for i in range(1, 6):
            numero_mesa = f"{i:03d}"
            votantes = 350 + (i * 10)  # Variar votantes por mesa
            
            cursor.execute('''
                INSERT INTO mesas_votacion (numero, puesto_id, municipio_id, votantes_habilitados, activa)
                VALUES (?, ?, ?, ?, 1)
            ''', (numero_mesa, puesto_id, florencia_id, votantes))
            
            mesas_creadas += 1
    
    print(f"✅ {mesas_creadas} mesas de votación creadas\n")
    
    # Commit cambios
    conn.commit()
    
    print("="*60)
    print("✅ DATOS REALES DE DIVIPOLA CARGADOS EXITOSAMENTE")
    print("="*60)
    
    # Mostrar resumen
    print("\n=== RESUMEN ===\n")
    
    cursor.execute('SELECT COUNT(*) FROM municipios')
    print(f"📍 Municipios: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM zonas')
    print(f"📍 Zonas: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM puestos_votacion')
    print(f"📍 Puestos de Votación: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM mesas_votacion')
    print(f"📍 Mesas de Votación: {cursor.fetchone()[0]}")
    
    # Mostrar algunos municipios
    print("\n=== MUNICIPIOS DEL CAQUETÁ ===\n")
    cursor.execute('SELECT codigo, nombre, poblacion FROM municipios ORDER BY nombre LIMIT 10')
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]} ({row[2]:,} habitantes)")
    
    conn.close()

if __name__ == '__main__':
    try:
        cargar_datos_reales()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
