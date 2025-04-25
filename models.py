from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json
import os

class Report(db.Model):
    """Modelo para armazenar informações sobre laudos."""
    __tablename__ = 'reports'
    
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
    report_type = db.Column(db.String(100), nullable=True)  # Tipo de laudo (embalagem, matérias primas, etc)
    
    # Campos para análises citadas no laudo (informadas pelo fornecedor)
    brix = db.Column(db.Float, nullable=True)  # Sólidos solúveis (°Brix)
    ph = db.Column(db.Float, nullable=True)  # pH da amostra
    acidity = db.Column(db.Float, nullable=True)  # Acidez (g/100ml)
    
    # Campos para análises realizadas em laboratório
    lab_brix = db.Column(db.Float, nullable=True)  # Sólidos solúveis medidos em laboratório (°Brix)
    lab_ph = db.Column(db.Float, nullable=True)  # pH medido em laboratório
    lab_acidity = db.Column(db.Float, nullable=True)  # Acidez medida em laboratório (g/100ml)
    
    # Validação físico-química
    physicochemical_validation = db.Column(db.String(20), default='não verificado')  # 'ok', 'não padrão', 'não verificado'
    
    # Campos adicionais de rastreabilidade
    report_archived = db.Column(db.Boolean, default=False)  # Laudo arquivado (sim/não)
    microbiology_collected = db.Column(db.Boolean, default=False)  # Microbiologia coletada (sim/não)
    has_report_document = db.Column(db.Boolean, default=False)  # Possui documento do laudo (sim/não)
    
    # Campos adicionais de datas
    manufacturing_date = db.Column(db.Date, nullable=True)  # Data de fabricação
    expiration_date = db.Column(db.Date, nullable=True)  # Data de validade
    report_time = db.Column(db.Time, nullable=True)  # Hora do laudo
    
    # Novos campos para os módulos avançados
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    sample_id = db.Column(db.Integer, db.ForeignKey('sample.id'), nullable=True)
    template_id = db.Column(db.Integer, db.ForeignKey('report_templates.id'), nullable=True)
    
    # Campos para versão do documento
    version = db.Column(db.Integer, default=1)
    parent_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=True)  # Para controle de versões
    
    # Campos para impressão e visualização
    has_print_version = db.Column(db.Boolean, default=False)
    print_version_path = db.Column(db.String(500), nullable=True)
    
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
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Campos para assinatura digital
    signature_date = db.Column(db.DateTime, nullable=True)
    signature_hash = db.Column(db.String(256), nullable=True)
    
    # Indicadores técnicos/padrões de qualidade
    ph_value = db.Column(db.Float, nullable=True)
    brix_value = db.Column(db.Float, nullable=True)
    acidity_value = db.Column(db.Float, nullable=True)
    color_value = db.Column(db.String(50), nullable=True)
    density_value = db.Column(db.Float, nullable=True)
    
    # Campo para armazenar resultados de cálculos adicionais em formato JSON
    additional_metrics = db.Column(db.Text, nullable=True)  # JSON com métricas adicionais
    
    # Análise de tempo e eficiência
    analysis_start_time = db.Column(db.DateTime, nullable=True)
    analysis_end_time = db.Column(db.DateTime, nullable=True)
    
    # Relações com outras tabelas
    assigned_user = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_reports')
    approver_user = db.relationship('User', foreign_keys=[approved_by], backref='approved_reports')
    creator_user = db.relationship('User', foreign_keys=[created_by], backref='created_reports')
    client = db.relationship('Client', backref='reports')
    # template = db.relationship('ReportTemplate')
    parent_report = db.relationship('Report', remote_side=[id], backref='versions')  # Para histórico de versões
    attachments = db.relationship('ReportAttachment', back_populates='report')
    
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
            'report_type': self.report_type,
            
            # Dados de rastreabilidade
            'batch_number': self.batch_number,
            'raw_material_type': self.raw_material_type,
            'sample_code': self.sample_code,
            
            # Análises citadas no laudo (informadas pelo fornecedor)
            'brix': self.brix,
            'ph': self.ph,
            'acidity': self.acidity,
            
            # Análises realizadas em laboratório
            'lab_brix': self.lab_brix,
            'lab_ph': self.lab_ph,
            'lab_acidity': self.lab_acidity,
            
            # Validação físico-química
            'physicochemical_validation': self.physicochemical_validation,
            
            # Campos adicionais de rastreabilidade
            'report_archived': self.report_archived,
            'microbiology_collected': self.microbiology_collected,
            'has_report_document': self.has_report_document,
            
            # Datas
            'report_date': self.report_date.strftime('%d/%m/%Y') if self.report_date else None,
            'report_time': self.report_time.strftime('%H:%M') if self.report_time else None,
            'manufacturing_date': self.manufacturing_date.strftime('%d/%m/%Y') if self.manufacturing_date else None,
            'expiration_date': self.expiration_date.strftime('%d/%m/%Y') if self.expiration_date else None,
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
    contact_name = db.Column(db.String(150), nullable=True)  # Renomeado de contact para contact_name
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)  # Novo campo para endereço
    notes = db.Column(db.Text, nullable=True)  # Novo campo para observações
    type = db.Column(db.String(50), nullable=True)  # Novo campo para tipo de fornecedor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Supplier {self.name}>"
        
    def to_dict(self):
        """Converte objeto para dicionário."""
        return {
            'id': self.id,
            'name': self.name,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'notes': self.notes,
            'type': self.type,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M') if self.updated_at else None
        }


# [Antiga definição de ReportTemplate removida para evitar duplicação]


# [Antiga definição de ReportAttachment removida para evitar duplicação]


class ReportComment(db.Model):
    """Modelo para comentários internos em laudos."""
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_internal = db.Column(db.Boolean, default=True)  # Indica se o comentário é somente para equipe interna
    
    # Relações
    report = db.relationship('Report', backref=db.backref('comments', cascade='all, delete-orphan'))
    user = db.relationship('User', backref='report_comments')
    
    def __repr__(self):
        return f"<ReportComment {self.id} by {self.user_id} on {self.report_id}>"
    
    def to_dict(self):
        """Converte o comentário para dicionário."""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'comment': self.comment,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M'),
            'is_internal': self.is_internal
        }


class ReportHistory(db.Model):
    """Modelo para registrar histórico de modificações nos laudos."""
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # create, update, approve, reject, etc.
    details = db.Column(db.Text, nullable=True)  # Detalhes da ação (opcional)
    data_before = db.Column(db.Text, nullable=True)  # JSON com dados antes da modificação
    data_after = db.Column(db.Text, nullable=True)  # JSON com dados após a modificação
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relações
    report = db.relationship('Report', backref=db.backref('history', cascade='all, delete-orphan'))
    user = db.relationship('User', backref='report_actions')
    
    def __repr__(self):
        return f"<ReportHistory {self.id}: {self.action} on {self.report_id}>"
    
    def to_dict(self):
        """Converte o registro de histórico para dicionário."""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'action': self.action,
            'details': self.details,
            'data_before': json.loads(self.data_before) if self.data_before else None,
            'data_after': json.loads(self.data_after) if self.data_after else None,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M')
        }


class CustomFormula(db.Model):
    """Modelo para fórmulas personalizadas para cálculos técnicos."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    formula = db.Column(db.Text, nullable=False)  # Fórmula em formato Python ou expressão matemática
    parameters = db.Column(db.Text, nullable=False)  # JSON com parâmetros da fórmula
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relações
    creator = db.relationship('User', backref='created_formulas')
    
    def __repr__(self):
        return f"<CustomFormula {self.id}: {self.name}>"
    
    def to_dict(self):
        """Converte a fórmula para dicionário."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'formula': self.formula,
            'parameters': json.loads(self.parameters) if self.parameters else {},
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else None,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M'),
            'is_active': self.is_active
        }


class CalculationResult(db.Model):
    """Modelo para armazenar resultados de cálculos técnicos."""
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False)
    formula_id = db.Column(db.Integer, db.ForeignKey('custom_formula.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    input_data = db.Column(db.Text, nullable=False)  # JSON com dados de entrada
    result = db.Column(db.Text, nullable=False)  # JSON com resultados do cálculo
    calculated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relações
    report = db.relationship('Report', backref=db.backref('calculations', cascade='all, delete-orphan'))
    formula = db.relationship('CustomFormula', backref='calculation_results')
    calculator = db.relationship('User', backref='performed_calculations')
    
    def __repr__(self):
        return f"<CalculationResult {self.id}: {self.name} for {self.report_id}>"
    
    def to_dict(self):
        """Converte o resultado de cálculo para dicionário."""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'formula_id': self.formula_id,
            'formula_name': self.formula.name if self.formula else None,
            'name': self.name,
            'description': self.description,
            'input_data': json.loads(self.input_data) if self.input_data else {},
            'result': json.loads(self.result) if self.result else {},
            'calculated_by': self.calculated_by,
            'calculator_name': self.calculator.name if self.calculator else None,
            'calculated_at': self.calculated_at.strftime('%d/%m/%Y %H:%M')
        }


class Client(db.Model):
    """Modelo para clientes/fornecedores."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # cliente, fornecedor
    contact_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<Client {self.id}: {self.name} ({self.type})>"
    
    def to_dict(self):
        """Converte o cliente/fornecedor para dicionário."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M'),
            'is_active': self.is_active
        }


class Sample(db.Model):
    """Modelo para registro de amostras a serem analisadas."""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    material_type = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.String(50), nullable=True)
    batch_number = db.Column(db.String(100), nullable=True)
    received_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiration_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='recebida')  # recebida, em_analise, finalizada, arquivada
    received_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    storage_location = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relações
    client = db.relationship('Client', backref='samples')
    receiver = db.relationship('User', backref='received_samples')
    
    def __repr__(self):
        return f"<Sample {self.id}: {self.code}>"
    
    def to_dict(self):
        """Converte a amostra para dicionário."""
        # Consultar a contagem de relatórios relacionados
        reports_count = 0  # Implementaremos isso depois para evitar problemas circulares
        
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'material_type': self.material_type,
            'quantity': self.quantity,
            'batch_number': self.batch_number,
            'received_date': self.received_date.strftime('%d/%m/%Y %H:%M'),
            'expiration_date': self.expiration_date.strftime('%d/%m/%Y') if self.expiration_date else None,
            'status': self.status,
            'received_by': self.received_by,
            'receiver_name': self.receiver.name if self.receiver else None,
            'storage_location': self.storage_location,
            'notes': self.notes,
            'reports_count': reports_count
        }


class Notification(db.Model):
    """Modelo para notificações do sistema."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)  # Link para redirecionamento
    type = db.Column(db.String(20), default='info')  # info, warning, alert, success
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    
    # Relações
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f"<Notification {self.id} for {self.user_id}: {self.title}>"
    
    def to_dict(self):
        """Converte a notificação para dicionário."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'type': self.type,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'read_at': self.read_at.strftime('%d/%m/%Y %H:%M') if self.read_at else None,
            'is_read': self.is_read
        }


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


class TechnicalDocument(db.Model):
    """Modelo para documentos técnicos do laboratório (POPs, fichas técnicas, etc.)."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    document_type = db.Column(db.String(50), nullable=False)  # pop, ficha_tecnica, certificado, instrucao, planilha, manual, outro
    
    # Arquivos
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    
    # Metadados
    revision = db.Column(db.String(20), nullable=True)
    valid_until = db.Column(db.Date, nullable=True)
    author = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.String(200), nullable=True)  # tags separadas por vírgula
    
    # Controle de status e acesso
    status = db.Column(db.String(20), default='ativo')  # ativo, em_revisao, obsoleto
    restricted_access = db.Column(db.Boolean, default=False)
    
    # Campos de controle
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('technical_document.id'), nullable=True)  # Para versões
    version = db.Column(db.Integer, default=1)
    
    # Relações
    uploader = db.relationship('User', backref='uploaded_documents')
    parent_document = db.relationship('TechnicalDocument', remote_side=[id], backref='versions')
    
    def __repr__(self):
        return f"<TechnicalDocument {self.id}: {self.title} ({self.document_type})>"
    
    def to_dict(self):
        """Converte o documento para dicionário."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'document_type': self.document_type,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'revision': self.revision,
            'valid_until': self.valid_until.strftime('%d/%m/%Y') if self.valid_until else None,
            'author': self.author,
            'tags': self.tags,
            'status': self.status,
            'restricted_access': self.restricted_access,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.name if self.uploader else None,
            'upload_date': self.upload_date.strftime('%d/%m/%Y %H:%M'),
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M'),
            'version': self.version,
            'parent_id': self.parent_id
        }
    
    def get_file_url(self):
        """Retorna URL para acesso ao arquivo."""
        from flask import url_for
        return url_for('documents.download_document', document_id=self.id)
    
    def get_extension(self):
        """Retorna a extensão do arquivo."""
        if not self.file_type:
            return ''
        return self.file_type.lower()
    
    def get_icon_class(self):
        """Retorna uma classe de ícone adequada para o tipo de documento."""
        ext = self.get_extension()
        if ext in ['pdf']:
            return 'fa-file-pdf'
        elif ext in ['doc', 'docx']:
            return 'fa-file-word'
        elif ext in ['xls', 'xlsx']:
            return 'fa-file-excel'
        elif ext in ['ppt', 'pptx']:
            return 'fa-file-powerpoint'
        elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            return 'fa-file-image'
        else:
            return 'fa-file'


class DocumentAttachment(db.Model):
    """Modelo para anexos de documentos técnicos."""
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('technical_document.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relações
    document = db.relationship('TechnicalDocument', backref=db.backref('attachments', cascade='all, delete-orphan'))
    uploader = db.relationship('User', backref='document_attachments')
    
    def __repr__(self):
        return f"<DocumentAttachment {self.id}: {self.original_filename}>"
    
    def to_dict(self):
        """Converte o anexo para dicionário."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'description': self.description,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.name if self.uploader else None,
            'upload_date': self.upload_date.strftime('%d/%m/%Y %H:%M')
        }


# Modelo já definido anteriormente - removido para evitar duplicação


class AutomaticReport(db.Model):
    """Modelo para laudos gerados automaticamente a partir de templates."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    template_id = db.Column(db.Integer, db.ForeignKey('report_templates.id'), nullable=False)
    data = db.Column(db.JSON, nullable=False)  # Dados preenchidos do template
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(50), default='draft')  # draft, review, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    generated_file = db.Column(db.String(255), nullable=True)  # Arquivo PDF gerado
    file_path = db.Column(db.String(500), nullable=True)
    
    # Relações
    template = db.relationship('ReportTemplate', backref='automatic_reports')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_auto_reports')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_auto_reports')
    
    def __repr__(self):
        return f"<AutomaticReport {self.id}: {self.title}>"
    
    def to_dict(self):
        """Converte o laudo automático para dicionário."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'template_id': self.template_id,
            'template_name': self.template.name if self.template else None,
            'data': self.data,
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else None,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M'),
            'status': self.status,
            'approved_by': self.approved_by,
            'approver_name': self.approver.name if self.approver else None,
            'approved_at': self.approved_at.strftime('%d/%m/%Y %H:%M') if self.approved_at else None,
            'generated_file': self.generated_file,
            'file_path': self.file_path
        }
    
    def get_status_label(self):
        """Retorna um rótulo formatado para o status."""
        status_map = {
            'draft': 'Rascunho',
            'review': 'Em Revisão',
            'approved': 'Aprovado',
            'rejected': 'Rejeitado'
        }
        return status_map.get(self.status, self.status)
    
    def get_status_badge(self):
        """Retorna uma classe CSS para o status."""
        status_map = {
            'draft': 'secondary',
            'review': 'info',
            'approved': 'success',
            'rejected': 'danger'
        }
        return status_map.get(self.status, 'primary')


class ReportTemplate(db.Model):
    """Modelo para templates de laudos."""
    __tablename__ = 'report_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    original_filename = db.Column(db.String(255))
    structure = db.Column(db.Text)  # JSON como string
    template_type = db.Column(db.String(50))  # quality, production, maintenance, etc.
    version = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    creator = db.relationship('User', foreign_keys=[creator_id])
    reports = db.relationship('Report', overlaps="template")
    
    def __repr__(self):
        return f'<ReportTemplate {self.name} v{self.version}>'
    
    def to_dict(self):
        """Converte o modelo para um dicionário."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'file_path': self.file_path,
            'original_filename': self.original_filename,
            'template_type': self.template_type,
            'version': self.version,
            'is_active': self.is_active,
            'creator_id': self.creator_id,
            'creator_name': self.creator.name if self.creator else None,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M') if self.updated_at else None
        }
    
    def get_file_url(self):
        """Retorna URL para acesso ao arquivo do template."""
        if not self.file_path:
            return None
        
        from flask import url_for
        return url_for('templates.download_template', template_id=self.id)


class ReportAttachment(db.Model):
    """Modelo para anexos de laudos."""
    __tablename__ = 'report_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)  # em bytes
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relacionamentos
    report = db.relationship('Report', back_populates='attachments')
    uploader = db.relationship('User', foreign_keys=[uploader_id])


class StandardFields(db.Model):
    """Modelo para armazenar campos padronizados para preenchimento automático."""
    __tablename__ = 'standard_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Nome do conjunto de campos padrão
    empresa = db.Column(db.String(100), nullable=False, default="Zelopack")
    produto = db.Column(db.String(100), nullable=True)
    marca = db.Column(db.String(100), nullable=True)
    lote = db.Column(db.String(50), nullable=True)
    
    # Campos adicionais úteis
    data_producao = db.Column(db.Date, nullable=True)
    data_validade = db.Column(db.Date, nullable=True)
    responsavel = db.Column(db.String(100), nullable=True)
    departamento = db.Column(db.String(100), nullable=True)
    linha_producao = db.Column(db.String(50), nullable=True)
    
    # Controle de versão e metadados
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    creator = db.relationship('User', backref='standard_fields')
    
    def __repr__(self):
        return f"<StandardFields {self.id}: {self.name}>"
    
    def to_dict(self):
        """Converte os campos padrão para dicionário."""
        return {
            'id': self.id,
            'name': self.name,
            'empresa': self.empresa,
            'produto': self.produto,
            'marca': self.marca,
            'lote': self.lote,
            'data_producao': self.data_producao.strftime('%d/%m/%Y') if self.data_producao else None,
            'data_validade': self.data_validade.strftime('%d/%m/%Y') if self.data_validade else None,
            'responsavel': self.responsavel,
            'departamento': self.departamento,
            'linha_producao': self.linha_producao,
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else None,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M'),
            'is_active': self.is_active,
            'is_default': self.is_default
        }


class FormPreset(db.Model):
    """Modelo para armazenar predefinições de preenchimento de formulários."""
    __tablename__ = 'form_presets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    form_type = db.Column(db.String(100), nullable=True)  # Tipo/nome do formulário
    form_path = db.Column(db.String(500), nullable=True)  # Caminho relativo do arquivo no sistema
    file_path = db.Column(db.String(500), nullable=True)  # Campo mantido para compatibilidade
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data = db.Column(db.Text, nullable=False, default='{}')  # Campos e valores predefinidos em formato JSON
    fields_json = db.Column(db.Text, nullable=True)  # Novo campo para compatibilidade com a API de autofill
    is_default = db.Column(db.Boolean, default=False)  # Se é a predefinição padrão para este formulário
    is_active = db.Column(db.Boolean, default=True)
    use_standard_fields = db.Column(db.Boolean, default=True)  # Se deve usar campos padronizados
    standard_fields_id = db.Column(db.Integer, db.ForeignKey('standard_fields.id'), nullable=True)
    
    # Relacionamentos
    creator = db.relationship('User', backref='form_presets')
    standard_fields = db.relationship('StandardFields', backref='form_presets')
    
    def __repr__(self):
        return f"<FormPreset {self.id}: {self.name} for {self.form_path or self.form_type}>"
    
    def to_dict(self):
        """Converte a predefinição para dicionário."""
        try:
            data_dict = json.loads(self.data) if isinstance(self.data, str) else self.data
        except (json.JSONDecodeError, TypeError):
            data_dict = {}
            
        try:
            fields_dict = json.loads(self.fields_json) if self.fields_json else {}
        except (json.JSONDecodeError, TypeError):
            fields_dict = {}
            
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'form_path': self.form_path,
            'form_type': self.form_type,
            'file_path': self.file_path,
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else None,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M'),
            'data': data_dict,
            'fields': fields_dict,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'use_standard_fields': self.use_standard_fields,
            'standard_fields_id': self.standard_fields_id,
            'standard_fields_name': self.standard_fields.name if self.standard_fields else None
        }
    
    def get_download_url(self):
        """Retorna a URL para download da predefinição."""
        from flask import url_for
        return url_for('forms.download_preset', preset_id=self.id)
