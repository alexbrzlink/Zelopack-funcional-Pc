from app import db
from models_temp import User, Report

# Criar tabelas
with app.app_context():
    db.create_all()
    
    # Criar usuário admin
    admin = User(
        username='admin',
        email='admin@zelopack.com',
        name='Administrador',
        role='admin'
    )
    admin.set_password('Zelopack19')
    db.session.add(admin)
    db.session.commit()

print('Banco de dados inicializado com sucesso!')
