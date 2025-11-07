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

### Requirement 3: Visualización de Resultados OCR

**User Story:** Como testigo electoral, quiero ver los datos extraídos por el OCR en una tabla editable con indicadores de confianza, para que pueda revisar y corregir cualquier error antes de confirmar.

#### Acceptance Criteria

1. WHEN el OCR completa el procesamiento, THE Sistema SHALL mostrar una tabla con columnas: Posición, Candidato, Votos, Confianza y Acción
2. WHEN muestra la tabla, THE Sistema SHALL resaltar en amarillo las filas con confianza menor a 90%
3. WHEN muestra la tabla, THE Sistema SHALL mostrar la confianza promedio general en la parte superior
4. WHEN muestra la tabla, THE Sistema SHALL calcular y mostrar el total de votos detectados
5. WHEN el testigo hace clic en el ícono de editar, THE Sistema SHALL convertir el campo de votos en un input editable

### Requirement 4: Corrección Manual de Datos

**User Story:** Como testigo electoral, quiero poder editar manualmente cualquier número extraído por el OCR, para que pueda corregir errores de lectura antes de guardar los datos finales.

#### Acceptance Criteria

1. WHEN el testigo hace clic en editar un campo de votos, THE Sistema SHALL mostrar un input numérico con el valor actual
2. WHEN el testigo modifica un valor, THE Sistema SHALL marcar ese campo como "editado" visualmente
3. WHEN el testigo modifica un valor, THE Sistema SHALL recalcular el total de votos automáticamente
4. WHEN el testigo guarda un valor editado, THE Sistema SHALL validar que sea un número entero no negativo
5. IF el valor editado no es válido, THEN THE Sistema SHALL mostrar un mensaje de error y no permitir guardar

### Requirement 5: Confirmación y Guardado de Datos

**User Story:** Como testigo electoral, quiero confirmar los datos revisados y guardarlos en el sistema, para que queden registrados oficialmente los resultados de mi mesa.

#### Acceptance Criteria

1. WHEN el testigo hace clic en "Aceptar y Guardar", THE Sistema SHALL enviar los datos confirmados mediante POST a `/api/testigo/confirmar-datos-e14`
2. WHEN envía los datos, THE Sistema SHALL incluir mesa_id, imagen_e14_id, datos_confirmados, total_votos, observaciones y timestamp
3. WHEN el servidor recibe los datos, THE Sistema SHALL guardar los registros en la tabla `datos_ocr_e14` con estado "confirmado"
4. WHEN guarda exitosamente, THE Sistema SHALL mostrar un mensaje de confirmación al testigo
5. WHEN guarda exitosamente, THE Sistema SHALL actualizar el estado de la mesa a "datos_reportados"

### Requirement 6: Configuración de Estructura E14 por Admin

**User Story:** Como administrador, quiero configurar las zonas OCR del formulario E14 para cada tipo de elección, de manera que el sistema sepa dónde extraer los números de votos en las fotos.

#### Acceptance Criteria

1. WHEN el admin accede a configuración de E14, THE Sistema SHALL mostrar un formulario para definir posiciones y zonas OCR
2. WHEN el admin define una posición, THE Sistema SHALL solicitar: posición, tipo (candidato/voto_blanco/voto_nulo/no_marcado), candidato_id, y coordenadas de zona OCR (x, y, width, height)
3. WHEN el admin guarda la configuración, THE Sistema SHALL enviar los datos mediante POST a `/api/admin/configurar-estructura-e14`
4. WHEN el servidor recibe la configuración, THE Sistema SHALL guardar los registros en la tabla `estructura_e14`
5. WHEN guarda exitosamente, THE Sistema SHALL validar que todas las posiciones tengan zonas OCR definidas

### Requirement 7: Validación de Totales

**User Story:** Como testigo electoral, quiero que el sistema valide que el total de votos coincida con los votantes que sufragaron, para detectar inconsistencias antes de reportar.

#### Acceptance Criteria

1. WHEN el testigo confirma los datos, THE Sistema SHALL sumar todos los votos (candidatos + blancos + nulos + no marcados)
2. WHEN calcula el total, THE Sistema SHALL comparar con el número de votantes habilitados de la mesa
3. IF la diferencia es mayor a 5%, THEN THE Sistema SHALL mostrar una advertencia al testigo
4. WHEN muestra advertencia, THE Sistema SHALL permitir al testigo agregar observaciones explicando la diferencia
5. WHEN el testigo agrega observaciones, THE Sistema SHALL permitir confirmar los datos a pesar de la advertencia

### Requirement 8: Manejo de Errores OCR

**User Story:** Como testigo electoral, quiero que el sistema me notifique si el OCR no puede procesar la imagen, para que pueda tomar una nueva foto o ingresar los datos manualmente.

#### Acceptance Criteria

1. IF el OCR falla completamente, THEN THE Sistema SHALL mostrar un mensaje de error al testigo
2. WHEN muestra error OCR, THE Sistema SHALL ofrecer opciones: "Tomar nueva foto" o "Ingresar manualmente"
3. IF el testigo selecciona "Tomar nueva foto", THEN THE Sistema SHALL volver a la pantalla de captura
4. IF el testigo selecciona "Ingresar manualmente", THEN THE Sistema SHALL mostrar un formulario vacío para entrada manual
5. WHEN hay error OCR, THE Sistema SHALL registrar el error en logs con detalles de la imagen y mesa

### Requirement 9: Historial de Imágenes E14

**User Story:** Como testigo electoral, quiero ver todas las fotos E14 que he subido para mi mesa, para poder revisar o reprocesar imágenes anteriores si es necesario.

#### Acceptance Criteria

1. WHEN el testigo accede a "Ver Historial E14", THE Sistema SHALL obtener todas las imágenes mediante GET a `/api/testigo/fotos-e14/:mesa_id`
2. WHEN recibe las imágenes, THE Sistema SHALL mostrar una galería con miniaturas, fecha/hora y estado (procesado/confirmado/rechazado)
3. WHEN el testigo hace clic en una miniatura, THE Sistema SHALL mostrar la imagen en tamaño completo
4. WHEN muestra imagen completa, THE Sistema SHALL mostrar los datos extraídos asociados a esa imagen
5. WHEN el testigo selecciona una imagen, THE Sistema SHALL permitir reprocesar o eliminar la imagen

### Requirement 10: Indicadores de Calidad de Imagen

**User Story:** Como testigo electoral, quiero recibir retroalimentación sobre la calidad de la foto antes de procesarla, para asegurarme de que el OCR funcionará correctamente.

#### Acceptance Criteria

1. WHEN el testigo sube una imagen, THE Sistema SHALL analizar la resolución de la imagen
2. IF la resolución es menor a 1200x1600px, THEN THE Sistema SHALL mostrar una advertencia de baja resolución
3. WHEN analiza la imagen, THE Sistema SHALL detectar si está borrosa usando análisis de varianza de Laplacian
4. IF la imagen está borrosa, THEN THE Sistema SHALL mostrar una advertencia y sugerir tomar nueva foto
5. WHEN muestra advertencias de calidad, THE Sistema SHALL permitir al testigo continuar o tomar nueva foto
