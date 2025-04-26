"""
Rotas para o módulo de Configurações do Sistema.
"""
import logging
import json
import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import User, SystemConfig, db
from utils.activity_logger import log_view, log_action
from werkzeug.security import generate_password_hash

# Configuração do logger
logger = logging.getLogger(__name__)

# Criação do blueprint
configuracoes_bp = Blueprint('configuracoes', __name__, url_prefix='/configuracoes')


@configuracoes_bp.route('/')
@login_required
def index():
    """Página principal do módulo de configurações."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar as configurações do sistema.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização da página principal de configurações'
    )
    
    # Obter configurações atuais
    configs = SystemConfig.query.all()
    config_dict = {config.key: config.value for config in configs}
    
    return render_template('configuracoes/index.html', 
                          title='Configurações do Sistema', 
                          configs=config_dict)


@configuracoes_bp.route('/gerais')
@login_required
def gerais():
    """Configurações gerais do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar as configurações do sistema.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização das configurações gerais'
    )
    
    # Obter configurações gerais
    configs = SystemConfig.query.filter(SystemConfig.key.like('general.%')).all()
    config_dict = {config.key.replace('general.', ''): config.value for config in configs}
    
    return render_template('configuracoes/gerais.html', 
                          title='Configurações Gerais', 
                          configs=config_dict)


@configuracoes_bp.route('/email')
@login_required
def email():
    """Configurações de email do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar as configurações do sistema.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização das configurações de email'
    )
    
    # Obter configurações de email
    configs = SystemConfig.query.filter(SystemConfig.key.like('email.%')).all()
    config_dict = {config.key.replace('email.', ''): config.value for config in configs}
    
    return render_template('configuracoes/email.html', 
                          title='Configurações de Email', 
                          configs=config_dict)


@configuracoes_bp.route('/seguranca')
@login_required
def seguranca():
    """Configurações de segurança do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar as configurações do sistema.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização das configurações de segurança'
    )
    
    # Obter configurações de segurança
    configs = SystemConfig.query.filter(SystemConfig.key.like('security.%')).all()
    config_dict = {config.key.replace('security.', ''): config.value for config in configs}
    
    return render_template('configuracoes/seguranca.html', 
                          title='Configurações de Segurança', 
                          configs=config_dict)


@configuracoes_bp.route('/personalizar')
@login_required
def personalizar():
    """Configurações de personalização do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar as configurações do sistema.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização das configurações de personalização'
    )
    
    # Obter configurações de personalização
    configs = SystemConfig.query.filter(SystemConfig.key.like('ui.%')).all()
    config_dict = {config.key.replace('ui.', ''): config.value for config in configs}
    
    return render_template('configuracoes/personalizar.html', 
                          title='Personalização da Interface', 
                          configs=config_dict)


@configuracoes_bp.route('/update', methods=['POST'])
@login_required
def update_config():
    """Atualizar configurações do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    # Obter dados do formulário
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
    
    section = data.get('section', 'general')
    settings = data.get('settings', {})
    
    for key, value in settings.items():
        full_key = f"{section}.{key}"
        config = SystemConfig.query.filter_by(key=full_key).first()
        
        if config:
            # Atualizar configuração existente
            config.value = value
            config.updated_at = datetime.utcnow()
            config.updated_by = current_user.id
        else:
            # Criar nova configuração
            config = SystemConfig(
                key=full_key,
                value=value,
                created_by=current_user.id,
                updated_by=current_user.id
            )
            db.session.add(config)
        
    try:
        db.session.commit()
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='update',
            module='configuracoes',
            entity_type='SystemConfig',
            details=f'Atualização de configurações: {section}'
        )
        
        return jsonify({'success': True, 'message': 'Configurações atualizadas com sucesso!'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar configurações: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao atualizar configurações: {str(e)}'}), 500


@configuracoes_bp.route('/backup')
@login_required
def backup():
    """Página de backup e restauração do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar as configurações do sistema.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização da página de backup e restauração'
    )
    
    # Obter lista de backups disponíveis
    backup_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'backups')
    os.makedirs(backup_folder, exist_ok=True)
    
    backups = []
    for filename in os.listdir(backup_folder):
        if filename.endswith('.zip'):
            filepath = os.path.join(backup_folder, filename)
            backups.append({
                'name': filename,
                'size': os.path.getsize(filepath),
                'date': datetime.fromtimestamp(os.path.getmtime(filepath))
            })
    
    return render_template('configuracoes/backup.html', 
                          title='Backup e Restauração', 
                          backups=sorted(backups, key=lambda x: x['date'], reverse=True))


@configuracoes_bp.route('/create-backup', methods=['POST'])
@login_required
def create_backup():
    """Criar um backup do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Criar pasta de backups se não existir
        backup_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'backups')
        os.makedirs(backup_folder, exist_ok=True)
        
        # Nome do arquivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"zelopack_backup_{timestamp}.zip"
        backup_path = os.path.join(backup_folder, backup_filename)
        
        # Executar backup
        # Aqui você implementaria o código real para criar o backup
        # Por simplificação, apenas criamos um arquivo vazio
        with open(backup_path, 'w') as f:
            f.write('Backup simulado')
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='create',
            module='configuracoes',
            entity_type='Backup',
            details=f'Criação de backup: {backup_filename}'
        )
        
        return jsonify({
            'success': True, 
            'message': 'Backup criado com sucesso!',
            'filename': backup_filename
        })
    except Exception as e:
        logger.error(f"Erro ao criar backup: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao criar backup: {str(e)}'}), 500


@configuracoes_bp.route('/restore-backup/<filename>', methods=['POST'])
@login_required
def restore_backup(filename):
    """Restaurar um backup do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Verificar se o arquivo existe
        backup_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'backups')
        backup_path = os.path.join(backup_folder, filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'message': 'Arquivo de backup não encontrado'}), 404
        
        # Aqui você implementaria o código real para restaurar o backup
        # Por simplificação, apenas simulamos a restauração
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='restore',
            module='configuracoes',
            entity_type='Backup',
            details=f'Restauração de backup: {filename}'
        )
        
        return jsonify({
            'success': True, 
            'message': 'Backup restaurado com sucesso!'
        })
    except Exception as e:
        logger.error(f"Erro ao restaurar backup: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao restaurar backup: {str(e)}'}), 500


@configuracoes_bp.route('/delete-backup/<filename>', methods=['POST'])
@login_required
def delete_backup(filename):
    """Excluir um backup do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Verificar se o arquivo existe
        backup_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'backups')
        backup_path = os.path.join(backup_folder, filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'message': 'Arquivo de backup não encontrado'}), 404
        
        # Excluir arquivo
        os.remove(backup_path)
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='delete',
            module='configuracoes',
            entity_type='Backup',
            details=f'Exclusão de backup: {filename}'
        )
        
        return jsonify({
            'success': True, 
            'message': 'Backup excluído com sucesso!'
        })
    except Exception as e:
        logger.error(f"Erro ao excluir backup: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao excluir backup: {str(e)}'}), 500