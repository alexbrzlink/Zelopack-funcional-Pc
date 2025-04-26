from flask import render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc, func, or_
import datetime
import json
import os
import logging

from app import db
from models import TechnicalDocument, User, Task, Note
from blueprints.dashboard import dashboard_bp
from blueprints.dashboard.models import Task, CalendarEvent, DashboardConfig, DashboardWidget, get_user_tasks, get_user_events, save_dashboard_config

@dashboard_bp.route('/')
@login_required
def index():
    """Painel de controle personalizado."""
    # Obter documentos recentes
    recent_documents = TechnicalDocument.query.order_by(TechnicalDocument.upload_date.desc()).limit(5).all()
    
    # Coletar estatísticas
    stats = {
        'total_documents': TechnicalDocument.query.count(),
        'total_forms': TechnicalDocument.query.filter_by(document_type='formulario').count(),
        'uploads_today': TechnicalDocument.query.filter(
            func.date(TechnicalDocument.upload_date) == datetime.date.today()
        ).count(),
        'active_users': User.query.count()  # Todos os usuários (ajustar se houver campo de status)
    }
    
    # Obter tarefas do usuário (se existir o modelo)
    tasks = []
    try:
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.deadline).all()
    except:
        # O modelo Task pode não existir ainda
        pass
    
    # Obter notas do usuário (se existir o modelo)
    notes_content = ""
    try:
        note = Note.query.filter_by(user_id=current_user.id).first()
        if note:
            notes_content = note.content
    except:
        # O modelo Note pode não existir ainda
        pass
    
    return render_template(
        'dashboard/index.html',
        title='Painel de Controle',
        recent_documents=recent_documents,
        stats=stats,
        tasks=tasks,
        notes_content=notes_content
    )

@dashboard_bp.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def api_tasks():
    """API para gerenciar tarefas."""
    try:
        if request.method == 'GET':
            # Listar tarefas
            completed = request.args.get('completed')
            if completed is not None:
                completed = completed.lower() == 'true'
                tasks = get_user_tasks(completed=completed)
            else:
                tasks = get_user_tasks()
            
            return jsonify(tasks)
        
        elif request.method == 'POST':
            # Criar nova tarefa
            data = request.json
            task = Task(
                title=data.get('title'),
                description=data.get('description'),
                deadline=datetime.datetime.fromisoformat(data.get('deadline')) if data.get('deadline') else None,
                completed=data.get('completed', False),
                priority=data.get('priority', 'medium'),
                user_id=current_user.id
            )
            db.session.add(task)
            db.session.commit()
            
            return jsonify(task.to_dict()), 201
    
    except Exception as e:
        current_app.logger.error(f"Erro na API de tarefas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500


@dashboard_bp.route('/api/tasks/<int:task_id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def api_task(task_id):
    """API para gerenciar uma tarefa específica."""
    try:
        task = Task.query.get_or_404(task_id)
        
        # Verificar permissão
        if task.user_id != current_user.id:
            return jsonify({'error': 'Não autorizado'}), 403
        
        if request.method == 'GET':
            # Obter detalhes da tarefa
            return jsonify(task.to_dict())
        
        elif request.method == 'PATCH':
            # Atualizar tarefa existente
            data = request.json
            
            if 'title' in data:
                task.title = data['title']
            if 'description' in data:
                task.description = data['description']
            if 'deadline' in data and data['deadline']:
                task.deadline = datetime.datetime.fromisoformat(data['deadline'])
            if 'completed' in data:
                task.completed = data['completed']
            if 'priority' in data:
                task.priority = data['priority']
            
            db.session.commit()
            return jsonify(task.to_dict())
        
        elif request.method == 'DELETE':
            # Excluir tarefa
            db.session.delete(task)
            db.session.commit()
            return jsonify({'message': 'Tarefa excluída com sucesso'})
    
    except Exception as e:
        current_app.logger.error(f"Erro na API de tarefa {task_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500


@dashboard_bp.route('/api/tasks/completed', methods=['DELETE'])
@login_required
def api_tasks_completed():
    """API para excluir todas as tarefas concluídas."""
    try:
        data = request.json
        task_ids = data.get('task_ids', [])
        
        if task_ids:
            # Excluir tarefas específicas
            tasks = Task.query.filter(Task.id.in_(task_ids), Task.user_id == current_user.id).all()
        else:
            # Excluir todas as tarefas concluídas
            tasks = Task.query.filter_by(completed=True, user_id=current_user.id).all()
        
        for task in tasks:
            db.session.delete(task)
        
        db.session.commit()
        return jsonify({'message': f'{len(tasks)} tarefas concluídas removidas com sucesso'})
    
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir tarefas concluídas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500

@dashboard_bp.route('/api/notes', methods=['GET', 'POST'])
@login_required
def api_notes():
    """API para gerenciar notas rápidas."""
    # Verificar se o modelo Note existe
    try:
        if request.method == 'GET':
            # Obter notas do usuário
            note = Note.query.filter_by(user_id=current_user.id).first()
            if note:
                return jsonify({
                    'id': note.id,
                    'content': note.content,
                    'updated_at': note.updated_at.isoformat()
                })
            else:
                return jsonify({'content': ''})
        
        elif request.method == 'POST':
            # Salvar notas do usuário
            data = request.json
            content = data.get('content', '')
            
            # Verificar se já existe uma nota para o usuário
            note = Note.query.filter_by(user_id=current_user.id).first()
            
            if note:
                # Atualizar a nota existente
                note.content = content
                note.updated_at = datetime.datetime.utcnow()
            else:
                # Criar uma nova nota
                note = Note(
                    content=content,
                    user_id=current_user.id
                )
                db.session.add(note)
            
            db.session.commit()
            return jsonify({
                'id': note.id,
                'content': note.content,
                'updated_at': note.updated_at.isoformat()
            })
    
    except Exception as e:
        current_app.logger.error(f"Erro na API de notas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@dashboard_bp.route('/api/events', methods=['GET', 'POST'])
@login_required
def api_events():
    """API para gerenciar eventos de calendário."""
    try:
        if request.method == 'GET':
            # Listar eventos
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            if start_date:
                start_date = datetime.datetime.fromisoformat(start_date)
            if end_date:
                end_date = datetime.datetime.fromisoformat(end_date)
            
            events = get_user_events(start_date=start_date, end_date=end_date)
            return jsonify(events)
        
        elif request.method == 'POST':
            # Criar novo evento
            data = request.json
            event = CalendarEvent(
                title=data.get('title'),
                date=datetime.datetime.fromisoformat(data.get('date')) if data.get('date') else datetime.datetime.now(),
                description=data.get('description', ''),
                category=data.get('category', 'default'),
                color=data.get('color'),
                user_id=current_user.id
            )
            db.session.add(event)
            db.session.commit()
            
            return jsonify(event.to_dict()), 201
    
    except Exception as e:
        current_app.logger.error(f"Erro na API de eventos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500


@dashboard_bp.route('/api/events/<int:event_id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def api_event(event_id):
    """API para gerenciar um evento específico."""
    try:
        event = CalendarEvent.query.get_or_404(event_id)
        
        # Verificar permissão
        if event.user_id != current_user.id:
            return jsonify({'error': 'Não autorizado'}), 403
        
        if request.method == 'GET':
            # Obter detalhes do evento
            return jsonify(event.to_dict())
        
        elif request.method == 'PATCH':
            # Atualizar evento existente
            data = request.json
            
            if 'title' in data:
                event.title = data['title']
            if 'date' in data and data['date']:
                event.date = datetime.datetime.fromisoformat(data['date'])
            if 'description' in data:
                event.description = data['description']
            if 'category' in data:
                event.category = data['category']
            if 'color' in data:
                event.color = data['color']
            
            db.session.commit()
            return jsonify(event.to_dict())
        
        elif request.method == 'DELETE':
            # Excluir evento
            db.session.delete(event)
            db.session.commit()
            return jsonify({'message': 'Evento excluído com sucesso'})
    
    except Exception as e:
        current_app.logger.error(f"Erro na API de evento {event_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500


@dashboard_bp.route('/api/dashboard-config', methods=['GET', 'POST'])
@login_required
def api_dashboard_config():
    """API para salvar e carregar configurações do painel."""
    try:
        if request.method == 'GET':
            # Obter configuração atual do dashboard
            config = DashboardConfig.query.filter_by(user_id=current_user.id).first()
            if config:
                return jsonify(config.to_dict())
            else:
                # Retornar configuração padrão
                return jsonify({
                    'layout': 'grid',
                    'theme': 'light',
                    'auto_refresh': False,
                    'refresh_interval': 60,
                    'config_data': {}
                })
        
        elif request.method == 'POST':
            # Salvar configuração do dashboard
            data = request.json
            config = save_dashboard_config(data)
            return jsonify(config.to_dict())
    
    except Exception as e:
        current_app.logger.error(f"Erro na API de configuração do dashboard: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'details': str(e)}), 500

@dashboard_bp.route('/api/charts-data')
@login_required
def api_charts_data():
    """API para fornecer dados para os gráficos do painel."""
    try:
        # Dados para o gráfico de documentos por tipo
        doc_types = db.session.query(
            TechnicalDocument.document_type, 
            func.count(TechnicalDocument.id)
        ).group_by(TechnicalDocument.document_type).all()
        
        # Formatar os dados para o gráfico
        labels = []
        data = []
        
        for doc_type, count in doc_types:
            if doc_type == 'pop':
                labels.append('POPs')
            elif doc_type == 'ficha_tecnica':
                labels.append('Fichas Técnicas')
            elif doc_type == 'certificado':
                labels.append('Certificados')
            elif doc_type == 'manual':
                labels.append('Manuais')
            elif doc_type == 'formulario':
                labels.append('Formulários')
            else:
                labels.append('Outros')
            
            data.append(count)
        
        return jsonify({
            'documentsByType': {
                'labels': labels,
                'data': data
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"Erro na API de dados de gráficos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500