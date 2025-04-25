"""
Pacote de utilitários para o sistema Zelopack.
Contém funções e classes auxiliares usadas em todo o projeto.
"""

# Importar módulos comuns para facilitar o acesso
from .error_handler import (
    log_exception,
    handle_database_error,
    handle_calculation_error,
    handle_file_error,
    api_error_response,
    flash_error,
    simplify_error_for_user
)

# Importar utilidades do banco de dados
from .database import (
    cached_query,
    optimize_query,
    execute_with_retry,
    bulk_insert,
    get_table_stats,
    get_database_stats,
    clear_cache
)

# Inicialização do logger central
import logging

def setup_logging(app=None, level=logging.INFO):
    """
    Configura o sistema de logging central para o Zelopack.
    
    Args:
        app: Aplicação Flask (opcional)
        level: Nível de logging (padrão: INFO)
    """
    # Logger raiz
    root_logger = logging.getLogger('zelopack')
    root_logger.setLevel(level)
    
    # Handler para console com formatação avançada
    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Se houver um app Flask, configurar handler para arquivo de log
    if app:
        app.logger.setLevel(level)
        # Adicionar handler para app.logger se necessário
    
    return root_logger