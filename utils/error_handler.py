"""
Sistema centralizado de tratamento de erros para o Zelopack.
Fornece funções para registro, monitoramento e exibição amigável de erros.
"""

import logging
import traceback
import json
from datetime import datetime
from flask import flash, jsonify, current_app

# Configuração do logger específico para erros
error_logger = logging.getLogger('zelopack.errors')

def log_exception(exception, context=None):
    """
    Registra uma exceção com contexto adicional para facilitar a depuração.
    
    Args:
        exception: A exceção capturada
        context: Dicionário com informações adicionais sobre o contexto do erro
    """
    error_info = {
        'timestamp': datetime.now().isoformat(),
        'exception_type': exception.__class__.__name__,
        'message': str(exception),
        'traceback': traceback.format_exc(),
        'context': context or {}
    }
    
    # Registrar no log
    error_logger.error(
        f"Exceção: {error_info['exception_type']} - {error_info['message']}", 
        extra={'error_data': error_info}
    )
    
    # Registrar detalhes completos em nível de debug
    error_logger.debug(f"Detalhes completos do erro: {json.dumps(error_info, default=str, indent=2)}")
    
    return error_info

def handle_database_error(exception, session=None, operation=None):
    """
    Trata erros específicos de banco de dados e realiza limpeza necessária.
    
    Args:
        exception: A exceção de banco de dados
        session: A sessão SQLAlchemy ativa (opcional)
        operation: Descrição da operação que falhou (opcional)
    
    Returns:
        Dict com informações sobre o erro para uso interno
    """
    context = {'operation': operation or 'database_operation'}
    
    # Fazer rollback da sessão se fornecida
    if session:
        try:
            session.rollback()
            context['rollback'] = 'success'
        except Exception as rollback_error:
            context['rollback'] = 'failed'
            context['rollback_error'] = str(rollback_error)
    
    # Registrar o erro
    error_info = log_exception(exception, context)
    
    # Simplificar a mensagem para o usuário
    user_message = simplify_error_for_user(exception, error_type='database')
    
    return {
        'error_info': error_info,
        'user_message': user_message
    }

def handle_calculation_error(exception, calculation_type=None, input_data=None):
    """
    Trata erros em operações de cálculo.
    
    Args:
        exception: A exceção de cálculo
        calculation_type: Tipo/nome do cálculo (opcional)
        input_data: Dados de entrada que causaram o erro (opcional)
    
    Returns:
        Dict com informações sobre o erro para uso interno
    """
    context = {
        'calculation_type': calculation_type or 'unknown',
        'input_data': input_data
    }
    
    # Registrar o erro
    error_info = log_exception(exception, context)
    
    # Simplificar a mensagem para o usuário
    user_message = simplify_error_for_user(exception, error_type='calculation')
    
    return {
        'error_info': error_info,
        'user_message': user_message
    }

def handle_file_error(exception, file_path=None, operation=None):
    """
    Trata erros em operações de arquivo.
    
    Args:
        exception: A exceção de arquivo
        file_path: Caminho do arquivo (opcional)
        operation: Operação que estava sendo realizada (opcional)
    
    Returns:
        Dict com informações sobre o erro para uso interno
    """
    context = {
        'file_path': file_path or 'unknown',
        'operation': operation or 'file_operation'
    }
    
    # Registrar o erro
    error_info = log_exception(exception, context)
    
    # Simplificar a mensagem para o usuário
    user_message = simplify_error_for_user(exception, error_type='file')
    
    return {
        'error_info': error_info,
        'user_message': user_message
    }

def api_error_response(error_dict, status_code=400):
    """
    Cria uma resposta JSON padronizada para erros de API.
    
    Args:
        error_dict: Dicionário de erro de uma das funções handle_*_error
        status_code: Código HTTP de status (padrão: 400)
    
    Returns:
        Resposta JSON para erro de API
    """
    response = {
        'status': 'error',
        'message': error_dict.get('user_message', 'Ocorreu um erro desconhecido.'),
        'error_code': error_dict.get('error_info', {}).get('exception_type', 'unknown_error')
    }
    
    # Incluir detalhes técnicos se em modo debug
    if current_app.debug:
        response['debug_info'] = error_dict.get('error_info')
    
    return jsonify(response), status_code

def flash_error(error_dict):
    """
    Exibe uma mensagem flash para o usuário com base no erro.
    
    Args:
        error_dict: Dicionário de erro de uma das funções handle_*_error
    """
    flash(error_dict.get('user_message', 'Ocorreu um erro desconhecido.'), 'danger')

def simplify_error_for_user(exception, error_type='general'):
    """
    Converte mensagens de erro técnicas em mensagens amigáveis para usuários.
    
    Args:
        exception: A exceção original
        error_type: Tipo de erro (database, calculation, file, general)
    
    Returns:
        Mensagem simplificada e amigável
    """
    error_message = str(exception)
    
    # Mapeamento de erros comuns de banco de dados
    if error_type == 'database':
        if 'violates foreign key constraint' in error_message:
            return "Este registro não pode ser modificado porque está sendo usado em outro lugar do sistema."
        elif 'violates unique constraint' in error_message or 'UNIQUE constraint failed' in error_message:
            return "Um registro com estas informações já existe no sistema."
        elif 'violates not-null constraint' in error_message:
            return "Todos os campos obrigatórios precisam ser preenchidos."
        else:
            return "Houve um problema ao acessar o banco de dados. Por favor, tente novamente."
    
    # Mapeamento de erros comuns de cálculo
    elif error_type == 'calculation':
        if 'division by zero' in error_message:
            return "Não é possível dividir por zero. Por favor, verifique os valores informados."
        elif 'could not convert string to float' in error_message:
            return "Um dos valores não é um número válido. Use apenas números (com ponto para decimais)."
        elif 'invalid value encountered in' in error_message:
            return "Um dos cálculos resultou em um valor inválido. Verifique os números informados."
        else:
            return "Houve um erro ao realizar o cálculo. Por favor, revise os valores informados."
    
    # Mapeamento de erros comuns de arquivo
    elif error_type == 'file':
        if 'No such file or directory' in error_message:
            return "O arquivo solicitado não foi encontrado."
        elif 'Permission denied' in error_message:
            return "Sem permissão para acessar este arquivo."
        elif 'disk space' in error_message.lower():
            return "Não há espaço suficiente em disco para esta operação."
        else:
            return "Houve um problema ao acessar o arquivo solicitado."
    
    # Erro genérico
    else:
        return "Ocorreu um erro inesperado. Os administradores do sistema foram notificados."