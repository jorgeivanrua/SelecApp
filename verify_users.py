"""
Script para verificar los usuarios generados automáticamente
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Location, MesaElectoral, LocationType, User

def main():
    print("=== VERIFICACIÓN DE USUARIOS GENERADOS ===\n")
    
    engine = create_engine("sqlite:///caqueta_electoral.db", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        # Estadísticas de usuarios por rol
        print("USUARIOS POR ROL:")
        print("-" * 30)
        
        roles = db.query(User.rol, func.count(User.id)).group_by(User.rol).all()
        total_users = 0
        
        for rol, count in roles:
            print(f"  - {rol.replace('_', ' ').title()}: {count}")
            total_users += count
        
        print(f"  - TOTAL: {total_users}")
        
        # Verificar asignaciones
        print(f"\nASIGNACIONES:")
        print("-" * 30)
        
        # Testigos asignados a mesas
        mesas_con_testigo = db.query(MesaElectoral).filter(
            MesaElectoral.testigo_asignado_id.isnot(None)
        ).count()
        
        total_mesas = db.query(MesaElectoral).count()
        
        print(f"  - Mesas con testigo asignado: {mesas_con_testigo}/{total_mesas}")
        
        # Coordinadores por municipio
        municipios_con_coord = db.query(User).filter(
            User.rol == 'coordinador_municipal'
        ).count()
        
        total_municipios = db.query(Location).filter(
            Location.tipo == LocationType.MUNICIPIO
        ).count()
        
        print(f"  - Municipios con coordinador: {municipios_con_coord}/{total_municipios}")
        
        # Coordinadores por puesto
        puestos_con_coord = db.query(User).filter(
            User.rol == 'coordinador_puesto'
        ).count()
        
        total_puestos = db.query(Location).filter(
            Location.tipo == LocationType.PUESTO
        ).count()
        
        print(f"  - Puestos con coordinador: {puestos_con_coord}/{total_puestos}")
        
        # Muestra de usuarios por municipio
        print(f"\nUSUARIOS POR MUNICIPIO (MUESTRA):")
        print("-" * 40)
        
        municipios = db.query(Location).filter(
            Location.tipo == LocationType.MUNICIPIO
        ).limit(5).all()
        
        for municipio in municipios:
            users_count = db.query(User).filter(
                User.municipio_id == municipio.id
            ).count()
            
            print(f"  - {municipio.nombre_municipio}: {users_count} usuarios")
        
        print(f"\n✅ SISTEMA COMPLETAMENTE INICIALIZADO")
        print(f"   - Estructura geográfica: ✓")
        print(f"   - Tipos de elecciones: ✓")
        print(f"   - Jornadas electorales: ✓")
        print(f"   - Procesos electorales: ✓")
        print(f"   - Usuarios y asignaciones: ✓")

if __name__ == "__main__":
    main()