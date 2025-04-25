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
    try:
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
        
        status_dict = {status: count for status, count in status_counts if status is not None}
        
        return {
            'total_reports': total_reports,
            'pendentes': status_dict.get('pendente', 0),
            'aprovados': status_dict.get('aprovado', 0),
            'rejeitados': status_dict.get('rejeitado', 0)
        }
    except Exception as e:
        print(f"Erro ao obter estatísticas mensais: {e}")
        # Retornar dados padrão em caso de erro
        return {
            'total_reports': 0,
            'pendentes': 0,
            'aprovados': 0,
            'rejeitados': 0
        }

def get_report_stats_by_material():
    """Obtém estatísticas de laudos por tipo de matéria-prima"""
    try:
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
        
        # Se não houver dados, adicionar valores padrão
        if not materials:
            materials = ['Sem dados']
            counts = [0]
        
        return {
            'materials': materials,
            'counts': counts
        }
    except Exception as e:
        print(f"Erro ao obter estatísticas por material: {e}")
        # Retornar dados padrão em caso de erro
        return {
            'materials': ['Erro na consulta'],
            'counts': [0]
        }

def get_quality_indicators():
    """Obtém indicadores de qualidade (pH, Brix, Acidez)"""
    try:
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
        
        # Se não houver dados, adicionar exemplo para visualização
        if not months:
            current_month = datetime.now().strftime('%b/%y')
            months = [current_month]
            ph_values = [4.0]  # Valor exemplo dentro da faixa ideal
            brix_values = [12.5]  # Valor exemplo dentro da faixa ideal
            acidity_values = [1.0]  # Valor exemplo dentro da faixa ideal
        
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
    except Exception as e:
        print(f"Erro ao obter indicadores de qualidade: {e}")
        # Retornar dados padrão em caso de erro
        current_month = datetime.now().strftime('%b/%y')
        return {
            'months': [current_month],
            'ph': [4.0],
            'brix': [12.5],
            'acidity': [1.0],
            'alerts': {
                'ph': [],
                'brix': [],
                'acidity': []
            }
        }

def get_operational_efficiency():
    """Obtém indicadores de eficiência operacional"""
    try:
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
        
        # Se não houver analistas, adicionar dados padrão
        if not analysts:
            analysts = ['Administrador']
            report_counts = [0]
        
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
        
        # Se não houver dados de SLA, adicionar dados padrão
        if not sla_status:
            sla_status = ["No prazo", "Atrasado"]
            sla_counts = [1, 0]  # 100% no prazo como exemplo
        
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
    except Exception as e:
        print(f"Erro ao obter dados de eficiência operacional: {e}")
        # Retornar dados padrão em caso de erro
        return {
            'avg_analysis_time': 2.5,  # Valor exemplo
            'analyst_data': {
                'analysts': ['Administrador'],
                'report_counts': [0]
            },
            'sla_data': {
                'status': ["No prazo", "Atrasado"],
                'counts': [1, 0]
            }
        }

def get_recent_documents():
    """Obtém documentos recentes e pendentes"""
    try:
        # Últimos relatórios gerados
        recent_reports = Report.query.order_by(
            Report.upload_date.desc()
        ).limit(5).all()
        
        # Documentos pendentes para revisão ou assinatura
        pending_reports = Report.query.filter(
            Report.status == 'pendente'
        ).order_by(
            Report.upload_date.desc()
        ).limit(5).all()
        
        # Converter para dicionários de forma segura
        recent_reports_dict = []
        for report in recent_reports:
            try:
                # Criar dicionário manualmente para evitar erros com novos campos
                report_dict = {
                    'id': report.id,
                    'title': report.title,
                    'description': report.description,
                    'filename': report.filename,
                    'category': report.category,
                    'status': report.status,
                    'upload_date': report.upload_date.strftime('%d/%m/%Y %H:%M') if report.upload_date else None
                }
                recent_reports_dict.append(report_dict)
            except Exception as e:
                print(f"Erro ao converter relatório para dicionário: {e}")
        
        pending_reports_dict = []
        for report in pending_reports:
            try:
                # Criar dicionário manualmente para evitar erros com novos campos
                report_dict = {
                    'id': report.id,
                    'title': report.title,
                    'description': report.description,
                    'filename': report.filename,
                    'category': report.category,
                    'status': report.status,
                    'upload_date': report.upload_date.strftime('%d/%m/%Y %H:%M') if report.upload_date else None
                }
                pending_reports_dict.append(report_dict)
            except Exception as e:
                print(f"Erro ao converter relatório pendente para dicionário: {e}")
        
        return {
            'recent_reports': recent_reports_dict,
            'pending_reports': pending_reports_dict
        }
    except Exception as e:
        print(f"Erro ao obter documentos recentes: {e}")
        # Retornar listas vazias em caso de erro
        return {
            'recent_reports': [],
            'pending_reports': []
        }

def get_recent_activities():
    """Obtém atividades recentes"""
    try:
        # Utilizar uma abordagem diferente: buscar apenas Reports e depois User
        recent_reports = Report.query.filter(
            Report.assigned_to.isnot(None)
        ).order_by(
            Report.updated_date.desc()
        ).limit(10).all()
        
        activities = []
        for report in recent_reports:
            try:
                # Buscar usuário associado
                user = User.query.get(report.assigned_to)
                if not user:
                    continue
                
                action = ""
                if report.status == 'aprovado':
                    action = "aprovou"
                elif report.status == 'rejeitado':
                    action = "rejeitou"
                else:
                    action = "atualizou"
                
                # Verificar se os atributos existem antes de acessá-los
                report_title = report.title if hasattr(report, 'title') else 'Relatório sem título'
                report_id = report.id if hasattr(report, 'id') else 0
                
                # Formatar timestamp com tratamento de erro
                try:
                    timestamp = report.updated_date.strftime('%d/%m/%Y %H:%M')
                except:
                    timestamp = 'Data desconhecida'
                
                activity = {
                    'user': user.name if hasattr(user, 'name') else 'Usuário desconhecido',
                    'action': action,
                    'report_title': report_title,
                    'report_id': report_id,
                    'timestamp': timestamp
                }
                activities.append(activity)
            except Exception as e:
                print(f"Erro ao processar atividade específica: {e}")
                continue
        
        return {
            'activities': activities
        }
    except Exception as e:
        print(f"Erro ao obter atividades recentes: {e}")
        # Retornar lista vazia em caso de erro
        return {
            'activities': []
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
    try:
        data = get_report_stats_by_material()
        
        # Criar figura
        fig, ax = plt.subplots(figsize=(6, 4))
        
        # Verificar se há dados válidos
        if not data['materials'] or 'Sem dados' in data['materials'] or 'Erro' in data['materials']:
            # Se não houver dados, mostrar mensagem
            ax.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', va='center')
            ax.set_title('Laudos por Tipo de Matéria-Prima')
            plt.tight_layout()
            return plot_to_base64(fig)
        
        # Se tivermos materiais, criar o gráfico
        try:
            # Usar cores estáticas em vez de calcular pela quantidade
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
            # Garantir que temos cores suficientes
            while len(colors) < len(data['materials']):
                colors.extend(colors)
            # Usar apenas as cores necessárias
            pie_colors = colors[:len(data['materials'])]
            
            ax.pie(data['counts'], labels=[m.capitalize() for m in data['materials']], 
                   autopct='%1.1f%%', startangle=90, colors=pie_colors)
            
            ax.set_title('Laudos por Tipo de Matéria-Prima')
            ax.axis('equal')  # Gráfico circular
            plt.tight_layout()
            
            return plot_to_base64(fig)
        except Exception as e:
            print(f"Erro ao gerar gráfico de pizza: {e}")
            # Em caso de erro, mostrar apenas texto
            plt.clf()  # Limpar figura anterior
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.text(0.5, 0.5, 'Erro ao gerar gráfico', ha='center', va='center')
            ax.set_title('Laudos por Tipo de Matéria-Prima')
            plt.tight_layout()
            return plot_to_base64(fig)
    except Exception as e:
        print(f"Erro crítico em generate_material_chart: {e}")
        # Garantir que sempre retorna algo
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, 'Erro ao carregar dados', ha='center', va='center')
        ax.set_title('Laudos por Tipo de Matéria-Prima')
        plt.tight_layout()
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