from flask import render_template, jsonify, request, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func, desc, extract, case, and_
from datetime import datetime, timedelta
import os
import json
import io
import base64

from app import db
from models import Report, Category, Supplier, User
from blueprints.dashboard import dashboard_bp
from utils.dashboard import (
    get_report_stats_by_month,
    get_report_stats_by_material,
    get_quality_indicators,
    get_operational_efficiency,
    get_recent_documents,
    get_recent_activities,
    get_backup_info,
    generate_status_chart,
    generate_material_chart,
    generate_quality_indicators_chart,
    generate_efficiency_chart,
    generate_sla_chart
)

@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal com visão geral."""
    # Resumo de estatísticas
    monthly_stats = get_report_stats_by_month()
    
    # Gráficos em base64
    status_chart = generate_status_chart()
    material_chart = generate_material_chart()
    quality_chart = generate_quality_indicators_chart()
    efficiency_chart = generate_efficiency_chart()
    sla_chart = generate_sla_chart()
    
    # Dados de eficiência operacional
    efficiency_data = get_operational_efficiency()
    avg_analysis_time = efficiency_data['avg_analysis_time']
    
    # Dados de qualidade
    quality_data = get_quality_indicators()
    quality_alerts = quality_data['alerts']
    
    # Documentos recentes
    documents_data = get_recent_documents()
    recent_reports = documents_data['recent_reports']
    pending_reports = documents_data['pending_reports']
    
    # Atividades recentes
    activities_data = get_recent_activities()
    recent_activities = activities_data['activities']
    
    # Informações de backup
    backup_info = get_backup_info()
    
    return render_template(
        'dashboard/overview.html',
        title="Dashboard Zelopack",
        monthly_stats=monthly_stats,
        status_chart=status_chart,
        material_chart=material_chart,
        quality_chart=quality_chart,
        efficiency_chart=efficiency_chart,
        sla_chart=sla_chart,
        avg_analysis_time=avg_analysis_time,
        quality_alerts=quality_alerts,
        recent_reports=recent_reports,
        pending_reports=pending_reports,
        recent_activities=recent_activities,
        backup_info=backup_info
    )

@dashboard_bp.route('/quality-indicators')
@login_required
def quality_indicators():
    """Dashboard de indicadores de qualidade."""
    # Obter dados de qualidade
    quality_data = get_quality_indicators()
    
    # Gerar gráfico
    quality_chart = generate_quality_indicators_chart()
    
    return render_template(
        'dashboard/quality.html',
        title="Indicadores de Qualidade",
        quality_data=quality_data,
        quality_chart=quality_chart
    )

@dashboard_bp.route('/efficiency')
@login_required
def operational_efficiency():
    """Dashboard de eficiência operacional."""
    # Obter dados de eficiência
    efficiency_data = get_operational_efficiency()
    
    # Gerar gráficos
    efficiency_chart = generate_efficiency_chart()
    sla_chart = generate_sla_chart()
    
    return render_template(
        'dashboard/efficiency.html',
        title="Eficiência Operacional",
        efficiency_data=efficiency_data,
        efficiency_chart=efficiency_chart,
        sla_chart=sla_chart
    )

@dashboard_bp.route('/documents')
@login_required
def documents():
    """Dashboard de documentos recentes e pendentes."""
    # Obter dados de documentos
    documents_data = get_recent_documents()
    
    return render_template(
        'dashboard/documents.html',
        title="Documentos Recentes",
        recent_reports=documents_data['recent_reports'],
        pending_reports=documents_data['pending_reports']
    )

@dashboard_bp.route('/activities')
@login_required
def activities():
    """Dashboard de atividades recentes."""
    # Obter dados de atividades
    activities_data = get_recent_activities()
    
    return render_template(
        'dashboard/activities.html',
        title="Atividades Recentes",
        activities=activities_data['activities']
    )

@dashboard_bp.route('/backup-info')
@login_required
def backup_information():
    """Informações sobre backups do sistema."""
    # Obter informações de backup
    backup_info = get_backup_info()
    
    return render_template(
        'dashboard/backups.html',
        title="Informações de Backup",
        backup_info=backup_info
    )

@dashboard_bp.route('/manual-backup', methods=['POST'])
@login_required
def manual_backup():
    """Rota para iniciar um backup manual."""
    # Esta é uma simulação - em um sistema real,
    # aqui seria chamada uma função para gerar um backup real
    
    # Simular sucesso
    flash('Backup manual iniciado com sucesso! Aguarde alguns minutos para conclusão.', 'success')
    
    return redirect(url_for('dashboard.backup_information'))
