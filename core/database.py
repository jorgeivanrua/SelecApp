"""
Core Database Manager
Maneja todas las conexiones y operaciones de base de datos
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor centralizado de base de datos"""
    
    def __init__(self, database_url):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Context manager para sesiones de base de datos"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query, params=None):
        """Ejecutar query SQL directa"""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.fetchall()
    
    def execute_insert(self, query, params=None):
        """Ejecutar INSERT y retornar ID"""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.lastrowid
    
    def execute_update(self, query, params=None):
        """Ejecutar UPDATE/DELETE"""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.rowcount
    
    def get_table_info(self, table_name):
        """Obtener información de una tabla"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)
    
    def get_all_tables(self):
        """Obtener todas las tablas de la base de datos"""
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        return [row[0] for row in self.execute_query(query)]
    
    def health_check(self):
        """Verificar estado de la base de datos"""
        try:
            self.execute_query("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False