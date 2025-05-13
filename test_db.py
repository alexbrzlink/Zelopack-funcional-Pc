from flask import Flask
from extensions import db
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
db.init_app(app)

class TestModel(db.Model):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Testando a conexão
def test_connection():
    try:
        with app.app_context():
            db.create_all()
            print("Conexão com o banco de dados estabelecida com sucesso!")
            # Criar um registro de teste
            test_record = TestModel(name="Teste")
            db.session.add(test_record)
            db.session.commit()
            print("Registro de teste criado com sucesso!")
            # Ler o registro
            record = TestModel.query.first()
            print(f"Registro lido: {record.name}")
    except Exception as e:
        print(f"Erro ao testar conexão: {str(e)}")

if __name__ == "__main__":
    test_connection()
