"""
Rotas para o módulo de Estatísticas.
"""
import logging
import json
import io
import base64
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import TechnicalDocument, Supplier, User, UserActivity, db
import matplotlib
matplotlib.use('Agg')  # Define o backend não interativo
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import seaborn as sns
from sqlalchemy import func, extract
import numpy as np
from utils.activity_logger import log_view, log_action

# Configuração do logger
logger = logging.getLogger(__name__)

# Criação do blueprint
estatisticas_bp = Blueprint('estatisticas', __name__, url_prefix='/estatisticas')


@estatisticas_bp.route('/')
@login_required
def index():
    """Página principal do módulo de estatísticas."""
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='estatisticas',
        details='Visualização da página principal de estatísticas'
    )
    
    # Obter estatísticas gerais
    total_reports = TechnicalDocument.query.count()
    total_suppliers = Supplier.query.count()
    total_users = User.query.count()
    
    # Obter relatórios por mês (últimos 6 meses)
    today = datetime.now()
    six_months_ago = today - timedelta(days=180)
    
    # Consulta SQL para obter contagem de documentos por mês
    reports_by_month = db.session.query(
        extract('year', TechnicalDocument.upload_date).label('year'),
        extract('month', TechnicalDocument.upload_date).label('month'),
        func.count(TechnicalDocument.id).label('count')
    ).filter(
        TechnicalDocument.upload_date >= six_months_ago
    ).group_by(
        extract('year', TechnicalDocument.upload_date),
        extract('month', TechnicalDocument.upload_date)
    ).order_by(
        extract('year', TechnicalDocument.upload_date),
        extract('month', TechnicalDocument.upload_date)
    ).all()
    
    # Preparar dados para o gráfico de linha
    months = []
    counts = []
    
    # Preencher todos os meses, mesmo os que não têm laudos
    for i in range(6):
        month_date = today - timedelta(days=30 * (5 - i))
        month_name = month_date.strftime('%b/%Y')
        months.append(month_name)
        
        # Verificar se há registros para este mês
        count = 0
        for record in reports_by_month:
            if record.year == month_date.year and record.month == month_date.month:
                count = record.count
                break
        
        counts.append(count)
    
    # Gerar gráfico de linha para documentos por mês
    line_chart = create_line_chart(months, counts, 'Documentos por Mês', 'Mês', 'Quantidade')
    
    # Obter documentos por categoria (top 5)
    reports_by_category = db.session.query(
        TechnicalDocument.document_type,
        func.count(TechnicalDocument.id).label('count')
    ).group_by(
        TechnicalDocument.document_type
    ).order_by(
        func.count(TechnicalDocument.id).desc()
    ).limit(5).all()
    
    # Preparar dados para o gráfico de barras
    category_names = [doc.document_type for doc in reports_by_category]
    category_counts = [doc.count for doc in reports_by_category]
    
    # Gerar gráfico de barras para documentos por categoria
    bar_chart = create_bar_chart(category_names, category_counts, 'Documentos por Categoria', 'Categoria', 'Quantidade')
    
    # Obter atividades por módulo
    activities_by_module = db.session.query(
        UserActivity.module,
        func.count(UserActivity.id).label('count')
    ).group_by(
        UserActivity.module
    ).order_by(
        func.count(UserActivity.id).desc()
    ).all()
    
    # Preparar dados para o gráfico de pizza
    module_names = [activity.module for activity in activities_by_module]
    module_counts = [activity.count for activity in activities_by_module]
    
    # Gerar gráfico de pizza para atividades por módulo
    pie_chart = create_pie_chart(module_names, module_counts, 'Atividades por Módulo')
    
    # Atividades recentes
    recent_activities = UserActivity.query.order_by(UserActivity.timestamp.desc()).limit(10).all()
    
    return render_template('estatisticas/index.html', 
                          title='Estatísticas', 
                          total_reports=total_reports,
                          total_suppliers=total_suppliers,
                          total_users=total_users,
                          line_chart=line_chart,
                          bar_chart=bar_chart,
                          pie_chart=pie_chart,
                          recent_activities=recent_activities)


@estatisticas_bp.route('/documentos')
@login_required
def documents_statistics():
    """Estatísticas detalhadas de documentos."""
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='estatisticas',
        details='Visualização de estatísticas detalhadas de documentos'
    )
    
    # Obter documentos por tipo
    reports_by_category = db.session.query(
        TechnicalDocument.document_type,
        func.count(TechnicalDocument.id).label('count')
    ).group_by(
        TechnicalDocument.document_type
    ).order_by(
        func.count(TechnicalDocument.id).desc()
    ).all()
    
    # Preparar dados para o gráfico de barras
    category_names = [doc.document_type for doc in reports_by_category]
    category_counts = [doc.count for doc in reports_by_category]
    
    # Gerar gráfico de barras para documentos por tipo
    category_chart = create_bar_chart(category_names, category_counts, 'Documentos por Tipo', 'Tipo', 'Quantidade')
    
    # Obter documentos por status
    reports_by_status = db.session.query(
        TechnicalDocument.status,
        func.count(TechnicalDocument.id).label('count')
    ).group_by(
        TechnicalDocument.status
    ).order_by(
        func.count(TechnicalDocument.id).desc()
    ).all()
    
    # Preparar dados para o gráfico de pizza
    status_names = [doc.status for doc in reports_by_status]
    status_counts = [doc.count for doc in reports_by_status]
    
    # Gerar gráfico de pizza para documentos por status
    status_chart = create_pie_chart(status_names, status_counts, 'Documentos por Status')
    
    # Obter documentos por dia da semana
    reports_by_day = db.session.query(
        extract('dow', TechnicalDocument.upload_date).label('day'),
        func.count(TechnicalDocument.id).label('count')
    ).group_by(
        extract('dow', TechnicalDocument.upload_date)
    ).order_by(
        extract('dow', TechnicalDocument.upload_date)
    ).all()
    
    # Mapear dias da semana
    day_mapping = {
        0: 'Segunda',
        1: 'Terça',
        2: 'Quarta',
        3: 'Quinta',
        4: 'Sexta',
        5: 'Sábado',
        6: 'Domingo'
    }
    
    # Preparar dados para o gráfico de barras
    day_names = [day_mapping.get(int(report.day), 'Desconhecido') for report in reports_by_day]
    day_counts = [report.count for report in reports_by_day]
    
    # Gerar gráfico de barras para documentos por dia da semana
    day_chart = create_bar_chart(day_names, day_counts, 'Documentos por Dia da Semana', 'Dia', 'Quantidade')
    
    return render_template('estatisticas/documentos.html', 
                          title='Estatísticas de Documentos', 
                          category_chart=category_chart,
                          status_chart=status_chart,
                          day_chart=day_chart)


@estatisticas_bp.route('/usuarios')
@login_required
def users_statistics():
    """Estatísticas detalhadas de usuários."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar estatísticas de usuários.', 'danger')
        return redirect(url_for('estatisticas.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='estatisticas',
        details='Visualização de estatísticas detalhadas de usuários'
    )
    
    # Obter usuários por papel
    users_by_role = db.session.query(
        User.role,
        func.count(User.id).label('count')
    ).group_by(
        User.role
    ).order_by(
        func.count(User.id).desc()
    ).all()
    
    # Preparar dados para o gráfico de pizza
    role_names = [user.role for user in users_by_role]
    role_counts = [user.count for user in users_by_role]
    
    # Gerar gráfico de pizza para usuários por papel
    role_chart = create_pie_chart(role_names, role_counts, 'Usuários por Papel')
    
    # Obter atividades por usuário (top 10)
    activities_by_user = db.session.query(
        User.name,
        func.count(UserActivity.id).label('count')
    ).join(
        UserActivity, UserActivity.user_id == User.id
    ).group_by(
        User.name
    ).order_by(
        func.count(UserActivity.id).desc()
    ).limit(10).all()
    
    # Preparar dados para o gráfico de barras
    user_names = [user.name for user in activities_by_user]
    user_counts = [user.count for user in activities_by_user]
    
    # Gerar gráfico de barras para atividades por usuário
    user_chart = create_bar_chart(user_names, user_counts, 'Atividades por Usuário', 'Usuário', 'Quantidade')
    
    # Obter últimos usuários criados
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('estatisticas/usuarios.html', 
                          title='Estatísticas de Usuários', 
                          role_chart=role_chart,
                          user_chart=user_chart,
                          recent_users=recent_users)


@estatisticas_bp.route('/atividades')
@login_required
def activities_statistics():
    """Estatísticas detalhadas de atividades."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar estatísticas de atividades.', 'danger')
        return redirect(url_for('estatisticas.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='estatisticas',
        details='Visualização de estatísticas detalhadas de atividades'
    )
    
    # Obter atividades por tipo de ação
    activities_by_action = db.session.query(
        UserActivity.action,
        func.count(UserActivity.id).label('count')
    ).group_by(
        UserActivity.action
    ).order_by(
        func.count(UserActivity.id).desc()
    ).all()
    
    # Preparar dados para o gráfico de pizza
    action_names = [activity.action for activity in activities_by_action]
    action_counts = [activity.count for activity in activities_by_action]
    
    # Gerar gráfico de pizza para atividades por tipo de ação
    action_chart = create_pie_chart(action_names, action_counts, 'Atividades por Tipo de Ação')
    
    # Obter atividades por hora do dia
    activities_by_hour = db.session.query(
        extract('hour', UserActivity.timestamp).label('hour'),
        func.count(UserActivity.id).label('count')
    ).group_by(
        extract('hour', UserActivity.timestamp)
    ).order_by(
        extract('hour', UserActivity.timestamp)
    ).all()
    
    # Preparar dados para o gráfico de barras
    hour_names = [f"{int(activity.hour)}h" for activity in activities_by_hour]
    hour_counts = [activity.count for activity in activities_by_hour]
    
    # Gerar gráfico de barras para atividades por hora do dia
    hour_chart = create_bar_chart(hour_names, hour_counts, 'Atividades por Hora do Dia', 'Hora', 'Quantidade')
    
    # Obter atividades por dia da semana
    activities_by_day = db.session.query(
        extract('dow', UserActivity.timestamp).label('day'),
        func.count(UserActivity.id).label('count')
    ).group_by(
        extract('dow', UserActivity.timestamp)
    ).order_by(
        extract('dow', UserActivity.timestamp)
    ).all()
    
    # Mapear dias da semana
    day_mapping = {
        0: 'Segunda',
        1: 'Terça',
        2: 'Quarta',
        3: 'Quinta',
        4: 'Sexta',
        5: 'Sábado',
        6: 'Domingo'
    }
    
    # Preparar dados para o gráfico de barras
    day_names = [day_mapping.get(int(activity.day), 'Desconhecido') for activity in activities_by_day]
    day_counts = [activity.count for activity in activities_by_day]
    
    # Gerar gráfico de barras para atividades por dia da semana
    day_chart = create_bar_chart(day_names, day_counts, 'Atividades por Dia da Semana', 'Dia', 'Quantidade')
    
    return render_template('estatisticas/atividades.html', 
                          title='Estatísticas de Atividades', 
                          action_chart=action_chart,
                          hour_chart=hour_chart,
                          day_chart=day_chart)


# Funções auxiliares para geração de gráficos

def create_line_chart(x_data, y_data, title, x_label, y_label):
    """Criar gráfico de linha e retornar como base64."""
    plt.figure(figsize=(10, 5))
    sns.set_style("whitegrid")
    plt.plot(x_data, y_data, marker='o', linewidth=2, color='#3498db')
    plt.title(title, fontsize=16)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Salvar o gráfico em um buffer de memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Codificar em base64 para exibir no HTML
    data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return data


def create_bar_chart(x_data, y_data, title, x_label, y_label):
    """Criar gráfico de barras e retornar como base64."""
    plt.figure(figsize=(10, 5))
    sns.set_style("whitegrid")
    
    # Criar paleta de cores personalizada
    colors = sns.color_palette("Blues_d", len(x_data))
    
    # Criar o gráfico de barras
    bars = plt.bar(x_data, y_data, color=colors)
    
    # Adicionar valor em cima de cada barra
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.title(title, fontsize=16)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.tight_layout()
    
    # Salvar o gráfico em um buffer de memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Codificar em base64 para exibir no HTML
    data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return data


def create_pie_chart(labels, sizes, title):
    """Criar gráfico de pizza e retornar como base64."""
    plt.figure(figsize=(8, 8))
    sns.set_style("whitegrid")
    
    # Criar paleta de cores personalizada
    colors = sns.color_palette("Blues", len(labels))
    
    # Criar o gráfico de pizza
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
            shadow=False, startangle=90, wedgeprops={'edgecolor': 'w'})
    
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(title, fontsize=16)
    plt.tight_layout()
    
    # Salvar o gráfico em um buffer de memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Codificar em base64 para exibir no HTML
    data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return data