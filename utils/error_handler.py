"""
Módulo para tratamento centralizado de erros e exceções.
Fornece funções padronizadas para tratar erros em toda a aplicação.
"""

import logging
import traceback
import sys
from flask import flash, jsonify, render_template

# Configuração de logging
logger = logging.getLogger('zelopack')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Tipos de erros conhecidos 
DATABASE_ERROR = 'database'
VALIDATION_ERROR = 'validation'
AUTH_ERROR = 'authentication'
FILE_ERROR = 'file'
CALCULATION_ERROR = 'calculation'
GENERAL_ERROR = 'general'

def log_exception(exception, error_type=GENERAL_ERROR, context=None):
    """
    Registra detalhes da exceção no log com contexto adicional.
    
    Args:
        exception: Objeto de exceção
        error_type: Tipo de erro para categorização
        context: Dicionário com informações de contexto adicionais
    """
    tb = traceback.format_exc()
    
    # Formatar mensagem de erro
    error_msg = f"ERRO ({error_type}): {str(exception)}"
    
    # Adicionar informações de contexto se disponíveis
    if context:
        context_info = ", ".join(f"{k}={v}" for k, v in context.items())
        error_msg += f" | Contexto: {context_info}"
    
    # Registrar no log
    logger.error(error_msg)
    logger.debug(tb)  # Trace completo em nível de debug
    
    return error_msg

def handle_database_error(exception, operation=None, table=None):
    """
    Manipula erros de banco de dados de maneira padronizada.
    
    Args:
        exception: Exceção de banco de dados
        operation: Operação que foi tentada (select, insert, update, delete)
        table: Tabela afetada
    
    Returns:
        Mensagem de erro formatada
    """
    context = {
        'operation': operation,
        'table': table
    }
    
    error_msg = log_exception(exception, DATABASE_ERROR, context)
    
    # Tentar identificar tipos específicos de erro de BD
    error_type = "desconhecido"
    if "violates foreign key constraint" in str(exception):
        error_type = "violação de chave estrangeira"
    elif "duplicate key value violates unique constraint" in str(exception):
        error_type = "violação de unicidade"
    elif "connection" in str(exception).lower():
        error_type = "conexão com banco de dados"
    
    return f"Erro de banco de dados ({error_type}): {str(exception)}"

def handle_calculation_error(exception, calculation_type=None, inputs=None):
    """
    Manipula erros em cálculos técnicos.
    
    Args:
        exception: Exceção ocorrida durante o cálculo
        calculation_type: Tipo de cálculo tentado
        inputs: Valores de entrada que causaram o erro
    
    Returns:
        Mensagem de erro formatada
    """
    context = {
        'calculation_type': calculation_type,
        'inputs': inputs
    }
    
    error_msg = log_exception(exception, CALCULATION_ERROR, context)
    
    return f"Erro no cálculo: {str(exception)}"

def handle_file_error(exception, file_path=None, operation=None):
    """
    Manipula erros relacionados a operações com arquivos.
    
    Args:
        exception: Exceção ocorrida
        file_path: Caminho do arquivo
        operation: Operação (leitura, escrita, upload, download)
    
    Returns:
        Mensagem de erro formatada
    """
    context = {
        'file_path': file_path,
        'operation': operation
    }
    
    error_msg = log_exception(exception, FILE_ERROR, context)
    
    return f"Erro ao manipular arquivo: {str(exception)}"

def api_error_response(message, status_code=400, error_type=GENERAL_ERROR, details=None):
    """
    Cria uma resposta de erro padronizada para APIs.
    
    Args:
        message: Mensagem de erro
        status_code: Código HTTP de status
        error_type: Tipo de erro
        details: Detalhes adicionais (opcional)
    
    Returns:
        Resposta JSON formatada, código de status
    """
    response = {
        'success': False,
        'error': {
            'type': error_type,
            'message': message
        }
    }
    
    if details:
        response['error']['details'] = details
        
    return jsonify(response), status_code

def flash_error(exception, category='danger', error_type=GENERAL_ERROR):
    """
    Registra erro no log e envia mensagem flash para o usuário.
    
    Args:
        exception: Exceção a ser tratada
        category: Categoria da mensagem flash
        error_type: Tipo de erro
    """
    log_exception(exception, error_type)
    
    # Simplificar a mensagem para o usuário final
    user_friendly_message = simplify_error_for_user(exception)
    
    # Flash a mensagem para o usuário
    flash(user_friendly_message, category)

def simplify_error_for_user(exception):
    """
    Simplifica mensagens de erro para os usuários finais.
    
    Args:
        exception: Exceção original
    
    Returns:
        Mensagem simplificada amigável para usuários
    """
    error_message = str(exception)
    
    # Mapeamento de erros técnicos para mensagens amigáveis
    if "violates foreign key constraint" in error_message:
        return "Este registro não pode ser excluído porque está sendo usado em outras partes do sistema."
    
    elif "duplicate key value violates unique constraint" in error_message:
        return "Já existe um registro com estas informações no sistema."
    
    elif "connection" in error_message.lower() and "database" in error_message.lower():
        return "Não foi possível conectar ao banco de dados. Por favor, tente novamente em alguns instantes."
    
    elif "permission" in error_message.lower() or "acesso negado" in error_message.lower():
        return "Você não tem permissão para realizar esta ação."
    
    elif "division by zero" in error_message.lower():
        return "Não é possível realizar esta operação com divisão por zero."
    
    elif "file not found" in error_message.lower() or "no such file" in error_message.lower():
        return "O arquivo solicitado não foi encontrado."
    
    # Se não for um erro conhecido, retornar uma mensagem genérica
    return "Ocorreu um erro durante a operação. Por favor, tente novamente ou contate o suporte técnico."