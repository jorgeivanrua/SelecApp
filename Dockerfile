# Sistema Electoral ERP - Dockerfile para Producción
FROM python:3.11-slim

# Información del mantenedor
LABEL maintainer="Sistema Electoral Caquetá <admin@caqueta.gov.co>"
LABEL description="Sistema Electoral ERP - Departamento del Caquetá"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_DEBUG=False

# Crear usuario no-root
RUN groupadd -r electoral && useradd -r -g electoral electoral

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorios de trabajo
WORKDIR /app
RUN mkdir -p /app/logs /app/uploads /var/log/sistema-electoral /var/run/sistema-electoral

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios y establecer permisos
RUN chown -R electoral:electoral /app /var/log/sistema-electoral /var/run/sistema-electoral && \
    chmod +x /app/entrypoint.sh

# Cambiar al usuario no-root
USER electoral

# Exponer puerto
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Punto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]