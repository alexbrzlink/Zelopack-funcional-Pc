"""
Rotas para o módulo de Configurações.
"""
import logging
import json
import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import SystemConfig, User, db
from werkzeug.security import generate_password_hash
from utils.activity_logger import log_view, log_action
from werkzeug.utils import secure_filename

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
        flash('Acesso negado. Você não tem permissão para acessar configurações.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização da página principal de configurações'
    )
    
    # Obter configurações do sistema
    configs = {}
    system_configs = SystemConfig.query.all()
    
    for config in system_configs:
        if '.' in config.key:
            section, name = config.key.split('.', 1)
            if section not in configs:
                configs[section] = {}
            configs[section][name] = config.value
        else:
            configs[config.key] = config.value
    
    return render_template('configuracoes/index.html', 
                          title='Configurações', 
                          configs=configs)


@configuracoes_bp.route('/gerais')
@login_required
def gerais():
    """Página de configurações gerais."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar configurações.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização da página de configurações gerais'
    )
    
    # Obter configurações gerais
    configs = {}
    system_configs = SystemConfig.query.filter(SystemConfig.key.like('general.%')).all()
    
    for config in system_configs:
        _, name = config.key.split('.', 1)
        configs[name] = config.value
    
    return render_template('configuracoes/gerais.html', 
                          title='Configurações Gerais', 
                          configs=configs)


@configuracoes_bp.route('/email')
@login_required
def email():
    """Página de configurações de email."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar configurações.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização da página de configurações de email'
    )
    
    # Obter configurações de email
    configs = {}
    system_configs = SystemConfig.query.filter(SystemConfig.key.like('email.%')).all()
    
    for config in system_configs:
        _, name = config.key.split('.', 1)
        configs[name] = config.value
    
    return render_template('configuracoes/email.html', 
                          title='Configurações de Email', 
                          configs=configs)


@configuracoes_bp.route('/seguranca')
@login_required
def seguranca():
    """Página de configurações de segurança."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar configurações.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização da página de configurações de segurança'
    )
    
    # Obter configurações de segurança
    configs = {}
    system_configs = SystemConfig.query.filter(SystemConfig.key.like('security.%')).all()
    
    for config in system_configs:
        _, name = config.key.split('.', 1)
        configs[name] = config.value
    
    return render_template('configuracoes/seguranca.html', 
                          title='Configurações de Segurança', 
                          configs=configs)


@configuracoes_bp.route('/personalizar')
@login_required
def personalizar():
    """Página de personalização da interface."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar configurações.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização da página de personalização'
    )
    
    # Obter configurações de UI
    configs = {}
    system_configs = SystemConfig.query.filter(SystemConfig.key.like('ui.%')).all()
    
    for config in system_configs:
        _, name = config.key.split('.', 1)
        configs[name] = config.value
    
    return render_template('configuracoes/personalizar.html', 
                          title='Personalização', 
                          configs=configs)


@configuracoes_bp.route('/atualizar', methods=['POST'])
@login_required
def update_config():
    """Atualizar configurações do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Obter dados da requisição
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Dados inválidos'}), 400
        
        section = data.get('section')
        settings = data.get('settings')
        
        if not section or not settings:
            return jsonify({'success': False, 'message': 'Parâmetros incompletos'}), 400
        
        # Atualizar ou criar configurações
        for key, value in settings.items():
            config_key = f"{section}.{key}"
            
            # Verificar se a configuração já existe
            config = SystemConfig.query.filter_by(key=config_key).first()
            
            if config:
                # Atualizar configuração existente
                config.value = value
                config.updated_at = datetime.utcnow()
                config.updated_by = current_user.id
            else:
                # Criar nova configuração
                config = SystemConfig(
                    key=config_key,
                    value=value,
                    created_by=current_user.id,
                    updated_by=current_user.id
                )
                db.session.add(config)
            
        # Salvar alterações
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
        logger.error(f"Erro ao atualizar configurações: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar configurações: {str(e)}'}), 500


@configuracoes_bp.route('/upload-logo', methods=['POST'])
@login_required
def upload_logo():
    """Upload de logo do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        if 'logo' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['logo']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar extensão do arquivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'svg', 'gif'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'success': False, 'message': 'Formato de arquivo não permitido'}), 400
        
        # Criar diretório se não existir
        logo_dir = os.path.join(current_app.static_folder, 'img')
        os.makedirs(logo_dir, exist_ok=True)
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        file_path = os.path.join(logo_dir, filename)
        file.save(file_path)
        
        # Atualizar configuração
        config_key = 'general.system_logo'
        logo_url = f'/static/img/{filename}'
        
        config = SystemConfig.query.filter_by(key=config_key).first()
        
        if config:
            config.value = logo_url
            config.updated_at = datetime.utcnow()
            config.updated_by = current_user.id
        else:
            config = SystemConfig(
                key=config_key,
                value=logo_url,
                created_by=current_user.id,
                updated_by=current_user.id
            )
            db.session.add(config)
        
        db.session.commit()
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='update',
            module='configuracoes',
            entity_type='SystemConfig',
            details='Upload de nova logo do sistema'
        )
        
        return jsonify({'success': True, 'message': 'Logo atualizada com sucesso!', 'logo_url': logo_url})
    except Exception as e:
        logger.error(f"Erro ao fazer upload da logo: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao fazer upload da logo: {str(e)}'}), 500


@configuracoes_bp.route('/backup', methods=['GET'])
@login_required
def backup_page():
    """Página de backup e restauração do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar backup do sistema.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='configuracoes',
        details='Visualização da página de backup e restauração'
    )
    
    # Obter lista de backups disponíveis
    from utils.backup_manager import BackupManager
    backup_manager = BackupManager(current_app)
    available_backups = backup_manager.get_available_backups()
    
    return render_template('configuracoes/backup.html', 
                          title='Backup e Restauração', 
                          backups=available_backups)


@configuracoes_bp.route('/backup-config', methods=['GET'])
@login_required
def backup_config():
    """Gerar backup apenas das configurações."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para realizar backup de configurações.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        # Obter todas as configurações
        configs = {}
        system_configs = SystemConfig.query.all()
        
        for config in system_configs:
            if '.' in config.key:
                section, name = config.key.split('.', 1)
                if section not in configs:
                    configs[section] = {}
                configs[section][name] = config.value
            else:
                configs[config.key] = config.value
        
        # Converter para JSON
        config_json = json.dumps(configs, indent=2)
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='backup',
            module='configuracoes',
            entity_type='SystemConfig',
            details='Backup de configurações'
        )
        
        # Retornar arquivo JSON para download
        from flask import Response
        response = Response(
            config_json,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment;filename=zelopack_config_backup_{datetime.now().strftime("%Y%m%d")}.json'}
        )
        
        return response
    except Exception as e:
        logger.error(f"Erro ao gerar backup de configurações: {str(e)}")
        flash(f'Erro ao gerar backup de configurações: {str(e)}', 'danger')
        return redirect(url_for('configuracoes.index'))


@configuracoes_bp.route('/restaurar-config', methods=['POST'])
@login_required
def restore_config():
    """Restaurar configurações a partir de backup."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        if 'backup_file' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['backup_file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar extensão do arquivo
        if not file.filename.endswith('.json'):
            return jsonify({'success': False, 'message': 'Formato de arquivo inválido. É necessário um arquivo JSON.'}), 400
        
        # Ler arquivo
        try:
            content = file.read()
            configs = json.loads(content)
        except Exception:
            return jsonify({'success': False, 'message': 'Arquivo JSON inválido'}), 400
        
        # Atualizar configurações
        for section, settings in configs.items():
            if isinstance(settings, dict):
                for key, value in settings.items():
                    config_key = f"{section}.{key}"
                    update_single_config(config_key, value)
            else:
                update_single_config(section, settings)
        
        # Salvar alterações
        db.session.commit()
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='restore',
            module='configuracoes',
            entity_type='SystemConfig',
            details='Restauração de backup de configurações'
        )
        
        return jsonify({'success': True, 'message': 'Configurações restauradas com sucesso!'})
    except Exception as e:
        logger.error(f"Erro ao restaurar configurações: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao restaurar configurações: {str(e)}'}), 500


@configuracoes_bp.route('/criar-backup-sistema', methods=['POST'])
@login_required
def create_system_backup():
    """Criar backup completo do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Obter parâmetros
        include_uploads = request.form.get('include_uploads', 'true') == 'true'
        include_logs = request.form.get('include_logs', 'false') == 'true'
        
        # Criar backup
        from utils.backup_manager import BackupManager
        backup_manager = BackupManager(current_app)
        result = backup_manager.create_system_backup(
            include_uploads=include_uploads,
            include_logs=include_logs
        )
        
        if not result['success']:
            return jsonify({'success': False, 'message': f"Erro ao criar backup: {result.get('error', 'Erro desconhecido')}"})
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='backup',
            module='configuracoes',
            entity_type='System',
            details=f"Backup completo do sistema: {result['file_name']}"
        )
        
        return jsonify({
            'success': True, 
            'message': 'Backup do sistema criado com sucesso!',
            'file_name': result['file_name'],
            'created_at': result['created_at'],
            'size': result['size']
        })
    except Exception as e:
        logger.error(f"Erro ao criar backup do sistema: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao criar backup do sistema: {str(e)}'}), 500


@configuracoes_bp.route('/restaurar-sistema', methods=['POST'])
@login_required
def restore_system():
    """Restaurar sistema a partir de um backup."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Verificar se foi especificado um arquivo
        backup_file = request.form.get('backup_file')
        if not backup_file:
            return jsonify({'success': False, 'message': 'Nenhum arquivo de backup especificado'}), 400
        
        # Obter parâmetros
        restore_uploads = request.form.get('restore_uploads', 'true') == 'true'
        restore_logs = request.form.get('restore_logs', 'false') == 'true'
        
        # Criar gerenciador de backup
        from utils.backup_manager import BackupManager
        backup_manager = BackupManager(current_app)
        
        # Verificar se o arquivo existe
        backups = backup_manager.get_available_backups()
        backup_exists = any(b['file_name'] == backup_file for b in backups)
        
        if not backup_exists:
            return jsonify({'success': False, 'message': 'Arquivo de backup não encontrado'}), 404
        
        # Caminho do arquivo
        backup_path = os.path.join(backup_manager.backup_dir, backup_file)
        
        # Restaurar sistema
        result = backup_manager.restore_system_from_backup(
            backup_file_path=backup_path,
            restore_uploads=restore_uploads,
            restore_logs=restore_logs
        )
        
        if not result['success']:
            return jsonify({'success': False, 'message': f"Erro ao restaurar sistema: {result.get('error', 'Erro desconhecido')}"})
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='restore',
            module='configuracoes',
            entity_type='System',
            details=f"Restauração do sistema a partir do backup: {backup_file}"
        )
        
        return jsonify({
            'success': True, 
            'message': 'Sistema restaurado com sucesso!',
            'backup_info': result.get('backup_info', {}),
            'restored_at': result.get('restored_at')
        })
    except Exception as e:
        logger.error(f"Erro ao restaurar sistema: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao restaurar sistema: {str(e)}'}), 500


@configuracoes_bp.route('/excluir-backup', methods=['POST'])
@login_required
def delete_backup():
    """Excluir um backup."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Verificar se foi especificado um arquivo
        backup_file = request.form.get('backup_file')
        if not backup_file:
            return jsonify({'success': False, 'message': 'Nenhum arquivo de backup especificado'}), 400
        
        # Criar gerenciador de backup
        from utils.backup_manager import BackupManager
        backup_manager = BackupManager(current_app)
        
        # Excluir backup
        result = backup_manager.delete_backup(backup_file)
        
        if not result:
            return jsonify({'success': False, 'message': 'Erro ao excluir backup ou arquivo não encontrado'})
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='delete',
            module='configuracoes',
            entity_type='Backup',
            details=f"Exclusão de backup: {backup_file}"
        )
        
        return jsonify({
            'success': True, 
            'message': 'Backup excluído com sucesso!'
        })
    except Exception as e:
        logger.error(f"Erro ao excluir backup: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao excluir backup: {str(e)}'}), 500


@configuracoes_bp.route('/download-backup/<filename>')
@login_required
def download_backup(filename):
    """Download de um arquivo de backup."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para baixar backups.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        # Criar gerenciador de backup
        from utils.backup_manager import BackupManager
        backup_manager = BackupManager(current_app)
        
        # Caminho do arquivo
        backup_path = os.path.join(backup_manager.backup_dir, filename)
        
        # Verificar se o arquivo existe
        if not os.path.exists(backup_path):
            flash('Arquivo de backup não encontrado.', 'danger')
            return redirect(url_for('configuracoes.backup_page'))
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='download',
            module='configuracoes',
            entity_type='Backup',
            details=f"Download de backup: {filename}"
        )
        
        # Retornar arquivo para download
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Erro ao fazer download de backup: {str(e)}")
        flash(f'Erro ao fazer download de backup: {str(e)}', 'danger')
        return redirect(url_for('configuracoes.backup_page'))


def update_single_config(key, value):
    """Função auxiliar para atualizar uma configuração específica."""
    config = SystemConfig.query.filter_by(key=key).first()
    
    if config:
        config.value = value
        config.updated_at = datetime.utcnow()
        config.updated_by = current_user.id
    else:
        config = SystemConfig(
            key=key,
            value=value,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(config)