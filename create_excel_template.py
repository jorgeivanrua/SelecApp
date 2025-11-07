#!/usr/bin/env python3
"""
Crear plantilla de Excel para importación de datos electorales
"""

import pandas as pd
from datetime import datetime

def create_excel_template():
    """Crear archivo Excel con plantillas de ejemplo"""
    
    print("🔄 Creando plantilla de Excel...")
    
    # Datos de ejemplo para Partidos
    partidos_data = {
        'nombre': [
            'Partido Liberal Colombiano',
            'Partido Conservador Colombiano', 
            'Centro Democrático',
            'Cambio Radical',
            'Alianza Verde'
        ],
        'sigla': ['PLC', 'PCC', 'CD', 'CR', 'AV'],
        'color_principal': ['#FF0000', '#0000FF', '#FF8C00', '#FFD700', '#00FF00']
    }
    
    # Datos de ejemplo para Tipos de Elección
    tipos_eleccion_data = {
        'nombre': [
            'Alcalde Municipal',
            'Concejal Municipal',
            'Gobernador Departamental',
            'Diputado Departamental',
            'Senador'
        ],
        'descripcion': [
            'Alcalde del municipio',
            'Miembro del Concejo Municipal',
            'Gobernador del Departamento',
            'Miembro de la Asamblea Departamental',
            'Miembro del Senado de la República'
        ],
        'nivel': ['municipal', 'municipal', 'departamental', 'departamental', 'nacional']
    }
    
    # Datos de ejemplo para Coaliciones
    coaliciones_data = {
        'nombre': [
            'Coalición Centro Derecha',
            'Alianza Progresista'
        ],
        'descripcion': [
            'Coalición de partidos de centro derecha',
            'Alianza de partidos progresistas'
        ],
        'partidos_siglas': [
            'PCC, CD',
            'PLC, AV'
        ]
    }
    
    # Datos de ejemplo para Candidatos
    candidatos_data = {
        'cedula': ['12345678', '87654321', '11223344', '44332211', '55667788'],
        'nombre_completo': [
            'Juan Carlos Pérez García',
            'María Elena Rodríguez López',
            'Carlos Alberto Martínez Silva',
            'Ana Lucía González Herrera',
            'Luis Fernando Castro Morales'
        ],
        'partido_sigla': ['PLC', 'PCC', 'CD', 'AV', 'CR'],
        'cargo_nombre': [
            'Alcalde Municipal',
            'Concejal Municipal', 
            'Alcalde Municipal',
            'Concejal Municipal',
            'Concejal Municipal'
        ],
        'municipio_nombre': ['Florencia', 'Florencia', 'San Vicente del Caguán', 'Florencia', 'Florencia'],
        'telefono': ['3001234567', '3009876543', '3005555555', '3007777777', '3008888888'],
        'email': [
            'juan.perez@email.com',
            'maria.rodriguez@email.com',
            'carlos.martinez@email.com',
            'ana.gonzalez@email.com',
            'luis.castro@email.com'
        ],
        'numero_lista': [1, 1, 1, 2, 3]
    }
    
    # Crear DataFrames
    df_partidos = pd.DataFrame(partidos_data)
    df_tipos_eleccion = pd.DataFrame(tipos_eleccion_data)
    df_coaliciones = pd.DataFrame(coaliciones_data)
    df_candidatos = pd.DataFrame(candidatos_data)
    
    # Crear archivo Excel con múltiples hojas
    filename = 'plantilla_datos_electorales.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Escribir cada hoja
        df_partidos.to_excel(writer, sheet_name='Partidos', index=False)
        df_tipos_eleccion.to_excel(writer, sheet_name='TiposEleccion', index=False)
        df_coaliciones.to_excel(writer, sheet_name='Coaliciones', index=False)
        df_candidatos.to_excel(writer, sheet_name='Candidatos', index=False)
        
        # Crear hoja de instrucciones
        instrucciones = pd.DataFrame({
            'INSTRUCCIONES DE USO': [
                '1. Este archivo contiene 4 hojas con datos de ejemplo',
                '2. PARTIDOS: Contiene los partidos políticos con nombre, sigla y color',
                '3. TIPOSELECCION: Contiene los cargos electorales disponibles',
                '4. COALICIONES: Contiene coaliciones entre partidos (opcional)',
                '5. CANDIDATOS: Contiene los candidatos con sus datos básicos',
                '',
                'ORDEN DE IMPORTACIÓN:',
                '1. Primero se importan los PARTIDOS',
                '2. Luego los TIPOS DE ELECCIÓN',
                '3. Después las COALICIONES (opcional)',
                '4. Finalmente los CANDIDATOS',
                '',
                'COLUMNAS REQUERIDAS:',
                'Partidos: nombre, sigla',
                'TiposEleccion: nombre, nivel',
                'Coaliciones: nombre, partidos_siglas',
                'Candidatos: cedula, nombre_completo, partido_sigla, cargo_nombre',
                '',
                'NOTAS IMPORTANTES:',
                '- Las siglas de partidos deben coincidir exactamente',
                '- Los nombres de cargos deben coincidir exactamente',
                '- Las cédulas deben ser únicas',
                '- El nivel puede ser: municipal, departamental, nacional',
                '- En coaliciones, separar siglas con comas: "PLC, PCC"'
            ]
        })
        
        instrucciones.to_excel(writer, sheet_name='INSTRUCCIONES', index=False)
    
    print(f"✅ Plantilla creada: {filename}")
    print("\n📋 Estructura del archivo:")
    print("  - Hoja 'Partidos': Partidos políticos")
    print("  - Hoja 'TiposEleccion': Cargos electorales")
    print("  - Hoja 'Coaliciones': Coaliciones entre partidos")
    print("  - Hoja 'Candidatos': Candidatos con datos básicos")
    print("  - Hoja 'INSTRUCCIONES': Guía de uso")
    
    return filename

if __name__ == "__main__":
    try:
        filename = create_excel_template()
        print(f"\n🎉 Plantilla Excel creada exitosamente: {filename}")
        print("\n💡 Para usar la plantilla:")
        print("1. Modifica los datos de ejemplo con tus datos reales")
        print("2. Mantén la estructura de columnas")
        print("3. Usa la API /api/admin/import/excel/complete para importar")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()