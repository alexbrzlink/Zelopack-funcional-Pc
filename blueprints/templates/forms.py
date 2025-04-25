from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, DateField, FloatField, HiddenField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Optional, Length, ValidationError
import json

class TemplateForm(FlaskForm):
    """Formulário para criar ou editar templates de laudos."""
    name = StringField('Nome do Template', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Descrição', validators=[Optional(), Length(max=500)])
    structure = HiddenField('Estrutura JSON', validators=[DataRequired()])
    submit = SubmitField('Salvar Template')
    
    def validate_structure(self, field):
        try:
            json_data = json.loads(field.data)
            # Verificar se o JSON é válido para estrutura de template
            if not isinstance(json_data, dict):
                raise ValidationError('A estrutura do template deve ser um objeto JSON válido.')
        except json.JSONDecodeError:
            raise ValidationError('A estrutura do template não é um JSON válido.')


class AutoFillReportForm(FlaskForm):
    """Formulário para preenchimento automático de laudos a partir de templates."""
    title = StringField('Título do Laudo', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Descrição', validators=[Optional()])
    
    client_id = SelectField('Cliente', validators=[Optional()], coerce=int)
    sample_id = SelectField('Amostra', validators=[Optional()], coerce=int)
    
    report_date = DateField('Data do Laudo', validators=[DataRequired()])
    due_date = DateField('Prazo de Entrega', validators=[Optional()])
    
    priority = SelectField('Prioridade', choices=[
        ('baixa', 'Baixa'), 
        ('normal', 'Normal'), 
        ('alta', 'Alta'), 
        ('urgente', 'Urgente')
    ], default='normal')
    
    assigned_to = SelectField('Responsável', validators=[Optional()], coerce=int)
    
    # Campos para valores de análise
    ph_value = FloatField('pH', validators=[Optional()])
    brix_value = FloatField('Brix (°Bx)', validators=[Optional()])
    acidity_value = FloatField('Acidez (g/100mL)', validators=[Optional()])
    color_value = StringField('Cor', validators=[Optional(), Length(max=50)])
    density_value = FloatField('Densidade (g/cm³)', validators=[Optional()])
    
    # Campo para métricas adicionais em JSON
    additional_metrics = HiddenField('Métricas Adicionais (JSON)', validators=[Optional()])
    
    # Campo para upload de múltiplos arquivos anexos
    attachments = MultipleFileField('Anexos (fotos, gráficos, etc.)', validators=[Optional()])
    
    submit = SubmitField('Gerar Laudo')
    
    def validate_additional_metrics(self, field):
        if field.data:
            try:
                json_data = json.loads(field.data)
                if not isinstance(json_data, dict):
                    raise ValidationError('As métricas adicionais devem ser um objeto JSON válido.')
            except json.JSONDecodeError:
                raise ValidationError('As métricas adicionais não são um JSON válido.')