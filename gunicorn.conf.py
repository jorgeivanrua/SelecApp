#!/usr/bin/env python3
"""
Configuración de Gunicorn para Sistema Electoral ERP
Configuración optimizada para producción
"""

import multiprocessing
import os

# Configuración del servidor
bind = f"{os.environ.get('HOST', '0.0.0.0')}:{os.environ.get('PORT', '5000')}"
workers = int(os.environ.get('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 120
keepalive = 5

# Configuración de archivos
user = os.environ.get('USER', 'www-data')
group = os.environ.get('GROUP', 'www-data')
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Configuración de logs
accesslog = '/var/log/sistema-electoral/access.log'
errorlog = '/var/log/sistema-electoral/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de proceso
pidfile = '/var/run/sistema-electoral/gunicorn.pid'
daemon = False
raw_env = [
    'FLASK_ENV=production',
]

# Hooks de Gunicorn
def on_starting(server):
    """Ejecutar al iniciar el servidor"""
    server.log.info("Sistema Electoral ERP iniciando...")

def on_reload(server):
    """Ejecutar al recargar el servidor"""
    server.log.info("Sistema Electoral ERP recargando...")

def worker_int(worker):
    """Ejecutar cuando un worker recibe SIGINT"""
    worker.log.info("Worker recibió SIGINT, cerrando...")

def pre_fork(server, worker):
    """Ejecutar antes de hacer fork de un worker"""
    server.log.info(f"Worker {worker.pid} iniciando...")

def post_fork(server, worker):
    """Ejecutar después de hacer fork de un worker"""
    server.log.info(f"Worker {worker.pid} iniciado correctamente")

def worker_abort(worker):
    """Ejecutar cuando un worker es abortado"""
    worker.log.info(f"Worker {worker.pid} abortado")

# Configuración SSL (si se usa)
if os.environ.get('SSL_CERT') and os.environ.get('SSL_KEY'):
    keyfile = os.environ.get('SSL_KEY')
    certfile = os.environ.get('SSL_CERT')
    ssl_version = 2  # TLS
    ciphers = 'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'