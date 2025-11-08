#!/usr/bin/env python3
"""
Agregar puestos de votación de La Montañita desde DIVIPOLA
"""

import sqlite3
from datetime import datetime

def agregar_puestos_la_montanita():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    # Obtener ID de La Montañita
    cursor.execute("SELECT id, codigo FROM municipios WHERE nombre = 'La Montañita' AND activo = 1")
    municipio = cursor.fetchone()
    
    if not municipio:
        print("❌ No se encontró el municipio La Montañita")
        conn.close()
        return
    
    municipio_id = municipio[0]
    codigo_mun = municipio[1]
    
    print(f"Municipio: La Montañita (ID: {municipio_id}, Código: {codigo_mun})")
    
    # Obtener zonas de La Montañita
    cursor.execute("""
        SELECT id, codigo_zz, nombre 
        FROM zonas 
        WHERE municipio_id = ? AND activo = 1
        ORDER BY codigo_zz
    """, (municipio_id,))
    zonas = cursor.fetchall()
    
    print(f"\nZonas disponibles: {len(zonas)}")
    for zona in zonas:
        print(f"  Zona {zona[1]}: {zona[2]}")
    
    # Datos de puestos de La Montañita desde DIVIPOLA
    puestos_divipola = [
        {
            'nombre': 'PUESTO CABECERA MUNICIPAL',
            'direccion': 'I.E. COLSOCORRO KR 5 #4-14 BR. LAS BRISAS',
            'codigo_zz': '00',
            'codigo_pp': '00',
            'votantes': 7588,
            'mesas': 2
        },
        {
            'nombre': 'EL TRIUNFO',
            'direccion': 'I.E. JOSÉ HILARIO LÓPEZ',
            'codigo_zz': '99',
            'codigo_pp': '03',
            'votantes': 283,
            'mesas': 1
        },
        {
            'nombre': 'SANTUARIO',
            'direccion': 'I.E. SABIO CALDAS',
            'codigo_zz': '99',
            'codigo_pp': '05',
            'votantes': 999,
            'mesas': 1
        },
        {
            'nombre': 'LA UNION PENEYA',
            'direccion': 'I.E. SIMÓN BOLIVAR SEDE A KR 3 CL 7 VÍA P/PAL',
            'codigo_zz': '99',
            'codigo_pp': '45',
            'votantes': 3673,
            'mesas': 1
        },
        {
            'nombre': 'MATEGUADUA',
            'direccion': 'I.E. MATEGUADUA CALLE PRINCIPAL',
            'codigo_zz': '99',
            'codigo_pp': '50',
            'votantes': 770,
            'mesas': 1
        }
    ]
    
    print(f"\n{'='*70}")
    print("AGREGANDO PUESTOS DE LA MONTAÑITA")
    print(f"{'='*70}")
    
    for puesto_data in puestos_divipola:
        # Buscar zona correspondiente
        cursor.execute("""
            SELECT id FROM zonas 
            WHERE municipio_id = ? AND codigo_zz = ? AND activo = 1
        """, (municipio_id, puesto_data['codigo_zz']))
        zona = cursor.fetchone()
        
        if not zona:
            print(f"⚠️  No se encontró zona {puesto_data['codigo_zz']} para {puesto_data['nombre']}")
            continue
        
        zona_id = zona[0]
        
        # Generar código DIVIPOLA completo
        codigo_divipola = f"{codigo_mun}{puesto_data['codigo_zz']}{puesto_data['codigo_pp']}"
        
        # Verificar si ya existe
        cursor.execute("""
            SELECT id FROM puestos_votacion 
            WHERE codigo_divipola = ? OR (nombre = ? AND municipio_id = ?)
        """, (codigo_divipola, puesto_data['nombre'], municipio_id))
        
        if cursor.fetchone():
            print(f"  ⚠️  Puesto {puesto_data['nombre']} ya existe")
            continue
        
        # Insertar puesto
        cursor.execute("""
            INSERT INTO puestos_votacion (
                nombre, direccion, municipio_id, zona_id,
                codigo, codigo_divipola, codigo_pp,
                activo, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            puesto_data['nombre'],
            puesto_data['direccion'],
            municipio_id,
            zona_id,
            codigo_divipola,
            codigo_divipola,
            puesto_data['codigo_pp'],
            1,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        puesto_id = cursor.lastrowid
        
        # Crear mesas para el puesto
        votantes_por_mesa = puesto_data['votantes'] // puesto_data['mesas']
        resto = puesto_data['votantes'] % puesto_data['mesas']
        
        for i in range(puesto_data['mesas']):
            numero_mesa = i + 1
            votantes_mesa = votantes_por_mesa + (1 if i < resto else 0)
            
            cursor.execute("""
                INSERT INTO mesas_votacion (
                    numero, puesto_id, municipio_id, votantes_habilitados,
                    activa, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                numero_mesa,
                puesto_id,
                municipio_id,
                votantes_mesa,
                1,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
        
        print(f"  ✅ {puesto_data['nombre']} - {puesto_data['mesas']} mesas, {puesto_data['votantes']} votantes")
    
    conn.commit()
    
    # Verificar resultado
    cursor.execute("""
        SELECT COUNT(*) FROM puestos_votacion 
        WHERE municipio_id = ? AND activo = 1
    """, (municipio_id,))
    total_puestos = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM mesas_votacion m
        JOIN puestos_votacion p ON m.puesto_id = p.id
        WHERE p.municipio_id = ? AND m.activa = 1
    """, (municipio_id,))
    total_mesas = cursor.fetchone()[0]
    
    print(f"\n{'='*70}")
    print(f"✅ La Montañita ahora tiene {total_puestos} puestos y {total_mesas} mesas")
    print(f"{'='*70}")
    
    conn.close()

if __name__ == '__main__':
    agregar_puestos_la_montanita()
