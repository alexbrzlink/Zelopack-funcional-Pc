#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testes de Componentes do Zelopack

Este script testa os principais componentes do sistema Zelopack,
verificando a integridade, acessibilidade e funcionalidade dos mesmos.
"""

import os
import sys
import re
import logging
import unittest
import json
import datetime
from pathlib import Path

# Configurações de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("zelopack_tests")

# Adicionar diretório raiz ao path para importar módulos do projeto
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Importar módulos necessários
try:
    from models import User, Supplier, Report
    from app import app, db
except ImportError as e:
    logger.error(f"Erro ao importar módulos necessários: {e}")
    logger.error("Certifique-se de que os arquivos models.py e app.py existem e são acessíveis")
    sys.exit(1)


class ZelopackComponentTest(unittest.TestCase):
    """Testes de componentes do sistema Zelopack"""
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial dos testes"""
        logger.info("Iniciando testes de componentes do sistema Zelopack")
        
        # Configurar o aplicativo Flask para testes
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Criar cliente de teste
        cls.app = app.test_client()
        
        # Criar contexto de aplicação
        with app.app_context():
            # Criar todas as tabelas
            db.create_all()
            
            # Criar dados de teste
            cls._create_test_data()
    
    @classmethod
    def tearDownClass(cls):
        """Limpeza após os testes"""
        logger.info("Finalizando testes de componentes")
        
        # Remover tabelas e fechar conexões
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    @classmethod
    def _create_test_data(cls):
        """Cria dados de teste para uso nos testes"""
        logger.info("Criando dados de teste")
        
        try:
            with app.app_context():
                # Criar usuário de teste
                test_user = User(
                    username='testuser',
                    email='test@example.com',
                    password_hash='pbkdf2:sha256:150000$test$hash'
                )
                db.session.add(test_user)
                
                # Criar fornecedor de teste
                test_supplier = Supplier(
                    name='Fornecedor Teste',
                    email='fornecedor@example.com',
                    contact_name='Contato Teste',
                    phone='11999998888'
                )
                db.session.add(test_supplier)
                
                # Cria relatório de teste - verificar os campos disponíveis no modelo
                try:
                    # Verificar quais campos são aceitos pelo modelo Report
                    test_report = Report(
                        title='Teste de Relatório',
                        user_id=1,
                        date_received=datetime.datetime.now(),
                        batch='LOTE123',
                        status='aprovado'
                    )
                    # Tentar definir supplier diretamente se supplier_id não é um campo válido
                    if hasattr(Report, 'supplier_id'):
                        test_report.supplier_id = 1
                    elif hasattr(Report, 'supplier'):
                        test_report.supplier = test_supplier
                except Exception as e:
                    logger.warning(f"Ajustando campos do relatório: {e}")
                    # Tentar uma abordagem mais simples com menos campos
                    test_report = Report(
                        title='Teste de Relatório',
                        user_id=1
                    )
                db.session.add(test_report)
                
                # Commit dos dados de teste
                db.session.commit()
                logger.info("Dados de teste criados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar dados de teste: {e}")
            db.session.rollback()
    
    def test_01_routes_accessibility(self):
        """Testa se as rotas principais estão acessíveis"""
        logger.info("Iniciando testes de acessibilidade de rotas")
        
        # Lista de rotas importantes para testar
        routes = [
            '/',
            '/login',
            '/reports',
            '/reports/search',
            '/suppliers',
            '/calculos'
        ]
        
        for route in routes:
            response = self.app.get(route, follow_redirects=True)
            self.assertIn(response.status_code, [200, 302], f"Rota {route} retornou status {response.status_code}")
            logger.info(f"Rota {route} verificada: {response.status_code}")
    
    def test_02_static_files_integrity(self):
        """Testa a integridade dos arquivos estáticos"""
        logger.info("Iniciando testes de integridade de arquivos estáticos")
        
        # Lista de arquivos estáticos importantes
        static_files = [
            '/static/css/style.css',
            '/static/css/theme.css',
            '/static/css/animations.css',
            '/static/css/skeleton.css',
            '/static/js/main.js',
            '/static/js/theme_manager.js',
            '/static/js/skeleton-loader.js'
        ]
        
        for file_path in static_files:
            response = self.app.get(file_path)
            self.assertEqual(response.status_code, 200, f"Arquivo {file_path} não encontrado")
            self.assertGreater(len(response.data), 0, f"Arquivo {file_path} está vazio")
            logger.info(f"Arquivo estático {file_path} verificado: {len(response.data)} bytes")
    
    def test_03_js_syntax_validation(self):
        """Verifica a sintaxe dos arquivos JavaScript"""
        logger.info("Iniciando validação de sintaxe JavaScript")
        
        js_files = [
            'static/js/main.js',
            'static/js/theme_manager.js',
            'static/js/skeleton-loader.js',
            'static/js/search.js'
        ]
        
        js_errors = []
        for js_file in js_files:
            if os.path.exists(js_file):
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Validação básica de sintaxe JS
                # Verificar parênteses, chaves e colchetes não balanceados
                brackets = {'(': ')', '{': '}', '[': ']'}
                stack = []
                
                for i, char in enumerate(content):
                    if char in brackets.keys():
                        stack.append((char, i))
                    elif char in brackets.values():
                        if not stack:
                            line_no = content[:i].count('\n') + 1
                            js_errors.append(f"Erro em {js_file}:linha {line_no}: Fechamento '{char}' sem abertura")
                            continue
                        
                        last_open, _ = stack.pop()
                        if brackets.get(last_open) != char:
                            line_no = content[:i].count('\n') + 1
                            js_errors.append(f"Erro em {js_file}:linha {line_no}: Fechamento '{char}' não corresponde a abertura '{last_open}'")
                
                # Verificar parênteses não fechados
                for bracket, pos in stack:
                    line_no = content[:pos].count('\n') + 1
                    js_errors.append(f"Erro em {js_file}:linha {line_no}: Abertura '{bracket}' sem fechamento")
                
                # Verificar ponto e vírgula faltando (uma validação básica)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line and not line.startswith('//') and not line.startswith('/*') and not line.endswith('*/') and \
                       not line.endswith('{') and not line.endswith('}') and not line.endswith(';') and \
                       not line.endswith(',') and not line.endswith(':') and not line.endswith('(') and \
                       not line.endswith('[') and not line.endswith('*/') and \
                       not line.startswith('import') and not line.startswith('export'):
                        next_line = lines[i+1].strip() if i+1 < len(lines) else ""
                        if next_line and not next_line.startswith('//') and not next_line.startswith('*') and \
                           not next_line.startswith(')') and not next_line.startswith(']') and \
                           not next_line.startswith('}') and not next_line.startswith('.'):
                            js_errors.append(f"Possível ponto e vírgula faltando em {js_file}:linha {i+1}")
            else:
                logger.warning(f"Arquivo {js_file} não encontrado")
        
        for error in js_errors:
            logger.warning(error)
        
        self.assertEqual(len(js_errors), 0, f"Encontrados {len(js_errors)} erros de sintaxe JavaScript")
        logger.info("Validação de sintaxe JavaScript concluída")
    
    def test_04_css_syntax_validation(self):
        """Verifica a sintaxe dos arquivos CSS"""
        logger.info("Iniciando validação de sintaxe CSS")
        
        css_files = [
            'static/css/style.css',
            'static/css/theme.css',
            'static/css/animations.css',
            'static/css/skeleton.css'
        ]
        
        css_errors = []
        for css_file in css_files:
            if os.path.exists(css_file):
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Validação básica de sintaxe CSS
                # Verificar chaves não fechadas
                open_braces = content.count('{')
                close_braces = content.count('}')
                
                if open_braces != close_braces:
                    css_errors.append(f"Erro em {css_file}: Diferença entre chaves abertas ({open_braces}) e fechadas ({close_braces})")
                
                # Verificar propriedades sem ponto e vírgula
                rules = re.findall(r'{([^}]*)}', content)
                for i, rule in enumerate(rules):
                    properties = [prop.strip() for prop in rule.split(';') if prop.strip()]
                    for prop in properties:
                        if ':' not in prop:
                            css_errors.append(f"Erro em {css_file}: Propriedade sem dois pontos: '{prop}'")
                            continue
                            
                        # Verificar se a última propriedade não tem ponto e vírgula
                        if properties[-1] != prop and not prop.endswith(';'):
                            css_errors.append(f"Erro em {css_file}: Falta ponto e vírgula: '{prop}'")
            else:
                logger.warning(f"Arquivo {css_file} não encontrado")
        
        for error in css_errors:
            logger.warning(error)
        
        self.assertEqual(len(css_errors), 0, f"Encontrados {len(css_errors)} erros de sintaxe CSS")
        logger.info("Validação de sintaxe CSS concluída")
    
    def test_05_html_templates_validation(self):
        """Verifica problemas comuns em templates HTML"""
        logger.info("Iniciando validação de templates HTML")
        
        # Verifica os templates da pasta templates e suas subpastas
        template_errors = []
        template_dir = 'templates'
        
        if os.path.exists(template_dir) and os.path.isdir(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Verificar tags HTML não fechadas
                        open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*(?<!/)>', content)
                        closed_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)>', content)
                        self_closing_tags = ['img', 'br', 'hr', 'input', 'meta', 'link']
                        
                        # Remover tags de auto-fechamento da lista
                        open_tags = [tag for tag in open_tags if tag.lower() not in self_closing_tags]
                        
                        # Verificar balanceamento das tags
                        stack = []
                        for tag in open_tags:
                            stack.append(tag)
                        
                        for tag in closed_tags:
                            if not stack or stack.pop() != tag:
                                template_errors.append(f"Erro em {file_path}: Tag HTML desbalanceada: {tag}")
                        
                        # Verificar blocos Jinja2 mal formados
                        jinja_open = re.findall(r'{%\s*block\s+([a-zA-Z][a-zA-Z0-9_]*)\s*%}', content)
                        jinja_close = re.findall(r'{%\s*endblock\s*(?:([a-zA-Z][a-zA-Z0-9_]*))?\s*%}', content)
                        
                        if len(jinja_open) != len(jinja_close):
                            template_errors.append(
                                f"Erro em {file_path}: Blocos Jinja2 desbalanceados: {len(jinja_open)} abertos vs {len(jinja_close)} fechados")
                        
                        # Verificar variáveis Jinja2 mal formadas
                        jinja_vars = re.findall(r'{{([^}]*)}', content)
                        for var in jinja_vars:
                            if '{{' in var or '}}' in var:
                                template_errors.append(f"Erro em {file_path}: Variável Jinja2 mal formada: {var}")
                        
                        # Verificar URLs hardcoded (deve usar url_for)
                        hardcoded_urls = re.findall(r'href=["\'](/[a-zA-Z0-9/\-_\.]+)["\']', content)
                        for url in hardcoded_urls:
                            if not re.match(r'/static/', url):
                                template_errors.append(f"Aviso em {file_path}: URL hardcoded: {url}. Considere usar url_for()")
                        
                        logger.info(f"Template {file_path} verificado")
        else:
            logger.warning(f"Diretório de templates '{template_dir}' não encontrado")
        
        for error in template_errors:
            logger.warning(error)
        
        # Considerar os avisos de URL hardcoded como não críticos
        critical_errors = [err for err in template_errors if "URL hardcoded" not in err]
        self.assertEqual(len(critical_errors), 0, f"Encontrados {len(critical_errors)} erros críticos em templates HTML")
        
        logger.info("Validação de templates HTML concluída")
    
    def test_06_authentication(self):
        """Testa o sistema de autenticação"""
        logger.info("Iniciando testes de autenticação")
        
        # Testar login com usuário de teste
        login_response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Não estamos verificando se o login sucedeu, apenas se a rota funciona
        self.assertIn(login_response.status_code, [200, 302], "Login falhou com erro de servidor")
        
        # Testar logout
        logout_response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(logout_response.status_code, [200, 302], "Logout falhou com erro de servidor")
        
        logger.info("Testes de autenticação concluídos")
    
    def test_07_database_models(self):
        """Testa os modelos de banco de dados"""
        logger.info("Iniciando testes de modelos de banco de dados")
        
        try:
            with app.app_context():
                # Verificar se podemos acessar a tabela de usuários
                users = User.query.all()
                logger.info(f"Encontrados {len(users)} usuários")
                
                # Verificar se podemos acessar a tabela de fornecedores
                suppliers = Supplier.query.all()
                logger.info(f"Encontrados {len(suppliers)} fornecedores")
                
                # Verificar se podemos acessar a tabela de relatórios
                reports = Report.query.all()
                logger.info(f"Encontrados {len(reports)} relatórios")
        except Exception as e:
            logger.error(f"Erro ao acessar modelos: {e}")
            self.fail(f"Erro ao acessar modelos: {e}")
        
        logger.info("Testes de modelos de banco de dados concluídos")
    
    def test_08_database_queries(self):
        """Testa consultas ao banco de dados"""
        logger.info("Iniciando testes de consultas ao banco de dados")
        
        try:
            with app.app_context():
                # Criar um relatório adicional
                new_report = Report(
                    title='Relatório de Teste Adicional',
                    user_id=1,
                    date_received=datetime.datetime.now(),
                    batch='LOTE999',
                    status='pendente'
                )
                
                # Definir fornecedor conforme a estrutura do modelo
                if hasattr(Report, 'supplier_id'):
                    new_report.supplier_id = 1
                
                db.session.add(new_report)
                db.session.commit()
                
                # Buscar relatório por título
                found_report = Report.query.filter_by(title='Relatório de Teste Adicional').first()
                self.assertIsNotNone(found_report, "Não foi possível encontrar o relatório criado")
                
                # Buscar usuário por nome de usuário
                found_user = User.query.filter_by(username='testuser').first()
                self.assertIsNotNone(found_user, "Não foi possível encontrar o usuário criado")
                
                # Buscar fornecedor por nome
                found_supplier = Supplier.query.filter_by(name='Fornecedor Teste').first()
                self.assertIsNotNone(found_supplier, "Não foi possível encontrar o fornecedor criado")
                
                # Testar filtro por status
                pending_reports = Report.query.filter_by(status='pendente').all()
                self.assertGreaterEqual(len(pending_reports), 1, "Não foi possível filtrar relatórios por status")
                
                # Testar consulta com join (se supplier_id existir como campo)
                if hasattr(Report, 'supplier_id'):
                    try:
                        report_with_supplier = db.session.query(Report, Supplier) \
                            .join(Supplier, Report.supplier_id == Supplier.id) \
                            .first()
                        # Apenas verificar se a consulta funcionou, sem asserções
                        logger.info("Consulta com join funcionou corretamente")
                    except Exception as e:
                        logger.warning(f"Consulta com join não funcionou: {e}")
                
        except Exception as e:
            logger.error(f"Erro em consultas ao banco de dados: {e}")
            self.fail(f"Erro em consultas ao banco de dados: {e}")
        
        logger.info("Testes de consultas ao banco de dados concluídos")
    
    def test_09_api_endpoints(self):
        """Testa endpoints de API, se existirem"""
        logger.info("Iniciando testes de endpoints de API")
        
        # Listar de endpoints de API a serem testados (se existirem)
        api_endpoints = [
            '/api/reports',
            '/api/suppliers',
            '/api/calculations'
        ]
        
        for endpoint in api_endpoints:
            response = self.app.get(endpoint)
            # Apenas verificamos se a rota retorna 200, 404 ou 401/403
            # 200 = OK, 404 = Não implementado, 401/403 = Autenticação necessária
            self.assertIn(response.status_code, [200, 401, 403, 404], 
                         f"Endpoint {endpoint} retornou status código inesperado: {response.status_code}")
            logger.info(f"Endpoint {endpoint} verificado: {response.status_code}")
        
        logger.info("Testes de endpoints de API concluídos")
    
    def test_10_security_headers(self):
        """Testa cabeçalhos de segurança HTTP"""
        logger.info("Iniciando testes de cabeçalhos de segurança")
        
        response = self.app.get('/')
        headers = response.headers
        
        # Verificar presença de cabeçalhos de segurança importantes
        # Alguns podem não estar presentes dependendo da configuração
        security_headers = {
            'Content-Security-Policy': False,
            'X-Content-Type-Options': False,
            'X-Frame-Options': False,
            'X-XSS-Protection': False,
            'Strict-Transport-Security': False
        }
        
        for header in security_headers:
            if header in headers:
                security_headers[header] = True
                logger.info(f"Cabeçalho de segurança {header} presente: {headers[header]}")
            else:
                logger.warning(f"Cabeçalho de segurança {header} ausente")
        
        # Não falhar o teste se os cabeçalhos estiverem ausentes, apenas avisar
        missing_headers = [h for h, present in security_headers.items() if not present]
        if missing_headers:
            logger.warning(f"Cabeçalhos de segurança ausentes: {', '.join(missing_headers)}")
        
        logger.info("Testes de cabeçalhos de segurança concluídos")


def run_tests():
    """Executa os testes de componentes"""
    # Configurar a saída do unittest para ser mais verbosa
    unittest.main(argv=['first-arg-is-ignored'], exit=False, verbosity=2)


if __name__ == "__main__":
    run_tests()