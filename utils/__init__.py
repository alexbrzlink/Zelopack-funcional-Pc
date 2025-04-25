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