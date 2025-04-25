from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Verificar se o email alex@zelopack.com.br já está em uso
    user_by_email = User.query.filter_by(email='alex@zelopack.com.br').first()
    
    # Verificar se o usuário Alex existe
    user_by_username = User.query.filter_by(username='Alex').first()
    
    if user_by_username:
        print(f"Usuário Alex já existe (ID: {user_by_username.id})")
        print(f"Email: {user_by_username.email}")
        print(f"Função: {user_by_username.role}")
        print(f"Ativo: {user_by_username.is_active}")
        # Atualizando a senha
        user_by_username.set_password('Alex123')
        db.session.commit()
        print("Senha atualizada para 'Alex123'")
    elif user_by_email:
        print(f"Usuário com email alex@zelopack.com.br já existe (username: {user_by_email.username})")
        print(f"ID: {user_by_email.id}")
        print(f"Função: {user_by_email.role}")
        print(f"Ativo: {user_by_email.is_active}")
        # Atualizando o nome de usuário e a senha
        print(f"Alterando username de '{user_by_email.username}' para 'Alex'")
        user_by_email.username = 'Alex'
        user_by_email.set_password('Alex123')
        db.session.commit()
        print("Usuário atualizado com sucesso!")
    else:
        print("Usuário Alex não existe. Criando novo usuário...")
        # Criar usuário Alex
        new_user = User(
            username='Alex',
            email='alex@zelopack.com.br',
            name='Alex',
            role='admin',
            is_active=True
        )
        # Definir senha para o novo usuário
        new_user.set_password('Alex123')
        # Salvar no banco de dados
        db.session.add(new_user)
        db.session.commit()
        print("Usuário Alex criado com sucesso!")