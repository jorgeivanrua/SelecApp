"""
Script para probar la generación automática de usuarios
"""

from initialization_service import InitializationService

def main():
    print("=== Prueba de Generación Automática de Usuarios ===")
    
    service = InitializationService()
    
    # Generar usuarios automáticamente
    print("Generando usuarios automáticamente...")
    result = service.generate_users_automatically()
    
    if result['success']:
        print(f"✓ Generación exitosa:")
        print(f"  - Coordinadores departamentales: {result['coordinadores_departamento']}")
        print(f"  - Coordinadores municipales: {result['coordinadores_municipales']}")
        print(f"  - Coordinadores de puesto: {result['coordinadores_puesto']}")
        print(f"  - Testigos de mesa: {result['testigos_mesa']}")
        print(f"  - Total usuarios creados: {result['total_users_created']}")
        
        if result['errors']:
            print(f"  - Errores: {len(result['errors'])}")
            for error in result['errors'][:10]:
                print(f"    • {error}")
    else:
        print("✗ Error en la generación")
        for error in result['errors']:
            print(f"  • {error}")

if __name__ == "__main__":
    main()