import os

class Config:
    """Configurações base para a aplicação."""
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'zelopack-dev-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///zelopack.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limite máximo
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}

class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configurações para ambiente de produção."""
    DEBUG = False
    # Em produção, é recomendável usar um servidor WSGI como Gunicorn
    
# Configuração que será usada
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
