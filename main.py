from flask import redirect, url_for, flash
from flask_login import current_user, login_user
from app import app, db, socketio

# Importar eventos em tempo real para editor de documentos
from blueprints.documents import events

@app.route('/')
def index():
    """Redirecionar para a página inicial ou login se não estiver autenticado."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('dashboard.index'))

@app.route('/login-alex')
def login_alex():
    """Rota para login automático do usuário Alex"""
    from models import User
    from datetime import datetime
    
    # Buscar o usuário Alex diretamente
    user = User.query.filter_by(username='Alex').first()
    
    if user:
        # Atualizar o último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Fazer login do usuário
        login_user(user)
        flash(f'Bem-vindo, {user.name}! Login automático realizado com sucesso.', 'success')
    else:
        flash('Erro: Usuário Alex não encontrado!', 'danger')
    
    return redirect(url_for('dashboard.index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
