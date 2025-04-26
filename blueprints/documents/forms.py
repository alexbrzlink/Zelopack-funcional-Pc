from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, MultipleFileField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, ValidationError

class DocumentForm(FlaskForm):
    """Formulário para upload e gestão de documentos técnicos."""
    title = StringField('Título do Documento', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Descrição', validators=[Optional()])
    
    # Tipo de documento
    document_type = SelectField('Tipo de Documento', choices=[
        ('pop', 'POP - Procedimento Operacional Padrão'),
        ('ficha_tecnica', 'Ficha Técnica'),
        ('certificado', 'Certificado'),
        ('instrucao', 'Instrução de Trabalho'),
        ('planilha', 'Planilha de Controle'),
        ('manual', 'Manual'),
        ('formulario', 'Formulário'),
        ('outro', 'Outro')
    ])
    
    # Categoria do documento (para formulários)
    category = SelectField('Categoria', choices=[
        ('', 'Selecione uma categoria (opcional)'),
        ('blender', 'BLENDER'),
        ('laboratorio', 'LABORATÓRIO'),
        ('portaria', 'PORTARIA'),
        ('qualidade', 'QUALIDADE'),
        ('tba', 'TBA')
    ], default='', validators=[Optional()])
    
    # Campo para versão/revisão
    revision = StringField('Revisão/Versão', validators=[Optional(), Length(max=20)])
    
    # Data de validade (se aplicável)
    valid_until = DateField('Válido até', validators=[Optional()])
    
    # Responsável pela elaboração
    author = StringField('Elaborado por', validators=[Optional(), Length(max=100)])
    
    # Tags para busca
    tags = StringField('Tags (separadas por vírgula)', validators=[Optional(), Length(max=200)])
    
    # Status do documento
    status = SelectField('Status', choices=[
        ('ativo', 'Ativo'),
        ('em_revisao', 'Em Revisão'),
        ('obsoleto', 'Obsoleto')
    ], default='ativo')
    
    # Controle de acesso
    restricted_access = BooleanField('Acesso Restrito', default=False)
    
    # Campo de arquivo principal
    document_file = FileField('Arquivo Principal', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg'], 
                    'Somente arquivos PDF, Office ou imagens são permitidos.')
    ])
    
    # Campos para arquivos adicionais/anexos
    attachments = MultipleFileField('Anexos (opcional)', validators=[Optional()])
    
    submit = SubmitField('Salvar Documento')


class DocumentSearchForm(FlaskForm):
    """Formulário para busca de documentos técnicos."""
    search_term = StringField('Termo de Busca', validators=[Optional()])
    
    document_type = SelectField('Tipo de Documento', choices=[
        ('', 'Todos'),
        ('pop', 'POP - Procedimento Operacional Padrão'),
        ('ficha_tecnica', 'Ficha Técnica'),
        ('certificado', 'Certificado'),
        ('instrucao', 'Instrução de Trabalho'),
        ('planilha', 'Planilha de Controle'),
        ('manual', 'Manual'),
        ('formulario', 'Formulário'),
        ('outro', 'Outro')
    ], default='')
    
    category = SelectField('Categoria', choices=[
        ('', 'Todas'),
        ('blender', 'BLENDER'),
        ('laboratorio', 'LABORATÓRIO'),
        ('portaria', 'PORTARIA'),
        ('qualidade', 'QUALIDADE'),
        ('tba', 'TBA')
    ], default='')
    
    status = SelectField('Status', choices=[
        ('', 'Todos'),
        ('ativo', 'Ativo'),
        ('em_revisao', 'Em Revisão'),
        ('obsoleto', 'Obsoleto')
    ], default='')
    
    author = StringField('Elaborado por', validators=[Optional()])
    
    tag = StringField('Tag', validators=[Optional()])
    
    submit = SubmitField('Buscar')