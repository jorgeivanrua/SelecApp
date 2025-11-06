#!/usr/bin/env python3
"""
Script para mostrar un resumen completo de la base de datos electoral
"""

import sqlite3
from datetime import datetime

def show_database_summary():
    """Muestra un resumen completo de la base de datos"""
    
    conn = sqlite3.connect('caqueta_electoral.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("RESUMEN COMPLETO DE LA BASE DE DATOS ELECTORAL")
    print("Sistema de Recolección Inicial de Votaciones - Caquetá")
    print("=" * 60)
    print(f"Fecha de consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Estadísticas generales
    print("📊 ESTADÍSTICAS GENERALES:")
    cursor.execute("SELECT COUNT(*) FROM locations WHERE tipo='DEPARTAMENTO'")
    print(f"   • Departamentos: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM locations WHERE tipo='MUNICIPIO'")
    print(f"   • Municipios: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM locations WHERE tipo='PUESTO'")
    print(f"   • Puestos electorales: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM mesas_electorales")
    print(f"   • Mesas electorales: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    print(f"   • Usuarios del sistema: {cursor.fetchone()[0]}")
    print()
    
    # Datos electorales
    print("🗳️  DATOS ELECTORALES:")
    cursor.execute("SELECT COUNT(*) FROM election_types")
    print(f"   • Tipos de elección: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM electoral_journeys")
    print(f"   • Jornadas electorales: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM electoral_processes")
    print(f"   • Procesos electorales: {cursor.fetchone()[0]}")
    print()
    
    # Candidatos y partidos
    print("🏛️  CANDIDATOS Y PARTIDOS:")
    cursor.execute("SELECT COUNT(*) FROM political_parties")
    print(f"   • Partidos políticos: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM coalitions")
    print(f"   • Coaliciones: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM candidates")
    print(f"   • Candidatos: {cursor.fetchone()[0]}")
    print()
    
    # Detalle de tipos de elección
    print("📋 TIPOS DE ELECCIÓN CONFIGURADOS:")
    cursor.execute("SELECT nombre, codigo FROM election_types ORDER BY nombre")
    for nombre, codigo in cursor.fetchall():
        print(f"   • {nombre} ({codigo})")
    print()
    
    # Detalle de partidos políticos
    print("🎯 PARTIDOS POLÍTICOS REGISTRADOS:")
    cursor.execute("SELECT nombre_oficial, siglas FROM political_parties ORDER BY siglas")
    for nombre, siglas in cursor.fetchall():
        print(f"   • {siglas}: {nombre}")
    print()
    
    # Detalle de candidatos
    print("👥 CANDIDATOS REGISTRADOS:")
    cursor.execute("""
        SELECT c.nombre_completo, c.cargo_aspirado, p.siglas, et.nombre
        FROM candidates c
        LEFT JOIN political_parties p ON c.party_id = p.id
        LEFT JOIN election_types et ON c.election_type_id = et.id
        ORDER BY c.cargo_aspirado, c.nombre_completo
    """)
    
    current_cargo = None
    for nombre, cargo, partido, tipo_eleccion in cursor.fetchall():
        if cargo != current_cargo:
            print(f"\n   {cargo.upper().replace('_', ' ')}:")
            current_cargo = cargo
        partido_str = partido if partido else "Independiente"
        print(f"     • {nombre} ({partido_str}) - {tipo_eleccion}")
    print()
    
    # Detalle de coaliciones
    print("🤝 COALICIONES REGISTRADAS:")
    cursor.execute("SELECT nombre_coalicion, descripcion FROM coalitions")
    coalitions = cursor.fetchall()
    if coalitions:
        for nombre, descripcion in coalitions:
            print(f"   • {nombre}")
            if descripcion:
                print(f"     {descripcion}")
            
            # Mostrar partidos de la coalición
            cursor.execute("""
                SELECT p.siglas, p.nombre_oficial
                FROM coalition_parties cp
                JOIN political_parties p ON cp.party_id = p.id
                JOIN coalitions c ON cp.coalition_id = c.id
                WHERE c.nombre_coalicion = ?
            """, (nombre,))
            
            partidos_coalicion = cursor.fetchall()
            if partidos_coalicion:
                print("     Partidos miembros:")
                for siglas, nombre_partido in partidos_coalicion:
                    print(f"       - {siglas}: {nombre_partido}")
            print()
    else:
        print("   • No hay coaliciones registradas")
    print()
    
    # Resumen por municipio (top 5)
    print("🏘️  TOP 5 MUNICIPIOS POR NÚMERO DE MESAS:")
    cursor.execute("""
        SELECT l.nombre_municipio, COUNT(m.id) as total_mesas
        FROM locations l
        LEFT JOIN mesas_electorales m ON l.id = m.puesto_id
        WHERE l.tipo = 'MUNICIPIO'
        GROUP BY l.nombre_municipio
        ORDER BY total_mesas DESC
        LIMIT 5
    """)
    
    for municipio, mesas in cursor.fetchall():
        print(f"   • {municipio}: {mesas} mesas")
    print()
    
    # Estado de los procesos electorales
    print("⚙️  ESTADO DE PROCESOS ELECTORALES:")
    cursor.execute("SELECT estado, COUNT(*) FROM electoral_processes GROUP BY estado")
    for estado, count in cursor.fetchall():
        print(f"   • {estado.title()}: {count} procesos")
    print()
    
    print("=" * 60)
    print("✅ BASE DE DATOS COMPLETAMENTE INICIALIZADA")
    print("El sistema está listo para la recolección de votaciones")
    print("=" * 60)
    
    conn.close()

if __name__ == "__main__":
    show_database_summary()