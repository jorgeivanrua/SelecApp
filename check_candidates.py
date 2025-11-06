#!/usr/bin/env python3
"""
Script para verificar y cargar candidatos en la base de datos
"""

import sqlite3
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    Base, PoliticalParty, Coalition, Candidate, 
    ElectionType, CandidateResults
)

# Configurar base de datos
DATABASE_URL = "sqlite:///caqueta_electoral.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def check_and_load_candidates():
    """Verifica y carga candidatos de ejemplo"""
    
    # Crear sesión
    session = Session()
    
    try:
        print("=== VERIFICACIÓN DE CANDIDATOS ===")
        
        # Verificar tipos de elección
        election_types = session.query(ElectionType).all()
        print(f"Tipos de elección disponibles: {len(election_types)}")
        for et in election_types:
            print(f"  - {et.nombre} ({et.codigo})")
        
        # Verificar partidos
        parties = session.query(PoliticalParty).all()
        print(f"\nPartidos políticos disponibles: {len(parties)}")
        for party in parties:
            print(f"  - {party.nombre_oficial} ({party.siglas})")
        
        # Verificar candidatos existentes
        existing_candidates = session.query(Candidate).all()
        print(f"\nCandidatos existentes: {len(existing_candidates)}")
        
        if len(existing_candidates) == 0:
            print("\nCargando candidatos de ejemplo...")
            
            # Obtener tipos de elección específicos
            senado_type = session.query(ElectionType).filter(ElectionType.codigo == 'SEN').first()
            camara_type = session.query(ElectionType).filter(ElectionType.codigo == 'CAM').first()
            
            # Obtener partidos específicos
            partido_conservador = session.query(PoliticalParty).filter(PoliticalParty.siglas == 'PCC').first()
            partido_liberal = session.query(PoliticalParty).filter(PoliticalParty.siglas == 'PLC').first()
            centro_democratico = session.query(PoliticalParty).filter(PoliticalParty.siglas == 'CD').first()
            pacto_historico = session.query(PoliticalParty).filter(PoliticalParty.siglas == 'PH').first()
            
            candidates_data = []
            
            if senado_type:
                candidates_data.extend([
                    {
                        'nombre_completo': 'María Fernanda Cabal Molina',
                        'cedula': '52123456',
                        'numero_tarjeton': 1,
                        'cargo_aspirado': 'senador',
                        'election_type_id': senado_type.id,
                        'circunscripcion': 'nacional',
                        'party_id': centro_democratico.id if centro_democratico else None,
                        'biografia': 'Senadora de la República por el Centro Democrático'
                    },
                    {
                        'nombre_completo': 'Gustavo Francisco Petro Urrego',
                        'cedula': '19123456',
                        'numero_tarjeton': 2,
                        'cargo_aspirado': 'senador',
                        'election_type_id': senado_type.id,
                        'circunscripcion': 'nacional',
                        'party_id': pacto_historico.id if pacto_historico else None,
                        'biografia': 'Político y economista colombiano'
                    },
                    {
                        'nombre_completo': 'Paloma Valencia Laserna',
                        'cedula': '43123456',
                        'numero_tarjeton': 3,
                        'cargo_aspirado': 'senador',
                        'election_type_id': senado_type.id,
                        'circunscripcion': 'nacional',
                        'party_id': centro_democratico.id if centro_democratico else None,
                        'biografia': 'Senadora de la República'
                    }
                ])
            
            if camara_type:
                candidates_data.extend([
                    {
                        'nombre_completo': 'Katherine Miranda Peña',
                        'cedula': '52234567',
                        'numero_tarjeton': 1,
                        'cargo_aspirado': 'representante_camara',
                        'election_type_id': camara_type.id,
                        'circunscripcion': 'departamental',
                        'party_id': partido_liberal.id if partido_liberal else None,
                        'biografia': 'Representante a la Cámara por Bogotá'
                    },
                    {
                        'nombre_completo': 'Juan Diego Gómez González',
                        'cedula': '19234567',
                        'numero_tarjeton': 2,
                        'cargo_aspirado': 'representante_camara',
                        'election_type_id': camara_type.id,
                        'circunscripcion': 'departamental',
                        'party_id': partido_conservador.id if partido_conservador else None,
                        'biografia': 'Representante a la Cámara por Caquetá'
                    }
                ])
            
            # Crear candidatos
            created_count = 0
            for candidate_data in candidates_data:
                # Verificar si ya existe
                existing = session.query(Candidate).filter(
                    Candidate.cedula == candidate_data['cedula']
                ).first()
                
                if not existing:
                    candidate = Candidate(
                        nombre_completo=candidate_data['nombre_completo'],
                        cedula=candidate_data['cedula'],
                        numero_tarjeton=candidate_data['numero_tarjeton'],
                        cargo_aspirado=candidate_data['cargo_aspirado'],
                        election_type_id=candidate_data['election_type_id'],
                        circunscripcion=candidate_data['circunscripcion'],
                        party_id=candidate_data['party_id'],
                        biografia=candidate_data['biografia'],
                        activo=True,
                        habilitado_oficialmente=True
                    )
                    
                    session.add(candidate)
                    created_count += 1
                    print(f"  ✓ Candidato creado: {candidate_data['nombre_completo']} ({candidate_data['cargo_aspirado']})")
            
            # Confirmar cambios
            session.commit()
            print(f"\nTotal candidatos creados: {created_count}")
        
        # Verificar candidatos finales
        final_candidates = session.query(Candidate).all()
        print(f"\nCandidatos totales en la base de datos: {len(final_candidates)}")
        
        for candidate in final_candidates:
            if candidate.party_id:
                party = session.query(PoliticalParty).filter(PoliticalParty.id == candidate.party_id).first()
                party_name = party.siglas if party else "Desconocido"
            else:
                party_name = "Independiente"
            print(f"  - {candidate.nombre_completo} ({candidate.cargo_aspirado}) - {party_name}")
        
        print("\n=== VERIFICACIÓN COMPLETADA ===")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    check_and_load_candidates()