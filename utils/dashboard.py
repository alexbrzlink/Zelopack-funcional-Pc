"""
Utilitários para geração de estatísticas e dados para os dashboards
"""
import os
import base64
from datetime import datetime, timedelta
from io import BytesIO
import calendar
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Uso sem interface gráfica
import matplotlib.pyplot as plt
from sqlalchemy import func, extract, case, and_

from models import Report, User
from app import db

# Configurações globais para os gráficos
plt.style.use('ggplot')
COLORS = {
    'primary': '#3498db',
    'success': '#2ecc71',
    'info': '#3498db',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'pendente': '#f39c12',
    'aprovado': '#2ecc71',
    'rejeitado': '#e74c3c'
}

def get_report_stats_by_month():
    """Obtém estatísticas de laudos por mês"""
    # Obter o mês atual
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Estatísticas do mês atual
    start_date = datetime(current_year, current_month, 1)
    if current_month == 12:
        end_date = datetime(current_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(current_year, current_month + 1, 1) - timedelta(days=1)
    
    # Total de laudos no mês
    total_reports = Report.query.filter(
        Report.report_date.between(start_date, end_date)
    ).count()
    
    # Laudos por status
    status_counts = db.session.query(
        Report.status, func.count(Report.id)
    ).filter(
        Report.report_date.between(start_date, end_date)
    ).group_by(Report.status).all()
    
    status_dict = {status: count for status, count in status_counts}
    
    return {
        'total_reports': total_reports,
        'pendentes': status_dict.get('pendente', 0),
        'aprovados': status_dict.get('aprovado', 0),
        'rejeitados': status_dict.get('rejeitado', 0)
    }

def get_report_stats_by_material():
    """Obtém estatísticas de laudos por tipo de matéria-prima"""
    # Obter o mês atual
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Estatísticas do mês atual
    start_date = datetime(current_year, current_month, 1)
    if current_month == 12:
        end_date = datetime(current_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(current_year, current_month + 1, 1) - timedelta(days=1)
    
    # Laudos por tipo de matéria-prima
    material_counts = db.session.query(
        Report.raw_material_type, func.count(Report.id)
    ).filter(
        Report.report_date.between(start_date, end_date)
    ).group_by(Report.raw_material_type).all()
    
    # Formatar resultados
    materials = []
    counts = []
    for material, count in material_counts:
        if material:  # Ignorar valores nulos
            materials.append(material)
            counts.append(count)
    
    return {
        'materials': materials,
        'counts': counts
    }

def get_quality_indicators():
    """Obtém indicadores de qualidade (pH, Brix, Acidez)"""
    # Obter os últimos 6 meses
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # ~6 meses
    
    # Consulta para obter médias mensais dos indicadores
    quality_data = db.session.query(
        extract('month', Report.report_date).label('month'),
        extract('year', Report.report_date).label('year'),
        func.avg(Report.ph_value).label('avg_ph'),
        func.avg(Report.brix_value).label('avg_brix'),
        func.avg(Report.acidity_value).label('avg_acidity')
    ).filter(
        Report.report_date.between(start_date, end_date),
        Report.ph_value.isnot(None),
        Report.brix_value.isnot(None),
        Report.acidity_value.isnot(None)
    ).group_by(
        extract('year', Report.report_date),
        extract('month', Report.report_date)
    ).order_by(
        extract('year', Report.report_date),
        extract('month', Report.report_date)
    ).all()
    
    # Preparar dados para gráficos
    months = []
    ph_values = []
    brix_values = []
    acidity_values = []
    
    for month, year, avg_ph, avg_brix, avg_acidity in quality_data:
        month_name = calendar.month_abbr[int(month)]
        month_label = f"{month_name}/{str(year)[2:]}"
        months.append(month_label)
        ph_values.append(float(avg_ph) if avg_ph else 0)
        brix_values.append(float(avg_brix) if avg_brix else 0)
        acidity_values.append(float(avg_acidity) if avg_acidity else 0)
    
    # Obter valores de referência para alertas
    # (normalmente viriam de uma configuração)
    ph_ref = {'min': 3.5, 'max': 4.5}
    brix_ref = {'min': 10.0, 'max': 15.0}
    acidity_ref = {'min': 0.5, 'max': 1.5}
    
    # Verificar alertas (valores fora da faixa de referência)
    ph_alerts = []
    brix_alerts = []
    acidity_alerts = []
    
    # Verificar somente o último mês se houver dados
    if ph_values and len(ph_values) > 0:
        last_ph = ph_values[-1]
        if last_ph < ph_ref['min'] or last_ph > ph_ref['max']:
            ph_alerts.append(f"pH fora da faixa ideal ({ph_ref['min']} - {ph_ref['max']})")
            
    if brix_values and len(brix_values) > 0:
        last_brix = brix_values[-1]
        if last_brix < brix_ref['min'] or last_brix > brix_ref['max']:
            brix_alerts.append(f"Brix fora da faixa ideal ({brix_ref['min']} - {brix_ref['max']})")
            
    if acidity_values and len(acidity_values) > 0:
        last_acidity = acidity_values[-1]
        if last_acidity < acidity_ref['min'] or last_acidity > acidity_ref['max']:
            acidity_alerts.append(f"Acidez fora da faixa ideal ({acidity_ref['min']} - {acidity_ref['max']})")
    
    return {
        'months': months,
        'ph': ph_values,
        'brix': brix_values,
        'acidity': acidity_values,
        'alerts': {
            'ph': ph_alerts,
            'brix': brix_alerts,
            'acidity': acidity_alerts
        }
    }

def get_operational_efficiency():
    """Obtém indicadores de eficiência operacional"""
    # Dados do último mês
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Calcular tempo médio de análise
    avg_analysis_time = db.session.query(
        func.avg(
            func.extract('epoch', Report.analysis_end_time - Report.analysis_start_time) / 3600
        )
    ).filter(
        Report.analysis_start_time.isnot(None),
        Report.analysis_end_time.isnot(None),
        Report.analysis_start_time.between(start_date, end_date)
    ).scalar()
    
    # Convertendo para horas e arredondando
    avg_analysis_time = round(float(avg_analysis_time) if avg_analysis_time else 0, 2)
    
    # Análises por técnico/responsável
    analyst_data = db.session.query(
        User.name,
        func.count(Report.id).label('reports_count')
    ).join(
        User, User.id == Report.assigned_to
    ).filter(
        Report.assigned_to.isnot(None),
        Report.report_date.between(start_date, end_date)
    ).group_by(
        User.name
    ).order_by(
        func.count(Report.id).desc()
    ).limit(5).all()
    
    analysts = [data[0] for data in analyst_data]
    report_counts = [data[1] for data in analyst_data]
    
    # SLA (Prazo de entrega)
    sla_data = db.session.query(
        case(
            (Report.updated_date <= Report.due_date, "No prazo"),
            else_="Atrasado"
        ).label('status'),
        func.count(Report.id).label('count')
    ).filter(
        Report.due_date.isnot(None),
        Report.updated_date.isnot(None),
        Report.report_date.between(start_date, end_date)
    ).group_by(
        case(
            (Report.updated_date <= Report.due_date, "No prazo"),
            else_="Atrasado"
        )
    ).all()
    
    sla_status = [data[0] for data in sla_data]
    sla_counts = [data[1] for data in sla_data]
    
    return {
        'avg_analysis_time': avg_analysis_time,
        'analyst_data': {
            'analysts': analysts,
            'report_counts': report_counts
        },
        'sla_data': {
            'status': sla_status,
            'counts': sla_counts
        }
    }

def get_recent_documents():
    """Obtém documentos recentes e pendentes"""
    # Últimos relatórios gerados
    recent_reports = Report.query.order_by(
        Report.upload_date.desc()
    ).limit(5).all()
    
    # Documentos pendentes para revisão ou assinatura
    pending_reports = Report.query.filter(
        Report.status == 'pendente',
        Report.stage == 'validado'  # Fase de validação, precisa de assinatura
    ).order_by(
        Report.upload_date.desc()
    ).limit(5).all()
    
    return {
        'recent_reports': [report.to_dict() for report in recent_reports],
        'pending_reports': [report.to_dict() for report in pending_reports]
    }

def get_recent_activities():
    """Obtém atividades recentes"""
    # Esta função seria melhor implementada com um modelo 
    # específico para logs, mas vamos simular usando laudos recentemente atualizados
    
    recent_activities = db.session.query(
        Report, User
    ).join(
        User, User.id == Report.assigned_to
    ).filter(
        Report.assigned_to.isnot(None)
    ).order_by(
        Report.updated_date.desc()
    ).limit(10).all()
    
    activities = []
    for report, user in recent_activities:
        action = ""
        if report.status == 'aprovado':
            action = "aprovou"
        elif report.status == 'rejeitado':
            action = "rejeitou"
        else:
            action = "atualizou"
        
        activity = {
            'user': user.name,
            'action': action,
            'report_title': report.title,
            'report_id': report.id,
            'timestamp': report.updated_date.strftime('%d/%m/%Y %H:%M')
        }
        activities.append(activity)
    
    return {
        'activities': activities
    }

def get_backup_info():
    """Obtém informações sobre backups"""
    # Simulando informações de backup
    # Em um sistema real, isso viria de um sistema de backup configurado
    
    backup_file = "backup_zelopack_db_20240425_0930.sql"
    last_backup = datetime(2024, 4, 25, 9, 30, 0)
    
    return {
        'last_backup_file': backup_file,
        'last_backup_date': last_backup.strftime('%d/%m/%Y %H:%M'),
        'backup_size': "42.8 MB"
    }

def plot_to_base64(fig):
    """Converte um figura matplotlib para base64 para exibição em HTML"""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_str

def generate_status_chart():
    """Gera gráfico para status dos laudos"""
    stats = get_report_stats_by_month()
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(6, 4))
    
    labels = ['Pendentes', 'Aprovados', 'Rejeitados']
    values = [stats['pendentes'], stats['aprovados'], stats['rejeitados']]
    colors = [COLORS['pendente'], COLORS['aprovado'], COLORS['rejeitado']]
    
    ax.bar(labels, values, color=colors)
    ax.set_title('Status dos Laudos no Mês Atual')
    ax.set_ylabel('Quantidade')
    
    for i, v in enumerate(values):
        ax.text(i, v + 0.5, str(v), ha='center')
    
    return plot_to_base64(fig)

def generate_material_chart():
    """Gera gráfico para tipos de matéria-prima"""
    data = get_report_stats_by_material()
    
    if not data['materials']:
        # Se não houver dados, retornar gráfico vazio
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', va='center')
        ax.set_title('Laudos por Tipo de Matéria-Prima')
        return plot_to_base64(fig)
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Se tivermos materiais, criar o gráfico
    ax.pie(data['counts'], labels=[m.capitalize() for m in data['materials']], 
           autopct='%1.1f%%', startangle=90,
           colors=plt.cm.Paired(np.linspace(0, 1, len(data['materials']))))
    
    ax.set_title('Laudos por Tipo de Matéria-Prima')
    ax.axis('equal')  # Gráfico circular
    
    return plot_to_base64(fig)

def generate_quality_indicators_chart():
    """Gera gráfico para indicadores de qualidade"""
    data = get_quality_indicators()
    
    if not data['months']:
        # Se não houver dados, retornar gráfico vazio
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', va='center')
        ax.set_title('Indicadores de Qualidade - Média Mensal')
        return plot_to_base64(fig)
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(8, 4))
    
    ax.plot(data['months'], data['ph'], marker='o', label='pH', color='#3498db')
    ax.plot(data['months'], data['brix'], marker='s', label='Brix', color='#2ecc71')
    ax.plot(data['months'], data['acidity'], marker='^', label='Acidez', color='#e74c3c')
    
    ax.set_title('Indicadores de Qualidade - Média Mensal')
    ax.set_xlabel('Mês/Ano')
    ax.set_ylabel('Valor')
    ax.legend()
    
    if len(data['months']) > 6:
        # Se houver muitos meses, rotacionar os nomes
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    return plot_to_base64(fig)

def generate_efficiency_chart():
    """Gera gráfico para eficiência operacional"""
    data = get_operational_efficiency()
    
    # Criar figura para análises por analista
    fig, ax = plt.subplots(figsize=(6, 4))
    
    if not data['analyst_data']['analysts']:
        # Se não houver dados, retornar gráfico vazio
        ax.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', va='center')
        ax.set_title('Volume de Análises por Técnico')
        return plot_to_base64(fig)
    
    # Criar gráfico horizontal de barras
    y_pos = np.arange(len(data['analyst_data']['analysts']))
    ax.barh(y_pos, data['analyst_data']['report_counts'], color=COLORS['primary'])
    ax.set_yticks(y_pos)
    ax.set_yticklabels(data['analyst_data']['analysts'])
    ax.invert_yaxis()  # Maiores valores no topo
    ax.set_title('Volume de Análises por Técnico')
    ax.set_xlabel('Número de Laudos')
    
    # Adicionar valores nas barras
    for i, v in enumerate(data['analyst_data']['report_counts']):
        ax.text(v + 0.1, i, str(v), va='center')
    
    plt.tight_layout()
    
    return plot_to_base64(fig)

def generate_sla_chart():
    """Gera gráfico para SLA (Prazo de entrega)"""
    data = get_operational_efficiency()
    
    # Criar figura para SLA
    fig, ax = plt.subplots(figsize=(5, 5))
    
    if not data['sla_data']['status']:
        # Se não houver dados, retornar gráfico vazio
        ax.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', va='center')
        ax.set_title('Cumprimento de Prazo (SLA)')
        return plot_to_base64(fig)
    
    # Criar gráfico de pizza
    colors = [COLORS['success'], COLORS['danger']]
    ax.pie(data['sla_data']['counts'], labels=data['sla_data']['status'], 
           autopct='%1.1f%%', startangle=90, colors=colors)
    
    ax.set_title('Cumprimento de Prazo (SLA)')
    ax.axis('equal')  # Gráfico circular
    
    return plot_to_base64(fig)