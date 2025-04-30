import logging
from werkzeug.security import generate_password_hash
from app import app, db
from models import User

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_admin_user():
    """Reseta o usuário admin com senha 'admin123'"""
    with app.app_context():
        # Verificar se o usuário admin existe
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            logger.info("Resetando senha do usuário admin")
            admin.password_hash = generate_password_hash('admin123')
            admin.login_attempts = 0
            admin.is_locked = False
            admin.is_active = True
            db.session.commit()
            logger.info("Senha do admin resetada com sucesso para 'admin123'")
        else:
            logger.info("Criando novo usuário admin")
            new_admin = User(
                username='admin',
                email='admin@zelopack.com',
                name='Administrador',
                role='admin',
                is_active=True
            )
            new_admin.password_hash = generate_password_hash('admin123')
            db.session.add(new_admin)
            db.session.commit()
            logger.info("Novo usuário admin criado com senha 'admin123'")

if __name__ == "__main__":
    reset_admin_user()
    print("Usuário admin resetado/criado com sucesso!")
    print("Username: admin")
    print("Senha: admin123")