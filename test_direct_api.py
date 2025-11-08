#!/usr/bin/env python3
import sqlite3
from flask import jsonify

def test_zonas():
    municipio_id = 7
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, codigo_zz, nombre, descripcion, tipo_zona
        FROM zonas
        WHERE municipio_id = ? AND activo = 1
        ORDER BY codigo_zz
    ''', (municipio_id,))
    
    zonas = []
    for row in cursor.fetchall():
        print(f"Row: {row}")
        print(f"Row[0]: {row[0]}, Row[1]: {row[1]}, Row[2]: {row[2]}, Row[3]: {row[3]}, Row[4]: {row[4]}")
        zona_dict = {
            'id': row[0],
            'codigo': row[1],
            'nombre': row[2],
            'descripcion': row[3] or '',
            'tipo': row[4] or ''
        }
        print(f"Zona dict: {zona_dict}")
        zonas.append(zona_dict)
    
    conn.close()
    
    print(f"\nTotal zonas: {len(zonas)}")
    print(f"Primera zona: {zonas[0]}")
    return zonas

if __name__ == '__main__':
    test_zonas()
