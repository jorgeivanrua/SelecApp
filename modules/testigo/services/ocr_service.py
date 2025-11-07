"""
Servicio de OCR para procesamiento de formularios E14
Sistema Electoral Caquetá
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
from typing import Dict, List, Tuple
import os

logger = logging.getLogger(__name__)

class OCRService:
    """Servicio para procesamiento OCR de formularios E14"""
    
    def __init__(self):
        # Configurar ruta de Tesseract (ajustar según instalación)
        # Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def preprocesar_imagen(self, imagen_path: str) -> np.ndarray:
        """
        Preprocesar imagen para mejorar OCR
        """
        try:
            # Cargar imagen
            imagen = cv2.imread(imagen_path)
            
            if imagen is None:
                raise ValueError(f"No se pudo cargar la imagen: {imagen_path}")
            
            # Convertir a escala de grises
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            
            # Aplicar umbral adaptativo
            binaria = cv2.adaptiveThreshold(
                gris, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Eliminar ruido
            denoised = cv2.fastNlMeansDenoising(binaria, None, 10, 7, 21)
            
            # Mejorar contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            mejorada = clahe.apply(denoised)
            
            logger.info(f"Imagen preprocesada exitosamente: {imagen_path}")
            return mejorada
            
        except Exception as e:
            logger.error(f"Error preprocesando imagen: {e}")
            raise
    
    def extraer_numero_de_zona(self, imagen: np.ndarray, zona: Dict) -> Tuple[int, float]:
        """
        Extraer número de una zona específica de la imagen
        
        Args:
            imagen: Imagen preprocesada
            zona: Dict con x, y, width, height
            
        Returns:
            Tuple (número_extraído, confianza)
        """
        try:
            # Recortar zona de interés (ROI)
            x, y, w, h = zona['x'], zona['y'], zona['width'], zona['height']
            roi = imagen[y:y+h, x:x+w]
            
            # Configuración de Tesseract para números
            config = '--psm 7 -c tessedit_char_whitelist=0123456789'
            
            # Extraer texto con datos de confianza
            datos = pytesseract.image_to_data(
                roi, 
                config=config, 
                output_type=pytesseract.Output.DICT
            )
            
            # Obtener texto y confianza
            texto = ''.join([
                datos['text'][i] 
                for i in range(len(datos['text'])) 
                if int(datos['conf'][i]) > 0
            ])
            
            # Calcular confianza promedio
            confianzas = [
                int(datos['conf'][i]) 
                for i in range(len(datos['conf'])) 
                if int(datos['conf'][i]) > 0
            ]
            confianza = np.mean(confianzas) if confianzas else 0
            
            # Convertir a número
            try:
                numero = int(''.join(filter(str.isdigit, texto)))
            except:
                numero = 0
                confianza = 0
            
            return numero, confianza
            
        except Exception as e:
            logger.error(f"Error extrayendo número de zona: {e}")
            return 0, 0
    
    def procesar_e14(self, imagen_path: str, estructura_e14: List[Dict]) -> Dict:
        """
        Procesar formulario E14 completo con OCR
        
        Args:
            imagen_path: Ruta de la imagen
            estructura_e14: Lista de posiciones con zonas OCR
            
        Returns:
            Dict con datos extraídos y métricas
        """
        try:
            logger.info(f"Iniciando procesamiento OCR de: {imagen_path}")
            
            # Preprocesar imagen
            imagen_procesada = self.preprocesar_imagen(imagen_path)
            
            # Extraer datos de cada posición
            resultados = []
            total_votos = 0
            confianzas = []
            advertencias = []
            
            for posicion in estructura_e14:
                # Extraer número de la zona
                votos, confianza = self.extraer_numero_de_zona(
                    imagen_procesada, 
                    posicion['zona_ocr']
                )
                
                # Construir resultado
                resultado = {
                    'posicion': posicion['posicion'],
                    'tipo': posicion.get('tipo', 'candidato'),
                    'candidato': posicion.get('candidato'),
                    'partido': posicion.get('partido'),
                    'votos': votos,
                    'confianza': round(confianza, 2)
                }
                
                resultados.append(resultado)
                total_votos += votos
                confianzas.append(confianza)
                
                # Generar advertencias para baja confianza
                if confianza < 90:
                    advertencias.append(
                        f"Baja confianza en posición {posicion['posicion']} ({confianza:.0f}%)"
                    )
            
            # Calcular métricas
            confianza_promedio = np.mean(confianzas) if confianzas else 0
            
            resultado_final = {
                'success': True,
                'imagen_path': imagen_path,
                'datos_extraidos': resultados,
                'total_votos': total_votos,
                'confianza_promedio': round(confianza_promedio, 2),
                'advertencias': advertencias,
                'num_posiciones': len(resultados)
            }
            
            logger.info(f"OCR completado. Confianza promedio: {confianza_promedio:.2f}%")
            return resultado_final
            
        except Exception as e:
            logger.error(f"Error procesando E14 con OCR: {e}")
            return {
                'success': False,
                'error': str(e),
                'datos_extraidos': [],
                'total_votos': 0,
                'confianza_promedio': 0,
                'advertencias': [f"Error en procesamiento: {str(e)}"]
            }
    
    def validar_datos_extraidos(self, datos: List[Dict], votantes_habilitados: int) -> Dict:
        """
        Validar datos extraídos por OCR
        
        Args:
            datos: Lista de datos extraídos
            votantes_habilitados: Número de votantes habilitados en la mesa
            
        Returns:
            Dict con resultado de validación
        """
        try:
            total_votos = sum([d['votos'] for d in datos])
            
            validaciones = {
                'total_votos_valido': True,
                'dentro_rango': True,
                'errores': [],
                'advertencias': []
            }
            
            # Validar que total no exceda votantes habilitados
            if total_votos > votantes_habilitados:
                validaciones['total_votos_valido'] = False
                validaciones['errores'].append(
                    f"Total votos ({total_votos}) excede votantes habilitados ({votantes_habilitados})"
                )
            
            # Validar rango razonable (50-100% de participación)
            participacion = (total_votos / votantes_habilitados * 100) if votantes_habilitados > 0 else 0
            if participacion < 50 or participacion > 100:
                validaciones['dentro_rango'] = False
                validaciones['advertencias'].append(
                    f"Participación inusual: {participacion:.1f}%"
                )
            
            # Validar que no haya valores negativos
            for dato in datos:
                if dato['votos'] < 0:
                    validaciones['errores'].append(
                        f"Valor negativo en posición {dato['posicion']}"
                    )
            
            validaciones['es_valido'] = len(validaciones['errores']) == 0
            
            return validaciones
            
        except Exception as e:
            logger.error(f"Error validando datos: {e}")
            return {
                'es_valido': False,
                'errores': [str(e)],
                'advertencias': []
            }
    
    def guardar_imagen_procesada(self, imagen_original: str, imagen_procesada: np.ndarray, output_path: str):
        """
        Guardar imagen procesada para referencia
        """
        try:
            cv2.imwrite(output_path, imagen_procesada)
            logger.info(f"Imagen procesada guardada en: {output_path}")
        except Exception as e:
            logger.error(f"Error guardando imagen procesada: {e}")
