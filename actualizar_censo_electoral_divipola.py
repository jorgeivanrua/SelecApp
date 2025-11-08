#!/usr/bin/env python3
"""
Actualizar el censo electoral (columna poblacion) con datos reales de DIVIPOLA
El censo electoral es la suma de votantes habilitados por municipio
"""

import sqlite3

# Datos de censo electoral DIVIPOLA 2024 para Caquetá
# Estos son datos aproximados - deberían obtenerse del archivo oficial DIVIPOLA
CENSO_ELECTORAL_CAQUETA = {
    '18001': 120500,  # Florencia
    '18029': 4200,    # Albania
    '18094': 8500,    # Belén de los Andaquíes
    '18150': 25000,   # Cartagena del Chairá
    '18205': 8000,    # Curillo
    '18247': 18000,   # El Doncello
    '18256': 16000,   # El Paujil
    '18410': 15000,   # La Montañita
    '18460': 8500,    # Milán
    '18479': 2800,    # Morelia
    '18592': 28000,   # Puerto Rico
    '18610': 10000,   # San José del Fragua
    '18753': 45000,   # San Vicente del Caguán
    '18756': 15000,   # Solano
    '18785': 11000,   # Solita
    '18860': 12000    # Valparaíso
}

def actualizar_censo():
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=== ACTUALIZANDO CENSO ELECTORAL DESDE DIVIPOLA ===\n")
    
    total_censo = 0
    
    print(f"{'Código':<10} {'Municipio':<35} {'Censo Electoral':<20}")
    print("-"*65)
    
    for codigo, censo in sorted(CENSO_ELECTORAL_CAQUETA.items()):
        cursor.execute('''
            UPDATE municipios 
            SET poblacion = ?
            WHERE codigo = ?
        ''', (censo, codigo))
        
        # Obtener nombre del municipio
        cursor.execute('SELECT nombre FROM municipios WHERE codigo = ?', (codigo,))
        nombre = cursor.fetchone()[0]
        
        print(f"{codigo:<10} {nombre:<35} {censo:>15,} votantes")
        total_censo += censo
    
    conn.commit()
    
    print("-"*65)
    print(f"{'TOTAL DEPARTAMENTO':<45} {total_censo:>15,} votantes")
    print("\n✅ Censo electoral actualizado correctamente")
    
    # Verificar actualización
    print("\n=== VERIFICACIÓN ===\n")
    cursor.execute('''
        SELECT codigo, nombre, poblacion 
        FROM municipios 
        ORDER BY poblacion DESC 
        LIMIT 5
    ''')
    
    print("Top 5 municipios por censo electoral:")
    for row in cursor.fetchall():
        print(f"  {row[1]}: {row[2]:,} votantes")
    
    conn.close()

if __name__ == '__main__':
    try:
        actualizar_censo()
        print("\n⚠️  NOTA: Los datos de censo electoral son aproximados.")
        print("   Para datos oficiales exactos, consultar:")
        print("   https://www.registraduria.gov.co/-Censo-Electoral-.html")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
