#!/usr/bin/env python3
"""
Test del servicio de importación Excel
"""

from services.excel_import_service import ExcelImportService
import json

def test_excel_import():
    """Probar importación desde Excel"""
    
    print("🔄 Probando servicio de importación Excel...")
    
    # Crear instancia del servicio
    service = ExcelImportService()
    
    # Archivo de plantilla
    excel_file = 'plantilla_datos_electorales.xlsx'
    
    print(f"\n📋 Validando estructura del archivo: {excel_file}")
    
    # Validar estructura
    validation = service.validate_excel_structure(excel_file)
    print("Resultado de validación:")
    print(json.dumps(validation, indent=2, ensure_ascii=False))
    
    if validation['valid']:
        print("\n✅ Archivo válido, procediendo con importación...")
        
        # Importar todos los datos
        results = service.import_all_from_excel(excel_file)
        
        print("\n📊 Resultados de importación:")
        print(f"Total procesado: {results['total_processed']}")
        print(f"Total errores: {results['total_errors']}")
        
        # Mostrar detalles por categoría
        if results['parties']:
            print(f"\n🏛️ Partidos: {results['parties']['processed']} procesados")
            if results['parties']['parties_created']:
                for party in results['parties']['parties_created'][:3]:
                    print(f"  - {party['nombre']} ({party['sigla']})")
        
        if results['election_types']:
            print(f"\n🗳️ Tipos de elección: {results['election_types']['processed']} procesados")
            if results['election_types']['election_types_created']:
                for election_type in results['election_types']['election_types_created'][:3]:
                    print(f"  - {election_type['nombre']} ({election_type['nivel']})")
        
        if results['coalitions']:
            print(f"\n🤝 Coaliciones: {results['coalitions']['processed']} procesados")
            if results['coalitions']['coalitions_created']:
                for coalition in results['coalitions']['coalitions_created'][:3]:
                    print(f"  - {coalition['nombre']} ({coalition['partidos_count']} partidos)")
        
        if results['candidates']:
            print(f"\n👥 Candidatos: {results['candidates']['processed']} procesados")
            if results['candidates']['candidates_created']:
                for candidate in results['candidates']['candidates_created'][:3]:
                    print(f"  - {candidate['nombre']} ({candidate['partido']}) - {candidate['cargo']}")
        
        # Mostrar errores si los hay
        for category, data in results.items():
            if isinstance(data, dict) and data.get('errors'):
                print(f"\n❌ Errores en {category}:")
                for error in data['errors'][:3]:
                    print(f"  - {error}")
        
        print("\n✅ Importación completada!")
    
    else:
        print("\n❌ Archivo no válido:")
        for error in validation['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    test_excel_import()