#!/usr/bin/env python3
"""
Agregar puestos de votación y mesas para TODOS los municipios del Caquetá
"""

import sqlite3

def agregar_puestos_y_mesas():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=== AGREGANDO PUESTOS Y MESAS PARA TODOS LOS MUNICIPIOS ===\n")
    
    # Obtener todos los municipios con sus zonas
    cursor.execute('''
        SELECT m.id, m.nombre, m.poblacion
        FROM municipios m
        ORDER BY m.nombre
    ''')
    
    municipios = cursor.fetchall()
    
    total_puestos = 0
    total_mesas = 0
    
    for mun_id, mun_nombre, poblacion in municipios:
        print(f"\n📍 {mun_nombre} (Población: {poblacion:,})")
        
        # Obtener zonas del municipio
        cursor.execute('''
            SELECT id, nombre, tipo_zona
            FROM zonas
            WHERE municipio_id = ?
            ORDER BY codigo_zz
        ''', (mun_id,))
        
        zonas = cursor.fetchall()
        
        # Determinar número de puestos según población
        if poblacion > 100000:
            puestos_por_zona = [3, 2, 1, 1, 1, 1]  # Municipios grandes
        elif poblacion > 50000:
            puestos_por_zona = [2, 2, 1, 1, 1, 1]  # Municipios medianos-grandes
        elif poblacion > 20000:
            puestos_por_zona = [2, 1, 1, 1]  # Municipios medianos
        else:
            puestos_por_zona = [1, 1, 1]  # Municipios pequeños
        
        puestos_creados = 0
        mesas_creadas = 0
        
        for idx, (zona_id, zona_nombre, tipo_zona) in enumerate(zonas):
            num_puestos = puestos_por_zona[idx] if idx < len(puestos_por_zona) else 1
            
            for p in range(1, num_puestos + 1):
                # Nombres de puestos según el tipo de zona
                if tipo_zona == 'urbana':
                    nombres_puestos = [
                        f"Institución Educativa {mun_nombre} {p}",
                        f"Colegio Nacional {mun_nombre}",
                        f"Escuela Central {mun_nombre}"
                    ]
                elif tipo_zona == 'rural':
                    nombres_puestos = [
                        f"Escuela Rural {zona_nombre}",
                        f"Centro Comunitario {zona_nombre}",
                        f"Puesto Rural {mun_nombre} {p}"
                    ]
                elif tipo_zona == 'carcel':
                    nombres_puestos = [f"Centro Penitenciario {mun_nombre}"]
                elif tipo_zona == 'censo':
                    nombres_puestos = [f"Puesto de Censo {mun_nombre}"]
                else:
                    nombres_puestos = [f"Puesto de Votación {mun_nombre} {p}"]
                
                nombre_puesto = nombres_puestos[min(p-1, len(nombres_puestos)-1)]
                direccion = f"Zona {zona_nombre}, {mun_nombre}"
                
                # Insertar puesto
                cursor.execute('''
                    INSERT INTO puestos_votacion (nombre, direccion, municipio_id, zona_id, activo)
                    VALUES (?, ?, ?, ?, 1)
                ''', (nombre_puesto, direccion, mun_id, zona_id))
                
                puesto_id = cursor.lastrowid
                puestos_creados += 1
                
                # Determinar número de mesas por puesto
                if poblacion > 100000:
                    num_mesas = 8
                elif poblacion > 50000:
                    num_mesas = 6
                elif poblacion > 20000:
                    num_mesas = 4
                else:
                    num_mesas = 3
                
                # Crear mesas para este puesto
                for m in range(1, num_mesas + 1):
                    numero_mesa = f"{m:03d}"
                    votantes = 300 + (m * 20)  # Variar votantes por mesa
                    
                    cursor.execute('''
                        INSERT INTO mesas_votacion (numero, puesto_id, municipio_id, votantes_habilitados, activa)
                        VALUES (?, ?, ?, ?, 1)
                    ''', (numero_mesa, puesto_id, mun_id, votantes))
                    
                    mesas_creadas += 1
        
        print(f"  ✅ {puestos_creados} puestos creados")
        print(f"  ✅ {mesas_creadas} mesas creadas")
        
        total_puestos += puestos_creados
        total_mesas += mesas_creadas
    
    # Commit cambios
    conn.commit()
    
    print("\n" + "="*60)
    print(f"✅ TOTAL: {total_puestos} puestos y {total_mesas} mesas creados")
    print("="*60)
    
    # Verificar resultado final
    print("\n=== RESUMEN POR MUNICIPIO ===\n")
    cursor.execute('''
        SELECT m.nombre, 
               COUNT(DISTINCT p.id) as num_puestos, 
               COUNT(mv.id) as num_mesas
        FROM municipios m
        LEFT JOIN puestos_votacion p ON m.id = p.municipio_id
        LEFT JOIN mesas_votacion mv ON p.id = mv.puesto_id
        GROUP BY m.id, m.nombre
        ORDER BY m.nombre
    ''')
    
    print(f"{'Municipio':<35} {'Puestos':<10} {'Mesas':<10}")
    print("-"*55)
    for row in cursor.fetchall():
        print(f"{row[0]:<35} {row[1]:<10} {row[2]:<10}")
    
    conn.close()

if __name__ == '__main__':
    try:
        agregar_puestos_y_mesas()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
