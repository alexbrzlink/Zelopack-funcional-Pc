"""\nTeste automatizado das principais funcionalidades do sistema ZeloPack\n"""

import os
import sys
import logging
from datetime import datetime
from app import app
from extensions import db
from models import User, Report, TechnicalDocument, Supplier
from werkzeug.security import generate_password_hash

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Resultados dos testes
results = {
    'success': [],
    'failure': []
}

def log_success(message):
    """Registra um teste bem-sucedido"""
    logger.info(f"✅ SUCESSO: {message}")
    results['success'].append(message)

def log_failure(message, error=None):
    """Registra um teste falho"""
    if error:
        logger.error(f"❌ FALHA: {message}. Erro: {str(error)}")
        results['failure'].append(f"{message}. Erro: {str(error)}")
    else:
        logger.error(f"❌ FALHA: {message}")
        results['failure'].append(message)

def test_database_connection():
    """Testa a conexu00e3o com o banco de dados"""
    try:
        with app.app_context():
            # Verificar se pode executar uma query simples
            result = db.session.execute(db.text("SELECT 1")).scalar()
            if result == 1:
                log_success("Conexu00e3o com o banco de dados estabelecida com sucesso")
                return True
            else:
                log_failure("Conexu00e3o com o banco de dados falhou")
                return False
    except Exception as e:
        log_failure("Erro ao conectar ao banco de dados", e)
        return False

def test_user_management():
    """Testa operau00e7u00f5es de gerenciamento de usuu00e1rios"""
    try:
        with app.app_context():
            # Verificar se o usuu00e1rio admin existe
            admin = User.query.filter_by(username='admin').first()
            if admin:
                log_success("Usuu00e1rio admin encontrado no banco de dados")
            else:
                log_failure("Usuu00e1rio admin nu00e3o encontrado")
                
            # Criar um novo usuu00e1rio de teste
            test_user = User.query.filter_by(username='teste_automatizado').first()
            if test_user:
                db.session.delete(test_user)
                db.session.commit()
                
            new_user = User(
                username='teste_automatizado',
                email='teste@zelopack.com',
                name='Usuario de Teste',
                role='analista'
            )
            new_user.password_hash = generate_password_hash('teste123')
            db.session.add(new_user)
            db.session.commit()
            
            # Verificar se o usuu00e1rio foi criado
            created_user = User.query.filter_by(username='teste_automatizado').first()
            if created_user:
                log_success("Criado novo usuu00e1rio no banco de dados")
                
                # Atualizar o usuu00e1rio
                created_user.name = 'Nome Atualizado'
                db.session.commit()
                
                # Verificar se o nome foi atualizado
                updated_user = User.query.filter_by(username='teste_automatizado').first()
                if updated_user.name == 'Nome Atualizado':
                    log_success("Atualizado usuu00e1rio no banco de dados")
                else:
                    log_failure("Falha ao atualizar usuu00e1rio")
                
                # Excluir o usuu00e1rio de teste
                db.session.delete(created_user)
                db.session.commit()
                
                # Verificar se o usuu00e1rio foi excluu00eddo
                deleted_user = User.query.filter_by(username='teste_automatizado').first()
                if not deleted_user:
                    log_success("Excluu00eddo usuu00e1rio do banco de dados")
                else:
                    log_failure("Falha ao excluir usuu00e1rio")
            else:
                log_failure("Falha ao criar novo usuu00e1rio")
    except Exception as e:
        log_failure("Erro nos testes de gerenciamento de usuu00e1rios", e)

def test_supplier_management():
    """Testa operau00e7u00f5es de gerenciamento de fornecedores"""
    try:
        with app.app_context():
            # Criar um novo fornecedor de teste
            test_supplier = Supplier.query.filter_by(name='Fornecedor Teste Automatizado').first()
            if test_supplier:
                db.session.delete(test_supplier)
                db.session.commit()
                
            new_supplier = Supplier(
                name='Fornecedor Teste Automatizado',
                contact_name='Contato Teste',
                email='contato@fornecedor-teste.com',
                phone='(11) 99999-9999'
            )
            db.session.add(new_supplier)
            db.session.commit()
            
            # Verificar se o fornecedor foi criado
            created_supplier = Supplier.query.filter_by(name='Fornecedor Teste Automatizado').first()
            if created_supplier:
                log_success("Criado novo fornecedor no banco de dados")
                
                # Atualizar o fornecedor
                created_supplier.contact_name = 'Contato Atualizado'
                db.session.commit()
                
                # Verificar se o nome foi atualizado
                updated_supplier = Supplier.query.filter_by(name='Fornecedor Teste Automatizado').first()
                if updated_supplier.contact_name == 'Contato Atualizado':
                    log_success("Atualizado fornecedor no banco de dados")
                else:
                    log_failure("Falha ao atualizar fornecedor")
                
                # Excluir o fornecedor de teste
                db.session.delete(created_supplier)
                db.session.commit()
                
                # Verificar se o fornecedor foi excluu00eddo
                deleted_supplier = Supplier.query.filter_by(name='Fornecedor Teste Automatizado').first()
                if not deleted_supplier:
                    log_success("Excluu00eddo fornecedor do banco de dados")
                else:
                    log_failure("Falha ao excluir fornecedor")
            else:
                log_failure("Falha ao criar novo fornecedor")
    except Exception as e:
        log_failure("Erro nos testes de gerenciamento de fornecedores", e)

def test_report_management():
    """Testa operau00e7u00f5es de gerenciamento de laudos/relatu00f3rios"""
    try:
        with app.app_context():
            # Criar um novo relatu00f3rio de teste
            test_report = Report.query.filter_by(title='Relatu00f3rio Teste Automatizado').first()
            if test_report:
                db.session.delete(test_report)
                db.session.commit()
                
            # Criar arquivo de teste
            file_content = b"Conteudo de teste para o arquivo PDF"
            test_file = FileStorage(
                stream=BytesIO(file_content),
                filename="teste.pdf",
                content_type="application/pdf"
            )
            
            # Criar direu00e7u00f5es para salvar o arquivo
            upload_dir = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'reports')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, 'teste_automatizado.pdf')
            
            # Salvar o arquivo
            with open(file_path, 'wb') as f:
                f.write(file_content)
                
            # Criar o relatu00f3rio no banco de dados
            new_report = Report(
                title='Relatu00f3rio Teste Automatizado',
                description='Descriu00e7u00e3o de teste',
                filename='teste_automatizado.pdf',
                original_filename='teste.pdf',
                file_path=file_path,
                file_type='application/pdf',
                file_size=len(file_content),
                status='pendente',
                upload_date=datetime.utcnow()
            )
            db.session.add(new_report)
            db.session.commit()
            
            # Verificar se o relatu00f3rio foi criado
            created_report = Report.query.filter_by(title='Relatu00f3rio Teste Automatizado').first()
            if created_report:
                log_success("Criado novo relatu00f3rio no banco de dados")
                
                # Atualizar o relatu00f3rio
                created_report.status = 'aprovado'
                db.session.commit()
                
                # Verificar se o status foi atualizado
                updated_report = Report.query.filter_by(title='Relatu00f3rio Teste Automatizado').first()
                if updated_report.status == 'aprovado':
                    log_success("Atualizado relatu00f3rio no banco de dados")
                else:
                    log_failure("Falha ao atualizar relatu00f3rio")
                
                # Excluir o relatu00f3rio de teste
                db.session.delete(created_report)
                db.session.commit()
                
                # Verificar se o relatu00f3rio foi excluu00eddo
                deleted_report = Report.query.filter_by(title='Relatu00f3rio Teste Automatizado').first()
                if not deleted_report:
                    log_success("Excluu00eddo relatu00f3rio do banco de dados")
                else:
                    log_failure("Falha ao excluir relatu00f3rio")
                    
                # Limpar arquivo temporário
                if os.path.exists(file_path):
                    os.remove(file_path)
            else:
                log_failure("Falha ao criar novo relatu00f3rio")
    except Exception as e:
        log_failure("Erro nos testes de gerenciamento de relatu00f3rios", e)

def test_technical_document_management():
    """Testa operau00e7u00f5es de gerenciamento de documentos tu00e9cnicos"""
    try:
        with app.app_context():
            # Criar um novo documento de teste
            test_doc = TechnicalDocument.query.filter_by(title='Documento Teste Automatizado').first()
            if test_doc:
                db.session.delete(test_doc)
                db.session.commit()
                
            # Criar arquivo de teste
            file_content = b"Conteudo de teste para o documento tecnico"
            
            # Criar direu00e7u00f5es para salvar o arquivo
            upload_dir = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'documents')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, 'doc_teste_automatizado.docx')
            
            # Salvar o arquivo
            with open(file_path, 'wb') as f:
                f.write(file_content)
                
            # Criar o documento no banco de dados
            admin = User.query.filter_by(username='admin').first()
            new_doc = TechnicalDocument(
                title='Documento Teste Automatizado',
                description='Descriu00e7u00e3o de teste',
                filename='doc_teste_automatizado.docx',
                original_filename='teste.docx',
                file_path=file_path,
                file_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                file_size=len(file_content),
                document_type='POP',
                status='rascunho',
                created_by=admin.id if admin else 1
            )
            db.session.add(new_doc)
            db.session.commit()
            
            # Verificar se o documento foi criado
            created_doc = TechnicalDocument.query.filter_by(title='Documento Teste Automatizado').first()
            if created_doc:
                log_success("Criado novo documento tu00e9cnico no banco de dados")
                
                # Atualizar o documento
                created_doc.status = 'publicado'
                db.session.commit()
                
                # Verificar se o status foi atualizado
                updated_doc = TechnicalDocument.query.filter_by(title='Documento Teste Automatizado').first()
                if updated_doc.status == 'publicado':
                    log_success("Atualizado documento tu00e9cnico no banco de dados")
                else:
                    log_failure("Falha ao atualizar documento tu00e9cnico")
                
                # Excluir o documento de teste
                db.session.delete(created_doc)
                db.session.commit()
                
                # Verificar se o documento foi excluu00eddo
                deleted_doc = TechnicalDocument.query.filter_by(title='Documento Teste Automatizado').first()
                if not deleted_doc:
                    log_success("Excluu00eddo documento tu00e9cnico do banco de dados")
                else:
                    log_failure("Falha ao excluir documento tu00e9cnico")
                    
                # Limpar arquivo temporário
                if os.path.exists(file_path):
                    os.remove(file_path)
            else:
                log_failure("Falha ao criar novo documento tu00e9cnico")
    except Exception as e:
        log_failure("Erro nos testes de gerenciamento de documentos tu00e9cnicos", e)

def generate_report():
    """Gera um relatu00f3rio de testes"""
    total = len(results['success']) + len(results['failure'])
    success_rate = (len(results['success']) / total) * 100 if total > 0 else 0
    
    report = f"""\n====================================================\n
        RELATU00d3RIO DE TESTES - ZeloPack Industria\n
====================================================\n
Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n
Resumo:\n
- Total de testes: {total}\n- Sucessos: {len(results['success'])} ({success_rate:.1f}%)\n- Falhas: {len(results['failure'])} ({100-success_rate:.1f}%)\n
----------------------------------------------------\n\nTestes bem-sucedidos:\n"""
    
    for i, success in enumerate(results['success'], 1):
        report += f"\n{i}. \u2705 {success}"
    
    report += "\n\n----------------------------------------------------\n\nFalhas encontradas:\n"
    
    if results['failure']:
        for i, failure in enumerate(results['failure'], 1):
            report += f"\n{i}. \u274c {failure}"
    else:
        report += "\n\u2728 Nenhuma falha encontrada! \u2728"
    
    report += "\n\n====================================================\n"
    
    # Salvar relatu00f3rio em arquivo
    with open('relatorio_testes.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report

if __name__ == '__main__':
    print("\n\u2699\ufe0f Iniciando testes automatizados do sistema ZeloPack\n")
    
    # Executar testes
    db_ok = test_database_connection()
    if db_ok:
        test_user_management()
        test_supplier_management()
        test_report_management()
        test_technical_document_management()
    
    # Gerar relatu00f3rio
    report = generate_report()
    print("\n" + report)
    print(f"\nRelatu00f3rio salvo em: {os.path.abspath('relatorio_testes.txt')}")
