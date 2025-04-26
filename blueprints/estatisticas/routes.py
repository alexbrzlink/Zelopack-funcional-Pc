"""
Rotas para o módulo de Estatísticas.
"""
import logging
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import User, Report, Supplier, UserActivity, db
from utils.activity_logger import log_view, log_action
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64
import seaborn as sns
import numpy as np

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
    
    # Dados para os gráficos
    stats = get_system_statistics()
    
    return render_template('estatisticas/index.html', 
                          title='Estatísticas', 
                          stats=stats)


@estatisticas_bp.route('/laudos')
@login_required
def laudos():
    """Estatísticas de laudos técnicos."""
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='estatisticas',
        details='Visualização de estatísticas de laudos'
    )
    
    # Obter dados para os gráficos
    graphs = generate_report_graphs()
    
    return render_template('estatisticas/laudos.html', 
                          title='Estatísticas de Laudos', 
                          graphs=graphs)


@estatisticas_bp.route('/usuarios')
@login_required
def usuarios():
    """Estatísticas de usuários."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar as estatísticas de usuários.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='estatisticas',
        details='Visualização de estatísticas de usuários'
    )
    
    # Obter dados para os gráficos
    graphs = generate_user_graphs()
    
    return render_template('estatisticas/usuarios.html', 
                          title='Estatísticas de Usuários', 
                          graphs=graphs)


@estatisticas_bp.route('/atividades')
@login_required
def atividades():
    """Estatísticas de atividades do sistema."""
    # Verificar se o usuário é administrador
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para acessar as estatísticas de atividades.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='estatisticas',
        details='Visualização de estatísticas de atividades'
    )
    
    # Obter dados para os gráficos
    graphs = generate_activity_graphs()
    
    return render_template('estatisticas/atividades.html', 
                          title='Estatísticas de Atividades', 
                          graphs=graphs)


@estatisticas_bp.route('/fornecedores')
@login_required
def fornecedores():
    """Estatísticas de fornecedores."""
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='estatisticas',
        details='Visualização de estatísticas de fornecedores'
    )
    
    # Obter dados para os gráficos
    graphs = generate_supplier_graphs()
    
    return render_template('estatisticas/fornecedores.html', 
                          title='Estatísticas de Fornecedores', 
                          graphs=graphs)


@estatisticas_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard interativo com todas as estatísticas."""
    # Registrar visualização
    log_view(
        user_id=current_user.id,
        module='estatisticas',
        details='Visualização do dashboard de estatísticas'
    )
    
    # Obter todos os dados para os gráficos
    stats = get_system_statistics()
    report_graphs = generate_report_graphs()
    user_graphs = generate_user_graphs() if current_user.role == 'admin' else {}
    activity_graphs = generate_activity_graphs() if current_user.role == 'admin' else {}
    supplier_graphs = generate_supplier_graphs()
    
    return render_template('estatisticas/dashboard.html', 
                          title='Dashboard de Estatísticas', 
                          stats=stats,
                          report_graphs=report_graphs,
                          user_graphs=user_graphs,
                          activity_graphs=activity_graphs,
                          supplier_graphs=supplier_graphs)


# ----- Funções auxiliares para geração de estatísticas -----

def get_system_statistics():
    """Retorna estatísticas gerais do sistema."""
    # Contagens gerais
    total_reports = Report.query.count()
    total_users = User.query.count()
    total_suppliers = Supplier.query.count()
    
    # Atividades recentes (últimos 7 dias)
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    recent_activities = UserActivity.query.filter(UserActivity.created_at >= week_ago).count()
    
    # Contagem de laudos por categoria
    reports_by_category = {}
    categories = ['materias_primas', 'edulcorantes', 'corantes', 'açúcar', 'embalagem']
    for category in categories:
        count = Report.query.filter_by(category=category).count()
        reports_by_category[category] = count
    
    # Gerar gráfico de laudos por categoria
    pie_chart = generate_pie_chart(reports_by_category, 'Laudos por Categoria')
    
    # Contagem de laudos por mês (últimos 6 meses)
    reports_by_month = {}
    for i in range(6):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start.replace(month=month_start.month + 1) if month_start.month < 12 
                    else month_start.replace(year=month_start.year + 1, month=1)) - timedelta(seconds=1)
        
        count = Report.query.filter(Report.created_at.between(month_start, month_end)).count()
        month_name = month_start.strftime('%b/%Y')
        reports_by_month[month_name] = count
    
    # Inverter a ordem para que seja cronológica
    reports_by_month = {k: reports_by_month[k] for k in sorted(reports_by_month.keys(), reverse=True)}
    
    # Gerar gráfico de laudos por mês
    bar_chart = generate_bar_chart(reports_by_month, 'Laudos por Mês')
    
    # Montar o objeto de estatísticas
    stats = {
        'total_reports': total_reports,
        'total_users': total_users,
        'total_suppliers': total_suppliers,
        'recent_activities': recent_activities,
        'reports_by_category': reports_by_category,
        'reports_by_month': reports_by_month,
        'pie_chart': pie_chart,
        'bar_chart': bar_chart
    }
    
    return stats


def generate_report_graphs():
    """Gera gráficos para estatísticas de laudos."""
    graphs = {}
    
    # Contagem de laudos por categoria
    reports_by_category = {}
    categories = ['materias_primas', 'edulcorantes', 'corantes', 'açúcar', 'embalagem']
    for category in categories:
        count = Report.query.filter_by(category=category).count()
        # Traduzir categorias para nomes mais amigáveis
        category_name = {
            'materias_primas': 'Matérias-Primas',
            'edulcorantes': 'Edulcorantes',
            'corantes': 'Corantes',
            'açúcar': 'Açúcar',
            'embalagem': 'Embalagem'
        }.get(category, category)
        reports_by_category[category_name] = count
    
    # Gerar gráfico de pizza de laudos por categoria
    graphs['category_pie'] = generate_pie_chart(reports_by_category, 'Laudos por Categoria')
    
    # Laudos por fornecedor (top 10)
    suppliers_with_most_reports = db.session.query(
        Supplier.name, db.func.count(Report.id).label('report_count')
    ).join(Report, Report.supplier_id == Supplier.id
    ).group_by(Supplier.id
    ).order_by(db.desc('report_count')
    ).limit(10).all()
    
    reports_by_supplier = {s.name: s.report_count for s in suppliers_with_most_reports}
    
    # Gerar gráfico de barras horizontal de laudos por fornecedor
    graphs['supplier_bar'] = generate_horizontal_bar_chart(reports_by_supplier, 'Laudos por Fornecedor (Top 10)')
    
    # Laudos por mês (últimos 12 meses)
    now = datetime.utcnow()
    reports_by_month = {}
    for i in range(12):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start.replace(month=month_start.month + 1) if month_start.month < 12 
                    else month_start.replace(year=month_start.year + 1, month=1)) - timedelta(seconds=1)
        
        count = Report.query.filter(Report.created_at.between(month_start, month_end)).count()
        month_name = month_start.strftime('%b/%Y')
        reports_by_month[month_name] = count
    
    # Inverter a ordem para que seja cronológica
    reports_by_month = {k: v for k, v in sorted(reports_by_month.items(), key=lambda item: datetime.strptime(item[0], '%b/%Y'))}
    
    # Gerar gráfico de linha de laudos por mês
    graphs['month_line'] = generate_line_chart(reports_by_month, 'Laudos por Mês (Últimos 12 Meses)')
    
    return graphs


def generate_user_graphs():
    """Gera gráficos para estatísticas de usuários."""
    graphs = {}
    
    # Usuários por função
    users_by_role = {}
    roles = ['admin', 'user', 'lab', 'viewer']
    for role in roles:
        count = User.query.filter_by(role=role).count()
        # Traduzir funções para nomes mais amigáveis
        role_name = {
            'admin': 'Administrador',
            'user': 'Usuário Padrão',
            'lab': 'Laboratório',
            'viewer': 'Visualizador'
        }.get(role, role)
        users_by_role[role_name] = count
    
    # Gerar gráfico de pizza de usuários por função
    graphs['role_pie'] = generate_pie_chart(users_by_role, 'Usuários por Função')
    
    # Usuários ativos vs inativos
    users_status = {
        'Ativos': User.query.filter_by(is_active=True).count(),
        'Inativos': User.query.filter_by(is_active=False).count()
    }
    
    # Gerar gráfico de barras de usuários ativos vs inativos
    graphs['status_bar'] = generate_bar_chart(users_status, 'Status dos Usuários')
    
    # Usuários criados por mês (últimos 12 meses)
    now = datetime.utcnow()
    users_by_month = {}
    for i in range(12):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start.replace(month=month_start.month + 1) if month_start.month < 12 
                    else month_start.replace(year=month_start.year + 1, month=1)) - timedelta(seconds=1)
        
        count = User.query.filter(User.created_at.between(month_start, month_end)).count()
        month_name = month_start.strftime('%b/%Y')
        users_by_month[month_name] = count
    
    # Inverter a ordem para que seja cronológica
    users_by_month = {k: v for k, v in sorted(users_by_month.items(), key=lambda item: datetime.strptime(item[0], '%b/%Y'))}
    
    # Gerar gráfico de linha de usuários por mês
    graphs['month_line'] = generate_line_chart(users_by_month, 'Novos Usuários por Mês')
    
    return graphs


def generate_activity_graphs():
    """Gera gráficos para estatísticas de atividades."""
    graphs = {}
    
    # Atividades por tipo de ação
    activities_by_action = db.session.query(
        UserActivity.action, db.func.count(UserActivity.id).label('count')
    ).group_by(UserActivity.action
    ).order_by(db.desc('count')
    ).all()
    
    action_counts = {}
    for action, count in activities_by_action:
        # Traduzir ações para nomes mais amigáveis
        action_name = {
            'login': 'Login',
            'logout': 'Logout',
            'create': 'Criação',
            'update': 'Atualização',
            'delete': 'Exclusão',
            'view': 'Visualização',
            'download': 'Download',
            'export': 'Exportação'
        }.get(action, action.title())
        action_counts[action_name] = count
    
    # Gerar gráfico de pizza de atividades por tipo de ação
    graphs['action_pie'] = generate_pie_chart(action_counts, 'Atividades por Tipo de Ação')
    
    # Atividades por módulo
    activities_by_module = db.session.query(
        UserActivity.module, db.func.count(UserActivity.id).label('count')
    ).group_by(UserActivity.module
    ).order_by(db.desc('count')
    ).all()
    
    module_counts = {}
    for module, count in activities_by_module:
        # Traduzir módulos para nomes mais amigáveis
        module_name = {
            'auth': 'Autenticação',
            'reports': 'Laudos',
            'suppliers': 'Fornecedores',
            'calculos': 'Cálculos',
            'admin': 'Administração',
            'dashboard': 'Dashboard',
            'documents': 'Documentos',
            'forms': 'Formulários',
            'estatisticas': 'Estatísticas',
            'configuracoes': 'Configurações',
            'alertas': 'Alertas',
            'banco_dados': 'Banco de Dados'
        }.get(module, module.title())
        module_counts[module_name] = count
    
    # Gerar gráfico de barras de atividades por módulo
    graphs['module_bar'] = generate_bar_chart(module_counts, 'Atividades por Módulo')
    
    # Atividades por dia (últimos 30 dias)
    now = datetime.utcnow()
    activities_by_day = {}
    for i in range(30):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start.replace(hour=23, minute=59, second=59)
        
        count = UserActivity.query.filter(UserActivity.created_at.between(day_start, day_end)).count()
        day_name = day_start.strftime('%d/%m')
        activities_by_day[day_name] = count
    
    # Inverter a ordem para que seja cronológica
    activities_by_day = {k: activities_by_day[k] for k in sorted(activities_by_day.keys(), key=lambda x: datetime.strptime(x, '%d/%m'))}
    
    # Gerar gráfico de linha de atividades por dia
    graphs['day_line'] = generate_line_chart(activities_by_day, 'Atividades por Dia (Últimos 30 Dias)')
    
    return graphs


def generate_supplier_graphs():
    """Gera gráficos para estatísticas de fornecedores."""
    graphs = {}
    
    # Fornecedores por país
    suppliers_by_country = db.session.query(
        Supplier.country, db.func.count(Supplier.id).label('count')
    ).group_by(Supplier.country
    ).order_by(db.desc('count')
    ).all()
    
    country_counts = {country: count for country, count in suppliers_by_country}
    
    # Gerar gráfico de pizza de fornecedores por país
    graphs['country_pie'] = generate_pie_chart(country_counts, 'Fornecedores por País')
    
    # Fornecedores por categoria
    suppliers_by_category = {}
    categories = ['materias_primas', 'edulcorantes', 'corantes', 'açúcar', 'embalagem']
    for category in categories:
        # Para cada fornecedor, verificar se ele tem laudos nesta categoria
        query = db.session.query(Supplier).distinct(
        ).join(Report, Report.supplier_id == Supplier.id
        ).filter(Report.category == category)
        
        count = query.count()
        
        # Traduzir categorias para nomes mais amigáveis
        category_name = {
            'materias_primas': 'Matérias-Primas',
            'edulcorantes': 'Edulcorantes',
            'corantes': 'Corantes',
            'açúcar': 'Açúcar',
            'embalagem': 'Embalagem'
        }.get(category, category)
        suppliers_by_category[category_name] = count
    
    # Gerar gráfico de barras de fornecedores por categoria
    graphs['category_bar'] = generate_bar_chart(suppliers_by_category, 'Fornecedores por Categoria')
    
    # Top 10 fornecedores com mais laudos
    top_suppliers = db.session.query(
        Supplier.name, db.func.count(Report.id).label('report_count')
    ).join(Report, Report.supplier_id == Supplier.id
    ).group_by(Supplier.id
    ).order_by(db.desc('report_count')
    ).limit(10).all()
    
    top_suppliers_data = {s.name: s.report_count for s in top_suppliers}
    
    # Gerar gráfico de barras horizontal para top 10 fornecedores
    graphs['top_suppliers_bar'] = generate_horizontal_bar_chart(top_suppliers_data, 'Top 10 Fornecedores com Mais Laudos')
    
    return graphs


# ----- Funções auxiliares para geração de gráficos -----

def generate_pie_chart(data, title):
    """Gera um gráfico de pizza com os dados fornecidos."""
    plt.figure(figsize=(8, 6))
    plt.style.use('ggplot')
    
    # Verificar se há dados
    if not data or all(value == 0 for value in data.values()):
        plt.text(0.5, 0.5, 'Sem dados disponíveis', 
                horizontalalignment='center', verticalalignment='center', 
                transform=plt.gca().transAxes, fontsize=14)
        plt.axis('off')
    else:
        # Criando o gráfico de pizza
        wedges, texts, autotexts = plt.pie(
            data.values(), 
            labels=None,
            autopct='%1.1f%%',
            startangle=90,
            shadow=False,
            wedgeprops={'edgecolor': 'w', 'linewidth': 1}
        )
        
        # Aumentar o tamanho das porcentagens
        for autotext in autotexts:
            autotext.set_size(10)
            autotext.set_color('white')
        
        # Adicionar legenda
        plt.legend(wedges, data.keys(), title="Categorias",
                  loc="center left", bbox_to_anchor=(0.9, 0, 0.5, 1))
    
    plt.title(title, fontsize=16, pad=20)
    plt.tight_layout()
    
    # Converter o gráfico para base64 para exibição em HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    graph = base64.b64encode(image_png).decode('utf-8')
    return graph


def generate_bar_chart(data, title):
    """Gera um gráfico de barras com os dados fornecidos."""
    plt.figure(figsize=(10, 6))
    plt.style.use('ggplot')
    
    # Verificar se há dados
    if not data or all(value == 0 for value in data.values()):
        plt.text(0.5, 0.5, 'Sem dados disponíveis', 
                horizontalalignment='center', verticalalignment='center', 
                transform=plt.gca().transAxes, fontsize=14)
        plt.axis('off')
    else:
        # Criando o gráfico de barras
        bars = plt.bar(data.keys(), data.values(), color='#00978D')
        
        # Adicionar valores acima das barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Quantidade', fontsize=12)
    
    plt.title(title, fontsize=16, pad=20)
    plt.tight_layout()
    
    # Converter o gráfico para base64 para exibição em HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    graph = base64.b64encode(image_png).decode('utf-8')
    return graph


def generate_horizontal_bar_chart(data, title):
    """Gera um gráfico de barras horizontais com os dados fornecidos."""
    plt.figure(figsize=(10, 8))
    plt.style.use('ggplot')
    
    # Verificar se há dados
    if not data or all(value == 0 for value in data.values()):
        plt.text(0.5, 0.5, 'Sem dados disponíveis', 
                horizontalalignment='center', verticalalignment='center', 
                transform=plt.gca().transAxes, fontsize=14)
        plt.axis('off')
    else:
        # Converter para listas e ordenar por valor
        names = list(data.keys())
        values = list(data.values())
        
        # Ordenar ambas as listas pelo valor (maior para menor)
        names, values = zip(*sorted(zip(names, values), key=lambda x: x[1], reverse=True))
        
        # Criando o gráfico de barras horizontais
        bars = plt.barh(names, values, color='#00978D')
        
        # Adicionar valores ao lado das barras
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}', va='center', fontsize=9)
        
        plt.xlabel('Quantidade', fontsize=12)
    
    plt.title(title, fontsize=16, pad=20)
    plt.tight_layout()
    
    # Converter o gráfico para base64 para exibição em HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    graph = base64.b64encode(image_png).decode('utf-8')
    return graph


def generate_line_chart(data, title):
    """Gera um gráfico de linha com os dados fornecidos."""
    plt.figure(figsize=(12, 6))
    plt.style.use('ggplot')
    
    # Verificar se há dados
    if not data or all(value == 0 for value in data.values()):
        plt.text(0.5, 0.5, 'Sem dados disponíveis', 
                horizontalalignment='center', verticalalignment='center', 
                transform=plt.gca().transAxes, fontsize=14)
        plt.axis('off')
    else:
        # Criando o gráfico de linha
        x = list(data.keys())
        y = list(data.values())
        
        plt.plot(x, y, marker='o', linestyle='-', color='#00978D', linewidth=2, markersize=8)
        
        # Adicionar valores acima dos pontos
        for i, (xi, yi) in enumerate(zip(x, y)):
            plt.text(i, yi + 0.5, f'{int(yi)}', ha='center', va='bottom', fontsize=9)
        
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Quantidade', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.title(title, fontsize=16, pad=20)
    plt.tight_layout()
    
    # Converter o gráfico para base64 para exibição em HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    graph = base64.b64encode(image_png).decode('utf-8')
    return graph