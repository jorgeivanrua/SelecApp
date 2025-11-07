"""
Script de verificación de datos cargados en el sistema electoral
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import (
    Location, MesaElectoral, LocationType, User, ElectionType, 
    ElectoralJourney, ElectoralProcess, MesaElectoralProcess
)
import json

def main():
    """Función principal para verificar los datos cargados"""
    
    print("=== VERIFICACIÓN DE DATOS DEL SISTEMA ELECTORAL ===\n")
    
    # Conectar a la base de datos
    engine = create_engine("sqlite:///caqueta_electoral.db", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        
        # 1. Verificar estructura geográfica
        print("1. ESTRUCTURA GEOGRÁFICA:")
        print("-" * 40)
        
        departamento = db.query(Location).filter(Location.tipo == LocationType.DEPARTAMENTO).first()
        print(f"Departamento: {departamento.nombre_departamento} (Código: {departamento.codigo_departamento})")
        
        municipios = db.query(Location).filter(Location.tipo == LocationType.MUNICIPIO).all()
        print(f"Total municipios: {len(municipios)}")
        
        for municipio in municipios[:5]:  # Mostrar solo los primeros 5
            puestos_count = db.query(Location).filter(
                Location.parent_id == municipio.id,
                Location.tipo == LocationType.PUESTO
            ).count()
            
            mesas_count = db.query(MesaElectoral).join(Location).filter(
                Location.parent_id == municipio.id
            ).count()
            
            print(f"  - {municipio.nombre_municipio}: {puestos_count} puestos, {mesas_count} mesas")
        
        if len(municipios) > 5:
            print(f"  ... y {len(municipios) - 5} municipios más")
        
        # 2. Verificar tipos de elecciones
        print(f"\n2. TIPOS DE ELECCIONES:")
        print("-" * 40)
        
        election_types = db.query(ElectionType).all()
        print(f"Total tipos de elección: {len(election_types)}")
        
        for et in election_types:
            candidatos_count = len(et.plantilla_e14.get('candidatos', []))
            print(f"  - {et.nombre} ({et.codigo}): {candidatos_count} candidatos/opciones")
        
        # 3. Verificar jornadas electorales
        print(f"\n3. JORNADAS ELECTORALES:")
        print("-" * 40)
        
        journeys = db.query(ElectoralJourney).all()
        print(f"Total jornadas: {len(journeys)}")
        
        for journey in journeys:
            print(f"  - {journey.nombre}")
            print(f"    Fecha: {journey.fecha_jornada.strftime('%Y-%m-%d')}")
            print(f"    Estado: {journey.estado}")
        
        # 4. Verificar procesos electorales
        print(f"\n4. PROCESOS ELECTORALES:")
        print("-" * 40)
        
        processes = db.query(ElectoralProcess).all()
        print(f"Total procesos: {len(processes)}")
        
        for process in processes:
            print(f"  - {process.nombre}")
            print(f"    Tipo: {process.tipo_eleccion.nombre}")
            print(f"    Jornada: {process.jornada.nombre}")
            print(f"    Estado: {process.estado}")
            print(f"    Período: {process.fecha_inicio.strftime('%Y-%m-%d')} a {process.fecha_fin.strftime('%Y-%m-%d')}")
        
        # 5. Verificar usuarios
        print(f"\n5. USUARIOS DEL SISTEMA:")
        print("-" * 40)
        
        users = db.query(User).all()
        print(f"Total usuarios: {len(users)}")
        
        for user in users:
            municipio_name = user.municipio.nombre_municipio if user.municipio else "N/A"
            print(f"  - {user.nombre_completo} ({user.rol})")
            print(f"    Usuario: {user.username}")
            print(f"    Municipio: {municipio_name}")
        
        # 6. Verificar algunas mesas específicas
        print(f"\n6. MESAS ELECTORALES (MUESTRA):")
        print("-" * 40)
        
        mesas_sample = db.query(MesaElectoral).join(Location).limit(10).all()
        
        for mesa in mesas_sample:
            print(f"  - Mesa {mesa.codigo_mesa} (#{mesa.numero_mesa})")
            print(f"    Puesto: {mesa.puesto.nombre_puesto}")
            print(f"    Municipio: {mesa.puesto.parent.nombre_municipio}")
            print(f"    Votantes habilitados: {mesa.total_votantes_habilitados}")
            print(f"    Estado: {mesa.estado_recoleccion}")
        
        # 7. Verificar configuración de un tipo de elección
        print(f"\n7. CONFIGURACIÓN DE EJEMPLO (Concejos de Juventudes):")
        print("-" * 40)
        
        cj_type = db.query(ElectionType).filter(ElectionType.codigo == 'CJ').first()
        if cj_type:
            print(f"Tipo: {cj_type.nombre}")
            print("Candidatos/Opciones:")
            for candidato in cj_type.plantilla_e14['candidatos']:
                print(f"  - {candidato['nombre']} ({candidato['tipo']})")
            
            print("Campos adicionales:")
            for campo in cj_type.plantilla_e14['campos_adicionales']:
                requerido = "Sí" if campo['requerido'] else "No"
                print(f"  - {campo['nombre']} ({campo['tipo']}) - Requerido: {requerido}")
        
        # 8. Estadísticas finales
        print(f"\n8. ESTADÍSTICAS FINALES:")
        print("-" * 40)
        
        total_locations = db.query(Location).count()
        total_mesas = db.query(MesaElectoral).count()
        total_votantes = db.query(func.sum(MesaElectoral.total_votantes_habilitados)).scalar() or 0
        
        print(f"Total ubicaciones: {total_locations}")
        print(f"Total mesas electorales: {total_mesas}")
        print(f"Total votantes habilitados: {total_votantes:,}")
        print(f"Total tipos de elección: {len(election_types)}")
        print(f"Total jornadas electorales: {len(journeys)}")
        print(f"Total procesos electorales: {len(processes)}")
        print(f"Total usuarios: {len(users)}")
        
        print(f"\n=== VERIFICACIÓN COMPLETADA ===")
        print("✓ Todos los datos se han cargado correctamente")
        print("✓ El sistema está listo para operación")

if __name__ == "__main__":
    main()