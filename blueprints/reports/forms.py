from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, SubmitField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange

class ReportUploadForm(FlaskForm):
    """Formulário para upload de laudos."""
    # Informações básicas
    title = StringField('Título', validators=[Optional()])  # Validação customizada será feita na rota
    description = TextAreaField('Descrição', validators=[Optional()])
    file = FileField('Arquivo', validators=[Optional()])  # Alterado para Optional
    
    # Campos para categorização
    category = SelectField('Categoria', 
                         choices=[('', 'Selecione uma categoria'),
                                  ('materias_primas', 'Matérias Primas'),
                                  ('edulcorantes', 'Edulcorantes'),
                                  ('corantes', 'Corantes'),
                                  ('acucar', 'Açúcar'),
                                  ('embalagem', 'Embalagem')],
                         validators=[Optional()])
    supplier = SelectField('Fornecedor', validators=[Optional()])
    supplier_manual = StringField('Outro Fornecedor (digite se não estiver na lista)', validators=[Optional()])
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
    
    # Análises físico-químicas
    ph = DecimalField('pH', validators=[Optional(), NumberRange(min=0, max=14)])
    brix = DecimalField('Brix (°Bx)', validators=[Optional(), NumberRange(min=0, max=100)])
    acidity = DecimalField('Acidez (g/100ml)', validators=[Optional(), NumberRange(min=0)])
    
    # Datas adicionais
    manufacturing_date = DateField('Data de Fabricação', validators=[Optional()], format='%Y-%m-%d')
    expiration_date = DateField('Data de Validade', validators=[Optional()], format='%Y-%m-%d')
    report_time = TimeField('Hora do Laudo', validators=[Optional()], format='%H:%M')
    
    # Análises realizadas em laboratório
    lab_brix = DecimalField('Brix (°Bx) - Laboratório', validators=[Optional(), NumberRange(min=0, max=100)])
    lab_ph = DecimalField('pH - Laboratório', validators=[Optional(), NumberRange(min=0, max=14)])
    lab_acidity = DecimalField('Acidez (g/100ml) - Laboratório', validators=[Optional(), NumberRange(min=0)])
    
    # Validação físico-química
    physicochemical_validation = SelectField('Validação Físico-Química', 
                                         choices=[('não verificado', 'Não Verificado'),
                                                  ('ok', 'OK'),
                                                  ('não padrão', 'Não Padrão')],
                                         default='não verificado',
                                         validators=[Optional()])
    
    # Campos adicionais de rastreabilidade
    report_archived = BooleanField('Laudo Arquivado', default=False)
    microbiology_collected = BooleanField('Microbiologia Coletada', default=False)
    has_report_document = BooleanField('Possui Documento do Laudo', default=False)
    
    # Indicadores técnicos (mantidos para compatibilidade)
    ph_value = DecimalField('Valor de pH (antigo)', validators=[Optional()])
    brix_value = DecimalField('Valor Brix (antigo)', validators=[Optional()])
    acidity_value = DecimalField('Acidez (antigo)', validators=[Optional()])
    color_value = StringField('Cor', validators=[Optional()])
    density_value = DecimalField('Densidade', validators=[Optional()])
    
    submit = SubmitField('Enviar Laudo')

class SearchForm(FlaskForm):
    """Formulário para pesquisa de laudos."""
    query = StringField('Termo de Pesquisa', validators=[Optional()])
    category = SelectField('Categoria', 
                         choices=[('', 'Todas as categorias'),
                                  ('materias_primas', 'Matérias Primas'),
                                  ('edulcorantes', 'Edulcorantes'),
                                  ('corantes', 'Corantes'),
                                  ('acucar', 'Açúcar'),
                                  ('embalagem', 'Embalagem')],
                         validators=[Optional()])
    supplier = SelectField('Fornecedor', validators=[Optional()])
    date_from = DateField('Data Inicial', validators=[Optional()], format='%Y-%m-%d')
    date_to = DateField('Data Final', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Pesquisar')


class SupplierForm(FlaskForm):
    """Formulário para cadastro de fornecedores."""
    name = StringField('Nome do Fornecedor', validators=[DataRequired()])
    contact_name = StringField('Nome de Contato', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    phone = StringField('Telefone', validators=[Optional()])
    address = TextAreaField('Endereço', validators=[Optional()])
    notes = TextAreaField('Observações', validators=[Optional()])
    type = SelectField('Tipo', 
                     choices=[('materias_primas', 'Fornecedor de Matérias Primas'),
                              ('edulcorantes', 'Fornecedor de Edulcorantes'),
                              ('corantes', 'Fornecedor de Corantes'),
                              ('acucar', 'Fornecedor de Açúcar'),
                              ('embalagem', 'Fornecedor de Embalagem'),
                              ('outro', 'Outro')],
                     validators=[DataRequired()])
    submit = SubmitField('Salvar Fornecedor')
