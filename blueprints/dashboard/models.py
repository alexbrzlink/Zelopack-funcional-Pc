"""
Modelos do banco de dados para o módulo Dashboard.

Este módulo contém os modelos para tarefas, eventos de calendário e configurações de 
dashboard personalizáveis.
"""

from datetime import datetime
from app import db
from flask_login import current_user


class Task(db.Model):
    __tablename__ = 'dashboard_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Chave estrangeira para o usuário que criou a tarefa
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        """Converte o modelo Task em um dicionário para serialização."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'priority': self.priority,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class CalendarEvent(db.Model):
    __tablename__ = 'dashboard_events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), default='default')  # meeting, deadline, reminder, etc.
    color = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Chave estrangeira para o usuário que criou o evento
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        """Converte o modelo CalendarEvent em um dicionário para serialização."""
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'category': self.category,
            'color': self.color,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class DashboardWidget(db.Model):
    __tablename__ = 'dashboard_widgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    widget_type = db.Column(db.String(50), nullable=False)  # tasks, calendar, stats, etc.
    position = db.Column(db.Integer, default=0)
    settings = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DashboardConfig(db.Model):
    __tablename__ = 'dashboard_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    layout = db.Column(db.String(20), default='grid')  # grid, list, compact
    theme = db.Column(db.String(20), default='light')  # light, dark, custom
    auto_refresh = db.Column(db.Boolean, default=False)
    refresh_interval = db.Column(db.Integer, default=60)  # em segundos
    config_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte o modelo DashboardConfig em um dicionário para serialização."""
        return {
            'id': self.id,
            'layout': self.layout,
            'theme': self.theme,
            'auto_refresh': self.auto_refresh,
            'refresh_interval': self.refresh_interval,
            'config_data': self.config_data,
            'updated_at': self.updated_at.isoformat()
        }


def get_user_tasks(completed=None):
    """
    Obtém as tarefas do usuário atual, opcionalmente filtradas por status de conclusão.
    
    Args:
        completed (bool, optional): Se definido, filtra tarefas por status de conclusão.
    
    Returns:
        list: Lista de tarefas convertidas para dicionários.
    """
    query = Task.query.filter_by(user_id=current_user.id)
    
    if completed is not None:
        query = query.filter_by(completed=completed)
    
    tasks = query.order_by(Task.deadline.asc() if Task.deadline is not None else Task.created_at.desc()).all()
    return [task.to_dict() for task in tasks]


def get_user_events(start_date=None, end_date=None):
    """
    Obtém os eventos de calendário do usuário atual, opcionalmente filtrados por intervalo de datas.
    
    Args:
        start_date (datetime, optional): Data de início para filtrar eventos.
        end_date (datetime, optional): Data de término para filtrar eventos.
    
    Returns:
        list: Lista de eventos convertidos para dicionários.
    """
    query = CalendarEvent.query.filter_by(user_id=current_user.id)
    
    if start_date:
        query = query.filter(CalendarEvent.date >= start_date)
    
    if end_date:
        query = query.filter(CalendarEvent.date <= end_date)
    
    events = query.order_by(CalendarEvent.date.asc()).all()
    return [event.to_dict() for event in events]


def save_dashboard_config(config_data):
    """
    Salva a configuração do dashboard do usuário.
    
    Args:
        config_data (dict): Dados de configuração do dashboard.
    
    Returns:
        DashboardConfig: Instância da configuração salva.
    """
    user_config = DashboardConfig.query.filter_by(user_id=current_user.id).first()
    
    if not user_config:
        user_config = DashboardConfig(user_id=current_user.id)
    
    user_config.layout = config_data.get('layout', 'grid')
    user_config.theme = config_data.get('theme', 'light')
    user_config.auto_refresh = config_data.get('autoRefresh', False)
    user_config.refresh_interval = config_data.get('refreshInterval', 60)
    user_config.config_data = config_data
    
    db.session.add(user_config)
    db.session.commit()
    
    return user_config