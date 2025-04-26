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
        'active_users': User.query.filter_by(active=True).count()
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

@dashboard_bp.route('/api/tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def api_tasks():
    """API para gerenciar tarefas."""
    # Verificar se o modelo Task existe
    try:
        if request.method == 'GET':
            # Listar tarefas
            tasks = Task.query.filter_by(user_id=current_user.id).all()
            return jsonify([{
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'completed': task.completed,
                'priority': task.priority
            } for task in tasks])
        
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
            return jsonify({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'completed': task.completed,
                'priority': task.priority
            }), 201
        
        elif request.method == 'PUT':
            # Atualizar tarefa existente
            data = request.json
            task_id = data.get('id')
            task = Task.query.get_or_404(task_id)
            
            # Verificar permissão
            if task.user_id != current_user.id:
                return jsonify({'error': 'Não autorizado'}), 403
            
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
            return jsonify({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'completed': task.completed,
                'priority': task.priority
            })
        
        elif request.method == 'DELETE':
            # Excluir tarefa
            task_id = request.args.get('id')
            task = Task.query.get_or_404(task_id)
            
            # Verificar permissão
            if task.user_id != current_user.id:
                return jsonify({'error': 'Não autorizado'}), 403
            
            db.session.delete(task)
            db.session.commit()
            return jsonify({'message': 'Tarefa excluída com sucesso'})
    
    except Exception as e:
        current_app.logger.error(f"Erro na API de tarefas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

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

@dashboard_bp.route('/api/dashboard-config', methods=['GET', 'POST'])
@login_required
def api_dashboard_config():
    """API para salvar e carregar configurações do painel."""
    # Esta rota seria para salvar e carregar as configurações do painel no servidor
    # Para simplicidade, deixamos o armazenamento no lado do cliente (localStorage)
    try:
        if request.method == 'GET':
            # Implementação futura: carregar do banco de dados
            return jsonify({'message': 'Funcionalidade ainda não implementada'})
        
        elif request.method == 'POST':
            # Implementação futura: salvar no banco de dados
            return jsonify({'message': 'Configuração salva com sucesso'})
    
    except Exception as e:
        current_app.logger.error(f"Erro na API de configuração do dashboard: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

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