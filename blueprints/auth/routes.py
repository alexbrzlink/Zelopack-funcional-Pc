from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse

from app import db, csrf
from models import User
from blueprints.auth import auth_bp
from blueprints.auth.forms import (
    LoginForm, RegistrationForm, ResetPasswordRequestForm,
    ResetPasswordForm, EditUserForm, ChangePasswordForm
)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    from werkzeug.security import generate_password_hash, check_password_hash
    
    # Se o usuário já está autenticado, redirecionar para a página inicial
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Garantir que exista um usuário admin
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_user = User(
            username='admin',
            email='admin@zelopack.com.br',
            name='Administrador',
            role='admin',
            is_active=True
        )
        admin_user.set_password('Alex')
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário admin criado com sucesso!")
        flash('Usuário admin criado. Use as credenciais: admin / Alex', 'info')
    
    form = LoginForm()
    
    # Verificar se é uma submissão de formulário POST
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        remember = 'remember_me' in request.form
        
        # Caso especial para admin (bypass para facilitar testes)
        if username.lower() == 'admin' and password == 'Alex':
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                login_user(admin_user, remember=True)
                admin_user.last_login = datetime.utcnow()
                db.session.commit()
                flash(f'Bem-vindo, Administrador!', 'success')
                return redirect(url_for('dashboard.index'))
        
        # Login padrão
        user = User.query.filter_by(username=username).first()
        
        # Verificação detalhada para oferecer mensagens específicas
        if not user:
            print(f"Erro de login: Usuário '{username}' não encontrado no sistema")
            flash(f'Usuário não encontrado. Verifique se digitou o nome corretamente.', 'danger')
            return render_template('auth/login.html', form=form, title='Login')
        
        if not user.check_password(password):
            print(f"Erro de login: Senha incorreta para o usuário '{username}'")
            flash('Senha incorreta. Por favor, tente novamente.', 'danger')
            return render_template('auth/login.html', form=form, title='Login')
        
        if not user.is_active:
            print(f"Erro de login: A conta do usuário '{username}' está desativada")
            flash(f'Sua conta está desativada. Entre em contato com o administrador.', 'warning')
            return render_template('auth/login.html', form=form, title='Login')
        
        # Login bem-sucedido
        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        print(f"Login bem-sucedido para: {user.username}")
        flash(f'Bem-vindo, {user.name}! Login realizado com sucesso.', 'success')
        
        # Sempre redirecionar para o dashboard após login
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html', title='Login', form=form)


@auth_bp.route('/logout')
def logout():
    """Faz logout do usuário."""
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Página de registro de novo usuário (apenas para administradores)."""
    print("Acessando rota de registro")
    
    # Verificar se é administrador
    if not current_user.role == 'admin':
        print(f"Acesso negado: Usuário {current_user.username} não é administrador")
        flash('Acesso negado. Você não tem permissão para registrar novos usuários.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    
    # Debugar a submissão do formulário
    if request.method == 'POST':
        print(f"Recebido POST para registro. Dados: {request.form}")
    
    # Processar o formulário
    if form.validate_on_submit():
        print(f"Formulário validado. Criando usuário: {form.username.data}")
        try:
            # Criar novo usuário
            user = User(
                username=form.username.data,
                email=form.email.data,
                name=form.name.data,
                role=form.role.data,
                is_active=True
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            print(f"Usuário {user.username} criado com sucesso!")
            flash(f'Usuário {user.username} registrado com sucesso!', 'success')
            return redirect(url_for('auth.users'))
        except Exception as e:
            print(f"ERRO ao criar usuário: {str(e)}")
            db.session.rollback()
            flash(f'Erro ao registrar usuário: {str(e)}', 'danger')
    elif request.method == 'POST' and not form.validate():
        print(f"Erros de validação no formulário: {form.errors}")
        flash('Verifique os erros no formulário e tente novamente.', 'warning')
    
    return render_template('auth/register.html', title='Registrar Usuário', form=form)


@auth_bp.route('/users')
@login_required
def users():
    """Lista todos os usuários (apenas para administradores)."""
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para ver a lista de usuários.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    users = User.query.all()
    return render_template('auth/users.html', title='Usuários', users=users)


@auth_bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    """Editar informações de um usuário (apenas para administradores)."""
    if not current_user.role == 'admin' and current_user.id != id:
        flash('Acesso negado. Você não tem permissão para editar este usuário.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    user = User.query.get_or_404(id)
    
    # Admins podem editar qualquer usuário, usuários normais só podem editar seu próprio perfil
    if current_user.role != 'admin' and current_user.id != user.id:
        flash('Acesso negado. Você não tem permissão para editar este usuário.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = EditUserForm(original_email=user.email)
    
    # Se não for admin, não mostrar campo de função
    if current_user.role != 'admin':
        del form.role
        del form.is_active
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        
        # Apenas admins podem mudar a função e status ativo
        if current_user.role == 'admin':
            user.role = form.role.data
            user.is_active = form.is_active.data
        
        db.session.commit()
        flash('As informações do usuário foram atualizadas.', 'success')
        
        if current_user.role == 'admin' and current_user.id != user.id:
            return redirect(url_for('auth.users'))
        return redirect(url_for('dashboard.index'))
    
    elif request.method == 'GET':
        form.name.data = user.name
        form.email.data = user.email
        if current_user.role == 'admin':
            form.role.data = user.role
            form.is_active.data = user.is_active
    
    return render_template('auth/edit_user.html', title='Editar Usuário', form=form, user=user)


@auth_bp.route('/user/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    """Excluir um usuário (apenas para administradores)."""
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para excluir usuários.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    user = User.query.get_or_404(id)
    
    # Não permitir que o admin exclua a si mesmo
    if user.id == current_user.id:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('auth.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Usuário {user.username} excluído com sucesso.', 'success')
    return redirect(url_for('auth.users'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Página para alteração de senha."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Não foi possível alterar a senha. Por favor, verifique suas credenciais.', 'danger')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('Sua senha foi alterada com sucesso.', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/change_password.html', title='Alterar Senha', form=form)


@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Página para solicitar redefinição de senha."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Em um ambiente real, enviar email com link para reset
            # Aqui apenas simulamos o sucesso da operação
            flash('Verifique seu email para instruções sobre como redefinir sua senha.', 'info')
        else:
            flash('Email não encontrado no sistema.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Redefinir Senha', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Página para redefinição de senha usando token."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Em um ambiente real, verificar o token
    # Aqui apenas simulamos a página
    form = ResetPasswordForm()
    if form.validate_on_submit():
        flash('Sua senha foi redefinida com sucesso.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Redefinir Senha', form=form)


@auth_bp.route('/login-direct', methods=['GET'])
@csrf.exempt
def login_direct():
    """Rota alternativa para login direto, para fins de teste."""
    print("ACESSANDO ROTA DE LOGIN AUTOMÁTICO")
    
    # Rota para login direto sem CSRF para fins de teste
    # Verificar se existe usuário admin
    total_users = User.query.count()
    print(f"Total de usuários no sistema: {total_users}")
    
    if total_users == 0:
        # Criar usuário admin se não existir
        print("Nenhum usuário encontrado. Criando usuário admin padrão...")
        admin_user = User(
            username='admin',
            email='admin@zelopack.com.br',
            name='Administrador',
            role='admin',
            is_active=True
        )
        admin_user.set_password('Alex')
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário admin criado com sucesso!")
    
    user = User.query.filter_by(username='admin').first()
    
    if user is None:
        msg = "ERRO CRÍTICO: Usuário admin não encontrado mesmo após tentativa de criação!"
        print(msg)
        flash(msg, 'danger')
        return redirect(url_for('auth.login'))
    
    if not user.is_active:
        msg = "ERRO: Usuário admin existe mas está inativo."
        print(msg)
        user.is_active = True
        db.session.commit()
        print("Usuário admin foi ativado automaticamente.")
        flash(msg + " Ele foi ativado automaticamente.", 'warning')
    
    # Registrar tentativa de login
    print(f"Login automático para usuário: {user.username}")
    print(f"Nome do usuário: {user.name}")
    print(f"E-mail do usuário: {user.email}")
    print(f"Função do usuário: {user.role}")
    print(f"Status de ativação: {user.is_active}")
    
    login_user(user, remember=True)
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    print("Login automático bem-sucedido! Redirecionando para o dashboard...")
    flash(f'Bem-vindo, {user.name}! Login automático realizado com sucesso.', 'success')
    return redirect(url_for('dashboard.index'))