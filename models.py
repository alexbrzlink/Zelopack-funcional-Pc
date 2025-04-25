from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Report(db.Model):
    """Modelo para armazenar informações sobre laudos."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Tamanho em bytes
    
    # Campos para categorização e rastreabilidade
    category = db.Column(db.String(100), nullable=True)  # Mantém compatibilidade com versão anterior
    supplier = db.Column(db.String(150), nullable=True)  # Mantém compatibilidade com versão anterior
    batch_number = db.Column(db.String(100), nullable=True)
    raw_material_type = db.Column(db.String(100), nullable=True)  # Tipo de matéria-prima (laranja, maçã, etc)
    sample_code = db.Column(db.String(50), nullable=True)  # Código de rastreio da amostra
    
    # Campos de datas e prazos
    report_date = db.Column(db.Date, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)  # Prazo para finalização do laudo
    
    # Campos para fluxo de trabalho e status
    status = db.Column(db.String(20), default='pendente')  # pendente, aprovado, rejeitado
    stage = db.Column(db.String(20), default='rascunho')  # rascunho, validado, assinado
    priority = db.Column(db.String(20), default='normal')  # baixa, normal, alta, urgente
    
    # Campos para atribuição e responsabilidade
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Indicadores técnicos/padrões de qualidade
    ph_value = db.Column(db.Float, nullable=True)
    brix_value = db.Column(db.Float, nullable=True)
    acidity_value = db.Column(db.Float, nullable=True)
    color_value = db.Column(db.String(50), nullable=True)
    density_value = db.Column(db.Float, nullable=True)
    
    # Análise de tempo e eficiência
    analysis_start_time = db.Column(db.DateTime, nullable=True)
    analysis_end_time = db.Column(db.DateTime, nullable=True)
    
    # Relações com outras tabelas
    assigned_user = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_reports')
    approver_user = db.relationship('User', foreign_keys=[approved_by], backref='approved_reports')
    
    def __repr__(self):
        return f"<Report {self.id}: {self.title}>"
    
    def to_dict(self):
        """Converte objeto para dicionário."""
        assigned_to_name = None
        approved_by_name = None
        
        if self.assigned_to:
            from models import User
            assigned_user = User.query.get(self.assigned_to)
            if assigned_user:
                assigned_to_name = assigned_user.name
                
        if self.approved_by:
            from models import User
            approved_user = User.query.get(self.approved_by)
            if approved_user:
                approved_by_name = approved_user.name
        
        # Calcular tempo de análise se disponível
        analysis_time = None
        if self.analysis_start_time and self.analysis_end_time:
            analysis_time = (self.analysis_end_time - self.analysis_start_time).total_seconds() / 3600  # em horas
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            
            # Categorização
            'category': self.category,
            'supplier': self.supplier,
            
            # Dados de rastreabilidade
            'batch_number': self.batch_number,
            'raw_material_type': self.raw_material_type,
            'sample_code': self.sample_code,
            
            # Datas
            'report_date': self.report_date.strftime('%d/%m/%Y') if self.report_date else None,
            'upload_date': self.upload_date.strftime('%d/%m/%Y %H:%M'),
            'updated_date': self.updated_date.strftime('%d/%m/%Y %H:%M'),
            'due_date': self.due_date.strftime('%d/%m/%Y') if self.due_date else None,
            
            # Workflow
            'status': self.status,
            'stage': self.stage,
            'priority': self.priority,
            
            # Responsáveis
            'assigned_to': self.assigned_to,
            'assigned_to_name': assigned_to_name,
            'approved_by': self.approved_by,
            'approved_by_name': approved_by_name,
            
            # Indicadores técnicos
            'ph_value': self.ph_value,
            'brix_value': self.brix_value,
            'acidity_value': self.acidity_value,
            'color_value': self.color_value,
            'density_value': self.density_value,
            
            # Tempo
            'analysis_start_time': self.analysis_start_time.strftime('%d/%m/%Y %H:%M') if self.analysis_start_time else None,
            'analysis_end_time': self.analysis_end_time.strftime('%d/%m/%Y %H:%M') if self.analysis_end_time else None,
            'analysis_time_hours': round(analysis_time, 2) if analysis_time else None
        }


class Category(db.Model):
    """Modelo para categorias de laudos."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<Category {self.name}>"


class Supplier(db.Model):
    """Modelo para fornecedores relacionados aos laudos."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    contact = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f"<Supplier {self.name}>"


class User(UserMixin, db.Model):
    """Modelo para usuários do sistema."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='analista')  # admin, analista, gestor
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Define a senha criptografada para o usuário."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o objeto para dicionário (sem a senha)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.strftime('%d/%m/%Y %H:%M') if self.last_login else None,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else None
        }
