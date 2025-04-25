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
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Verificar se existe pelo menos um usuário admin (para fins de teste/dev)
    if User.query.count() == 0:
        # Criar usuário admin padrão para testes
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
        print(f"ATENÇÃO: Usuário de teste criado! Login: admin / Senha: Alex")
        flash('Usuário de teste criado! Login: admin / Senha: Alex', 'info')
    
    # Verificar se o usuário admin existe e está com senha correta
    admin = User.query.filter_by(username='admin').first()
    if admin:
        # Testar senha para garantir que está funcionando
        test_password = 'Alex'
        test_result = admin.check_password(test_password)
        direct_test = check_password_hash(admin.password_hash, test_password)
        
        print(f"Verificação da senha 'Alex' para admin: {test_result}")
        print(f"Verificação direta de hash para admin: {direct_test}")
        
        # Se a verificação da senha do admin falhar, redefinir
        if not test_result:
            print("ERRO: A senha do admin não está correta. Redefinindo...")
            admin.set_password('Alex')
            db.session.commit()
            flash('A senha do usuário admin foi redefinida para "Alex".', 'warning')
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data if form.username.data else ""
        password = form.password.data if form.password.data else ""
        
        # Logging para debug
        print(f"Tentativa de login: Usuário={username}, Senha={'*' * len(password)}")
        
        # Validação especial para admin
        if username.lower() == 'admin' and password == 'Alex':
            # Login direto para admin
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                login_user(admin_user, remember=True)
                admin_user.last_login = datetime.utcnow()
                db.session.commit()
                flash(f'Bem-vindo, {admin_user.name}! Login direto como admin realizado com sucesso.', 'success')
                return redirect(url_for('dashboard.index'))
        
        # Processo normal de login
        user = User.query.filter_by(username=username).first()
        
        if user is None:
            print(f"Erro de login: Usuário '{username}' não encontrado")
            flash(f"O usuário '{username}' não está cadastrado. Verifique se digitou corretamente.", 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.check_password(password):
            print(f"Erro de login: Senha incorreta para o usuário '{username}'")
            # Caso adicional para admin
            if username.lower() == 'admin':
                flash(f"Senha incorreta para o usuário admin. A senha correta é 'Alex'.", 'danger')
            else:
                flash(f"Senha incorreta para o usuário '{username}'. Por favor, tente novamente.", 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            print(f"Erro de login: Usuário '{username}' está inativo")
            flash(f"Esta conta ({username}) está desativada. Entre em contato com o administrador.", 'warning')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        print(f"Login bem-sucedido para o usuário '{username}'")
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Redirecionar para a página que o usuário estava tentando acessar
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
            
        flash(f'Bem-vindo, {user.name}! Login realizado com sucesso.', 'success')
        return redirect(next_page)
    
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
    if not current_user.role == 'admin':
        flash('Acesso negado. Você não tem permissão para registrar novos usuários.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            name=form.name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash(f'Usuário {user.username} registrado com sucesso!', 'success')
        return redirect(url_for('auth.users'))
    
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
            flash('Senha atual incorreta.', 'danger')
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