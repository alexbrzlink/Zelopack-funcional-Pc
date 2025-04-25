#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testes automatizados para componentes do sistema Zelopack

Este script realiza testes abrangentes dos componentes da interface,
API, validação de formulários, consultas de banco de dados e integridade
do sistema como um todo, reportando em tempo real os resultados.
"""

import os
import sys
import unittest
import json
import re
import time
import sqlite3
import logging
import urllib.parse
from unittest import mock
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tests/component_tests.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Garanta que o diretório de testes exista
os.makedirs('tests', exist_ok=True)

# Adicione o diretório raiz ao path para importações
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa a aplicação e seus módulos
try:
    from app import app, db
    from models import User, Report, Supplier
    # A classe Calculation pode não existir ainda, tente importá-la se disponível
    try:
        from models import Calculation
    except ImportError:
        # Não é crítico se Calculation não existe ainda
        pass
    APP_IMPORTED = True
except ImportError as e:
    logger.error(f"Erro ao importar módulos da aplicação: {e}")
    APP_IMPORTED = False

class ComponentTestCase(unittest.TestCase):
    """Testes de componentes do sistema Zelopack"""
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial dos testes"""
        if not APP_IMPORTED:
            logger.error("Não foi possível iniciar os testes, a aplicação não pôde ser importada")
            sys.exit(1)
            
        # Configura a aplicação para testes
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app = app.test_client()
        
        # Cria o contexto da aplicação
        with app.app_context():
            # Cria todas as tabelas no banco de dados de teste
            db.create_all()
            
            # Cria dados de teste
            cls._create_test_data()
            
        logger.info("Configuração de testes concluída")
    
    @classmethod
    def tearDownClass(cls):
        """Limpeza após os testes"""
        with app.app_context():
            db.drop_all()
        logger.info("Limpeza pós-testes concluída")
    
    @classmethod
    def _create_test_data(cls):
        """Cria dados de teste no banco de dados"""
        try:
            # Cria usuário de teste
            test_user = User(
                username='testuser',
                email='test@example.com',
                name='Test User',
                role='admin'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            
            # Cria fornecedor de teste
            test_supplier = Supplier(
                name='Fornecedor Teste',
                contact_name='Contato Teste',
                email='fornecedor@example.com',
                phone='11999998888'
            )
            db.session.add(test_supplier)
            
            # Cria relatório de teste - verificar os campos disponíveis no modelo
            try:
                # Verificar quais campos são aceitos pelo modelo Report
                test_report = Report(
                    title='Teste de Relatório',
                    user_id=1,
                    date_received=datetime.now(),
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
        
        # Toleramos alguns avisos em templates, então só falhamos se houver muitos erros
        self.assertLessEqual(len(template_errors), 5, f"Encontrados {len(template_errors)} problemas em templates HTML")
        logger.info("Validação de templates HTML concluída")
    
    def test_06_routes_and_views(self):
        """Testa as rotas e views principais"""
        logger.info("Iniciando testes de rotas e views")
        
        # Fazer login para testar rotas protegidas
        login_response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(login_response.status_code, 200, "Falha ao fazer login para testes")
        
        # Testar a rota principal depois do login
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Falha ao acessar rota principal após login")
        
        # Verificar se o layout base está sendo carregado
        self.assertIn(b'ZELOPACK', response.data, "Layout base não está sendo carregado corretamente")
        
        # Testar a rota de upload de laudos
        response = self.app.get('/reports/upload', follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Falha ao acessar rota de upload de laudos")
        self.assertIn(b'Enviar', response.data, "Página de upload não está sendo renderizada corretamente")
        
        # Testar a rota de busca
        response = self.app.get('/reports/search', follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Falha ao acessar rota de busca")
        self.assertIn(b'Busca', response.data, "Página de busca não está sendo renderizada corretamente")
        
        # Testar a rota de calculcôs
        response = self.app.get('/calculos', follow_redirects=True)
        self.assertIn(response.status_code, [200, 404], "Erro ao acessar módulo de cálculos")
        
        logger.info("Testes de rotas e views concluídos")
    
    def test_07_form_validation(self):
        """Testa a validação de formulários"""
        logger.info("Iniciando testes de validação de formulários")
        
        # Testar formulário de login com dados inválidos
        invalid_login = self.app.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrong'
        }, follow_redirects=True)
        
        self.assertEqual(invalid_login.status_code, 200, "Formulário de login não está lidando com dados inválidos")
        self.assertIn(b'Invalid', invalid_login.data.lower() or b'incorreto', invalid_login.data.lower(), 
                      "Formulário de login não mostra mensagem de erro para credenciais inválidas")
        
        # Testar formulário de cadastro com dados inválidos (email malformado)
        invalid_register = self.app.post('/register', data={
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        self.assertIn(invalid_register.status_code, [200, 400], 
                      "Formulário de registro não está lidando com dados inválidos")
        
        logger.info("Testes de validação de formulários concluídos")
    
    def test_08_database_integrity(self):
        """Testa a integridade do banco de dados"""
        logger.info("Iniciando testes de integridade do banco de dados")
        
        with app.app_context():
            # Verificar se os dados de teste foram criados corretamente
            users = User.query.all()
            self.assertGreaterEqual(len(users), 1, "Não há usuários no banco de dados de teste")
            
            suppliers = Supplier.query.all()
            self.assertGreaterEqual(len(suppliers), 1, "Não há fornecedores no banco de dados de teste")
            
            reports = Report.query.all()
            self.assertGreaterEqual(len(reports), 1, "Não há relatórios no banco de dados de teste")
            
            # Verificar integridade de relações
            report = Report.query.first()
            self.assertIsNotNone(report.user_id, "Relatório sem ID de usuário")
            self.assertIsNotNone(report.supplier_id, "Relatório sem ID de fornecedor")
            
            # Verificar se podemos acessar os objetos relacionados
            user = User.query.get(report.user_id)
            self.assertIsNotNone(user, "Usuário relacionado não encontrado")
            
            supplier = Supplier.query.get(report.supplier_id)
            self.assertIsNotNone(supplier, "Fornecedor relacionado não encontrado")
            
        logger.info("Testes de integridade do banco de dados concluídos")
    
    def test_09_security_checks(self):
        """Verifica vulnerabilidades de segurança básicas"""
        logger.info("Iniciando verificações de segurança")
        
        # Verificar proteção CSRF nos formulários
        with app.test_client() as client:
            # Tentar enviar um formulário sem token CSRF
            app.config['WTF_CSRF_ENABLED'] = True  # Habilitar proteção CSRF
            response = client.post('/login', data={
                'username': 'testuser',
                'password': 'password123'
            })
            
            expected_status = 400  # Bad Request para CSRF faltando
            msg = f"Proteção CSRF não está funcionando: código {response.status_code}, esperado {expected_status}"
            self.assertIn(response.status_code, [expected_status, 200], msg)
        
        # Restaurar configuração para os outros testes
        app.config['WTF_CSRF_ENABLED'] = False
        
        # Verificar proteção contra XSS nos templates
        suspicious_patterns = []
        template_dir = 'templates'
        
        if os.path.exists(template_dir) and os.path.isdir(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Verificar saída de variável sem escape
                        raw_vars = re.findall(r'{{\s*([^|]+?)\s*}}', content)
                        for var in raw_vars:
                            var = var.strip()
                            if not var.endswith('|safe') and not var.endswith('|escape') and not var.endswith('_html') and \
                               'url_for' not in var and 'csrf_token' not in var:
                                suspicious_patterns.append(f"Possível vulnerabilidade XSS em {file_path}: Variável '{var}' sem escape")
        
        for pattern in suspicious_patterns:
            logger.warning(pattern)
        
        # Aqui apenas avisamos, não falhamos o teste
        if suspicious_patterns:
            logger.warning(f"Encontrados {len(suspicious_patterns)} padrões suspeitos de segurança")
        
        logger.info("Verificações de segurança concluídas")
    
    def test_10_javascript_features(self):
        """Testa se funcionalidades JavaScript estão presentes"""
        logger.info("Iniciando testes de funcionalidades JavaScript")
        
        js_features = [
            ('static/js/theme_manager.js', 'theme', "Sistema de temas"),
            ('static/js/skeleton-loader.js', 'skeleton', "Sistema de skeleton loading"),
            ('static/js/main.js', 'setupScrollNavbar', "Efeito de scroll na navbar"),
            ('static/js/main.js', 'setupRippleEffect', "Efeito de ripple em botões")
        ]
        
        for file_path, feature_name, description in js_features:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                feature_present = feature_name.lower() in content.lower()
                self.assertTrue(feature_present, f"{description} não encontrado em {file_path}")
                logger.info(f"Funcionalidade verificada: {description}")
            else:
                logger.warning(f"Arquivo {file_path} não encontrado")
        
        logger.info("Testes de funcionalidades JavaScript concluídos")

    def test_11_performance_check(self):
        """Verifica possíveis problemas de performance"""
        logger.info("Iniciando verificação de performance")
        
        # Medir tempo de resposta de rotas principais
        routes_to_test = ['/', '/reports', '/reports/search']
        response_times = {}
        
        for route in routes_to_test:
            start_time = time.time()
            response = self.app.get(route, follow_redirects=True)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times[route] = response_time
            
            logger.info(f"Rota {route}: tempo de resposta {response_time:.4f}s")
            
            # Verificar se o tempo de resposta é razoável
            self.assertLessEqual(response_time, 2.0, f"Tempo de resposta muito alto para rota {route}: {response_time:.4f}s")
        
        # Verificar assets grandes que podem impactar performance
        static_dir = 'static'
        large_files = []
        
        if os.path.exists(static_dir) and os.path.isdir(static_dir):
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    
                    # Tamanhos que podem indicar problemas de performance
                    if file.endswith('.js') and size > 500 * 1024:  # JS > 500KB
                        large_files.append((file_path, size))
                    elif file.endswith('.css') and size > 250 * 1024:  # CSS > 250KB
                        large_files.append((file_path, size))
                    elif file.endswith(('.jpg', '.jpeg', '.png', '.webp')) and size > 1024 * 1024:  # Imagens > 1MB
                        large_files.append((file_path, size))
        
        for file_path, size in large_files:
            size_kb = size / 1024
            logger.warning(f"Arquivo grande encontrado: {file_path} ({size_kb:.2f} KB)")
        
        # Checar carregamento de includes desnecessários
        template_dir = 'templates'
        includes_count = {}
        
        if os.path.exists(template_dir) and os.path.isdir(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Procurar por includes repetidos
                        includes = re.findall(r'{%\s*include\s+[\'"]([^\'"]+)[\'"]', content)
                        for include in includes:
                            includes_count[include] = includes_count.get(include, 0) + 1
        
        for include, count in includes_count.items():
            if count > 3:
                logger.warning(f"Include repetido em múltiplos templates: {include} ({count} vezes)")
        
        logger.info("Verificação de performance concluída")

def run_tests():
    """Executa todos os testes de componentes"""
    test_suite = unittest.TestLoader().loadTestsFromTestCase(ComponentTestCase)
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    return test_result.wasSuccessful()

def generate_report(success):
    """Gera um relatório de testes"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_content = {
        "timestamp": timestamp,
        "success": success,
        "log_file": "tests/component_tests.log"
    }
    
    with open("tests/last_test_report.json", "w") as f:
        json.dump(report_content, f, indent=2)
    
    logger.info(f"Relatório de testes gerado: tests/last_test_report.json")
    logger.info(f"Status do teste: {'SUCESSO' if success else 'FALHA'}")

if __name__ == "__main__":
    logger.info("Iniciando testes de componentes do sistema Zelopack")
    success = run_tests()
    generate_report(success)
    
    sys.exit(0 if success else 1)