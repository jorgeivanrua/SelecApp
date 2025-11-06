# Plan de Implementación - Recolección Inicial de Información de Votaciones

- [x] 1. Configuración inicial, carga de datos DIVIPOLA y sistema de mapas



  - Crear servicio de inicialización para cargar datos DIVIPOLA desde CSV
  - Implementar validación de integridad de la jerarquía geográfica
  - Crear estructura automática de mesas electorales basada en datos DIVIPOLA
  - Integrar coordenadas GPS de ubicaciones electorales desde datos DIVIPOLA
  - Implementar MapService con OpenStreetMap y biblioteca Leaflet
  - Crear marcadores interactivos para todas las mesas y puestos electorales
  - Implementar geolocalización en tiempo real del usuario
  - Generar reporte de configuración inicial con totales por nivel y visualización geográfica
  - _Requerimientos: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_

- [ ] 2. Gestión de candidatos, partidos políticos y coaliciones
- [ ] 2.1 Crear modelos de datos para candidatos y partidos
  - Implementar modelo PoliticalParty con información completa (nombre, siglas, color, logo)
  - Crear modelo Coalition para coaliciones entre partidos
  - Implementar modelo CoalitionParty para relaciones entre coaliciones y partidos
  - Desarrollar modelo Candidate con información electoral completa
  - Crear modelo CandidateList para listas organizadas por partido/coalición
  - Establecer relaciones entre candidatos, partidos, coaliciones y tipos de elecciones
  - Definir enumeraciones CargoElectoral, TipoCircunscripcion, EstadoCandidato
  - _Requerimientos: 16.1, 16.2, 16.3, 16.4, 16.13_

- [ ] 2.2 Implementar CandidateManagementService
  - Crear función para gestionar partidos políticos con validación de datos
  - Implementar creación y gestión de coaliciones con partidos asociados
  - Desarrollar creación de candidatos con validación de duplicados
  - Implementar asociación de candidatos con partidos o coaliciones
  - Crear carga masiva de candidatos desde archivos CSV con validación
  - Desarrollar generación automática de listas de candidatos por circunscripción
  - Implementar búsqueda y filtrado avanzado de candidatos
  - Crear validación de consistencia con tarjetones electorales oficiales
  - _Requerimientos: 16.1, 16.2, 16.5, 16.6, 16.9, 16.14_

- [ ] 2.3 Crear APIs de gestión de candidatos y partidos
  - Implementar POST /api/parties para crear partidos políticos
  - Crear POST /api/coalitions para crear coaliciones
  - Desarrollar POST /api/candidates para crear candidatos individuales
  - Implementar POST /api/candidates/upload-csv para carga masiva
  - Crear GET /api/candidates/search para búsqueda avanzada
  - Desarrollar GET /api/candidates/by-party/{party_id} para candidatos por partido
  - Implementar GET /api/candidates/by-coalition/{coalition_id} para candidatos por coalición
  - Crear POST /api/candidates/validate-ballot para validar con tarjetón oficial
  - Desarrollar GET /api/candidate-lists/{election_type_id} para listas organizadas
  - _Requerimientos: 16.1, 16.2, 16.9, 16.10, 16.14_

- [ ] 2.4 Implementar CandidateReportingService
  - Crear función para calcular resultados por candidato individual
  - Implementar cálculo automático de totales por partido político
  - Desarrollar cálculo automático de totales por coalición
  - Crear generación de rankings de candidatos por votación
  - Implementar generación de rankings de partidos por votación total
  - Desarrollar reportes detallados con análisis estadístico por candidato
  - Crear reportes comparativos entre partidos y coaliciones
  - Implementar análisis de distribución geográfica de votos por candidato
  - _Requerimientos: 16.10, 16.11, 16.12, 16.15, 16.17_

- [ ] 2.5 Crear modelos de resultados y reportes
  - Implementar modelo CandidateResults para resultados por candidato
  - Crear modelo PartyResults para resultados agregados por partido
  - Desarrollar modelo CoalitionResults para resultados por coalición
  - Implementar modelo CandidateRanking para rankings de candidatos
  - Crear modelo DetailedCandidateReport para reportes detallados
  - Desarrollar modelo GeographicDistributionReport para análisis geográfico
  - Implementar modelo DashboardData para dashboards visuales
  - _Requerimientos: 16.15, 16.17, 16.18_

- [ ] 2.6 Integrar candidatos con formularios E-14
  - Modificar FormE14Extended para incluir datos de candidatos
  - Implementar mostrar nombres de candidatos junto a campos de votos
  - Desarrollar validación de votos contra lista oficial de candidatos
  - Crear cálculo automático de totales por candidato desde formularios
  - Implementar vinculación de votos con candidatos específicos
  - _Requerimientos: 16.8, 16.11_

- [ ] 2.7 Escribir pruebas para gestión de candidatos
  - Probar creación de partidos, coaliciones y candidatos
  - Verificar carga masiva desde CSV con validación de datos
  - Probar asociaciones entre candidatos y organizaciones políticas
  - Verificar cálculo de resultados por candidato y partido
  - Probar generación de rankings y reportes comparativos
  - Verificar integración con formularios E-14
  - _Requerimientos: 16.1, 16.2, 16.5, 16.11, 16.15_

- [ ] 3. Gestión de tipos de elecciones y plantillas E-14
- [ ] 2.1 Crear modelos para tipos de elecciones
  - Implementar modelo ElectionType con configuración de plantillas E-14
  - Crear modelo ElectoralProcess para procesos electorales específicos
  - Definir enumeración TipoEleccion con todos los tipos disponibles
  - Establecer relaciones entre procesos electorales y mesas
  - _Requerimientos: 10.1, 10.2, 10.3, 10.6_

- [ ] 2.2 Implementar ElectionTypeService para jornadas con múltiples elecciones
  - Crear función para configurar nuevos tipos de elecciones
  - Implementar creación de jornadas electorales con múltiples elecciones simultáneas
  - Desarrollar asignación de mesas a múltiples procesos electorales simultáneos
  - Implementar generación dinámica de formularios según tipo específico
  - Desarrollar validación de plantillas E-14 personalizadas
  - Crear configuración específica de OCR por tipo de elección
  - _Requerimientos: 10.1, 10.2, 10.3, 10.4, 10.6, 11.2_

- [ ] 2.3 Crear APIs de gestión de jornadas y elecciones simultáneas
  - Implementar POST /api/electoral-journeys para crear jornadas con múltiples elecciones
  - Crear GET /api/electoral-journeys/{id}/processes para listar procesos de una jornada
  - Desarrollar POST /api/mesa/{id}/assign-processes para asignar múltiples procesos a mesa
  - Implementar GET /api/mesa/{id}/active-processes para obtener procesos activos de mesa
  - Crear GET /api/electoral-process/{id}/form-structure para obtener estructura específica
  - _Requerimientos: 10.1, 10.3, 10.6, 11.2_

- [ ] 2.4 Escribir pruebas para gestión de tipos de elecciones
  - Probar creación de tipos de elecciones con plantillas personalizadas
  - Verificar generación dinámica de formularios
  - Probar configuración de procesos electorales
  - _Requerimientos: 10.1, 10.2, 10.4_

- [ ] 3. Plantillas predefinidas de formularios E-14
- [ ] 3.1 Crear plantillas para elecciones de juventudes y territoriales
  - Implementar plantilla E-14 para Concejos de Juventudes (base actual)
  - Crear plantilla E-14 para Senado con listas y candidatos
  - Desarrollar plantilla E-14 para Cámara de Representantes
  - Implementar plantilla E-14 para CITREP (Circunscripciones Territoriales)
  - _Requerimientos: 10.1, 10.2, 10.4_

- [ ] 3.2 Crear plantillas para elecciones presidenciales y territoriales
  - Implementar plantilla E-14 para elecciones Presidenciales
  - Crear plantilla E-14 para Gobernación departamental
  - Desarrollar plantilla E-14 para Asamblea Departamental
  - _Requerimientos: 10.1, 10.2, 10.4_

- [ ] 3.3 Crear plantillas para elecciones locales
  - Implementar plantilla E-14 para Alcaldía municipal
  - Crear plantilla E-14 para Concejo Municipal
  - Desarrollar plantilla E-14 para Juntas Administradoras Locales (Ediles)
  - _Requerimientos: 10.1, 10.2, 10.4_

- [ ] 3.4 Configurar OCR específico por tipo de formulario
  - Crear configuraciones de OCR para cada tipo de plantilla E-14
  - Implementar reglas de validación específicas por tipo de elección
  - Desarrollar mapeo de campos dinámicos para reconocimiento automático
  - _Requerimientos: 10.5, 2.3, 2.4_

- [ ] 3.5 Escribir pruebas para plantillas de formularios
  - Probar generación de formularios dinámicos para cada tipo
  - Verificar configuraciones de OCR específicas
  - Probar validaciones particulares de cada tipo de elección
  - _Requerimientos: 10.2, 10.4, 10.5_

- [ ] 4. Modelos de datos extendidos para recolección
- [ ] 4.1 Extender modelo MesaElectoral con campos de recolección y múltiples procesos
  - Agregar campos de estado de recolección y metadatos de proceso
  - Implementar enumeración EstadoRecoleccion con todos los estados del flujo
  - Establecer relaciones con testigos asignados y timestamps de proceso
  - Crear modelo MesaElectoralProcess para manejar múltiples procesos por mesa
  - Vincular mesas con jornadas electorales que contienen múltiples procesos
  - Implementar modelo ElectoralJourney para jornadas con elecciones simultáneas
  - _Requerimientos: 1.1, 9.1, 9.2, 10.3, 10.6_

- [ ] 4.2 Extender modelo FormE14 con campos de trazabilidad, proceso electoral específico y anomalías
  - Agregar campos de tiempo de captura y metadatos de dispositivo
  - Implementar campos para historial de cambios y comentarios de revisión
  - Crear campos para validaciones automáticas y alertas de calidad
  - Vincular formularios con procesos electorales específicos (no solo tipos)
  - Implementar almacenamiento dinámico de datos según plantilla del proceso
  - Agregar campo obligatorio para reporte de anomalías observadas por testigos
  - Permitir múltiples formularios E-14 por mesa (uno por cada proceso electoral)
  - _Requerimientos: 2.5, 2.6, 2.7, 2.14, 5.1, 5.2, 10.6_

- [ ] 4.3 Crear modelos de validación y auditoría
  - Implementar modelo ValidationResult para resultados de validaciones
  - Crear modelo AuditLog extendido para trazabilidad completa
  - Definir modelos para anomalías y reportes de calidad
  - _Requerimientos: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 4.4 Crear modelos para gestión de anomalías y texto de coincidencia
  - Implementar modelo AnomalyReport para reportes de anomalías por testigos
  - Crear modelo AnomalyConsolidation para consolidación por ubicación
  - Definir enumeraciones para categorías, severidad y estados de anomalías
  - Implementar modelo CoincidenceText para texto automático de coincidencia
  - Crear enumeración CoincidenceLevel para niveles de coincidencia
  - Establecer relaciones entre anomalías y formularios E-14
  - _Requerimientos: 11.1, 11.2, 11.3, 11.7, 2.6, 2.7_

- [ ] 4.5 Escribir pruebas unitarias para modelos extendidos
  - Crear tests para MesaElectoral con estados de recolección
  - Probar FormE14Extended con campos de trazabilidad, tipos de elección y anomalías
  - Verificar modelos de validación, auditoría y anomalías
  - _Requerimientos: 2.1, 5.1, 9.1, 10.4, 11.1_

- [ ] 5. Servicio de configuración inicial
- [ ] 5.1 Implementar InitializationService
  - Crear función para cargar y procesar datos DIVIPOLA desde CSV
  - Implementar validación de códigos geográficos y jerarquía
  - Desarrollar creación automática de estructura de mesas electorales
  - _Requerimientos: 1.1, 1.2, 1.3, 1.4_

- [ ] 5.2 Crear APIs de configuración inicial
  - Implementar endpoint POST /api/initialization/load-divipola
  - Crear endpoint GET /api/initialization/status para verificar estado
  - Desarrollar endpoint GET /api/initialization/report para reporte inicial
  - _Requerimientos: 1.4, 1.5_

- [ ] 5.3 Implementar validaciones de integridad geográfica
  - Crear validadores para códigos DIVIPOLA duplicados o inválidos
  - Implementar verificación de completitud de jerarquía
  - Desarrollar detección de inconsistencias en datos geográficos
  - _Requerimientos: 1.4, 6.1, 6.2_

- [ ] 5.4 Escribir pruebas para configuración inicial
  - Probar carga de datos DIVIPOLA con archivo de prueba
  - Verificar validaciones de integridad geográfica
  - Probar generación de reporte de configuración
  - _Requerimientos: 1.1, 1.4, 1.5_

- [ ] 6. Servicio de procesamiento OCR y captura de imágenes
- [ ] 6.1 Implementar OCRService para reconocimiento de formularios E-14
  - Integrar biblioteca de OCR (Tesseract/Google Vision API) para extraer datos
  - Crear función para validar calidad de imagen antes del procesamiento
  - Implementar detección de completitud del formulario físico
  - Desarrollar mejora automática de imagen para mejor reconocimiento
  - Configurar OCR dinámico según tipo de elección seleccionado
  - _Requerimientos: 2.2, 2.3, 2.4, 10.5_

- [ ] 6.2 Crear APIs de captura con imagen
  - Implementar POST /api/forms/e14/upload-image para subir foto del E-14
  - Crear GET /api/forms/e14/{id}/ocr-data para obtener datos reconocidos
  - Desarrollar PUT /api/forms/e14/{id}/validate-data para comparar OCR vs manual
  - Implementar POST /api/forms/e14/{id}/submit para envío final con imagen
  - _Requerimientos: 2.2, 2.3, 2.5, 2.8_

- [ ] 6.3 Implementar FormE14CaptureService extendido
  - Crear función para procesar imagen y extraer datos automáticamente
  - Implementar comparación entre datos OCR y datos ingresados manualmente
  - Desarrollar generación automática de texto informativo sobre coincidencia de datos
  - Implementar cálculo de porcentaje de coincidencia entre OCR y datos manuales
  - Crear clasificación automática del nivel de coincidencia (ALTA, MEDIA, BAJA, CRITICA)
  - Desarrollar validación matemática en tiempo real
  - Crear sistema de auto-guardado cada 30 segundos incluyendo imagen y texto de coincidencia
  - _Requerimientos: 2.4, 2.5, 2.6, 2.7, 2.12_

- [ ] 6.4 Implementar validaciones de captura con OCR
  - Crear validador de duplicados para evitar múltiples E-14 por mesa
  - Implementar validación de permisos por testigo y mesa asignada
  - Desarrollar validaciones matemáticas de consistencia de votos
  - Crear validación de discrepancias entre OCR y datos manuales
  - Validar que el tipo de formulario coincida con el proceso electoral
  - _Requerimientos: 2.5, 2.6, 6.1, 6.2, 10.6_

- [ ] 6.5 Escribir pruebas para captura E-14 con OCR
  - Probar procesamiento OCR con imágenes de formularios de prueba
  - Verificar comparación entre datos OCR y manuales
  - Probar validaciones matemáticas y detección de duplicados
  - Verificar almacenamiento de imágenes y metadatos
  - _Requerimientos: 2.2, 2.3, 2.4, 2.8_

- [ ] 7. Interfaz web optimizada para captura con cámara
- [ ] 7.1 Crear interfaz de captura de imagen del E-14
  - Implementar acceso a cámara del dispositivo móvil/tablet
  - Crear vista previa de imagen con guías de alineación para el formulario
  - Implementar captura de foto con validación de calidad automática
  - Agregar funcionalidad de recorte y ajuste de imagen
  - _Requerimientos: 2.2, 7.4_

- [ ] 7.2 Crear interfaz de selección de tipo de elección y formulario dinámico
  - Implementar selector de tipo de elección para mostrar todos los procesos activos de la mesa
  - Crear formulario HTML dinámico que se adapte al tipo de elección seleccionado
  - Mostrar datos reconocidos por OCR específicos para cada tipo de formulario
  - Agregar campos editables para corrección manual de datos OCR por tipo
  - Implementar visualización del texto automático de coincidencia OCR vs manual
  - Mostrar porcentaje y nivel de coincidencia con indicadores visuales (colores)
  - Crear calculadoras automáticas para verificar totales según tipo de elección
  - Implementar comparación visual entre datos OCR y manuales
  - Permitir navegación entre múltiples formularios E-14 de la misma mesa
  - _Requerimientos: 2.2, 2.4, 2.5, 2.6, 2.7, 2.14, 7.1, 7.2, 10.6_

- [ ] 7.3 Implementar interfaz móvil optimizada con cámara
  - Crear diseño responsivo optimizado para tablets y móviles
  - Implementar teclado numérico automático para campos de votos
  - Agregar indicadores visuales de progreso y validación
  - Crear vista de comparación lado a lado (imagen vs datos)
  - _Requerimientos: 7.4, 7.1, 2.8_

- [ ] 7.4 Crear dashboard de testigo electoral con historial de imágenes
  - Implementar vista de mesa asignada con información completa
  - Crear galería de imágenes de formularios capturados
  - Agregar indicadores de estado y tiempo de captura
  - Mostrar nivel de confianza del OCR y discrepancias detectadas
  - _Requerimientos: 7.1, 2.5, 2.8, 9.2_

- [ ] 7.5 Escribir pruebas end-to-end para interfaz de captura con cámara
  - Probar flujo completo desde captura de imagen hasta envío
  - Verificar funcionamiento de cámara en dispositivos móviles
  - Probar validaciones client-side y comparación OCR vs manual
  - Verificar auto-guardado incluyendo imágenes
  - Probar captura obligatoria de reportes de anomalías
  - _Requerimientos: 2.2, 2.4, 2.6, 7.1, 7.4_

- [ ] 8. Servicio de gestión de anomalías electorales
- [ ] 8.1 Implementar AnomalyService
  - Crear función para registrar reportes de anomalías desde formularios E-14
  - Implementar clasificación automática de anomalías por categorías
  - Desarrollar sistema de validación de anomalías por coordinadores
  - Crear generación automática de alertas para anomalías críticas
  - _Requerimientos: 11.1, 11.2, 11.3, 11.5_

- [ ] 8.2 Crear APIs de gestión de anomalías
  - Implementar POST /api/anomalies para crear reportes de anomalías
  - Crear GET /api/anomalies/pending para listar anomalías pendientes de revisión
  - Desarrollar PUT /api/anomalies/{id}/validate para validar anomalías
  - Implementar GET /api/anomalies/statistics para estadísticas de anomalías
  - Crear POST /api/anomalies/export para exportar reportes
  - _Requerimientos: 11.2, 11.3, 11.6, 11.8_

- [ ] 8.3 Implementar consolidación y estadísticas de anomalías
  - Crear función para consolidar anomalías por ubicación geográfica
  - Implementar generación de estadísticas por tipo, gravedad y ubicación
  - Desarrollar detección de patrones anómalos en reportes
  - Crear sistema de escalamiento automático para anomalías críticas
  - _Requerimientos: 11.4, 11.6, 11.7_

- [ ] 8.4 Crear interfaz de gestión de anomalías para coordinadores
  - Implementar dashboard de anomalías por puesto y municipio
  - Crear interfaz de revisión y validación de reportes de anomalías
  - Desarrollar vista de estadísticas y tendencias de anomalías
  - Implementar sistema de comentarios y seguimiento de acciones
  - _Requerimientos: 11.2, 11.3, 11.5, 11.6_

- [ ] 8.5 Escribir pruebas para gestión de anomalías
  - Probar creación y clasificación automática de reportes de anomalías
  - Verificar validación y seguimiento por coordinadores
  - Probar generación de estadísticas y consolidaciones
  - Verificar exportación de reportes para autoridades
  - _Requerimientos: 11.1, 11.2, 11.6, 11.8_

- [ ] 9. Servicio de validación y supervisión
- [ ] 9.1 Implementar ValidationService
  - Crear función para validaciones cruzadas de formularios E-14
  - Implementar detección de anomalías comparando con mesas similares
  - Desarrollar generación de reportes de calidad de datos
  - Integrar validación de reportes de anomalías en el proceso de supervisión
  - _Requerimientos: 3.3, 6.1, 6.2, 6.4, 11.2_

- [ ] 9.2 Crear APIs de validación y supervisión
  - Implementar GET /api/forms/e14/pending-review para formularios pendientes
  - Crear POST /api/forms/e14/{id}/approve para aprobación de coordinadores
  - Desarrollar POST /api/forms/e14/{id}/reject para rechazo con comentarios
  - _Requerimientos: 3.1, 3.2, 3.4, 3.5_

- [ ] 9.3 Implementar detección automática de anomalías
  - Crear algoritmos para detectar valores atípicos estadísticamente
  - Implementar alertas por tiempos de captura excesivos
  - Desarrollar detección de patrones sospechosos de votación
  - _Requerimientos: 6.4, 6.5_

- [ ] 9.4 Escribir pruebas para validación y supervisión
  - Probar validaciones cruzadas y detección de anomalías
  - Verificar flujo de aprobación/rechazo por coordinadores
  - Probar generación de reportes de calidad
  - _Requerimientos: 3.3, 6.1, 6.4_

- [ ] 10. Interfaz de supervisión para coordinadores
- [ ] 10.1 Crear dashboard de coordinador de puesto
  - Implementar vista de todos los formularios E-14 del puesto
  - Crear filtros por estado, fecha y alertas de calidad
  - Agregar funcionalidad de revisión detallada con comentarios
  - Mostrar reportes de anomalías asociados a cada formulario
  - _Requerimientos: 3.1, 3.2, 3.3, 11.2_

- [ ] 10.2 Implementar interfaz de aprobación/rechazo
  - Crear formulario de revisión con campos de comentarios
  - Implementar botones de aprobación y rechazo con confirmación
  - Agregar sistema de notificaciones automáticas a testigos
  - Incluir revisión de reportes de anomalías en el proceso de aprobación
  - _Requerimientos: 3.4, 3.5, 9.4, 11.3_

- [ ] 10.3 Crear reportes de calidad en tiempo real
  - Implementar dashboard con métricas de calidad por puesto
  - Crear gráficos de progreso y estadísticas de validación
  - Agregar alertas visuales para anomalías detectadas
  - Incluir estadísticas de anomalías reportadas por puesto
  - _Requerimientos: 6.5, 8.1, 8.2, 11.6_

- [ ] 10.4 Implementar generación de informes PDF por puesto
  - Crear funcionalidad para generar automáticamente informes PDF cuando todos los E-14 de un puesto estén procesados
  - Implementar plantillas PDF con datos detallados del puesto, fecha, hora y estadísticas
  - Desarrollar inclusión de gráficos estadísticos y resúmenes de anomalías en el PDF
  - Crear sistema de descarga individual de informes PDF por puesto
  - _Requerimientos: 3.6, 3.7, 3.8_

- [ ] 10.5 Escribir pruebas para interfaz de supervisión e informes PDF
  - Probar dashboard de coordinador con datos de prueba
  - Verificar flujo de aprobación/rechazo desde interfaz
  - Probar reportes de calidad y alertas visuales
  - Verificar integración con gestión de anomalías
  - Probar generación automática de informes PDF por puesto
  - _Requerimientos: 3.1, 3.4, 3.6, 6.5, 11.2_

- [ ] 11. Servicio de consolidación municipal y verificación E-24
- [ ] 11.1 Implementar ConsolidationService para múltiples tipos de elecciones con candidatos
  - Crear función para verificar disponibilidad de consolidación por tipo de elección
  - Implementar generación automática de formularios E-24 separados por tipo de elección
  - Desarrollar cálculos automáticos de totales municipales independientes por tipo
  - Crear consolidación separada para cada proceso electoral (Senado, Cámara, CITREP, etc.)
  - Implementar cálculo automático de resultados por candidato durante consolidación
  - Desarrollar cálculo de totales por partido y coalición desde resultados de candidatos
  - Crear generación automática de rankings durante proceso de consolidación
  - _Requerimientos: 4.1, 4.2, 4.3, 16.11, 16.12_

- [ ] 11.2 Implementar E24VerificationService
  - Crear función para procesar imagen del E-24 oficial de Registraduría
  - Implementar comparación automática entre E-24 generado vs E-24 oficial
  - Desarrollar detección de discrepancias con niveles de severidad
  - Crear generación automática de reportes de reclamaciones
  - _Requerimientos: 4.4, 4.5, 4.6, 4.7, 4.8_

- [ ] 11.3 Crear APIs de consolidación y verificación
  - Implementar GET /api/consolidation/{municipio_id}/status para verificar estado
  - Crear POST /api/forms/e24/generate para generar E-24 automáticamente
  - Desarrollar POST /api/forms/e24/{id}/upload-official para subir E-24 oficial
  - Implementar GET /api/forms/e24/{id}/discrepancies para consultar discrepancias
  - Crear POST /api/forms/e24/{id}/generate-claims para generar reclamaciones
  - _Requerimientos: 4.1, 4.2, 4.4, 4.7, 4.8_

- [ ] 11.4 Implementar interfaz de verificación para coordinadores municipales
  - Crear dashboard para mostrar E-24 generado vs E-24 oficial lado a lado
  - Implementar interfaz de captura de foto del E-24 oficial
  - Desarrollar vista de discrepancias detectadas con evidencia fotográfica
  - Crear generador de reportes de reclamaciones con documentación
  - _Requerimientos: 4.4, 4.6, 4.8, 4.9_

- [ ] 11.5 Implementar generación de informes PDF municipales por tipo de elección
  - Crear funcionalidad para generar automáticamente informes PDF separados por tipo de elección
  - Implementar plantillas PDF específicas para cada tipo de elección con consolidación de puestos
  - Desarrollar inclusión de gráficos comparativos entre puestos por tipo de elección
  - Crear informe PDF consolidado general que incluya todos los tipos de elecciones
  - Implementar sistema de descarga de informes PDF individuales y consolidado general
  - _Requerimientos: 4.10, 4.11, 4.12_

- [ ] 11.6 Escribir pruebas para consolidación, verificación E-24 e informes PDF
  - Probar generación automática de E-24 desde múltiples E-14
  - Verificar procesamiento OCR de E-24 oficial y comparación
  - Probar detección de discrepancias y generación de reclamaciones
  - Verificar interfaz de verificación para coordinadores municipales
  - Probar generación automática de informes PDF municipales
  - _Requerimientos: 4.1, 4.2, 4.5, 4.8, 4.10_

- [ ] 12. Servicio de generación de informes PDF
- [ ] 12.1 Implementar PDFReportService
  - Crear función para generar informes PDF detallados por puesto
  - Implementar generación de informes PDF consolidados municipales
  - Desarrollar plantillas PDF profesionales con logos y formato oficial
  - Crear sistema de inclusión de gráficos estadísticos en PDFs
  - _Requerimientos: 3.6, 3.7, 4.10, 4.11_

- [ ] 12.2 Crear APIs de generación de informes PDF
  - Implementar POST /api/reports/puesto/{id}/generate para generar PDF de puesto
  - Crear POST /api/reports/municipal/{id}/generate para generar PDF municipal
  - Desarrollar GET /api/reports/{id}/download para descargar PDFs generados
  - Implementar GET /api/reports/status/{id} para verificar estado de generación
  - _Requerimientos: 3.8, 4.12_

- [ ] 12.3 Implementar modelos y almacenamiento de informes PDF
  - Crear modelo PDFReport para almacenar metadatos de informes generados
  - Implementar modelo ReportStatistics para estadísticas incluidas en informes
  - Desarrollar sistema de almacenamiento seguro de archivos PDF
  - Crear sistema de hash de integridad para verificar PDFs
  - _Requerimientos: 3.7, 4.11_

- [ ] 12.4 Crear plantillas y diseño de informes PDF
  - Diseñar plantilla profesional para informes de puesto con datos detallados
  - Crear plantilla de informe municipal con consolidación de puestos
  - Implementar inclusión automática de fecha, hora y firmas digitales
  - Desarrollar gráficos estadísticos integrados (participación, anomalías, etc.)
  - _Requerimientos: 3.6, 3.7, 4.10, 4.11_

- [ ] 12.5 Escribir pruebas para servicio de informes PDF
  - Probar generación de PDFs por puesto con datos completos
  - Verificar generación de PDFs municipales con consolidación
  - Probar descarga y almacenamiento de archivos PDF
  - Verificar integridad y formato de PDFs generados
  - _Requerimientos: 3.6, 3.8, 4.10, 4.12_

- [ ] 13. Sistema de trazabilidad y auditoría
- [ ] 13.1 Implementar AuditService extendido
  - Crear función para logging automático de todas las acciones
  - Implementar generación de reportes de trazabilidad por mesa
  - Desarrollar detección de patrones anómalos en el proceso
  - Incluir trazabilidad de reportes de anomalías en el sistema de auditoría
  - Incluir trazabilidad de generación de informes PDF en el sistema
  - _Requerimientos: 5.1, 5.2, 5.3, 5.4, 11.7_

- [ ] 13.2 Crear APIs de auditoría y trazabilidad
  - Implementar GET /api/audit/mesa/{id}/timeline para línea de tiempo
  - Crear GET /api/audit/patterns/anomalous para patrones anómalos
  - Desarrollar POST /api/audit/export para exportación de logs
  - _Requerimientos: 5.3, 5.5_

- [ ] 13.3 Implementar sistema de alertas automáticas
  - Crear alertas por retrasos significativos en el proceso
  - Implementar notificaciones por patrones anómalos detectados
  - Desarrollar escalamiento automático de problemas críticos
  - _Requerimientos: 5.4, 8.3_

- [ ] 13.4 Escribir pruebas para sistema de auditoría
  - Probar logging automático de acciones y generación de reportes
  - Verificar detección de patrones anómalos y alertas
  - Probar exportación de logs y trazabilidad completa
  - _Requerimientos: 5.1, 5.2, 5.3_

- [ ] 14. Reportes y monitoreo en tiempo real
- [ ] 14.1 Implementar dashboards de progreso en tiempo real con mapas de calor
  - Crear dashboard con progreso por departamento y municipio
  - Implementar mapas de calor del progreso geográfico con múltiples métricas
  - Desarrollar visualización de densidad de progreso por mesa, puesto y municipio
  - Crear alternancia entre diferentes tipos de mapas de calor (completitud, participación, anomalías)
  - Desarrollar gráficos de velocidad de procesamiento
  - Incluir métricas de anomalías reportadas en dashboards
  - Incluir métricas de informes PDF generados en dashboards
  - Implementar exportación de capturas de mapas de calor para reportes
  - _Requerimientos: 8.1, 8.2, 8.4, 8.5, 8.6, 11.6_

- [ ] 14.2 Crear sistema de métricas y KPIs
  - Implementar cálculo de porcentajes de avance en tiempo real
  - Crear métricas de calidad de datos por nivel geográfico
  - Desarrollar indicadores de rendimiento del proceso
  - _Requerimientos: 8.2, 8.5_

- [ ] 14.3 Implementar alertas automáticas de monitoreo
  - Crear alertas por retrasos significativos en captura
  - Implementar notificaciones por problemas de calidad masivos
  - Desarrollar alertas de disponibilidad del sistema
  - _Requerimientos: 8.3, 13.2_

- [ ] 14.4 Escribir pruebas para reportes y monitoreo
  - Probar dashboards con datos de prueba masivos
  - Verificar cálculo de métricas y KPIs en tiempo real
  - Probar sistema de alertas automáticas
  - _Requerimientos: 8.1, 8.2, 8.3_

- [ ] 15. Panel de administración integral con gestión de testigos
- [ ] 15.1 Implementar AdminPanelService extendido con gestión de candidatos
  - Crear servicio para configuración de jornadas electorales con múltiples elecciones
  - Implementar carga y gestión de plantillas E-14 por tipo de elección
  - Desarrollar actualización de datos DIVIPOLA desde archivos CSV
  - Crear generación de reportes administrativos del sistema
  - Implementar gestión de usuarios, roles y permisos
  - Integrar gestión completa de candidatos, partidos y coaliciones
  - Desarrollar herramientas de validación de candidatos con tarjetones oficiales
  - Crear dashboards de resultados por candidato y partido en tiempo real
  - _Requerimientos: 12.1, 12.2, 12.3, 12.4, 12.14, 16.1, 16.14, 16.18_

- [ ] 15.2 Implementar WitnessManagementService completo
  - Crear función para carga masiva de testigos desde archivos CSV
  - Implementar creación individual de testigos con validación de datos
  - Desarrollar asignación de testigos a mesas específicas
  - Crear función de reasignación de testigos entre mesas del mismo puesto
  - Implementar gestión de testigos suplentes con prioridades
  - Desarrollar activación automática de suplentes cuando titular no se presenta
  - Implementar validación de cobertura completa de mesas
  - Desarrollar generación de reportes de asignación por ubicación
  - Crear sistema de búsqueda avanzada con múltiples filtros
  - Implementar histórico completo de asignaciones y cambios
  - _Requerimientos: 12.5, 12.6, 12.8, 12.9, 12.10, 12.20, 12.21, 12.22, 12.23_

- [ ] 15.3 Crear modelos de datos completos para gestión de testigos
  - Implementar modelo Witness con información personal y de contacto
  - Crear modelo WitnessAssignment para historial de asignaciones
  - Implementar modelo WitnessCredentials para gestión de acceso
  - Crear modelo SubstituteWitness para gestión de suplentes
  - Implementar modelo AssignmentHistory para trazabilidad completa
  - Definir enumeraciones WitnessStatus, AssignmentStatus y AssignmentAction
  - Establecer relaciones entre testigos, mesas, suplentes y ubicaciones geográficas
  - _Requerimientos: 12.5, 12.8, 12.9, 12.17, 12.20, 12.22_

- [ ] 15.4 Crear APIs completas de gestión de testigos
  - Implementar POST /api/admin/witnesses/upload-csv para carga masiva
  - Crear POST /api/admin/witnesses para crear testigos individuales
  - Desarrollar POST /api/admin/witnesses/{id}/assign para asignar a mesa
  - Implementar PUT /api/admin/witnesses/{id}/reassign para reasignaciones
  - Crear POST /api/admin/witnesses/{id}/assign-substitute para asignar suplentes
  - Implementar POST /api/admin/witnesses/{id}/activate-substitute para activar suplentes
  - Desarrollar POST /api/admin/witnesses/{id}/generate-credentials para generar credenciales
  - Crear POST /api/admin/witnesses/bulk-credentials para generación masiva
  - Implementar POST /api/admin/witnesses/{id}/send-credentials para enviar credenciales
  - Desarrollar GET /api/admin/witnesses/search para búsqueda avanzada
  - Crear GET /api/admin/witnesses/{id}/history para histórico de asignaciones
  - Implementar GET /api/admin/witnesses/unassigned/{municipio_id} para testigos disponibles
  - Desarrollar GET /api/admin/coverage/validate/{puesto_id} para validar cobertura
  - Crear GET /api/admin/reports/assignments/{location_id} para reportes
  - _Requerimientos: 12.6, 12.7, 12.8, 12.9, 12.10, 12.17, 12.18, 12.19, 12.20, 12.21, 12.22, 12.23_

- [ ] 15.5 Crear interfaz web del panel de administración con gestión de testigos
  - Implementar dashboard administrativo con estadísticas del sistema
  - Crear interfaz para configurar cantidad y tipos de elecciones simultáneas
  - Desarrollar formulario de carga de plantillas E-14 personalizadas
  - Implementar interfaz de actualización de datos DIVIPOLA
  - Crear módulo de gestión de testigos con carga masiva desde CSV
  - Desarrollar interfaz visual de asignación con arrastrar y soltar
  - Implementar vista de mesas por municipio, puesto y mesa con estado de asignación
  - Crear herramientas de validación de cobertura con alertas visuales
  - Desarrollar herramientas de gestión de usuarios y roles
  - _Requerimientos: 12.1, 12.2, 12.4, 12.5, 12.6, 12.7, 12.8, 12.14_

- [ ] 15.6 Implementar interfaz de asignación visual de testigos
  - Crear vista jerárquica de departamento > municipio > puesto > mesa
  - Implementar funcionalidad de arrastrar y soltar testigos a mesas
  - Desarrollar indicadores visuales de cobertura (verde: asignado, amarillo: solo suplente, rojo: sin testigo)
  - Crear panel lateral con lista de testigos disponibles por municipio
  - Implementar filtros por ubicación geográfica y estado de asignación
  - Desarrollar validación en tiempo real de asignaciones
  - Crear interfaz para asignar testigos suplentes con indicadores de prioridad
  - Implementar búsqueda rápida de testigos por nombre o cédula
  - _Requerimientos: 12.7, 12.8, 12.9, 12.20, 12.23_

- [ ] 15.7 Implementar sistema de credenciales y acceso para testigos
  - Crear generador automático de usuarios y contraseñas seguras
  - Implementar sistema de envío de credenciales por SMS, email y WhatsApp
  - Desarrollar generador de códigos QR con credenciales de acceso
  - Crear interfaz de gestión masiva de credenciales
  - Implementar sistema de validación de credenciales en login
  - Desarrollar funcionalidad de reseteo de contraseñas
  - Crear reportes de testigos sin credenciales generadas
  - _Requerimientos: 12.17, 12.18, 12.19, 12.24_

- [ ] 15.8 Implementar gestión avanzada de testigos suplentes
  - Crear interfaz para asignar múltiples suplentes por mesa con prioridades
  - Implementar activación automática de suplentes cuando titular no se presenta
  - Desarrollar notificaciones automáticas a suplentes cuando son activados
  - Crear dashboard de estado de suplentes por puesto y municipio
  - Implementar histórico de activaciones de suplentes
  - Desarrollar reportes de utilización de suplentes
  - _Requerimientos: 12.20, 12.21, 12.22_

- [ ] 15.9 Implementar búsqueda avanzada y reportes de testigos
  - Crear sistema de búsqueda por múltiples criterios (nombre, cédula, municipio, estado)
  - Implementar filtros avanzados con operadores lógicos
  - Desarrollar exportación de resultados de búsqueda a CSV/Excel
  - Crear reportes estadísticos de testigos por ubicación geográfica
  - Implementar reportes de cobertura con gráficos visuales
  - Desarrollar histórico completo de cambios y asignaciones
  - Crear dashboard de métricas de gestión de testigos
  - _Requerimientos: 12.10, 12.22, 12.23_

- [ ] 15.10 Implementar sistema de mensajes generales
  - Crear SystemMessageService para mensajes del sistema
  - Implementar creación y programación de mensajes generales
  - Desarrollar difusión de mensajes por roles específicos
  - Crear interfaz de gestión de mensajes para administradores
  - Incluir notificaciones específicas para testigos sobre credenciales y asignaciones
  - _Requerimientos: 12.12, 12.18_

- [ ] 15.11 Implementar centro de impresión extendido
  - Crear PrintCenterService para gestión de impresiones
  - Implementar impresión de informes PDF generados
  - Desarrollar impresión de evidencias fotográficas con layouts personalizados
  - Crear cola de impresión para múltiples documentos
  - Implementar configuración de impresoras y plantillas de impresión
  - Incluir impresión de reportes de asignación de testigos
  - Desarrollar impresión de credenciales y códigos QR para testigos
  - Crear impresión de listados de testigos por puesto y municipio
  - _Requerimientos: 12.11, 12.10, 12.24_

- [ ] 15.12 Crear APIs de administración extendidas
  - Implementar POST /api/admin/configure-journey para configurar jornadas
  - Crear POST /api/admin/upload-template para cargar plantillas E-14
  - Desarrollar POST /api/admin/update-divipola para actualizar datos geográficos
  - Implementar GET /api/admin/system-stats para estadísticas del sistema
  - Crear POST /api/admin/broadcast-message para mensajes generales
  - Desarrollar POST /api/admin/print-documents para impresiones
  - Incluir todas las APIs de gestión de testigos desarrolladas en 15.4
  - _Requerimientos: 12.1, 12.2, 12.4, 12.11, 12.12_

- [ ] 15.13 Escribir pruebas completas para panel de administración con gestión de testigos
  - Probar configuración de jornadas con múltiples elecciones
  - Verificar carga de plantillas E-14 y actualización DIVIPOLA
  - Probar carga masiva de testigos desde CSV
  - Verificar asignación y reasignación de testigos a mesas
  - Probar gestión de testigos suplentes y activación automática
  - Verificar generación y envío de credenciales por múltiples canales
  - Probar generación de códigos QR para acceso rápido
  - Verificar búsqueda avanzada y filtros de testigos
  - Probar validación de cobertura completa de mesas
  - Verificar interfaz visual de asignación con arrastrar y soltar
  - Probar generación de reportes de asignación y estadísticas
  - Verificar histórico completo de asignaciones y cambios
  - Probar sistema de mensajes generales y centro de impresión
  - Verificar gestión de usuarios y estadísticas del sistema
  - _Requerimientos: 12.1, 12.2, 12.4, 12.5, 12.6, 12.7, 12.8, 12.10, 12.17, 12.18, 12.19, 12.20, 12.21, 12.22, 12.23, 12.24_

- [ ] 16. Interfaces diferenciadas por rol y dispositivo
- [ ] 16.1 Implementar RoleBasedUIService
  - Crear servicio para detectar rol y dispositivo del usuario
  - Implementar generación de configuración de interfaz específica por rol
  - Desarrollar sistema de filtrado de datos según permisos de rol
  - Crear generación de menús de navegación contextuales
  - Implementar sistema de widgets de dashboard específicos por rol
  - Desarrollar validación de acceso a acciones por rol
  - _Requerimientos: 15.1, 15.7, 15.9_

- [ ] 16.2 Crear modelos de configuración de interfaces
  - Implementar modelo UIConfiguration para configuración por rol y dispositivo
  - Crear modelo NavigationMenu para menús contextuales
  - Desarrollar modelo DashboardWidget para widgets específicos
  - Implementar modelo MobileLayoutConfig para layouts móviles
  - Crear enumeraciones UserRole, DeviceType, LayoutType
  - _Requerimientos: 15.1, 15.2, 15.3, 15.4_

- [ ] 16.3 Desarrollar interfaz móvil simplificada para testigos
  - Crear vista móvil que muestre solo mesa asignada y formularios activos
  - Implementar navegación con máximo 2 niveles de profundidad
  - Desarrollar botones grandes optimizados para pantallas táctiles
  - Crear accesos directos a captura de formularios y estado de progreso
  - Implementar notificaciones push específicas para testigos
  - Ocultar funcionalidades administrativas y de coordinación
  - _Requerimientos: 15.2, 15.6, 15.8_

- [ ] 16.4 Desarrollar interfaz móvil optimizada para coordinadores
  - Crear vista móvil que muestre solo mesas de su puesto/municipio
  - Implementar dashboard con validaciones pendientes y alertas de cobertura
  - Desarrollar acceso rápido a reportes de anomalías y aprobaciones
  - Crear navegación contextual con máximo 3 niveles
  - Implementar notificaciones específicas para coordinadores
  - Ocultar funcionalidades de administración general
  - _Requerimientos: 15.3, 15.6, 15.8_

- [ ] 16.5 Desarrollar interfaz completa de escritorio para administradores
  - Crear interfaz completa con acceso a todas las funcionalidades
  - Implementar dashboard administrativo con múltiples widgets
  - Desarrollar navegación completa con sidebar y menús desplegables
  - Crear herramientas avanzadas de gestión y configuración
  - Implementar vistas de datos complejas y reportes detallados
  - _Requerimientos: 15.4, 15.7, 15.10_

- [ ] 16.6 Implementar detección automática de dispositivo y adaptación
  - Crear sistema de detección de tipo de dispositivo (móvil, tablet, escritorio)
  - Implementar adaptación automática de tamaños de elementos
  - Desarrollar sistema de breakpoints responsivos
  - Crear optimización automática de imágenes según dispositivo
  - Implementar carga diferida de componentes según capacidad del dispositivo
  - _Requerimientos: 15.5, 15.6_

- [ ] 16.7 Crear APIs de configuración de interfaces
  - Implementar GET /api/ui/config/{user_id} para obtener configuración de interfaz
  - Crear GET /api/ui/navigation/{role} para obtener menú de navegación
  - Desarrollar GET /api/ui/dashboard/{role} para obtener widgets de dashboard
  - Implementar GET /api/ui/actions/{role} para obtener acciones disponibles
  - Crear POST /api/ui/preferences para guardar preferencias de usuario
  - _Requerimientos: 15.1, 15.7, 15.9_

- [ ] 16.8 Escribir pruebas para interfaces diferenciadas
  - Probar detección automática de rol y dispositivo
  - Verificar generación correcta de interfaces por rol
  - Probar adaptación responsiva en diferentes dispositivos
  - Verificar ocultación de funcionalidades según rol
  - Probar navegación contextual y accesos directos
  - Verificar rendimiento en dispositivos móviles
  - _Requerimientos: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [ ] 17. Sistema de mapas y geolocalización en tiempo real
- [ ] 16.1 Implementar MapService con OpenStreetMap y mapas de calor
  - Integrar biblioteca Leaflet para mapas interactivos gratuitos y veloces
  - Crear función para inicializar datos del mapa con coordenadas GPS
  - Implementar generación de marcadores para mesas y puestos electorales
  - Desarrollar actualización de estado de marcadores en tiempo real
  - Implementar generación de datos de mapa de calor basado en métricas de progreso
  - Crear cálculo de densidad de progreso por zonas geográficas
  - _Requerimientos: 13.1, 13.2, 13.9, 13.10, 13.12_

- [ ] 16.2 Implementar geolocalización y navegación
  - Crear función para obtener ubicación actual del usuario mediante GPS
  - Implementar cálculo de rutas desde ubicación actual hasta mesas específicas
  - Desarrollar búsqueda de ubicaciones por nombre, código o dirección
  - Crear función para encontrar mesas cercanas a una ubicación específica
  - _Requerimientos: 13.3, 13.6, 13.9_

- [ ] 16.3 Crear interfaz de mapa interactivo con mapa de calor
  - Implementar mapa web con navegación, zoom y desplazamiento
  - Crear marcadores con diferentes colores según estado de mesas
  - Desarrollar ventanas emergentes con información detallada de mesas
  - Implementar filtros por departamento, municipio, puesto y estado
  - Crear alternancia entre vista de marcadores y vista de mapa de calor
  - Implementar gradiente visual con escala de colores para intensidad de progreso
  - Desarrollar capas de mapa de calor para diferentes métricas (completitud, participación, anomalías)
  - Crear vista optimizada para dispositivos móviles con GPS
  - _Requerimientos: 13.4, 13.5, 13.7, 13.8, 13.9, 13.10, 13.11_

- [ ] 16.4 Crear APIs de mapas, geolocalización y mapa de calor
  - Implementar GET /api/map/markers para obtener marcadores del mapa
  - Crear POST /api/map/update-status para actualizar estado de marcadores
  - Desarrollar GET /api/map/user-location para geolocalización del usuario
  - Implementar GET /api/map/route para cálculo de rutas
  - Crear GET /api/map/search para búsqueda de ubicaciones
  - Implementar GET /api/map/heatmap/{metric} para obtener datos de mapa de calor
  - Crear POST /api/map/heatmap/update para actualizar mapa de calor en tiempo real
  - Desarrollar GET /api/map/heatmap/export para exportar imagen del mapa de calor
  - _Requerimientos: 13.2, 13.3, 13.6, 13.9, 13.10, 13.12, 13.14_

- [ ] 16.5 Implementar modelos y lógica de mapa de calor
  - Crear modelo HeatmapData para almacenar datos de mapa de calor
  - Implementar modelo HeatmapPoint para puntos individuales con intensidad
  - Desarrollar modelo ProgressDensity para cálculo de densidad por área
  - Crear enumeraciones HeatmapMetric y AreaLevel para diferentes tipos de métricas
  - Implementar algoritmos de cálculo de intensidad basados en progreso de recolección
  - _Requerimientos: 13.9, 13.10, 13.12_

- [ ] 16.6 Escribir pruebas para sistema de mapas y mapa de calor
  - Probar inicialización de mapas con datos DIVIPOLA
  - Verificar geolocalización y cálculo de rutas
  - Probar actualización de marcadores en tiempo real
  - Verificar funcionamiento en dispositivos móviles
  - Probar generación de mapas de calor con diferentes métricas
  - Verificar actualización en tiempo real de mapas de calor
  - _Requerimientos: 13.1, 13.3, 13.9, 13.10, 13.12, 13.14_

- [ ] 19. Optimización y recuperación del proceso
- [ ] 19.1 Implementar sistema de recuperación automática
  - Crear función para detectar y recuperar sesiones interrumpidas
  - Implementar backup automático cada 15 minutos durante proceso activo
  - Desarrollar herramientas de recuperación manual para casos excepcionales
  - _Requerimientos: 14.1, 14.2, 14.3, 14.5_

- [ ] 17.2 Optimizar rendimiento para carga masiva
  - Implementar caché local de formularios en progreso
  - Crear procesamiento asíncrono para validaciones masivas
  - Desarrollar optimización de consultas para consolidaciones
  - _Requerimientos: 14.4, 7.3_

- [ ] 17.3 Crear herramientas de administración del proceso
  - Implementar panel de control para administradores del proceso
  - Crear herramientas de diagnóstico y resolución de problemas
  - Desarrollar funciones de reinicio y recuperación de procesos
  - _Requerimientos: 14.5, 5.4_

- [ ] 17.4 Escribir pruebas de recuperación y rendimiento
  - Probar recuperación automática de sesiones interrumpidas
  - Verificar rendimiento con simulación de carga masiva
  - Probar herramientas de administración y diagnóstico
  - _Requerimientos: 14.1, 14.2, 14.4_

- [ ] 18. Dashboards y reportes visuales de candidatos
- [ ] 18.1 Implementar dashboards visuales de resultados
  - Crear dashboard principal con gráficos de resultados por candidato
  - Implementar gráficos de torta para distribución de votos por partido
  - Desarrollar gráficos de barras para rankings de candidatos
  - Crear mapas de calor geográficos con resultados por candidato
  - Implementar gráficos de líneas para tendencias de votación
  - Desarrollar indicadores KPI para métricas principales de candidatos
  - _Requerimientos: 16.18_

- [ ] 18.2 Crear APIs de dashboards y visualización
  - Implementar GET /api/dashboards/candidates/{election_type_id} para datos de dashboard
  - Crear GET /api/charts/pie-chart/{party_id} para gráficos de torta
  - Desarrollar GET /api/charts/bar-chart/{election_type_id} para gráficos de barras
  - Implementar GET /api/maps/candidate-heatmap/{candidate_id} para mapas de calor
  - Crear GET /api/reports/candidate/{id}/detailed para reportes detallados
  - Desarrollar GET /api/reports/comparative-parties para reportes comparativos
  - _Requerimientos: 16.17, 16.18_

- [ ] 18.3 Implementar exportación de reportes de candidatos
  - Crear exportación de resultados en formato PDF con gráficos
  - Implementar exportación a Excel con datos detallados por candidato
  - Desarrollar exportación a CSV para análisis externos
  - Crear exportación de mapas de calor como imágenes
  - Implementar generación de reportes oficiales para autoridades electorales
  - _Requerimientos: 16.17_

- [ ] 18.4 Crear interfaz web de dashboards de candidatos
  - Implementar dashboard interactivo con filtros por tipo de elección
  - Crear vista de resultados en tiempo real durante proceso electoral
  - Desarrollar interfaz de comparación entre candidatos y partidos
  - Implementar vista de distribución geográfica con mapas interactivos
  - Crear herramientas de análisis histórico y tendencias
  - _Requerimientos: 16.18_

- [ ] 18.5 Escribir pruebas para dashboards y reportes
  - Probar generación de gráficos con datos de prueba
  - Verificar cálculos de métricas y KPIs de candidatos
  - Probar exportación en múltiples formatos
  - Verificar actualización en tiempo real de dashboards
  - Probar interfaz interactiva con filtros y comparaciones
  - _Requerimientos: 16.17, 16.18_

- [ ] 19. Sistema de alertas para testigos faltantes y cobertura de mesas
- [ ] 19.1 Implementar WitnessAlertService
  - Crear función para detectar automáticamente mesas huérfanas (sin testigo asignado o inactivo)
  - Implementar generación automática de alertas cuando una mesa no tenga cobertura
  - Desarrollar cálculo en tiempo real del porcentaje de cobertura por puesto
  - Crear sistema de escalamiento automático a coordinadores municipales cuando cobertura < 80%
  - _Requerimientos: 14.1, 14.2, 14.4, 14.9_

- [ ] 19.2 Implementar sistema de notificaciones múltiples
  - Crear función para enviar notificaciones push a dispositivos móviles de testigos
  - Implementar envío de SMS a testigos disponibles sobre mesas faltantes
  - Desarrollar envío de emails con información detallada de mesas que necesitan cobertura
  - Crear sistema de notificación a todos los testigos del puesto sobre mesas huérfanas
  - _Requerimientos: 14.3, 14.6_

- [ ] 19.3 Crear APIs de gestión de alertas y cobertura
  - Implementar GET /api/alerts/orphan-mesas/{puesto_id} para obtener mesas huérfanas
  - Crear POST /api/alerts/generate para generar alertas automáticas
  - Desarrollar POST /api/alerts/notify-witnesses para notificar testigos disponibles
  - Implementar GET /api/coverage/puesto/{id} para obtener reporte de cobertura en tiempo real
  - Crear POST /api/coverage/accept para que testigos acepten cobertura de mesas
  - Desarrollar GET /api/alerts/history para obtener histórico de alertas
  - _Requerimientos: 14.2, 14.3, 14.4, 14.5, 14.10_

- [ ] 19.4 Implementar modelos de datos para alertas
  - Crear modelo WitnessAlert para almacenar alertas generadas
  - Implementar modelo CoverageReport para reportes de cobertura por ubicación
  - Desarrollar modelo WitnessAvailability para gestionar disponibilidad de testigos
  - Crear enumeraciones AlertType, AlertPriority, AlertStatus para clasificación
  - _Requerimientos: 14.1, 14.4, 14.8, 14.10_

- [ ] 19.5 Integrar alertas con sistema de mapas
  - Implementar marcadores especiales parpadeantes rojos para mesas huérfanas en el mapa
  - Crear actualización automática de marcadores cuando se detecten mesas sin testigo
  - Desarrollar filtros en el mapa para mostrar solo mesas que necesitan cobertura
  - Implementar notificaciones geográficas basadas en proximidad de testigos
  - _Requerimientos: 14.7_

- [ ] 19.6 Crear interfaz de gestión de alertas para coordinadores
  - Implementar dashboard de cobertura en tiempo real por puesto
  - Crear vista de alertas activas con opciones de gestión manual
  - Desarrollar interfaz para asignar manualmente testigos a mesas huérfanas
  - Implementar reportes de cobertura históricos y estadísticas
  - _Requerimientos: 14.4, 14.8, 14.9_

- [ ] 19.7 Implementar interfaz móvil para testigos
  - Crear notificaciones push nativas en aplicación móvil
  - Implementar botón de "Aceptar Cobertura" para mesas disponibles
  - Desarrollar vista de mesas cercanas que necesitan testigo
  - Crear sistema de confirmación de disponibilidad para testigos
  - _Requerimientos: 14.3, 14.5, 14.6_

- [ ] 19.8 Escribir pruebas para sistema de alertas
  - Probar detección automática de mesas huérfanas
  - Verificar generación y envío de notificaciones múltiples
  - Probar cálculo de cobertura en tiempo real
  - Verificar escalamiento automático a coordinadores municipales
  - Probar integración con sistema de mapas
  - _Requerimientos: 14.1, 14.2, 14.4, 14.6, 14.7, 14.9_

- [ ] 20. Optimización y recuperación del proceso
- [ ] 20.1 Implementar sistema de recuperación automática
  - Crear APIs de integración con módulos existentes del sistema
  - Implementar sincronización de usuarios y permisos
  - Desarrollar exportación de datos para módulos posteriores
  - Incluir exportación de reportes de anomalías para autoridades
  - Incluir integración de informes PDF con sistema principal
  - Integrar panel de administración con sistema principal
  - Integrar sistema de mapas con módulos existentes
  - Integrar sistema de alertas de testigos con módulos existentes
  - _Requerimientos: 1.1, 5.5, 11.8, 14.10_

- [ ] 20.2 Optimizar rendimiento para carga masiva
  - Crear configuraciones optimizadas para proceso electoral
  - Implementar monitoreo específico para recolección de datos
  - Desarrollar scripts de inicialización del proceso electoral
  - Configurar sistema de notificaciones push, SMS y email para producción
  - _Requerimientos: 1.5, 8.5, 14.6_

- [ ] 20.3 Crear herramientas de administración del proceso
  - Documentar flujo completo de recolección de datos
  - Crear manuales de usuario por rol específico
  - Desarrollar guías de resolución de problemas comunes
  - Incluir documentación del sistema de reportes de anomalías
  - Incluir documentación de generación de informes PDF
  - Documentar panel de administración y todas sus funcionalidades
  - Documentar sistema de mapas y geolocalización
  - Documentar sistema de alertas para testigos faltantes y procedimientos de cobertura
  - _Requerimientos: 5.5, 15.5, 11.8, 12.10, 13.1, 14.8_

- [ ] 20.4 Escribir pruebas de recuperación y rendimiento
  - Probar recuperación automática de sesiones interrumpidas
  - Verificar rendimiento con simulación de carga masiva
  - Probar herramientas de administración y diagnóstico
  - _Requerimientos: 17.1, 17.2, 17.4_

- [ ] 21. Integración y configuración final
- [ ] 21.1 Integrar con sistema electoral principal
  - Crear APIs de integración con módulos existentes del sistema
  - Implementar sincronización de usuarios y permisos
  - Desarrollar exportación de datos para módulos posteriores
  - Incluir exportación de reportes de anomalías para autoridades
  - Incluir integración de informes PDF con sistema principal
  - Integrar panel de administración con sistema principal
  - Integrar sistema de mapas con módulos existentes
  - Integrar sistema de alertas de testigos con módulos existentes
  - Integrar dashboards de candidatos con sistema principal
  - Incluir exportación de resultados por candidato y partido
  - _Requerimientos: 1.1, 5.5, 11.8, 14.10, 16.17_

- [ ] 21.2 Configurar entorno de producción específico
  - Crear configuraciones optimizadas para proceso electoral
  - Implementar monitoreo específico para recolección de datos
  - Desarrollar scripts de inicialización del proceso electoral
  - Configurar sistema de notificaciones push, SMS y email para producción
  - Configurar dashboards de candidatos para producción
  - _Requerimientos: 1.5, 8.5, 14.6, 16.18_

- [ ] 21.3 Crear documentación del proceso de recolección
  - Documentar flujo completo de recolección de datos
  - Crear manuales de usuario por rol específico
  - Desarrollar guías de resolución de problemas comunes
  - Incluir documentación del sistema de reportes de anomalías
  - Incluir documentación de generación de informes PDF
  - Documentar panel de administración y todas sus funcionalidades
  - Documentar sistema de mapas y geolocalización
  - Documentar sistema de alertas para testigos faltantes y procedimientos de cobertura
  - Documentar gestión completa de candidatos, partidos y coaliciones
  - Incluir documentación de dashboards y reportes de candidatos
  - _Requerimientos: 5.5, 15.5, 11.8, 12.10, 13.1, 14.8, 16.1, 16.18_

- [ ] 21.4 Escribir pruebas de integración completas
  - Probar flujo completo desde configuración hasta consolidación
  - Verificar integración con sistema electoral principal
  - Probar proceso completo con datos reales de DIVIPOLA
  - Verificar flujo completo incluyendo gestión de anomalías
  - Probar generación completa de informes PDF por puesto y municipio
  - Verificar funcionamiento completo del panel de administración
  - Probar sistema de mapas con geolocalización en tiempo real
  - Verificar sistema completo de alertas para testigos faltantes
  - Probar gestión completa de candidatos desde carga hasta reportes
  - Verificar cálculo de resultados por candidato, partido y coalición
  - Probar dashboards visuales con datos reales de candidatos
  - _Requerimientos: 1.1, 4.5, 5.5, 11.1, 12.1, 13.1, 14.1, 16.1, 16.11, 16.18_