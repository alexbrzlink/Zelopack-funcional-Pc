from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, DateField, FloatField
from wtforms import SubmitField, BooleanField, HiddenField, MultipleFileField, IntegerField
from wtforms.validators import DataRequired, Optional, Length, ValidationError
import os
import json


class ImportTemplateForm(FlaskForm):
    """Formulário para importação de templates de formulários da Zelopack."""
    template_file = FileField('Arquivo do Formulário', 
                              validators=[
                                  FileRequired(),
                                  FileAllowed(['xlsx', 'xls', 'docx', 'doc', 'pdf'], 
                                             'Somente arquivos Excel, Word ou PDF são permitidos.')
                              ])
    template_type = SelectField('Tipo de Formulário', 
                               choices=[
                                   ('quality', 'Controle de Qualidade'),
                                   ('production', 'Controle de Produção'),
                                   ('maintenance', 'Manutenção'),
                                   ('laboratory', 'Laboratório'),
                                   ('other', 'Outro')
                               ])
    name = StringField('Nome do Template', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Descrição', validators=[Optional(), Length(max=500)])
    is_active = BooleanField('Ativo', default=True)
    version = StringField('Versão', default='1.0', validators=[Length(max=10)])
    submit = SubmitField('Importar Template')
    
    def validate_name(self, name):
        """Verifica se o nome do template não contém caracteres inválidos."""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in name.data:
                raise ValidationError(f'O nome do template não pode conter o caractere "{char}".')


class CreateTemplateForm(FlaskForm):
    """Formulário para criação manual de templates de laudos."""
    name = StringField('Nome do Template', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Descrição', validators=[Optional(), Length(max=500)])
    structure = HiddenField('Estrutura do Template (JSON)', validators=[DataRequired()])
    is_active = BooleanField('Ativo', default=True)
    version = StringField('Versão', default='1.0', validators=[Length(max=10)])
    submit = SubmitField('Salvar Template')
    
    def validate_structure(self, structure):
        """Verifica se a estrutura do template é um JSON válido e contém pelo menos um campo."""
        try:
            structure_data = json.loads(structure.data)
            
            if not isinstance(structure_data, dict):
                raise ValidationError('A estrutura do template deve ser um objeto JSON válido.')
                
            if 'fields' not in structure_data or not isinstance(structure_data['fields'], dict):
                raise ValidationError('A estrutura do template deve conter um objeto "fields".')
                
            if len(structure_data['fields']) == 0:
                raise ValidationError('O template deve conter pelo menos um campo.')
                
            # Verificar se cada campo tem nome e rótulo
            for field_id, field in structure_data['fields'].items():
                if 'name' not in field or not field['name']:
                    raise ValidationError('Todos os campos devem ter um nome definido.')
                if 'label' not in field or not field['label']:
                    raise ValidationError('Todos os campos devem ter um rótulo definido.')
                if 'type' not in field:
                    raise ValidationError('Todos os campos devem ter um tipo definido.')
                    
        except json.JSONDecodeError:
            raise ValidationError('A estrutura do template não é um JSON válido.')


class FillReportForm(FlaskForm):
    """Formulário para preenchimento de um relatório baseado em um template."""
    title = StringField('Título do Laudo', validators=[DataRequired(), Length(max=200)])
    report_date = DateField('Data do Laudo', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[Optional(), Length(max=1000)])
    
    # Campos para associar a cliente e amostra
    client_id = SelectField('Cliente', coerce=int, validators=[Optional()])
    sample_id = SelectField('Amostra', coerce=int, validators=[Optional()])
    
    # Campos para workflow
    priority = SelectField('Prioridade', choices=[
        ('baixa', 'Baixa'), 
        ('normal', 'Normal'), 
        ('alta', 'Alta'), 
        ('urgente', 'Urgente')
    ], default='normal')
    assigned_to = SelectField('Responsável', coerce=int, validators=[Optional()])
    due_date = DateField('Prazo', validators=[Optional()])
    
    # Campos para dados da análise
    ph_value = FloatField('pH', validators=[Optional()])
    brix_value = FloatField('Brix (°Bx)', validators=[Optional()])
    acidity_value = FloatField('Acidez (g/100mL)', validators=[Optional()])
    color_value = StringField('Cor', validators=[Optional(), Length(max=50)])
    density_value = FloatField('Densidade (g/cm³)', validators=[Optional()])
    
    # Campo oculto para armazenar métricas adicionais (JSON)
    additional_metrics = HiddenField('Métricas Adicionais (JSON)')
    
    # Arquivos anexos
    attachments = MultipleFileField('Anexos', validators=[Optional()])
    
    submit = SubmitField('Gerar Laudo')
    
    def validate_additional_metrics(self, additional_metrics):
        """Verifica se as métricas adicionais são um JSON válido."""
        if additional_metrics.data:
            try:
                json.loads(additional_metrics.data)
            except json.JSONDecodeError:
                raise ValidationError('As métricas adicionais não estão em um formato JSON válido.')