#!/usr/bin/env python3
from app import app, db

def fix_database():
    print("Tentando restaurar a sessão do banco de dados...")
    with app.app_context():
        try:
            db.session.rollback()
            print("Sessão do banco de dados restaurada com sucesso!")
        except Exception as e:
            print(f"Erro ao restaurar a sessão: {e}")

if __name__ == "__main__":
    fix_database()