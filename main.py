from flask import redirect, url_for
from flask_login import current_user
from app import app

# Importar a rota de login para Alex
from login_as_alex import login_alex_web

@app.route('/')
def index():
    """Redirecionar para a página inicial ou login se não estiver autenticado."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('dashboard.index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
