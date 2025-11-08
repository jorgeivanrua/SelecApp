#!/usr/bin/env python3
"""
Corregir nombres de municipios en la BD para que coincidan con DIVIPOLA
"""

import sqlite3

def corregir_nombres():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("CORRECCIÓN DE NOMBRES DE MUNICIPIOS")
    print("=" * 80)
    
    # Mapeo de nombres incorrectos a correctos (según DIVIPOLA)
    correcciones = {
        'Belén de los Andaquíes': 'BELEN DE LOS ANDAQUIES',
        'Cartagena del Chairá': 'CARTAGENA DEL CHAIRA',
        'Milán': 'MILAN',
        'San José del Fragua': 'SAN JOSE DEL FRAGUA',
        'San Vicente del Caguán': 'SAN VICENTE DEL CAGUAN',
        'Valparaíso': 'VALPARAISO'
    }
    
    for nombre_actual, nombre_correcto in correcciones.items():
        cursor.execute('''
            UPDATE municipios
            SET nombre = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE nombre = ?
        ''', (nombre_correcto.title(), nombre_actual))
        
        if cursor.rowcount > 0:
            print(f"✅ {nombre_actual:30} -> {nombre_correcto.title()}")
        else:
            print(f"⚠️  {nombre_actual:30} no encontrado")
    
    conn.commit()
    
    print("\n" + "=" * 80)
    print("CORRECCIÓN COMPLETADA")
    print("=" * 80)
    
    # Verificar
    print("\nMunicipios actualizados:")
    cursor.execute('SELECT nombre FROM municipios WHERE activo = 1 ORDER BY nombre')
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    
    conn.close()

if __name__ == '__main__':
    corregir_nombres()
