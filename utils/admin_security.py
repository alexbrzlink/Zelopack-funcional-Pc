"""
Módulo de segurança exclusivo para administradores.
Implementa recursos avançados de segurança, autenticação e controle de acesso.
"""
import secrets
import base64
import json
import time
import os
import re
import json
import logging
import hashlib
import functools
import ipaddress
from datetime import datetime, timedelta
from flask import request, redirect, url_for, flash, current_app, session
from flask_login import current_user
from werkzeug.security import check_password_hash

# Configuração do logger
logger = logging.getLogger(__name__)

# Cache de tentativas de login (em produção, isso deveria estar em Redis ou banco de dados)
# {username: {'attempts': int, 'blocked_until': datetime}}
LOGIN_ATTEMPTS = {}

# Cache de senhas anteriores (em produção, isso deveria estar em Redis ou banco de dados)
# {user_id: [hash1, hash2, ...]}
PASSWORD_HISTORY = {}

# Configurações padrão
DEFAULT_SETTINGS = {
    'password_complexity': True,
    'password_expiration_enabled': True,
    'password_expiration_days': 90,
    'password_history_enabled': True,
    'password_history_count': 5,
    'account_lockout_enabled': True,
    'account_lockout_attempts': 5,
    'account_lockout_duration': 30,  # minutos
    'session_timeout': 60,  # minutos
    'ip_restriction_enabled': False,
    'allowed_ips': [],
    'two_factor_enabled': False,
    'two_factor_method': 'email'
}


def admin_required(f):
    """
    Decorador para restringir acesso apenas a administradores.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    
    return decorated_function


def get_security_settings(app=None):
    """
    Obtém as configurações de segurança do banco de dados.
    
    Args:
        app: Aplicação Flask
        
    Returns:
        dict: Configurações de segurança
    """
    settings = DEFAULT_SETTINGS.copy()
    
    try:
        if app:
            with app.app_context():
                from models import SystemConfig
                
                # Carregar configurações do banco de dados
                for key in settings.keys():
                    config_key = f"security.{key}"
                    config = SystemConfig.query.filter_by(key=config_key).first()
                    
                    if config:
                        # Converter para tipo apropriado
                        if isinstance(settings[key], bool):
                            settings[key] = config.value.lower() == 'true'
                        elif isinstance(settings[key], int):
                            try:
                                settings[key] = int(config.value)
                            except ValueError:
                                pass
                        elif isinstance(settings[key], list):
                            try:
                                if config.value:
                                    settings[key] = config.value.split('\n')
                            except Exception:
                                pass
                        else:
                            settings[key] = config.value
    except Exception as e:
        logger.error(f"Erro ao carregar configurações de segurança: {str(e)}")
    
    return settings


def verify_password_complexity(password):
    """
    Verifica se a senha atende aos requisitos de complexidade.
    
    Args:
        password: Senha a ser verificada
        
    Returns:
        Tuple (bool, str): (atende_requisitos, mensagem_erro)
    """
    # Verificar comprimento mínimo
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres."
    
    # Verificar presença de letra maiúscula
    if not re.search(r'[A-Z]', password):
        return False, "A senha deve conter pelo menos uma letra maiúscula."
    
    # Verificar presença de letra minúscula
    if not re.search(r'[a-z]', password):
        return False, "A senha deve conter pelo menos uma letra minúscula."
    
    # Verificar presença de número
    if not re.search(r'[0-9]', password):
        return False, "A senha deve conter pelo menos um número."
    
    # Verificar presença de caractere especial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "A senha deve conter pelo menos um caractere especial."
    
    return True, ""


def check_password_history(user_id, password_hash, count=5):
    """
    Verifica se a senha já foi usada anteriormente.
    
    Args:
        user_id: ID do usuário
        password_hash: Hash da nova senha
        count: Número de senhas anteriores a verificar
        
    Returns:
        bool: True se a senha não foi usada anteriormente, False caso contrário
    """
    if user_id not in PASSWORD_HISTORY:
        return True
    
    # Verificar senhas anteriores
    history = PASSWORD_HISTORY[user_id][:count]
    
    for old_hash in history:
        if password_hash == old_hash:
            return False
    
    return True


def add_password_to_history(user_id, password_hash, count=5):
    """
    Adiciona uma senha ao histórico.
    
    Args:
        user_id: ID do usuário
        password_hash: Hash da senha
        count: Número máximo de senhas a manter no histórico
    """
    if user_id not in PASSWORD_HISTORY:
        PASSWORD_HISTORY[user_id] = []
    
    # Adicionar nova senha ao início
    PASSWORD_HISTORY[user_id].insert(0, password_hash)
    
    # Limitar tamanho do histórico
    PASSWORD_HISTORY[user_id] = PASSWORD_HISTORY[user_id][:count]


def check_password_expiration(last_password_change, expiration_days=90):
    """
    Verifica se a senha está expirada.
    
    Args:
        last_password_change: Data da última alteração de senha
        expiration_days: Dias até a expiração
        
    Returns:
        bool: True se a senha está expirada, False caso contrário
    """
    if not last_password_change:
        return True
    
    # Calcular data de expiração
    expiration_date = last_password_change + timedelta(days=expiration_days)
    
    return datetime.now() > expiration_date


def record_login_attempt(username, success=False):
    """
    Registra uma tentativa de login.
    
    Args:
        username: Nome de usuário
        success: Se a tentativa foi bem-sucedida
        
    Returns:
        Tuple (bool, str): (bloqueado, mensagem_erro)
    """
    # Inicializar registro de tentativas
    if username not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[username] = {'attempts': 0, 'blocked_until': None}
    
    # Verificar se a conta está bloqueada
    if LOGIN_ATTEMPTS[username]['blocked_until']:
        if datetime.now() < LOGIN_ATTEMPTS[username]['blocked_until']:
            # Conta ainda bloqueada
            remaining = LOGIN_ATTEMPTS[username]['blocked_until'] - datetime.now()
            minutes = remaining.seconds // 60
            return True, f"Conta temporariamente bloqueada. Tente novamente em {minutes} minutos."
        else:
            # Bloqueio expirado
            LOGIN_ATTEMPTS[username]['blocked_until'] = None
            LOGIN_ATTEMPTS[username]['attempts'] = 0
    
    # Se for sucesso, resetar tentativas
    if success:
        LOGIN_ATTEMPTS[username]['attempts'] = 0
        return False, ""
    
    # Incrementar contador de tentativas
    LOGIN_ATTEMPTS[username]['attempts'] += 1
    
    # Verificar se deve bloquear
    settings = get_security_settings(current_app)
    
    if settings['account_lockout_enabled'] and LOGIN_ATTEMPTS[username]['attempts'] >= settings['account_lockout_attempts']:
        # Bloquear conta
        duration = settings['account_lockout_duration']
        LOGIN_ATTEMPTS[username]['blocked_until'] = datetime.now() + timedelta(minutes=duration)
        
        # Registrar evento de bloqueio
        logger.warning(f"Conta bloqueada após {LOGIN_ATTEMPTS[username]['attempts']} tentativas: {username}")
        
        # Notificar usuário
        if duration == 0:
            return True, "Conta bloqueada devido a múltiplas tentativas de login. Entre em contato com o administrador."
        else:
            return True, f"Conta temporariamente bloqueada por {duration} minutos devido a múltiplas tentativas de login."
    
    return False, ""


def check_ip_restriction(request_ip, allowed_ips):
    """
    Verifica se o IP está na lista de IPs permitidos.
    
    Args:
        request_ip: IP da requisição
        allowed_ips: Lista de IPs permitidos
        
    Returns:
        bool: True se o IP é permitido, False caso contrário
    """
    # Se a lista estiver vazia, permitir todos
    if not allowed_ips:
        return True
    
    # Converter para lista se for string
    if isinstance(allowed_ips, str):
        allowed_ips = [ip.strip() for ip in allowed_ips.split(',')]
    
    # Verificar cada item na lista de IPs permitidos
    for allowed in allowed_ips:
        # Verificar se é um intervalo CIDR
        if '/' in allowed:
            try:
                network = ipaddress.ip_network(allowed, strict=False)
                if ipaddress.ip_address(request_ip) in network:
                    return True
            except ValueError:
                continue
        # Verificar IP direto
        elif request_ip == allowed:
            return True
    
    return False


def check_session_timeout():
    """
    Verifica se a sessão atual expirou.
    
    Returns:
        bool: True se a sessão expirou, False caso contrário
    """
    if 'last_activity' not in session:
        return False
    
    # Obter configurações
    settings = get_security_settings(current_app)
    timeout_minutes = settings['session_timeout']
    
    # Verificar tempo
    last_activity = datetime.fromtimestamp(session['last_activity'])
    if datetime.now() > last_activity + timedelta(minutes=timeout_minutes):
        return True
    
    return False


def update_last_activity():
    """
    Atualiza o timestamp da última atividade na sessão.
    """
    session['last_activity'] = datetime.now().timestamp()


def check_admin_security_requirements(view_func):
    """
    Decorador que verifica requisitos de segurança para administradores.
    - Restrição de IP
    - Timeout de sessão
    - Autenticação de dois fatores
    """
    @functools.wraps(view_func)
    def decorated_function(*args, **kwargs):
        # Verificar autenticação
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Obter configurações
        settings = get_security_settings(current_app)
        
        # Verificar restrição de IP
        if settings['ip_restriction_enabled']:
            client_ip = request.remote_addr
            if not check_ip_restriction(client_ip, settings['allowed_ips']):
                logger.warning(f"Tentativa de acesso de IP não autorizado: {client_ip}")
                flash('Acesso negado. Seu endereço IP não está autorizado.', 'danger')
                return redirect(url_for('index'))
        
        # Verificar timeout de sessão
        if check_session_timeout():
            logger.info(f"Sessão expirada para usuário: {current_user.username}")
            flash('Sua sessão expirou devido a inatividade. Por favor, faça login novamente.', 'warning')
            return redirect(url_for('auth.logout'))
        
        # Atualizar timestamp de atividade
        update_last_activity()
        
        # Verificar 2FA
        if settings['two_factor_enabled'] and 'admin_2fa_verified' not in session:
            # Salvar URL original para redirecionamento após verificação
            session['next_url'] = request.url
            flash('É necessária verificação de dois fatores para acessar esta área.', 'warning')
            return redirect(url_for('auth.two_factor'))
        
        return view_func(*args, **kwargs)
    
    return decorated_function