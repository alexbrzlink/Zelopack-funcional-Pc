"""
Teste automatizado das principais funcionalidades do sistema ZeloPack
"""

import os
import logging
from datetime import datetime
from app import app
from extensions import db
from models import User, Report, TechnicalDocument, Supplier
from werkzeug.security import generate_password_hash

# Configurau00e7u00e3o do logger
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
                
            # Contar nu00famero de usuu00e1rios
            users_count = User.query.count()
            log_success(f"Sistema possui {users_count} usuu00e1rios cadastrados")
            
            # Testar consulta de permissu00f5es
            if admin and hasattr(admin, 'role'):
                log_success(f"Usuu00e1rio admin tem a funu00e7u00e3o: {admin.role}")
    except Exception as e:
        log_failure("Erro nos testes de gerenciamento de usuu00e1rios", e)

def test_supplier_management():
    """Testa operau00e7u00f5es de gerenciamento de fornecedores"""
    try:
        with app.app_context():
            # Contar nu00famero de fornecedores
            suppliers_count = Supplier.query.count()
            log_success(f"Sistema possui {suppliers_count} fornecedores cadastrados")
            
            # Verificar primeiro fornecedor
            supplier = Supplier.query.first()
            if supplier:
                log_success(f"Fornecedor encontrado: {supplier.name}")
                # Verificar campos do fornecedor
                supplier_fields = [c.name for c in Supplier.__table__.columns]
                log_success(f"Campos do fornecedor: {', '.join(supplier_fields)}")
            else:
                log_failure("Nenhum fornecedor encontrado no banco de dados")
    except Exception as e:
        log_failure("Erro nos testes de gerenciamento de fornecedores", e)

def test_report_management():
    """Testa operau00e7u00f5es de gerenciamento de laudos/relatu00f3rios"""
    try:
        with app.app_context():
            # Contar nu00famero de relatu00f3rios
            reports_count = Report.query.count()
            log_success(f"Sistema possui {reports_count} relatu00f3rios cadastrados")
            
            # Verificar campos dos relatu00f3rios
            report_fields = [c.name for c in Report.__table__.columns]
            log_success(f"Campos dos relatu00f3rios: {', '.join(report_fields)}")
    except Exception as e:
        log_failure("Erro nos testes de gerenciamento de relatu00f3rios", e)

def test_document_management():
    """Testa operau00e7u00f5es de gerenciamento de documentos tu00e9cnicos"""
    try:
        with app.app_context():
            # Contar nu00famero de documentos
            docs_count = TechnicalDocument.query.count()
            log_success(f"Sistema possui {docs_count} documentos tu00e9cnicos cadastrados")
            
            # Verificar campos dos documentos
            doc_fields = [c.name for c in TechnicalDocument.__table__.columns]
            log_success(f"Campos dos documentos: {', '.join(doc_fields)}")
    except Exception as e:
        log_failure("Erro nos testes de gerenciamento de documentos tu00e9cnicos", e)

def generate_report():
    """Gera um relatu00f3rio de testes"""
    total = len(results['success']) + len(results['failure'])
    success_rate = (len(results['success']) / total) * 100 if total > 0 else 0
    
    report = f"""
====================================================

        RELATÓRIO DE TESTES - ZeloPack Industria

====================================================

Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Resumo:

- Total de testes: {total}
- Sucessos: {len(results['success'])} ({success_rate:.1f}%)
- Falhas: {len(results['failure'])} ({100-success_rate:.1f}%)

----------------------------------------------------

Testes bem-sucedidos:
"""
    
    for i, success in enumerate(results['success'], 1):
        report += f"\n{i}. ✅ {success}"
    
    report += "\n\n----------------------------------------------------\n\nFalhas encontradas:\n"
    
    if results['failure']:
        for i, failure in enumerate(results['failure'], 1):
            report += f"\n{i}. ❌ {failure}"
    else:
        report += "\n✨ Nenhuma falha encontrada! ✨"
    
    report += "\n\n====================================================\n"
    
    # Salvar relatu00f3rio em arquivo
    try:
        with open('relatorio_testes.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        log_success(f"Relatu00f3rio salvo em: {os.path.abspath('relatorio_testes.txt')}")
    except Exception as e:
        log_failure("Erro ao salvar relatu00f3rio", e)
    
    return report

def check_routes():
    """Verifica se as principais rotas estu00e3o registradas"""
    with app.app_context():
        try:
            # Verificar rotas registradas
            routes = []
            for rule in app.url_map.iter_rules():
                route = {
                    'endpoint': rule.endpoint,
                    'methods': ','.join(rule.methods),
                    'path': str(rule)
                }
                routes.append(route)
            
            log_success(f"Sistema possui {len(routes)} rotas registradas")
            
            # Verificar rotas principais - usando endpoints corretos
            main_routes = ['index', 'auth.login', 'dashboard.index', 'documents.index', 'documents.search']
            for route in main_routes:
                found = any(r['endpoint'] == route for r in routes)
                if found:
                    log_success(f"Rota '{route}' encontrada")
                else:
                    log_failure(f"Rota '{route}' não encontrada")
                    
        except Exception as e:
            log_failure("Erro ao verificar rotas", e)

if __name__ == '__main__':
    print("\n⚙️ Iniciando testes automatizados do sistema ZeloPack\n")
    
    # Executar testes
    db_ok = test_database_connection()
    if db_ok:
        test_user_management()
        test_supplier_management()
        test_report_management()
        test_document_management()
        check_routes()
    
    # Gerar relatu00f3rio
    report = generate_report()
    print("\n" + report)
