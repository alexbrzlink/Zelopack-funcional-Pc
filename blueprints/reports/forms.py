from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Optional

class ReportUploadForm(FlaskForm):
    """Formulário para upload de laudos."""
    # Informações básicas
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[Optional()])
    file = FileField('Arquivo', validators=[FileRequired()])
    
    # Campos para categorização
    category = SelectField('Categoria', validators=[Optional()])
    supplier = SelectField('Fornecedor', validators=[Optional()])
    batch_number = StringField('Número do Lote', validators=[Optional()])
    raw_material_type = SelectField('Tipo de Matéria-Prima', 
                                   choices=[('', 'Selecione um tipo'), 
                                           ('laranja', 'Laranja'),
                                           ('maca', 'Maçã'),
                                           ('uva', 'Uva'),
                                           ('manga', 'Manga'),
                                           ('morango', 'Morango'),
                                           ('outro', 'Outro')],
                                   validators=[Optional()])
    sample_code = StringField('Código da Amostra', validators=[Optional()])
    
    # Datas e prazos
    report_date = DateField('Data do Laudo', validators=[Optional()], format='%Y-%m-%d')
    due_date = DateField('Data Limite', validators=[Optional()], format='%Y-%m-%d')
    
    # Fluxo de trabalho
    status = SelectField('Status', 
                        choices=[('pendente', 'Pendente'),
                                ('aprovado', 'Aprovado'),
                                ('rejeitado', 'Rejeitado')],
                        default='pendente',
                        validators=[Optional()])
    
    priority = SelectField('Prioridade', 
                          choices=[('baixa', 'Baixa'),
                                  ('normal', 'Normal'),
                                  ('alta', 'Alta'),
                                  ('urgente', 'Urgente')],
                          default='normal',
                          validators=[Optional()])
    
    # Atribuição
    assigned_to = SelectField('Atribuir para', validators=[Optional()])
    
    # Indicadores técnicos
    ph_value = DecimalField('Valor de pH', validators=[Optional()])
    brix_value = DecimalField('Valor Brix', validators=[Optional()])
    acidity_value = DecimalField('Acidez', validators=[Optional()])
    color_value = StringField('Cor', validators=[Optional()])
    density_value = DecimalField('Densidade', validators=[Optional()])
    
    submit = SubmitField('Enviar Laudo')

class SearchForm(FlaskForm):
    """Formulário para pesquisa de laudos."""
    query = StringField('Termo de Pesquisa', validators=[Optional()])
    category = SelectField('Categoria', validators=[Optional()])
    supplier = SelectField('Fornecedor', validators=[Optional()])
    date_from = DateField('Data Inicial', validators=[Optional()], format='%Y-%m-%d')
    date_to = DateField('Data Final', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Pesquisar')
