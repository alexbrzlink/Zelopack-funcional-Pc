"""
Script para atualizar o banco de dados com os novos modelos do painel de controle.
"""
from app import app, db
import models

def update_database():
    """Atualiza o banco de dados com os novos modelos."""
    print("Atualizando o banco de dados com os novos modelos...")
    
    # Criar as tabelas se não existirem
    try:
        with app.app_context():
            db.create_all()
            print("Banco de dados atualizado com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar o banco de dados: {str(e)}")

if __name__ == "__main__":
    update_database()