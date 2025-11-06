#!/usr/bin/env python3
"""
Configuración del Sistema Electoral ERP
Configuraciones para desarrollo, testing y producción
"""

import os
from datetime import timedelta

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_EXPIRES_HOURS', 24)))
    
    # Base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Configuración de correo (para notificaciones)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuración de logs
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    
    # Configuración de Redis (para cache y sesiones)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Configuración de seguridad
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    DATABASE_URL = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///caqueta_electoral_dev.db'
    
    # Configuración menos estricta para desarrollo
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DATABASE_URL = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///caqueta_electoral_test.db'
    WTF_CSRF_ENABLED = False
    
    # Configuración menos estricta para testing
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/caqueta_electoral'
    
    # Configuración de logs para producción
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log de errores por email
        import logging
        from logging.handlers import SMTPHandler
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Sistema Electoral Error',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        
        # Log a archivo
        from logging.handlers import RotatingFileHandler
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/sistema_electoral.log',
                                         maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Sistema Electoral startup')

class DockerConfig(ProductionConfig):
    """Configuración para contenedores Docker"""
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Log a stdout para contenedores
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}