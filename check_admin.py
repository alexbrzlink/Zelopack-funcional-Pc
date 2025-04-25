from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    print(f'Usuário admin existe: {user is not None}')
    if user:
        print(f'Senha válida: {user.check_password("Alex")}')
        print(f'Nome: {user.name}')
        print(f'Email: {user.email}')
        print(f'Ativo: {user.is_active}')
