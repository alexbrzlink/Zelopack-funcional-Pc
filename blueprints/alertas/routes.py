"""
Rotas para o módulo de Alertas do Sistema.
"""
import logging
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Alert, User, db
from utils.activity_logger import log_view, log_action

# Configuração do logger
logger = logging.getLogger(__name__)

# Criação do blueprint
alertas_bp = Blueprint('alertas', __name__, url_prefix='/alertas')


@alertas_bp.route('/')
@login_required
def index():
    """Página principal do módulo de alertas."""
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='alertas',
        details='Visualização da página principal de alertas'
    )
    
    # Obter alertas do usuário atual (que são diretamente para ele ou para todos)
    alerts = Alert.query.filter(
        db.or_(
            Alert.target_user_id == current_user.id,
            Alert.target_user_id == None
        ),
        Alert.is_active == True
    ).order_by(Alert.created_at.desc()).all()
    
    # Separar alertas por tipo
    alerts_by_type = {
        'info': [],
        'warning': [],
        'danger': [],
        'success': []
    }
    
    for alert in alerts:
        alerts_by_type[alert.type].append(alert)
    
    return render_template('alertas/index.html', 
                          title='Alertas', 
                          alerts=alerts,
                          alerts_by_type=alerts_by_type)


@alertas_bp.route('/todos')
@login_required
def all_alerts():
    """Página com todos os alertas do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para visualizar todos os alertas.', 'danger')
        return redirect(url_for('alertas.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='alertas',
        details='Visualização de todos os alertas do sistema'
    )
    
    # Obter todos os alertas
    alerts = Alert.query.order_by(Alert.created_at.desc()).all()
    
    return render_template('alertas/todos.html', 
                          title='Todos os Alertas', 
                          alerts=alerts)


@alertas_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def create():
    """Página para criação de novos alertas."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para criar alertas.', 'danger')
        return redirect(url_for('alertas.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='alertas',
        details='Visualização da página de criação de alerta'
    )
    
    if request.method == 'POST':
        # Obter dados do formulário
        title = request.form.get('title')
        message = request.form.get('message')
        alert_type = request.form.get('type')
        module = request.form.get('module', 'sistema')
        target_user_id = request.form.get('target_user_id')
        
        # Validar campos obrigatórios
        if not title or not message or not alert_type:
            flash('Por favor, preencha todos os campos obrigatórios.', 'warning')
        else:
            # Criar novo alerta
            alert = Alert(
                title=title,
                message=message,
                type=alert_type,
                module=module,
                created_by=current_user.id,
                target_user_id=target_user_id if target_user_id and target_user_id != '0' else None
            )
            
            # Se houver data de expiração
            expires_days = request.form.get('expires_days')
            if expires_days and expires_days.isdigit():
                alert.expires_at = datetime.utcnow() + timedelta(days=int(expires_days))
            
            db.session.add(alert)
            db.session.commit()
            
            # Registrar atividade
            log_action(
                user_id=current_user.id,
                action='create',
                module='alertas',
                entity_type='Alert',
                entity_id=alert.id,
                details=f'Criação de alerta: {title}'
            )
            
            flash('Alerta criado com sucesso!', 'success')
            return redirect(url_for('alertas.index'))
    
    # Obter lista de usuários para o campo de destinatário
    users = User.query.filter_by(is_active=True).order_by(User.name).all()
    
    # Listar módulos disponíveis
    modules = [
        ('sistema', 'Sistema'),
        ('reports', 'Laudos'),
        ('users', 'Usuários'),
        ('suppliers', 'Fornecedores'),
        ('calculos', 'Cálculos'),
        ('documents', 'Documentos'),
        ('forms', 'Formulários'),
        ('estatisticas', 'Estatísticas'),
        ('configuracoes', 'Configurações'),
        ('alertas', 'Alertas'),
        ('banco_dados', 'Banco de Dados')
    ]
    
    return render_template('alertas/criar.html', 
                          title='Criar Alerta', 
                          users=users,
                          modules=modules)


@alertas_bp.route('/marcar-lido/<int:id>', methods=['POST'])
@login_required
def mark_read(id):
    """Marcar um alerta como lido."""
    alert = Alert.query.get_or_404(id)
    
    # Verificar se o alerta é para o usuário atual ou se ele é admin
    if alert.target_user_id and alert.target_user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    alert.is_read = True
    db.session.commit()
    
    # Registrar atividade
    log_action(
        user_id=current_user.id,
        action='update',
        module='alertas',
        entity_type='Alert',
        entity_id=alert.id,
        details='Alerta marcado como lido'
    )
    
    return jsonify({'success': True})


@alertas_bp.route('/desativar/<int:id>', methods=['POST'])
@login_required
def deactivate(id):
    """Desativar um alerta."""
    alert = Alert.query.get_or_404(id)
    
    # Verificar se o usuário é admin
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    alert.is_active = False
    db.session.commit()
    
    # Registrar atividade
    log_action(
        user_id=current_user.id,
        action='update',
        module='alertas',
        entity_type='Alert',
        entity_id=alert.id,
        details='Alerta desativado'
    )
    
    return jsonify({'success': True})


@alertas_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Excluir um alerta."""
    alert = Alert.query.get_or_404(id)
    
    # Verificar se o usuário é admin
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    # Registrar atividade antes de excluir
    log_action(
        user_id=current_user.id,
        action='delete',
        module='alertas',
        entity_type='Alert',
        entity_id=alert.id,
        details=f'Exclusão de alerta: {alert.title}'
    )
    
    db.session.delete(alert)
    db.session.commit()
    
    return jsonify({'success': True})


@alertas_bp.route('/api/alertas-nao-lidos')
@login_required
def unread_alerts_api():
    """API para obter os alertas não lidos do usuário."""
    # Obter alertas não lidos do usuário atual (ou para todos)
    alerts = Alert.query.filter(
        db.or_(
            Alert.target_user_id == current_user.id,
            Alert.target_user_id == None
        ),
        Alert.is_read == False,
        Alert.is_active == True
    ).order_by(Alert.created_at.desc()).all()
    
    # Converter alertas para dicionário
    alerts_data = [alert.to_dict() for alert in alerts]
    
    return jsonify({
        'count': len(alerts),
        'alerts': alerts_data
    })


def create_system_alert(title, message, alert_type='info', module='sistema', target_user_id=None):
    """
    Função auxiliar para criar alertas do sistema.
    
    Args:
        title: Título do alerta
        message: Mensagem do alerta
        alert_type: Tipo do alerta (info, warning, danger, success)
        module: Módulo do sistema
        target_user_id: ID do usuário destinatário (opcional)
    
    Returns:
        Alert: O alerta criado
    """
    try:
        alert = Alert(
            title=title,
            message=message,
            type=alert_type,
            module=module,
            target_user_id=target_user_id
        )
        
        db.session.add(alert)
        db.session.commit()
        
        logger.info(f"Alerta do sistema criado: {title}")
        return alert
    except Exception as e:
        logger.error(f"Erro ao criar alerta do sistema: {str(e)}")
        db.session.rollback()
        return None