# Requirements Document - Dashboard Testigo con OCR

## Introduction

Este documento define los requisitos para implementar el dashboard del testigo electoral con capacidades de reconocimiento óptico de caracteres (OCR) para procesar formularios E14. El sistema permitirá a los testigos de mesa capturar, procesar y validar datos de votación mediante fotografías de formularios físicos, reduciendo errores de transcripción manual y acelerando el proceso de reporte de resultados.

## Glossary

- **Sistema**: Dashboard del testigo electoral con OCR
- **Testigo**: Usuario con rol de testigo electoral asignado a una mesa de votación
- **E14**: Formulario físico de escrutinio de mesa utilizado para registrar votos
- **OCR**: Optical Character Recognition (Reconocimiento Óptico de Caracteres)
- **Mesa**: Mesa de votación específica en un puesto electoral
- **Zona OCR**: Área rectangular definida en el formulario E14 donde se extraerá texto
- **Confianza**: Porcentaje de certeza del OCR sobre el texto extraído (0-100%)
- **Admin**: Usuario administrador que configura la estructura del E14
- **Estructura E14**: Configuración de posiciones y zonas OCR del formulario

## Requirements

### Requirement 1: Subir y Procesar Imagen E14

**User Story:** Como testigo electoral, quiero subir una foto del formulario E14 físico para que el sistema extraiga automáticamente los números de votos, de manera que pueda reportar resultados rápidamente sin errores de transcripción.

#### Acceptance Criteria

1. WHEN el testigo selecciona una imagen del formulario E14, THE Sistema SHALL validar que el formato sea JPG, PNG o PDF
2. WHEN el testigo selecciona una imagen, THE Sistema SHALL validar que el tamaño no exceda 10MB
3. WHEN la imagen es válida, THE Sistema SHALL mostrar una vista previa antes de procesar
4. WHEN el testigo confirma la subida, THE Sistema SHALL enviar la imagen al servidor mediante POST a `/api/testigo/subir-e14-ocr`
5. WHEN el servidor recibe la imagen, THE Sistema SHALL guardar la imagen en `uploads/e14/originales/` con nombre único basado en mesa_id y timestamp

### Requirement 2: Procesamiento OCR Automático

**User Story:** Como testigo electoral, quiero que el sistema procese automáticamente la foto del E14 y extraiga los números de votos, para que no tenga que transcribir manualmente cada número.

#### Acceptance Criteria

1. WHEN el servidor recibe una imagen E14, THE Sistema SHALL preprocesar la imagen aplicando escala de grises, mejora de contraste y eliminación de ruido
2. WHEN la imagen está preprocesada, THE Sistema SHALL obtener la estructura E14 configurada por el admin para esa elección
3. WHEN tiene la estructura E14, THE Sistema SHALL extraer texto de cada zona OCR definida usando Tesseract
4. WHEN extrae texto de una zona, THE Sistema SHALL convertir el texto a número entero y calcular el nivel de confianza
5. WHEN completa todas las zonas, THE Sistema SHALL retornar los datos extraídos con confianza promedio y total de votos
6. IF el OCR falla en una zona, THEN THE Sistema SHALL asignar valor 0 y confianza 0% a esa posición

### Requirement 3: Visualización de Resultados OCR en Formulario Completo

**User Story:** Como testigo electoral, quiero ver los datos extraídos por el OCR en un formulario completo del E14 con todos los campos editables, para que pueda revisar y corregir cualquier error antes de confirmar.

#### Acceptance Criteria

1. WHEN el OCR completa el procesamiento, THE Sistema SHALL llenar automáticamente el formulario E14 con los datos extraídos
2. WHEN llena el formulario, THE Sistema SHALL incluir: departamento, municipio, zona, puesto, mesa, tipo de elección, horarios, candidatos con partidos y votos, votos especiales, información de votantes, datos del acta y observaciones
3. WHEN muestra el formulario, THE Sistema SHALL mostrar un indicador de estado del OCR (procesando/completado/error)
4. WHEN muestra el formulario, THE Sistema SHALL calcular y mostrar el total de votos automáticamente
5. WHEN muestra el formulario, THE Sistema SHALL validar el total contra votantes habilitados con indicador visual (verde/amarillo/rojo)

### Requirement 4: Edición Completa de Datos del E14

**User Story:** Como testigo electoral, quiero poder editar manualmente todos los campos del formulario E14 extraídos por el OCR, para que pueda corregir errores de lectura y completar información faltante antes de guardar los datos finales.

#### Acceptance Criteria

1. WHEN el testigo modifica cualquier campo del formulario, THE Sistema SHALL permitir la edición sin restricciones
2. WHEN el testigo modifica un campo de votos, THE Sistema SHALL recalcular el total de votos automáticamente
3. WHEN el testigo modifica un campo de votos, THE Sistema SHALL actualizar el indicador de validación (verde/amarillo/rojo)
4. WHEN el testigo modifica un campo numérico, THE Sistema SHALL validar que sea un número entero no negativo
5. WHEN el testigo agrega o elimina candidatos, THE Sistema SHALL actualizar dinámicamente la lista y recalcular totales
6. WHEN el testigo completa los campos del acta, THE Sistema SHALL validar que los campos obligatorios estén llenos antes de permitir envío

### Requirement 5: Captura de Campos Completos del E14

**User Story:** Como testigo electoral, quiero capturar todos los campos del formulario E14 oficial incluyendo información del acta, horarios y datos de votantes, para que el registro sea completo y cumpla con los requisitos legales.

#### Acceptance Criteria

1. WHEN el testigo completa el formulario, THE Sistema SHALL capturar: departamento, municipio, zona, puesto, mesa, tipo de elección
2. WHEN el testigo completa el formulario, THE Sistema SHALL capturar: hora de apertura y hora de cierre de la votación
3. WHEN el testigo completa el formulario, THE Sistema SHALL capturar: candidatos con nombre, partido y votos
4. WHEN el testigo completa el formulario, THE Sistema SHALL capturar: votos en blanco, votos nulos, tarjetas no marcadas y total de tarjetas
5. WHEN el testigo completa el formulario, THE Sistema SHALL capturar: votantes habilitados, votantes que sufragaron y certificados electorales
6. WHEN el testigo completa el formulario, THE Sistema SHALL capturar: número de acta E14, jurado presidente y testigos del acta
7. WHEN el testigo completa el formulario, THE Sistema SHALL capturar: checkboxes de acta firmada y proceso normal
8. WHEN el testigo completa el formulario, THE Sistema SHALL capturar: observaciones detalladas del proceso

### Requirement 6: Confirmación y Guardado de Datos Completos

**User Story:** Como testigo electoral, quiero confirmar los datos revisados y guardarlos en el sistema con toda la información del E14, para que queden registrados oficialmente los resultados completos de mi mesa.

#### Acceptance Criteria

1. WHEN el testigo hace clic en "Enviar Formulario E14", THE Sistema SHALL validar que la foto esté capturada
2. WHEN el testigo hace clic en "Enviar Formulario E14", THE Sistema SHALL validar que haya al menos un voto registrado
3. WHEN envía los datos, THE Sistema SHALL incluir todos los 25+ campos del formulario E14 completo
4. WHEN envía los datos, THE Sistema SHALL enviar mediante POST a `/api/testigo/enviar-e14`
5. WHEN el servidor recibe los datos, THE Sistema SHALL guardar los registros en las tablas correspondientes
6. WHEN guarda exitosamente, THE Sistema SHALL mostrar un mensaje de confirmación al testigo
7. WHEN guarda exitosamente, THE Sistema SHALL actualizar el contador de capturas E14 en el dashboard
8. WHEN guarda exitosamente, THE Sistema SHALL recargar la página para permitir nueva captura

### Requirement 7: Configuración de Estructura E14 por Admin

**User Story:** Como administrador, quiero configurar las zonas OCR del formulario E14 para cada tipo de elección, de manera que el sistema sepa dónde extraer los números de votos en las fotos.

#### Acceptance Criteria

1. WHEN el admin accede a configuración de E14, THE Sistema SHALL mostrar un formulario para definir posiciones y zonas OCR
2. WHEN el admin define una posición, THE Sistema SHALL solicitar: posición, tipo (candidato/voto_blanco/voto_nulo/no_marcado), candidato_id, y coordenadas de zona OCR (x, y, width, height)
3. WHEN el admin guarda la configuración, THE Sistema SHALL enviar los datos mediante POST a `/api/admin/configurar-estructura-e14`
4. WHEN el servidor recibe la configuración, THE Sistema SHALL guardar los registros en la tabla `estructura_e14`
5. WHEN guarda exitosamente, THE Sistema SHALL validar que todas las posiciones tengan zonas OCR definidas

### Requirement 8: Validación de Totales

**User Story:** Como testigo electoral, quiero que el sistema valide que el total de votos coincida con los votantes que sufragaron, para detectar inconsistencias antes de reportar.

#### Acceptance Criteria

1. WHEN el testigo confirma los datos, THE Sistema SHALL sumar todos los votos (candidatos + blancos + nulos + no marcados)
2. WHEN calcula el total, THE Sistema SHALL comparar con el número de votantes habilitados de la mesa
3. IF la diferencia es mayor a 5%, THEN THE Sistema SHALL mostrar una advertencia al testigo
4. WHEN muestra advertencia, THE Sistema SHALL permitir al testigo agregar observaciones explicando la diferencia
5. WHEN el testigo agrega observaciones, THE Sistema SHALL permitir confirmar los datos a pesar de la advertencia

### Requirement 9: Manejo de Errores OCR

**User Story:** Como testigo electoral, quiero que el sistema me notifique si el OCR no puede procesar la imagen, para que pueda tomar una nueva foto o ingresar los datos manualmente.

#### Acceptance Criteria

1. IF el OCR falla completamente, THEN THE Sistema SHALL mostrar un mensaje de error al testigo
2. WHEN muestra error OCR, THE Sistema SHALL ofrecer opciones: "Tomar nueva foto" o "Ingresar manualmente"
3. IF el testigo selecciona "Tomar nueva foto", THEN THE Sistema SHALL volver a la pantalla de captura
4. IF el testigo selecciona "Ingresar manualmente", THEN THE Sistema SHALL mostrar un formulario vacío para entrada manual
5. WHEN hay error OCR, THE Sistema SHALL registrar el error en logs con detalles de la imagen y mesa

### Requirement 10: Historial de Imágenes E14

**User Story:** Como testigo electoral, quiero ver todas las fotos E14 que he subido para mi mesa, para poder revisar o reprocesar imágenes anteriores si es necesario.

#### Acceptance Criteria

1. WHEN el testigo accede a "Ver Historial E14", THE Sistema SHALL obtener todas las imágenes mediante GET a `/api/testigo/fotos-e14/:mesa_id`
2. WHEN recibe las imágenes, THE Sistema SHALL mostrar una galería con miniaturas, fecha/hora y estado (procesado/confirmado/rechazado)
3. WHEN el testigo hace clic en una miniatura, THE Sistema SHALL mostrar la imagen en tamaño completo
4. WHEN muestra imagen completa, THE Sistema SHALL mostrar los datos extraídos asociados a esa imagen
5. WHEN el testigo selecciona una imagen, THE Sistema SHALL permitir reprocesar o eliminar la imagen

### Requirement 11: Indicadores de Calidad de Imagen

**User Story:** Como testigo electoral, quiero recibir retroalimentación sobre la calidad de la foto antes de procesarla, para asegurarme de que el OCR funcionará correctamente.

#### Acceptance Criteria

1. WHEN el testigo sube una imagen, THE Sistema SHALL analizar la resolución de la imagen
2. IF la resolución es menor a 1200x1600px, THEN THE Sistema SHALL mostrar una advertencia de baja resolución
3. WHEN analiza la imagen, THE Sistema SHALL detectar si está borrosa usando análisis de varianza de Laplacian
4. IF la imagen está borrosa, THEN THE Sistema SHALL mostrar una advertencia y sugerir tomar nueva foto
5. WHEN muestra advertencias de calidad, THE Sistema SHALL permitir al testigo continuar o tomar nueva foto

### Requirement 12: Dashboard Enfocado sin Distracciones

**User Story:** Como testigo electoral, quiero un dashboard limpio y enfocado solo en la captura del E14, para que pueda completar mi tarea sin distracciones o elementos innecesarios.

#### Acceptance Criteria

1. WHEN el testigo accede al dashboard, THE Sistema SHALL mostrar solo: estadísticas de la mesa, área de captura de foto y formulario E14
2. WHEN el testigo accede al dashboard, THE Sistema SHALL NOT mostrar acciones rápidas o botones de navegación secundaria
3. WHEN el testigo accede al dashboard, THE Sistema SHALL mantener el menú de navegación principal para acceso a otras funciones
4. WHEN el testigo completa el formulario, THE Sistema SHALL mantener el foco en el botón de envío como única acción principal
5. WHEN el testigo envía el formulario, THE Sistema SHALL recargar el dashboard para permitir nueva captura sin navegación adicional
