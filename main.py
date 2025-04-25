from flask import redirect, url_for
from app import app

@app.route('/')
def index():
    """Redirecionar para a página inicial do módulo de laudos."""
    return redirect(url_for('reports.index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
