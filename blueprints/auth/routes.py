"""
Rotas de autenticação com recursos avançados de segurança.
"""

import logging
from datetime import datetime, timedelta
from flask import (
    render_template, redirect, url_for, request,
    flash, session, jsonify, current_app
)
from flask_login import (
    login_user, logout_user, login_required,
    current_user
)
from werkzeug.security import (
    check_password_hash, generate_password_hash
)

from . import auth_bp
from models import User, db, SystemConfig
from utils.admin_security import (
    get_security_settings, verify_password_complexity,
    check_password_history, add_password_to_history,
    check_password_expiration, record_login_attempt,
    admin_required, check_admin_security_requirements
)
from utils.two_factor_auth import TwoFactorAuth
from utils.activity_logger import log_action

# Configuração do logger
logger = logging.getLogger(__name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Página de login com verificações avançadas de segurança.
    """
    # Redirecionar se já estiver logado
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Importar formulário
    from .forms import LoginForm
    form = LoginForm()
    
    # Verificação especial para login de demonstração
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == 'admin' and password == 'Alex':
            user = User.query.filter_by(username='admin').first()
            if user:
                login_user(user, remember=True)
                return redirect(url_for('dashboard.index'))
            else:
                flash('Usuário admin não encontrado. Por favor use o link de login automático.', 'warning')
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember_me.data
        
        # Buscar usuário
        user = User.query.filter_by(username=username).first()
        
        # Verificar tentativas de login
        blocked, message = record_login_attempt(username, success=False)
        if blocked:
            flash(message, 'danger')
            return render_template('auth/login.html', form=form, current_year=datetime.now().year)
        
        # Verificar usuário e senha
        if user and check_password_hash(user.password_hash, password):
            # Registrar sucesso (resetar contador de tentativas)
            record_login_attempt(username, success=True)
            
            # Verificar se usuário é administrador e precisa de 2FA
            settings = get_security_settings(current_app)
            if user.role == 'admin' and settings['two_factor_enabled']:
                # Armazenar ID do usuário para 2FA
                session['user_id_2fa'] = user.id
                session['remember_me'] = remember
                
                # Verificar método de 2FA preferido
                two_factor_method = settings['two_factor_method']
                
                # Redirecionar para verificação em duas etapas
                if two_factor_method == 'totp':
                    # Verificar se o usuário já configurou TOTP
                    totp_key = SystemConfig.query.filter_by(
                        key=f'totp.{user.id}').first()
                    
                    if not totp_key:
                        # Redirecionar para seleção de método
                        return redirect(url_for('auth.two_factor', method_selection=True))
                
                # Enviar código e redirecionar
                if two_factor_method == 'email':
                    # Enviar código por e-mail
                    two_factor = TwoFactorAuth(current_app)
                    two_factor.send_token_by_email(user.id, user.email)
                    
                    # Redirecionar para verificação
                    return redirect(url_for('auth.two_factor', method='email'))
                
                elif two_factor_method == 'sms':
                    # Verificar se o usuário tem telefone cadastrado
                    if not user.phone:
                        # Redirecionar para seleção de método
                        return redirect(url_for('auth.two_factor', method_selection=True))
                    
                    # Enviar código por SMS
                    two_factor = TwoFactorAuth(current_app)
                    two_factor.send_token_by_sms(user.id, user.phone)
                    
                    # Redirecionar para verificação
                    return redirect(url_for('auth.two_factor', method='sms'))
                
                elif two_factor_method == 'totp':
                    # Redirecionar para verificação TOTP
                    return redirect(url_for('auth.two_factor', method='totp'))
                
                else:
                    # Método não suportado, usar seleção
                    return redirect(url_for('auth.two_factor', method_selection=True))
            
            # Verificar validade da senha (apenas para admins)
            if user.role == 'admin' and settings['password_expiration_enabled']:
                # Verificar se a senha expirou
                if check_password_expiration(
                    user.last_password_change,
                    settings['password_expiration_days']
                ):
                    # Redirecionar para alteração de senha
                    login_user(user, remember=remember)
                    flash('Sua senha expirou. Por favor, altere-a para continuar.', 'warning')
                    return redirect(url_for('auth.change_password'))
            
            # Login normal
            login_user(user, remember=remember)
            
            # Registrar atividade
            log_action(
                user_id=user.id,
                action='login',
                module='auth',
                entity_type='User',
                entity_id=user.id,
                details=f'Login de usuário: {user.username}'
            )
            
            # Inicializar timestamp de atividade para timeout
            session['last_activity'] = datetime.now().timestamp()
            
            # Redirecionar para página solicitada ou inicial
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            return redirect(url_for('index'))
        
        else:
            # Falha de autenticação
            flash('Usuário ou senha inválidos.', 'danger')
    
    return render_template('auth/login.html', form=form, current_year=datetime.now().year)


@auth_bp.route('/two-factor', methods=['GET', 'POST'])
def two_factor():
    """
    Verificação em duas etapas para administradores.
    """
    # Verificar se há um usuário pendente de verificação
    if 'user_id_2fa' not in session:
        flash('Sessão de verificação expirada. Por favor, faça login novamente.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Obter parâmetros
    method_selection = request.args.get('method_selection') == 'true'
    method = request.args.get('method')
    totp_setup = request.args.get('totp_setup') == 'true'
    
    if totp_setup:
        # Configuração de TOTP
        user_id = session['user_id_2fa']
        user = User.query.get(user_id)
        
        if user:
            # Gerar configuração TOTP
            two_factor = TwoFactorAuth(current_app)
            setup_data = two_factor.setup_totp(user_id, user.username)
            
            # Armazenar chave na sessão temporariamente
            session['totp_secret_key'] = setup_data['secret_key']
            
            return render_template(
                'auth/two_factor.html',
                totp_setup=True,
                totp_setup_data=setup_data
            )
    
    elif method_selection:
        # Seleção de método
        return render_template(
            'auth/two_factor.html',
            method_selection=True,
            selected_method=request.args.get('selected_method', 'email')
        )
    
    elif method:
        # Verificação com método específico
        return render_template(
            'auth/two_factor.html',
            method=method
        )
    
    else:
        # Padrão: seleção de método
        return render_template(
            'auth/two_factor.html',
            method_selection=True,
            selected_method='email'
        )


@auth_bp.route('/select-two-factor-method', methods=['POST'])
def select_two_factor_method():
    """
    Seleciona e inicializa um método de verificação em duas etapas.
    """
    # Verificar se há um usuário pendente de verificação
    if 'user_id_2fa' not in session:
        flash('Sessão de verificação expirada. Por favor, faça login novamente.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Obter método selecionado
    method = request.form.get('method')
    
    if not method or method not in ['email', 'sms', 'totp']:
        flash('Método de verificação inválido.', 'danger')
        return redirect(url_for('auth.two_factor', method_selection=True))
    
    # Obter dados do usuário
    user_id = session['user_id_2fa']
    user = User.query.get(user_id)
    
    if not user:
        flash('Usuário não encontrado. Por favor, faça login novamente.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Processar de acordo com o método
    if method == 'email':
        # Enviar código por e-mail
        two_factor = TwoFactorAuth(current_app)
        success = two_factor.send_token_by_email(user.id, user.email)
        
        if not success:
            flash('Erro ao enviar código de verificação por e-mail. Tente outro método.', 'danger')
            return redirect(url_for('auth.two_factor', method_selection=True))
        
        return redirect(url_for('auth.two_factor', method='email'))
    
    elif method == 'sms':
        # Verificar se o usuário tem telefone cadastrado
        if not user.phone:
            flash('Você não tem um número de telefone cadastrado. Por favor, escolha outro método.', 'warning')
            return redirect(url_for('auth.two_factor', method_selection=True))
        
        # Enviar código por SMS
        two_factor = TwoFactorAuth(current_app)
        success = two_factor.send_token_by_sms(user.id, user.phone)
        
        if not success:
            flash('Erro ao enviar código de verificação por SMS. Tente outro método.', 'danger')
            return redirect(url_for('auth.two_factor', method_selection=True))
        
        return redirect(url_for('auth.two_factor', method='sms'))
    
    elif method == 'totp':
        # Verificar se o usuário já configurou TOTP
        totp_config = SystemConfig.query.filter_by(key=f'totp.{user.id}').first()
        
        if not totp_config:
            # Redirecionar para configuração
            return redirect(url_for('auth.two_factor', totp_setup=True))
        
        # Redirecionar para verificação
        return redirect(url_for('auth.two_factor', method='totp'))


@auth_bp.route('/verify-two-factor', methods=['POST'])
def verify_two_factor():
    """
    Verifica o código de verificação em duas etapas.
    """
    # Verificar se há um usuário pendente de verificação
    if 'user_id_2fa' not in session:
        flash('Sessão de verificação expirada. Por favor, faça login novamente.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Obter código de verificação
    code = request.form.get('code')
    method = request.args.get('method')
    
    if not code:
        flash('Por favor, digite o código de verificação.', 'danger')
        return redirect(url_for('auth.two_factor', method=method))
    
    # Obter dados do usuário
    user_id = session['user_id_2fa']
    user = User.query.get(user_id)
    
    if not user:
        flash('Usuário não encontrado. Por favor, faça login novamente.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Verificar de acordo com o método
    if method == 'totp':
        # Verificar TOTP
        two_factor = TwoFactorAuth(current_app)
        
        # Obter chave TOTP do usuário
        totp_config = SystemConfig.query.filter_by(key=f'totp.{user.id}').first()
        
        if not totp_config:
            flash('Configuração TOTP não encontrada. Por favor, configure novamente.', 'danger')
            return redirect(url_for('auth.two_factor', totp_setup=True))
        
        # Verificar código
        if not two_factor.verify_totp(user.id, code, totp_config.value):
            flash('Código de verificação inválido. Tente novamente.', 'danger')
            return redirect(url_for('auth.two_factor', method='totp'))
    
    else:
        # Verificar código email/SMS
        two_factor = TwoFactorAuth(current_app)
        
        if not two_factor.verify_token(user.id, code):
            flash('Código de verificação inválido ou expirado. Tente novamente.', 'danger')
            return redirect(url_for('auth.two_factor', method=method))
    
    # Verificação bem-sucedida
    
    # Marcar como verificado
    session['admin_2fa_verified'] = True
    
    # Fazer login
    remember_me = session.get('remember_me', False)
    login_user(user, remember=remember_me)
    
    # Registrar atividade
    log_action(
        user_id=user.id,
        action='login',
        module='auth',
        entity_type='User',
        entity_id=user.id,
        details=f'Login com verificação em duas etapas: {user.username}'
    )
    
    # Inicializar timestamp de atividade para timeout
    session['last_activity'] = datetime.now().timestamp()
    
    # Limpar variáveis de sessão
    session.pop('user_id_2fa', None)
    session.pop('remember_me', None)
    
    # Redirecionar para página solicitada ou inicial
    next_url = session.pop('next_url', None)
    if next_url:
        return redirect(next_url)
    
    flash('Verificação concluída com sucesso!', 'success')
    return redirect(url_for('index'))


@auth_bp.route('/verify-totp-setup', methods=['POST'])
def verify_totp_setup():
    """
    Verifica e salva a configuração TOTP.
    """
    # Verificar se há um usuário pendente de verificação
    if 'user_id_2fa' not in session or 'totp_secret_key' not in session:
        flash('Sessão de configuração expirada. Por favor, faça login novamente.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Obter código e chave secreta
    code = request.form.get('code')
    secret_key = session.get('totp_secret_key')
    
    if not code or not secret_key:
        flash('Por favor, digite o código de verificação.', 'danger')
        return redirect(url_for('auth.two_factor', totp_setup=True))
    
    # Obter dados do usuário
    user_id = session['user_id_2fa']
    user = User.query.get(user_id)
    
    if not user:
        flash('Usuário não encontrado. Por favor, faça login novamente.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Verificar código
    two_factor = TwoFactorAuth(current_app)
    
    if not two_factor.verify_totp(user.id, code, secret_key):
        flash('Código de verificação inválido. Verifique se o código está correto e tente novamente.', 'danger')
        return redirect(url_for('auth.two_factor', totp_setup=True))
    
    # Código válido, salvar configuração
    totp_config = SystemConfig.query.filter_by(key=f'totp.{user.id}').first()
    
    if totp_config:
        # Atualizar configuração existente
        totp_config.value = secret_key
        totp_config.updated_at = datetime.utcnow()
        totp_config.updated_by = user.id
    else:
        # Criar nova configuração
        totp_config = SystemConfig(
            key=f'totp.{user.id}',
            value=secret_key,
            description=f'TOTP secret key for user {user.username}',
            created_by=user.id,
            updated_by=user.id
        )
        db.session.add(totp_config)
    
    # Salvar alterações
    db.session.commit()
    
    # Limpar variável de sessão
    session.pop('totp_secret_key', None)
    
    # Registrar atividade
    log_action(
        user_id=user.id,
        action='configure',
        module='auth',
        entity_type='TOTP',
        details=f'Configuração de TOTP para usuário: {user.username}'
    )
    
    # Redirecionar para verificação
    flash('Aplicativo autenticador configurado com sucesso!', 'success')
    return redirect(url_for('auth.two_factor', method='totp'))


@auth_bp.route('/resend-two-factor-code', methods=['POST'])
def resend_two_factor_code():
    """
    Reenvia o código de verificação em duas etapas.
    """
    # Verificar se há um usuário pendente de verificação
    if 'user_id_2fa' not in session:
        return jsonify({
            'success': False,
            'message': 'Sessão de verificação expirada. Por favor, faça login novamente.'
        })
    
    # Obter método
    method = request.args.get('method')
    
    if not method or method not in ['email', 'sms']:
        return jsonify({
            'success': False,
            'message': 'Método de verificação inválido.'
        })
    
    # Obter dados do usuário
    user_id = session['user_id_2fa']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'Usuário não encontrado. Por favor, faça login novamente.'
        })
    
    # Reenviar código
    two_factor = TwoFactorAuth(current_app)
    
    if method == 'email':
        # Enviar código por e-mail
        success = two_factor.send_token_by_email(user.id, user.email)
    else:
        # Enviar código por SMS
        success = two_factor.send_token_by_sms(user.id, user.phone)
    
    if not success:
        return jsonify({
            'success': False,
            'message': f'Erro ao reenviar código de verificação por {method}. Tente outro método.'
        })
    
    return jsonify({
        'success': True,
        'message': 'Código reenviado com sucesso!'
    })


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Encerra a sessão do usuário.
    """
    if current_user.is_authenticated:
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='logout',
            module='auth',
            entity_type='User',
            entity_id=current_user.id,
            details=f'Logout de usuário: {current_user.username}'
        )
    
    # Limpar sessão
    session.clear()
    logout_user()
    
    flash('Você saiu do sistema com sucesso.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """
    Página para solicitação de redefinição de senha.
    """
    # Redirecionar se já estiver logado
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Importar formulário
    from .forms import ResetPasswordRequestForm
    form = ResetPasswordRequestForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Gerar token de redefinição
            from utils.admin_security import generate_reset_token
            token = generate_reset_token(user.id)
            
            # Enviar email com instruções (em produção)
            # Simulação: Mostrar token para teste
            flash(f'Um email com instruções para redefinição de senha foi enviado para {form.email.data}', 'info')
            session['reset_token_demo'] = token  # Apenas para demonstração
            
            # Log de atividade
            log_action(
                user_id=user.id,
                action='reset_password_request',
                module='auth',
                entity_type='User',
                entity_id=user.id,
                details=f'Solicitação de redefinição de senha para {user.email}'
            )
        else:
            # Mesmo que o email não exista, mostrar a mesma mensagem para evitar enumeração
            flash(f'Um email com instruções para redefinição de senha foi enviado para {form.email.data}', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form, current_year=datetime.now().year)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Página para redefinição de senha com token.
    """
    # Redirecionar se já estiver logado
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Verificar token
    from utils.admin_security import verify_reset_token
    user_id = verify_reset_token(token)
    
    if not user_id:
        flash('O link de redefinição é inválido ou expirou.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Importar formulário
    from .forms import ResetPasswordForm
    form = ResetPasswordForm()
    
    # Verificar se é admin para requisitos especiais de senha
    admin_mode = user.role == 'admin'
    
    if form.validate_on_submit():
        # Verificar requisitos de senha para administradores
        if admin_mode:
            from utils.admin_security import validate_admin_password
            valid, message = validate_admin_password(form.password.data)
            
            if not valid:
                flash(f'A senha não atende aos requisitos de segurança: {message}', 'danger')
                return render_template('auth/reset_password.html', form=form, token=token, admin_mode=admin_mode)
            
            # Verificar histórico de senhas
            from utils.admin_security import check_password_history
            if check_password_history(user.id, form.password.data):
                flash('Esta senha foi usada recentemente. Por favor, escolha uma senha diferente.', 'danger')
                return render_template('auth/reset_password.html', form=form, token=token, admin_mode=admin_mode)
        
        # Redefinir senha
        user.password_hash = generate_password_hash(form.password.data)
        
        # Registrar alteração de senha
        from utils.admin_security import log_password_change
        log_password_change(user.id, form.password.data)
        
        # Atualizar timestamp de alteração
        user.last_password_change = datetime.now()
        
        # Registrar atividade
        log_action(
            user_id=user.id,
            action='reset_password',
            module='auth',
            entity_type='User',
            entity_id=user.id,
            details='Redefinição de senha'
        )
        
        db.session.commit()
        
        flash('Sua senha foi redefinida com sucesso!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form, token=token, admin_mode=admin_mode, current_year=datetime.now().year)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Página para alteração de senha com verificações avançadas de segurança.
    """
    admin_mode = current_user.role == 'admin'
    settings = get_security_settings(current_app)
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verificar campos
        if not current_password or not new_password or not confirm_password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('auth/change_password.html', admin_mode=admin_mode)
        
        # Verificar senha atual
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Senha atual incorreta.', 'danger')
            return render_template('auth/change_password.html', admin_mode=admin_mode)
        
        # Verificar se as senhas são iguais
        if new_password != confirm_password:
            flash('A nova senha e a confirmação não são iguais.', 'danger')
            return render_template('auth/change_password.html', admin_mode=admin_mode)
        
        # Verificar se a nova senha é diferente da atual
        if current_password == new_password:
            flash('A nova senha deve ser diferente da senha atual.', 'danger')
            return render_template('auth/change_password.html', admin_mode=admin_mode)
        
        # Verificar requisitos adicionais para administradores
        if admin_mode:
            # Verificar complexidade da senha
            if settings['password_complexity']:
                valid, message = verify_password_complexity(new_password)
                if not valid:
                    flash(message, 'danger')
                    return render_template('auth/change_password.html', admin_mode=admin_mode)
            
            # Verificar histórico de senhas
            if settings['password_history_enabled']:
                # Gerar hash da nova senha
                new_password_hash = generate_password_hash(new_password)
                
                # Verificar se a senha já foi usada
                if not check_password_history(
                    current_user.id,
                    new_password_hash,
                    settings['password_history_count']
                ):
                    flash('A nova senha não pode ser uma das últimas senhas utilizadas.', 'danger')
                    return render_template('auth/change_password.html', admin_mode=admin_mode)
        
        # Atualizar senha
        current_user.password_hash = generate_password_hash(new_password)
        current_user.last_password_change = datetime.utcnow()
        
        # Adicionar ao histórico de senhas (para administradores)
        if admin_mode and settings['password_history_enabled']:
            add_password_to_history(
                current_user.id,
                current_user.password_hash,
                settings['password_history_count']
            )
        
        # Salvar alterações
        db.session.commit()
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='update',
            module='auth',
            entity_type='User',
            entity_id=current_user.id,
            details='Alteração de senha'
        )
        
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('index'))
    
    return render_template('auth/change_password.html', admin_mode=admin_mode)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Página de perfil do usuário.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Verificar campos
        if not name or not email:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('auth/profile.html')
        
        # Atualizar dados
        current_user.name = name
        current_user.email = email
        
        # Salvar alterações
        db.session.commit()
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='update',
            module='auth',
            entity_type='User',
            entity_id=current_user.id,
            details='Atualização de perfil'
        )
        
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')


@auth_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    """
    Página de gerenciamento de usuários (apenas administradores).
    """
    users = User.query.all()
    return render_template('auth/usuarios.html', users=users)
    
    
@auth_bp.route('/usuario/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_usuario():
    """
    Formulário para adicionar novo usuário.
    """
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        
        # Verificar se o usuário já existe
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('Usuário ou email já existe no sistema.', 'danger')
            return render_template('auth/form_usuario.html', user=None)
        
        # Verificar complexidade da senha
        if not verify_password_complexity(password):
            flash('A senha não atende aos requisitos de complexidade.', 'danger')
            return render_template('auth/form_usuario.html', user=None)
        
        # Criar novo usuário
        new_user = User(
            username=username,
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=is_admin,
            active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='create',
            module='auth',
            entity_type='User',
            entity_id=new_user.id,
            details=f'Criação de usuário: {username}'
        )
        
        flash(f'Usuário {username} criado com sucesso!', 'success')
        return redirect(url_for('auth.usuarios'))
    
    return render_template('auth/form_usuario.html', user=None)
    
    
@auth_bp.route('/usuario/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(user_id):
    """
    Formulário para editar usuário existente.
    """
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        is_admin = 'is_admin' in request.form
        
        # Verificar se o username/email já existe em outro usuário
        existing_user = User.query.filter(
            ((User.username == username) | (User.email == email)) & 
            (User.id != user_id)
        ).first()
        
        if existing_user:
            flash('Usuário ou email já existe no sistema.', 'danger')
            return render_template('auth/form_usuario.html', user=user)
        
        # Atualizar dados
        user.username = username
        user.name = name
        user.email = email
        user.is_admin = is_admin
        
        db.session.commit()
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='update',
            module='auth',
            entity_type='User',
            entity_id=user.id,
            details=f'Atualização de usuário: {username}'
        )
        
        flash(f'Usuário {username} atualizado com sucesso!', 'success')
        return redirect(url_for('auth.usuarios'))
    
    return render_template('auth/form_usuario.html', user=user)
    
    
@auth_bp.route('/usuario/<int:user_id>/excluir')
@login_required
@admin_required
def excluir_usuario(user_id):
    """
    Excluir um usuário do sistema.
    """
    user = User.query.get_or_404(user_id)
    
    # Não permitir excluir o próprio usuário
    if user.id == current_user.id:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('auth.usuarios'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    # Registrar atividade
    log_action(
        user_id=current_user.id,
        action='delete',
        module='auth',
        entity_type='User',
        entity_id=user_id,
        details=f'Exclusão de usuário: {username}'
    )
    
    flash(f'Usuário {username} excluído com sucesso!', 'success')
    return redirect(url_for('auth.usuarios'))
    
    
@auth_bp.route('/usuario/<int:user_id>/desativar')
@login_required
@admin_required
def desativar_usuario(user_id):
    """
    Desativar um usuário do sistema.
    """
    user = User.query.get_or_404(user_id)
    
    # Não permitir desativar o próprio usuário
    if user.id == current_user.id:
        flash('Você não pode desativar seu próprio usuário.', 'danger')
        return redirect(url_for('auth.usuarios'))
    
    user.active = False
    db.session.commit()
    
    # Registrar atividade
    log_action(
        user_id=current_user.id,
        action='update',
        module='auth',
        entity_type='User',
        entity_id=user.id,
        details=f'Desativação de usuário: {user.username}'
    )
    
    flash(f'Usuário {user.username} desativado com sucesso!', 'success')
    return redirect(url_for('auth.usuarios'))
    
    
@auth_bp.route('/usuario/<int:user_id>/ativar')
@login_required
@admin_required
def ativar_usuario(user_id):
    """
    Ativar um usuário do sistema.
    """
    user = User.query.get_or_404(user_id)
    user.active = True
    db.session.commit()
    
    # Registrar atividade
    log_action(
        user_id=current_user.id,
        action='update',
        module='auth',
        entity_type='User',
        entity_id=user.id,
        details=f'Ativação de usuário: {user.username}'
    )
    
    flash(f'Usuário {user.username} ativado com sucesso!', 'success')
    return redirect(url_for('auth.usuarios'))
    
    
@auth_bp.route('/usuario/<int:user_id>/reset-senha', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_usuario_senha(user_id):
    """
    Redefinir a senha de um usuário.
    """
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/reset_usuario_senha.html', user=user)
        
        # Verificar complexidade da senha
        if not verify_password_complexity(password):
            flash('A senha não atende aos requisitos de complexidade.', 'danger')
            return render_template('auth/reset_usuario_senha.html', user=user)
        
        # Atualizar senha
        user.password_hash = generate_password_hash(password)
        user.password_changed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Registrar atividade
        log_action(
            user_id=current_user.id,
            action='update',
            module='auth',
            entity_type='User',
            entity_id=user.id,
            details=f'Redefinição de senha para usuário: {user.username}'
        )
        
        flash(f'Senha do usuário {user.username} redefinida com sucesso!', 'success')
        return redirect(url_for('auth.usuarios'))
    
    return render_template('auth/reset_usuario_senha.html', user=user)


@auth_bp.route('/admin-security', methods=['GET'])
@login_required
@admin_required
@check_admin_security_requirements
def admin_security():
    """
    Página de segurança para administradores.
    """
    settings = get_security_settings(current_app)
    
    return render_template(
        'auth/admin_security.html',
        settings=settings
    )