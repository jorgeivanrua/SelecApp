"""
Servicio de Exportación de Reportes
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import logging
import io
import csv
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class ExportService:
    """Servicio para exportación de reportes a diferentes formatos"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str = None) -> io.BytesIO:
        """Exportar datos a formato CSV"""
        try:
            if not data:
                return None
            
            # Crear buffer en memoria
            output = io.StringIO()
            
            # Obtener campos del primer registro
            fieldnames = list(data[0].keys())
            
            # Crear writer CSV
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
            # Convertir a bytes
            csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
            csv_bytes.seek(0)
            
            return csv_bytes
            
        except Exception as e:
            self.logger.error(f"Error exportando a CSV: {e}")
            return None
    
    def export_to_json(self, data: Any, filename: str = None) -> io.BytesIO:
        """Exportar datos a formato JSON"""
        try:
            # Convertir a JSON con formato legible
            json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
            
            # Crear buffer en memoria
            json_bytes = io.BytesIO(json_str.encode('utf-8'))
            json_bytes.seek(0)
            
            return json_bytes
            
        except Exception as e:
            self.logger.error(f"Error exportando a JSON: {e}")
            return None
    
    def export_to_excel(self, data: Dict[str, Any], report_type: str) -> io.BytesIO:
        """Exportar datos a formato Excel (simulado)"""
        try:
            # Esta es una implementación básica
            # En producción se usaría openpyxl o xlsxwriter
            
            # Por ahora, creamos un CSV que Excel puede abrir
            if 'candidates' in data:
                csv_data = data['candidates']
            elif 'parties' in data:
                csv_data = data['parties']
            elif 'municipalities' in data:
                csv_data = data['municipalities']
            else:
                # Convertir a formato tabular genérico
                csv_data = [data]
            
            return self.export_to_csv(csv_data)
            
        except Exception as e:
            self.logger.error(f"Error exportando a Excel: {e}")
            return None
    
    def export_to_pdf(self, data: Dict[str, Any], report_type: str) -> io.BytesIO:
        """Exportar datos a formato PDF (simulado)"""
        try:
            # Esta es una implementación básica
            # En producción se usaría reportlab o weasyprint
            
            # Por ahora, creamos un archivo de texto simple
            pdf_content = self._generate_text_report(data, report_type)
            
            pdf_bytes = io.BytesIO(pdf_content.encode('utf-8'))
            pdf_bytes.seek(0)
            
            return pdf_bytes
            
        except Exception as e:
            self.logger.error(f"Error exportando a PDF: {e}")
            return None
    
    def _generate_text_report(self, data: Dict[str, Any], report_type: str) -> str:
        """Generar reporte en formato texto"""
        try:
            lines = []
            lines.append("=" * 80)
            lines.append(f"REPORTE: {report_type.upper()}")
            lines.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("=" * 80)
            lines.append("")
            
            # Agregar contenido según el tipo de reporte
            if 'general_stats' in data:
                lines.append("ESTADÍSTICAS GENERALES:")
                lines.append("-" * 40)
                for key, value in data['general_stats'].items():
                    lines.append(f"  {key}: {value}")
                lines.append("")
            
            if 'candidates' in data:
                lines.append("CANDIDATOS:")
                lines.append("-" * 40)
                for i, candidate in enumerate(data['candidates'][:10], 1):
                    lines.append(f"{i}. {candidate.get('nombre_completo', 'N/A')} - Votos: {candidate.get('total_votos', 0)}")
                lines.append("")
            
            if 'parties' in data:
                lines.append("PARTIDOS:")
                lines.append("-" * 40)
                for i, party in enumerate(data['parties'][:10], 1):
                    lines.append(f"{i}. {party.get('siglas', 'N/A')} - Votos: {party.get('total_votos_partido', 0)}")
                lines.append("")
            
            if 'municipalities' in data:
                lines.append("MUNICIPIOS:")
                lines.append("-" * 40)
                for i, mun in enumerate(data['municipalities'][:10], 1):
                    lines.append(f"{i}. {mun.get('nombre_municipio', 'N/A')} - Completado: {mun.get('porcentaje_completado', 0)}%")
                lines.append("")
            
            lines.append("=" * 80)
            lines.append("Fin del reporte")
            lines.append("=" * 80)
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de texto: {e}")
            return "Error generando reporte"
    
    def get_export_formats(self) -> List[Dict[str, str]]:
        """Obtener formatos de exportación disponibles"""
        return [
            {
                'format': 'csv',
                'name': 'CSV (Comma Separated Values)',
                'mime_type': 'text/csv',
                'extension': '.csv'
            },
            {
                'format': 'json',
                'name': 'JSON (JavaScript Object Notation)',
                'mime_type': 'application/json',
                'extension': '.json'
            },
            {
                'format': 'excel',
                'name': 'Excel (Microsoft Excel)',
                'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'extension': '.xlsx'
            },
            {
                'format': 'pdf',
                'name': 'PDF (Portable Document Format)',
                'mime_type': 'application/pdf',
                'extension': '.pdf'
            }
        ]
    
    def log_export(self, user_id: int, report_type: str, export_format: str, success: bool):
        """Registrar exportación en el log"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crear tabla de logs si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS export_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    report_type VARCHAR(100) NOT NULL,
                    export_format VARCHAR(50) NOT NULL,
                    success BOOLEAN NOT NULL,
                    exported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                INSERT INTO export_logs (user_id, report_type, export_format, success)
                VALUES (?, ?, ?, ?)
            """, (user_id, report_type, export_format, success))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Exportación registrada: {report_type} a {export_format} por usuario {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error registrando exportación: {e}")
    
    def get_export_history(self, user_id: int = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener historial de exportaciones"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT el.*, u.nombre_completo as user_name
                FROM export_logs el
                LEFT JOIN users u ON el.user_id = u.id
            """
            
            params = []
            
            if user_id:
                query += " WHERE el.user_id = ?"
                params.append(user_id)
            
            query += " ORDER BY el.exported_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            history = []
            for row in results:
                history.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'user_name': row['user_name'],
                    'report_type': row['report_type'],
                    'export_format': row['export_format'],
                    'success': bool(row['success']),
                    'exported_at': row['exported_at']
                })
            
            conn.close()
            return history
            
        except Exception as e:
            self.logger.error(f"Error obteniendo historial de exportaciones: {e}")
            return []