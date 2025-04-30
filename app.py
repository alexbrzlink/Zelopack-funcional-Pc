from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_caching import Cache

# Inicialização do app e das extensões
app = Flask(__name__)
app.secret_key = 'zelopack-secret-key'  # Para ambientes de produção, use os.environ.get('SECRET_KEY')
app.config['SESSION_COOKIE_SECURE'] = True

# Inicialização do Socket.IO
socketio = SocketIO(app)

# Inicialização do Cache
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Importar e registrar os blueprints
from editor import editor_bp
from technical import technical_bp

app.register_blueprint(editor_bp)
app.register_blueprint(technical_bp)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)