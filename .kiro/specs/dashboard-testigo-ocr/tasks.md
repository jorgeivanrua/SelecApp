# Implementation Plan - Dashboard Testigo con OCR

## Overview
Este plan de implementación detalla las tareas necesarias para completar el dashboard del testigo electoral con captura de foto, OCR automático y formulario completo del E14.

## Tasks

- [x] 1. Estructura base del dashboard
  - Crear template HTML con layout de 2 columnas
  - Implementar header con información de la mesa
  - Agregar estadísticas rápidas (4 cards)
  - _Requirements: 12.1, 12.2_

- [x] 2. Implementar área de captura de foto
  - [x] 2.1 Crear contenedor de preview con estilos
    - Diseño visual con icono de cámara
    - Estados: vacío, con imagen, procesando
    - Click para activar selector de archivo
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 2.2 Implementar selector de archivo
    - Input file con accept="image/*"
    - Soporte para capture="environment" (cámara móvil)
    - Validación de formato y tamaño
    - _Requirements: 1.1, 1.2_

  - [x] 2.3 Mostrar preview de imagen
    - Leer archivo con FileReader
    - Mostrar imagen en contenedor
    - Indicador visual de foto cargada
    - _Requirements: 1.3_

- [x] 3. Implementar OCR automático
  - [x] 3.1 Activar OCR al capturar foto
    - Llamar función procesarOCR automáticamente
    - Mostrar indicador de procesamiento
    - Simular delay de 2 segundos
    - _Requirements: 2.1, 2.2_

  - [x] 3.2 Generar datos simulados del OCR
    - Crear objeto con candidatos, votos, datos del acta
    - Incluir niveles de confianza simulados
    - Calcular totales automáticamente
    - _Requirements: 2.3, 2.4, 2.5_

  - [x] 3.3 Llenar formulario con datos del OCR
    - Limpiar candidatos existentes
    - Agregar candidatos del OCR dinámicamente
    - Llenar campos de votos especiales
    - Llenar campos del acta si están disponibles
    - _Requirements: 3.1, 3.2, 3.5_

- [x] 4. Implementar formulario E14 completo
  - [x] 4.1 Sección de información de ubicación
    - Departamento (readonly)
    - Municipio (readonly)
    - Zona (readonly)
    - Puesto (readonly)
    - Mesa (readonly)
    - Tipo de Elección (readonly)
    - _Requirements: 5.1_

  - [x] 4.2 Sección de horarios
    - Hora de Apertura (time input, editable)
    - Hora de Cierre (time input, editable)
    - _Requirements: 5.2_

  - [x] 4.3 Sección de candidatos dinámicos
    - Contenedor para lista de candidatos
    - Función agregarCandidato()
    - Función eliminarCandidato(id)
    - Inputs: nombre, partido, votos
    - Botón "Agregar Candidato"
    - _Requirements: 4.5, 5.3_

  - [x] 4.4 Sección de votos especiales
    - Votos en Blanco (number input)
    - Votos Nulos (number input)
    - Tarjetas No Marcadas (number input)
    - Total Tarjetas (readonly, calculado)
    - _Requirements: 5.4_

  - [x] 4.5 Sección de información de votantes
    - Votantes Habilitados (readonly)
    - Votantes que Sufragaron (number input)
    - Certificados Electorales (number input)
    - _Requirements: 5.5_

  - [x] 4.6 Sección de totales y validación
    - Total Votos (calculado automáticamente)
    - Indicador de validación (verde/amarillo/rojo)
    - Función calcularTotales()
    - Lógica de validación visual
    - _Requirements: 3.5, 8.1, 8.2, 8.3_

  - [x] 4.7 Sección de información del acta
    - Número de Acta E14 (text input)
    - Jurado Presidente (text input)
    - Testigos del Acta (text input)
    - Checkbox: Acta firmada
    - Checkbox: Proceso normal
    - _Requirements: 5.6, 5.7_

  - [x] 4.8 Sección de observaciones
    - Textarea con 4 filas
    - Placeholder descriptivo
    - _Requirements: 5.8_

- [x] 5. Implementar validaciones en tiempo real
  - [x] 5.1 Validación de campos numéricos
    - Atributo min="0" en inputs numéricos
    - Prevenir valores negativos
    - _Requirements: 4.4_

  - [x] 5.2 Cálculo automático de totales
    - Event listener en inputs con clase 'voto-input'
    - Sumar todos los votos al cambiar cualquier campo
    - Actualizar display de total
    - _Requirements: 4.3_

  - [x] 5.3 Validación contra votantes habilitados
    - Comparar total con votantes habilitados
    - Actualizar indicador visual (verde/amarillo/rojo)
    - Mostrar mensaje descriptivo
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 5.4 Validación de formulario completo
    - Verificar que foto esté capturada
    - Verificar que haya al menos un voto
    - Habilitar/deshabilitar botón de envío
    - _Requirements: 6.1, 6.2_

- [x] 6. Implementar envío de formulario
  - [x] 6.1 Recopilar datos del formulario
    - Capturar todos los 25+ campos
    - Crear objeto con estructura completa
    - Incluir array de candidatos
    - _Requirements: 6.3_

  - [x] 6.2 Enviar datos a la API
    - POST a /api/testigo/enviar-e14
    - Incluir token de autenticación
    - Manejar respuesta exitosa
    - Manejar errores
    - _Requirements: 6.4_

  - [x] 6.3 Confirmación y feedback
    - Mostrar alerta de confirmación antes de enviar
    - Mostrar spinner durante envío
    - Mostrar mensaje de éxito
    - Actualizar contador de capturas
    - Recargar página para nueva captura
    - _Requirements: 6.6, 6.7, 6.8_

- [x] 7. Eliminar acciones rápidas innecesarias
  - Remover sección completa de acciones rápidas
  - Mantener solo el formulario principal
  - Limpiar estilos CSS relacionados
  - _Requirements: 12.2, 12.3, 12.4_

- [ ] 8. Actualizar API backend
  - [ ] 8.1 Actualizar endpoint /api/testigo/enviar-e14
    - Recibir todos los campos nuevos del formulario
    - Validar estructura de datos
    - Guardar en base de datos
    - _Requirements: 6.4, 6.5_

  - [ ] 8.2 Actualizar esquema de base de datos
    - Agregar columnas faltantes en capturas_e14
    - Crear índices necesarios
    - Migración de datos existentes
    - _Requirements: 6.5_

  - [ ]* 8.3 Implementar tests de API
    - Test de envío completo
    - Test de validaciones
    - Test de errores
    - _Requirements: 6.4, 6.5_

- [ ] 9. Implementar OCR real (futuro)
  - [ ] 9.1 Integrar Tesseract OCR
    - Instalar dependencias
    - Configurar procesamiento de imagen
    - Definir zonas OCR del E14
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 9.2 Preprocesamiento de imagen
    - Escala de grises
    - Mejora de contraste
    - Eliminación de ruido
    - _Requirements: 2.1_

  - [ ] 9.3 Extracción de datos
    - Procesar cada zona OCR
    - Convertir texto a números
    - Calcular confianza
    - _Requirements: 2.3, 2.4_

  - [ ]* 9.4 Tests de OCR
    - Test con imágenes de muestra
    - Test de precisión
    - Test de manejo de errores
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 10. Implementar validación de calidad de imagen
  - [ ] 10.1 Análisis de resolución
    - Verificar dimensiones mínimas
    - Mostrar advertencia si es baja
    - _Requirements: 11.1, 11.2_

  - [ ] 10.2 Detección de desenfoque
    - Análisis de varianza de Laplacian
    - Mostrar advertencia si está borrosa
    - _Requirements: 11.3, 11.4_

  - [ ] 10.3 Feedback al usuario
    - Mostrar recomendaciones
    - Permitir continuar o retomar
    - _Requirements: 11.5_

- [ ]* 11. Implementar tests end-to-end
  - Flujo completo de captura
  - Validación de datos guardados
  - Manejo de errores
  - _Requirements: All_

- [ ]* 12. Documentación
  - Manual de usuario para testigos
  - Guía de troubleshooting
  - Documentación técnica de API
  - _Requirements: All_

## Notes

- Las tareas marcadas con [x] están completadas
- Las tareas marcadas con * son opcionales
- Las tareas 1-7 están implementadas y funcionando
- Las tareas 8-12 son mejoras futuras
- Prioridad: Completar tarea 8 (API backend) antes de producción
