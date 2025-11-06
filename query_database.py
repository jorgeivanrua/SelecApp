"""
Script para consultar la base de datos de Caquetá y verificar los datos cargados
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Location, MesaElectoral, LocationType
import json

def main():
    """Función principal para consultar la base de datos"""
    
    # Conectar a la base de datos
    engine = create_engine("sqlite:///caqueta_electoral.db", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        print("=== CONSULTA BASE DE DATOS CAQUETÁ ===\n")
        
        # 1. Información del departamento
        departamento = db.query(Location).filter(
            Location.tipo == LocationType.DEPARTAMENTO
        ).first()
        
        if departamento:
            print(f"DEPARTAMENTO: {departamento.nombre_departamento}")
            print(f"Código: {departamento.codigo_departamento}")
            print(f"ID: {departamento.id}\n")
        
        # 2. Listar municipios
        municipios = db.query(Location).filter(
            Location.tipo == LocationType.MUNICIPIO
        ).order_by(Location.nombre_municipio).all()
        
        print(f"MUNICIPIOS ({len(municipios)}):")
        for i, municipio in enumerate(municipios, 1):
            # Contar puestos y mesas por municipio
            puestos_count = db.query(Location).filter(
                Location.parent_id == municipio.id,
                Location.tipo == LocationType.PUESTO
            ).count()
            
            mesas_count = db.query(MesaElectoral).join(Location).filter(
                Location.parent_id == municipio.id
            ).count()
            
            print(f"  {i:2d}. {municipio.nombre_municipio} (Código: {municipio.codigo_municipio})")
            print(f"      Puestos: {puestos_count}, Mesas: {mesas_count}")
        
        print()
        
        # 3. Detalles de Florencia (municipio principal)
        florencia = db.query(Location).filter(
            Location.nombre_municipio == "FLORENCIA",
            Location.tipo == LocationType.MUNICIPIO
        ).first()
        
        if florencia:
            print("DETALLE DE FLORENCIA:")
            print(f"ID: {florencia.id}")
            print(f"Código: {florencia.codigo_municipio}")
            
            # Puestos de Florencia
            puestos_florencia = db.query(Location).filter(
                Location.parent_id == florencia.id,
                Location.tipo == LocationType.PUESTO
            ).order_by(Location.nombre_puesto).limit(10).all()
            
            print(f"\nPrimeros 10 puestos de Florencia:")
            for puesto in puestos_florencia:
                mesas_puesto = db.query(MesaElectoral).filter(
                    MesaElectoral.puesto_id == puesto.id
                ).count()
                
                print(f"  - {puesto.nombre_puesto}")
                print(f"    Dirección: {puesto.direccion or 'N/A'}")
                print(f"    Coordenadas: {puesto.latitud}, {puesto.longitud}")
                print(f"    Mesas: {mesas_puesto}")
                print()
        
        # 4. Estadísticas de mesas
        total_mesas = db.query(MesaElectoral).count()
        from sqlalchemy import func
        total_votantes = db.query(func.sum(MesaElectoral.total_votantes_habilitados)).scalar() or 0
        
        print(f"ESTADÍSTICAS GENERALES:")
        print(f"Total mesas electorales: {total_mesas}")
        print(f"Total votantes habilitados: {total_votantes:,}")
        print(f"Promedio votantes por mesa: {total_votantes/total_mesas:.1f}")
        
        # 5. Mesas con más votantes
        print(f"\nMesas con más votantes:")
        mesas_grandes = db.query(MesaElectoral).join(Location).filter(
            Location.id == MesaElectoral.puesto_id
        ).order_by(MesaElectoral.total_votantes_habilitados.desc()).limit(5).all()
        
        for mesa in mesas_grandes:
            puesto = mesa.puesto
            municipio = db.query(Location).filter(Location.id == puesto.parent_id).first()
            print(f"  Mesa {mesa.codigo_mesa}: {mesa.total_votantes_habilitados} votantes")
            print(f"    Puesto: {puesto.nombre_puesto}")
            print(f"    Municipio: {municipio.nombre_municipio if municipio else 'N/A'}")
            print()
        
        # 6. Verificar coordenadas GPS
        puestos_con_gps = db.query(Location).filter(
            Location.tipo == LocationType.PUESTO,
            Location.latitud.isnot(None),
            Location.longitud.isnot(None)
        ).count()
        
        total_puestos = db.query(Location).filter(
            Location.tipo == LocationType.PUESTO
        ).count()
        
        print(f"COORDENADAS GPS:")
        print(f"Puestos con coordenadas: {puestos_con_gps}/{total_puestos}")
        print(f"Porcentaje con GPS: {(puestos_con_gps/total_puestos)*100:.1f}%")
        
        # 7. Exportar muestra de datos para verificación
        print(f"\nExportando muestra de datos...")
        
        # Muestra de mesas de Florencia
        mesas_muestra = db.query(MesaElectoral).join(Location).filter(
            Location.parent_id == florencia.id if florencia else False
        ).limit(5).all()
        
        muestra_data = []
        for mesa in mesas_muestra:
            puesto = mesa.puesto
            muestra_data.append({
                "codigo_mesa": mesa.codigo_mesa,
                "numero_mesa": mesa.numero_mesa,
                "votantes_habilitados": mesa.total_votantes_habilitados,
                "puesto": puesto.nombre_puesto,
                "direccion": puesto.direccion,
                "coordenadas": {
                    "latitud": puesto.latitud,
                    "longitud": puesto.longitud
                },
                "estado": mesa.estado_recoleccion
            })
        
        with open("muestra_mesas_caqueta.json", "w", encoding="utf-8") as f:
            json.dump(muestra_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Muestra exportada a: muestra_mesas_caqueta.json")
        
        print(f"\n=== CONSULTA COMPLETADA ===")

if __name__ == "__main__":
    main()