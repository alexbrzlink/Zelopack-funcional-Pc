import os
from flask import Flask
from extensions import db

# Criar aplicau00e7u00e3o Flask
app = Flask(__name__)

# Configurau00e7u00e3o do banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', 'postgresql://postgres:190321@localhost:5432/zelopack_db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar o banco de dados
db.init_app(app)

# Rota de teste
@app.route('/')
def index():
    return 'Conexu00e3o com o banco de dados estabelecida com sucesso!'

# Criar tabelas e inicializar banco de dados
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
