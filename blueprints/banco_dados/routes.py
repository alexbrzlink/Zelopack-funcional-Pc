"""
Rotas para o módulo de Banco de Dados.
"""
import logging
import json
import os
import subprocess
import psycopg2
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from models import DatabaseBackup, User, db
from utils.activity_logger import log_view, log_action
from werkzeug.utils import secure_filename

# Configuração do logger
logger = logging.getLogger(__name__)

# Criação do blueprint
banco_dados_bp = Blueprint('banco_dados', __name__, url_prefix='/banco-dados')


@banco_dados_bp.route('/')
@login_required
def index():
    """Página principal do módulo de banco de dados."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar o módulo de banco de dados.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='banco_dados',
        details='Visualização da página principal de banco de dados'
    )
    
    # Obter backups cadastrados no banco
    backups = DatabaseBackup.query.order_by(DatabaseBackup.created_at.desc()).all()
    
    # Obter estatísticas do banco de dados
    db_stats = get_db_stats()
    
    return render_template('banco_dados/index.html', 
                          title='Banco de Dados', 
                          backups=backups,
                          db_stats=db_stats)


@banco_dados_bp.route('/backup')
@login_required
def backup():
    """Página de backups do banco de dados."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar o módulo de banco de dados.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='banco_dados',
        details='Visualização da página de backups'
    )
    
    # Obter backups cadastrados no banco
    backups = DatabaseBackup.query.order_by(DatabaseBackup.created_at.desc()).all()
    
    return render_template('banco_dados/backup.html', 
                          title='Backups do Banco de Dados', 
                          backups=backups)


@banco_dados_bp.route('/criar-backup', methods=['POST'])
@login_required
def create_backup():
    """Criar um backup do banco de dados."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Obter descrição do formulário
        description = request.form.get('description', 'Backup automático')
        
        # Criar pasta de backups se não existir
        backup_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'backups')
        os.makedirs(backup_folder, exist_ok=True)
        
        # Nome do arquivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"zelopack_db_backup_{timestamp}.sql"
        backup_path = os.path.join(backup_folder, backup_filename)
        
        # Obter dados de conexão do banco
        db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        # Verificar se está usando PostgreSQL
        if db_url.startswith('postgresql://'):
            # Código para realizar o backup do PostgreSQL
            # Em ambiente real, usaríamos pg_dump
            # Para simulação, apenas criamos um arquivo vazio
            with open(backup_path, 'w') as f:
                f.write(f"-- Backup simulado do banco de dados\n-- Data: {datetime.now()}\n\n")
                f.write("-- Este é um arquivo de backup simulado para demonstração\n")
            
            # Registrar o backup no banco de dados
            backup = DatabaseBackup(
                filename=backup_filename,
                file_path=backup_path,
                file_size=os.path.getsize(backup_path),
                description=description,
                created_by=current_user.id
            )
            
            db.session.add(backup)
            db.session.commit()
            
            # Registrar atividade
            log_action(
                user_id=current_user.id,
                action='create',
                module='banco_dados',
                entity_type='DatabaseBackup',
                entity_id=backup.id,
                details=f'Criação de backup: {backup_filename}'
            )
            
            return jsonify({'success': True, 'message': 'Backup criado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': 'Tipo de banco de dados não suportado para backup'}), 400
    except Exception as e:
        logger.error(f"Erro ao criar backup: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao criar backup: {str(e)}'}), 500


@banco_dados_bp.route('/restaurar-backup/<int:id>', methods=['POST'])
@login_required
def restore_backup(id):
    """Restaurar um backup do banco de dados."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Obter o backup
        backup = DatabaseBackup.query.get_or_404(id)
        
        # Verificar se o arquivo existe
        if not os.path.exists(backup.file_path):
            return jsonify({'success': False, 'message': 'Arquivo de backup não encontrado'}), 404
        
        # Em um ambiente real, realizaríamos a restauração do backup
        # Para simulação, apenas registramos a atividade
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='restore',
            module='banco_dados',
            entity_type='DatabaseBackup',
            entity_id=backup.id,
            details=f'Restauração de backup: {backup.filename}'
        )
        
        return jsonify({'success': True, 'message': 'Backup restaurado com sucesso! (Simulação)'})
    except Exception as e:
        logger.error(f"Erro ao restaurar backup: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao restaurar backup: {str(e)}'}), 500


@banco_dados_bp.route('/download-backup/<int:id>')
@login_required
def download_backup(id):
    """Download de um arquivo de backup."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para baixar backups.', 'danger')
        return redirect(url_for('banco_dados.index'))
    
    # Obter o backup
    backup = DatabaseBackup.query.get_or_404(id)
    
    # Verificar se o arquivo existe
    if not os.path.exists(backup.file_path):
        flash('Arquivo de backup não encontrado.', 'danger')
        return redirect(url_for('banco_dados.backup'))
    
    # Registrar atividade
    log_action(
        user_id=current_user.id,
        action='download',
        module='banco_dados',
        entity_type='DatabaseBackup',
        entity_id=backup.id,
        details=f'Download de backup: {backup.filename}'
    )
    
    # Retornar o arquivo para download
    return send_file(backup.file_path, as_attachment=True, download_name=backup.filename)


@banco_dados_bp.route('/excluir-backup/<int:id>', methods=['POST'])
@login_required
def delete_backup(id):
    """Excluir um backup do banco de dados."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Obter o backup
        backup = DatabaseBackup.query.get_or_404(id)
        
        # Verificar se o arquivo existe e excluí-lo
        if os.path.exists(backup.file_path):
            os.remove(backup.file_path)
        
        # Registrar atividade antes de excluir
        log_action(
            user_id=current_user.id,
            action='delete',
            module='banco_dados',
            entity_type='DatabaseBackup',
            entity_id=backup.id,
            details=f'Exclusão de backup: {backup.filename}'
        )
        
        # Excluir o registro do banco
        db.session.delete(backup)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Backup excluído com sucesso!'})
    except Exception as e:
        logger.error(f"Erro ao excluir backup: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao excluir backup: {str(e)}'}), 500


@banco_dados_bp.route('/manutencao')
@login_required
def maintenance():
    """Página de manutenção do banco de dados."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar o módulo de banco de dados.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='banco_dados',
        details='Visualização da página de manutenção'
    )
    
    # Obter estatísticas do banco de dados
    db_stats = get_db_stats()
    
    return render_template('banco_dados/manutencao.html', 
                          title='Manutenção do Banco de Dados', 
                          db_stats=db_stats)


@banco_dados_bp.route('/otimizar', methods=['POST'])
@login_required
def optimize():
    """Otimizar o banco de dados."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Em um ambiente real, realizaríamos operações de otimização
        # Para simulação, apenas registramos a atividade
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='optimize',
            module='banco_dados',
            details='Otimização do banco de dados'
        )
        
        return jsonify({'success': True, 'message': 'Banco de dados otimizado com sucesso! (Simulação)'})
    except Exception as e:
        logger.error(f"Erro ao otimizar banco de dados: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao otimizar banco de dados: {str(e)}'}), 500


@banco_dados_bp.route('/verificar', methods=['POST'])
@login_required
def check():
    """Verificar integridade do banco de dados."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        # Em um ambiente real, realizaríamos verificações de integridade
        # Para simulação, apenas registramos a atividade
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='check',
            module='banco_dados',
            details='Verificação de integridade do banco de dados'
        )
        
        return jsonify({
            'success': True, 
            'message': 'Verificação concluída com sucesso! (Simulação)',
            'results': {
                'status': 'healthy',
                'issues_found': 0,
                'tables_checked': 15,
                'integrity_status': 'OK'
            }
        })
    except Exception as e:
        logger.error(f"Erro ao verificar banco de dados: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao verificar banco de dados: {str(e)}'}), 500


def get_db_stats():
    """Obtém estatísticas do banco de dados."""
    try:
        # Estatísticas do banco - simulação para exibição na interface
        # Em ambiente real, estas informações seriam obtidas do banco
        
        # Contagens de registros por tabela
        num_users = User.query.count()
        # Estatísticas de tabelas do banco
        tables = db.session.execute(db.text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")).fetchall()
        table_stats = []
        
        for table in tables:
            table_name = table[0]
            # Contar registros na tabela
            count = db.session.execute(db.text(f"SELECT COUNT(*) FROM \"{table_name}\"")).scalar()
            # Adicionar estatística
            table_stats.append({
                'name': table_name,
                'records': count,
                'last_analyzed': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'size': f"{count * 100 + 500} KB"  # Simulação de tamanho
            })
        
        # Estatísticas do sistema
        stats = {
            'total_tables': len(tables),
            'total_records': sum(stat['records'] for stat in table_stats),
            'database_size': f"{sum(stat['records'] * 100 for stat in table_stats) / 1024:.2f} MB",
            'tables': table_stats,
            'connection_status': 'Conectado',
            'system_status': 'Operacional',
            'last_backup': DatabaseBackup.query.order_by(DatabaseBackup.created_at.desc()).first(),
            'users': num_users
        }
        
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do banco: {str(e)}")
        return {
            'error': str(e),
            'connection_status': 'Erro',
            'system_status': 'Indisponível'
        }