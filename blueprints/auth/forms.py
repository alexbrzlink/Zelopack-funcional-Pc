from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

# Mensagens de erro personalizadas em português
mensagens_erro = {
    'required': 'Este campo é obrigatório',
    'email': 'Por favor informe um email válido',
    'length': 'Este campo deve ter entre {min} e {max} caracteres',
    'equal_to': 'Os campos não coincidem',
    'usuario_existente': 'Este nome de usuário já está sendo usado',
    'email_existente': 'Este email já está sendo usado',
}

class LoginForm(FlaskForm):
    """Formulário para login de usuários."""
    username = StringField('Nome de Usuário', validators=[DataRequired(message=mensagens_erro['required'])])
    password = PasswordField('Senha', validators=[DataRequired(message=mensagens_erro['required'])])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')
    



class RegistrationForm(FlaskForm):
    """Formulário para registro de novos usuários."""
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')]
    )
    role = SelectField(
        'Função', 
        choices=[
            ('analista', 'Analista de Qualidade'),
            ('gestor', 'Gestor'),
            ('admin', 'Administrador')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        """Verifica se o nome de usuário já existe."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(mensagens_erro['usuario_existente'])
        
        # Verificar se o nome de usuário contém caracteres inválidos
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username.data):
            raise ValidationError('Nome de usuário pode conter apenas letras, números e sublinhado (_).')

    def validate_email(self, email):
        """Verifica se o email já está em uso."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(mensagens_erro['email_existente'])
            
        # Verificar domínio do email (opcional)
        if not email.data.endswith(('.com', '.com.br', '.org', '.net', '.gov', '.edu')):
            raise ValidationError('Por favor, use um domínio de email válido.')


class ResetPasswordRequestForm(FlaskForm):
    """Formulário para solicitação de redefinição de senha."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Redefinição de Senha')


class ResetPasswordForm(FlaskForm):
    """Formulário para redefinição de senha."""
    password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Confirmar Nova Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')]
    )
    submit = SubmitField('Redefinir Senha')


class EditUserForm(FlaskForm):
    """Formulário para edição de perfil de usuário."""
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField(
        'Função', 
        choices=[
            ('analista', 'Analista de Qualidade'),
            ('gestor', 'Gestor'),
            ('admin', 'Administrador')
        ],
        validators=[DataRequired()]
    )
    is_active = BooleanField('Ativo')
    submit = SubmitField('Salvar Alterações')

    def __init__(self, original_email=None, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        """Verifica se o email já está em uso."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError(mensagens_erro['email_existente'])
            
            # Verificar domínio do email (opcional)
            if not email.data.endswith(('.com', '.com.br', '.org', '.net', '.gov', '.edu')):
                raise ValidationError('Por favor, use um domínio de email válido.')


class ChangePasswordForm(FlaskForm):
    """Formulário para alteração de senha."""
    current_password = PasswordField('Senha Atual', validators=[DataRequired()])
    password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Confirmar Nova Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')]
    )
    submit = SubmitField('Alterar Senha')