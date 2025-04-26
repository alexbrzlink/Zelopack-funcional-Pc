"""
Utilitário para registro de atividades dos usuários no sistema.
Fornece funções para facilitar o registro de ações em diferentes módulos.
"""

from flask import request, current_app, g
from models import UserActivity, db
import json
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

def get_request_info():
    """
    Obtém informações do request atual (IP, User-Agent).
    
    Returns:
        tuple: (ip_address, user_agent)
    """
    if request:
        # Tentar obter o IP real, mesmo atrás de proxies
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip:  # Formato: client, proxy1, proxy2, ...
            ip = ip.split(',')[0].strip()
            
        user_agent = request.headers.get('User-Agent', 'Desconhecido')
        return ip, user_agent
    
    return None, None

def log_login(user_id, status='success', details=None):
    """
    Registra uma tentativa de login no sistema.
    
    Args:
        user_id: ID do usuário que está tentando fazer login
        status: 'success' para login bem-sucedido, 'failed' para falha
        details: Detalhes adicionais (opcional)
    """
    ip, user_agent = get_request_info()
    
    activity_details = details or {}
    if status == 'failed':
        activity_details = {
            'message': 'Tentativa de login mal-sucedida',
            'reason': details.get('reason', 'Credenciais inválidas')
        }
    else:
        activity_details = {
            'message': 'Login bem-sucedido'
        }
    
    UserActivity.log_activity(
        user_id=user_id,
        action='login',
        module='auth',
        details=json.dumps(activity_details) if isinstance(activity_details, dict) else activity_details,
        ip_address=ip,
        user_agent=user_agent,
        status=status
    )

def log_logout(user_id):
    """
    Registra o logout do usuário no sistema.
    
    Args:
        user_id: ID do usuário que está fazendo logout
    """
    ip, user_agent = get_request_info()
    
    UserActivity.log_activity(
        user_id=user_id,
        action='logout',
        module='auth',
        details='Logout do sistema',
        ip_address=ip,
        user_agent=user_agent
    )

def log_create(user_id, module, entity_type, entity_id, data):
    """
    Registra a criação de uma entidade no sistema.
    
    Args:
        user_id: ID do usuário que criou a entidade
        module: Módulo do sistema (reports, users, suppliers, etc.)
        entity_type: Tipo da entidade criada (Report, User, etc.)
        entity_id: ID da entidade criada
        data: Dados da entidade criada
    """
    ip, user_agent = get_request_info()
    
    UserActivity.log_activity(
        user_id=user_id,
        action='create',
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        after_state=data,
        ip_address=ip,
        user_agent=user_agent
    )

def log_update(user_id, module, entity_type, entity_id, before_data, after_data):
    """
    Registra a atualização de uma entidade no sistema.
    
    Args:
        user_id: ID do usuário que atualizou a entidade
        module: Módulo do sistema (reports, users, suppliers, etc.)
        entity_type: Tipo da entidade atualizada (Report, User, etc.)
        entity_id: ID da entidade atualizada
        before_data: Dados da entidade antes da atualização
        after_data: Dados da entidade após a atualização
    """
    ip, user_agent = get_request_info()
    
    UserActivity.log_activity(
        user_id=user_id,
        action='update',
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        before_state=before_data,
        after_state=after_data,
        ip_address=ip,
        user_agent=user_agent
    )

def log_delete(user_id, module, entity_type, entity_id, data):
    """
    Registra a exclusão de uma entidade no sistema.
    
    Args:
        user_id: ID do usuário que excluiu a entidade
        module: Módulo do sistema (reports, users, suppliers, etc.)
        entity_type: Tipo da entidade excluída (Report, User, etc.)
        entity_id: ID da entidade excluída
        data: Dados da entidade excluída
    """
    ip, user_agent = get_request_info()
    
    UserActivity.log_activity(
        user_id=user_id,
        action='delete',
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        before_state=data,
        ip_address=ip,
        user_agent=user_agent
    )

def log_view(user_id, module, entity_type=None, entity_id=None, details=None):
    """
    Registra uma visualização de página ou entidade.
    
    Args:
        user_id: ID do usuário que visualizou a página/entidade
        module: Módulo do sistema (reports, users, suppliers, etc.)
        entity_type: Tipo da entidade visualizada (opcional)
        entity_id: ID da entidade visualizada (opcional)
        details: Detalhes adicionais (opcional)
    """
    ip, user_agent = get_request_info()
    
    UserActivity.log_activity(
        user_id=user_id,
        action='view',
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip,
        user_agent=user_agent
    )

def log_download(user_id, module, entity_type, entity_id, filename):
    """
    Registra o download de um arquivo.
    
    Args:
        user_id: ID do usuário que baixou o arquivo
        module: Módulo do sistema (reports, documents, etc.)
        entity_type: Tipo da entidade baixada (Report, Document, etc.)
        entity_id: ID da entidade baixada
        filename: Nome do arquivo baixado
    """
    ip, user_agent = get_request_info()
    
    details = {
        'action': 'download',
        'filename': filename
    }
    
    UserActivity.log_activity(
        user_id=user_id,
        action='download',
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details),
        ip_address=ip,
        user_agent=user_agent
    )

def log_export(user_id, module, format, filters=None):
    """
    Registra a exportação de dados.
    
    Args:
        user_id: ID do usuário que exportou os dados
        module: Módulo do sistema (reports, users, suppliers, etc.)
        format: Formato da exportação (PDF, Excel, CSV, etc.)
        filters: Filtros aplicados na exportação (opcional)
    """
    ip, user_agent = get_request_info()
    
    details = {
        'action': 'export',
        'format': format,
        'filters': filters or {}
    }
    
    UserActivity.log_activity(
        user_id=user_id,
        action='export',
        module=module,
        details=json.dumps(details),
        ip_address=ip,
        user_agent=user_agent
    )

def log_action(user_id, action, module, entity_type=None, entity_id=None, details=None, before_state=None, after_state=None):
    """
    Registra uma ação genérica no sistema.
    
    Args:
        user_id: ID do usuário que realizou a ação
        action: Tipo de ação
        module: Módulo do sistema
        entity_type: Tipo da entidade (opcional)
        entity_id: ID da entidade (opcional)
        details: Detalhes da ação (opcional)
        before_state: Estado antes da ação (opcional)
        after_state: Estado após a ação (opcional)
    """
    ip, user_agent = get_request_info()
    
    UserActivity.log_activity(
        user_id=user_id,
        action=action,
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        before_state=before_state,
        after_state=after_state,
        ip_address=ip,
        user_agent=user_agent
    )

def get_latest_activities(limit=20, user_id=None, module=None, action=None):
    """
    Retorna as atividades mais recentes do sistema.
    
    Args:
        limit: Limite de atividades a serem retornadas
        user_id: Filtrar por ID de usuário (opcional)
        module: Filtrar por módulo (opcional)
        action: Filtrar por tipo de ação (opcional)
        
    Returns:
        Lista de atividades
    """
    query = UserActivity.query.order_by(UserActivity.created_at.desc())
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if module:
        query = query.filter_by(module=module)
    if action:
        query = query.filter_by(action=action)
    
    return query.limit(limit).all()

def get_user_activity_summary(user_id, days=30):
    """
    Retorna um resumo das atividades de um usuário.
    
    Args:
        user_id: ID do usuário
        days: Número de dias para analisar
        
    Returns:
        Dicionário com resumo das atividades
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total de atividades
    total_activities = UserActivity.query.filter(
        UserActivity.user_id == user_id,
        UserActivity.created_at >= start_date
    ).count()
    
    # Atividades por módulo
    activities_by_module = db.session.query(
        UserActivity.module, 
        func.count(UserActivity.id)
    ).filter(
        UserActivity.user_id == user_id,
        UserActivity.created_at >= start_date
    ).group_by(UserActivity.module).all()
    
    # Atividades por tipo de ação
    activities_by_action = db.session.query(
        UserActivity.action, 
        func.count(UserActivity.id)
    ).filter(
        UserActivity.user_id == user_id,
        UserActivity.created_at >= start_date
    ).group_by(UserActivity.action).all()
    
    # Último login
    last_login = UserActivity.query.filter(
        UserActivity.user_id == user_id,
        UserActivity.action == 'login',
        UserActivity.status == 'success'
    ).order_by(UserActivity.created_at.desc()).first()
    
    return {
        'total_activities': total_activities,
        'activities_by_module': dict(activities_by_module),
        'activities_by_action': dict(activities_by_action),
        'last_login': last_login.created_at if last_login else None
    }