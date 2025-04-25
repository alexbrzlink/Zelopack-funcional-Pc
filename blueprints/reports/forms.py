from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional

class ReportUploadForm(FlaskForm):
    """Formulário para upload de laudos."""
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[Optional()])
    file = FileField('Arquivo', validators=[FileRequired()])
    category = SelectField('Categoria', validators=[Optional()])
    supplier = SelectField('Fornecedor', validators=[Optional()])
    batch_number = StringField('Número do Lote', validators=[Optional()])
    report_date = DateField('Data do Laudo', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Enviar Laudo')

class SearchForm(FlaskForm):
    """Formulário para pesquisa de laudos."""
    query = StringField('Termo de Pesquisa', validators=[Optional()])
    category = SelectField('Categoria', validators=[Optional()])
    supplier = SelectField('Fornecedor', validators=[Optional()])
    date_from = DateField('Data Inicial', validators=[Optional()], format='%Y-%m-%d')
    date_to = DateField('Data Final', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Pesquisar')
