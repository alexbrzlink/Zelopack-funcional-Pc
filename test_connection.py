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

# Modelo simples para teste
class TestModel(db.Model):
    __tablename__ = 'test_connection'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Testar conexu00e3o
with app.app_context():
    # Criar tabelas
    db.create_all()
    
    # Inserir um registro de teste
    test = TestModel(name="Teste de conexu00e3o")
    db.session.add(test)
    db.session.commit()
    
    # Verificar se o registro foi inserido
    result = TestModel.query.filter_by(name="Teste de conexu00e3o").first()
    if result:
        print("\n\n=== CONEXU00c3O COM O BANCO DE DADOS ESTABELECIDA COM SUCESSO! ===\n")
        print(f"Registro inserido: ID={result.id}, Nome={result.name}\n")
    else:
        print("\n\n=== ERRO: Nu00e3o foi possu00edvel inserir ou recuperar dados do banco ===\n")
