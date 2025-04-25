from app import app, db
from models import User
from flask_login import login_user
from datetime import datetime

# Rota customizada para fazer login como o usuário Alex direto
def login_as_alex():
    with app.app_context():
        user = User.query.filter_by(username='Alex').first()
        if user:
            print(f"Usuário Alex encontrado (ID: {user.id})")
            print(f"Email: {user.email}")
            print(f"Função: {user.role}")
            print(f"Ativo: {user.is_active}")
            
            # Atualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            return user
        else:
            print("Usuário Alex não encontrado!")
            return None

# Adicionando uma função de acesso simples para ser chamada via web
@app.route('/login-as-alex')
def login_alex_web():
    user = login_as_alex()
    if user:
        from flask import flash, redirect, url_for
        from flask_login import login_user
        
        login_user(user)
        flash(f'Bem-vindo, {user.name}! Login realizado com sucesso.', 'success')
        return redirect(url_for('dashboard.index'))
    else:
        from flask import flash, redirect, url_for
        flash('Usuário Alex não encontrado!', 'danger')
        return redirect(url_for('auth.login'))

# Registrar a nova rota
with app.app_context():
    print("Adicionando nova rota de login para Alex")
    # Já está registrado no decorator acima