#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SISTEMA AUTOMATIZADO DE TESTES E MELHORIAS DO ZELOPACK

Este script executa testes contínuos e automáticos do sistema Zelopack,
detectando problemas e aplicando melhorias automaticamente.

USO SIMPLES:
  python auto_check.py

OPÇÕES:
  python auto_check.py --test      # Apenas executar testes
  python auto_check.py --fix       # Executar testes e corrigir problemas automaticamente
  python auto_check.py --watch     # Monitorar alterações e testar continuamente
  python auto_check.py --schedule  # Agendar testes periódicos (a cada 2 horas)
"""

import os
import sys
import re
import time
import json
import glob
import argparse
import logging
import subprocess
import threading
import datetime
import shutil
from pathlib import Path

# Configurações de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("zelopack_auto_check.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("zelopack_auto_check")

# Cores para o terminal
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Diretórios e arquivos importantes
TEST_DIR = "tests"
REPORTS_DIR = os.path.join(TEST_DIR, "reports")
FIXES_DIR = os.path.join(TEST_DIR, "fixes")
LAST_CHECK_FILE = os.path.join(TEST_DIR, "last_check.json")
TEST_COMPONENTS_SCRIPT = os.path.join(TEST_DIR, "test_components.py")
MONITOR_SCRIPT = os.path.join(TEST_DIR, "zelopack_monitor.py")
AI_ASSISTANT_SCRIPT = os.path.join(TEST_DIR, "zelopack_ai_assistant.py")

# Criar diretórios necessários
os.makedirs(TEST_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(FIXES_DIR, exist_ok=True)

class ZelopackAutoCheck:
    """Sistema automatizado de testes e melhorias"""
    
    def __init__(self):
        """Inicializa o sistema de verificação automática"""
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_file = os.path.join(REPORTS_DIR, f"check_report_{self.timestamp}.json")
        self.found_issues = []
        self.applied_fixes = []
        self.test_results = {}
        self.components_checked = {}
        self.load_last_check()
    
    def load_last_check(self):
        """Carrega informações do último check executado"""
        if os.path.exists(LAST_CHECK_FILE):
            try:
                with open(LAST_CHECK_FILE, 'r') as f:
                    self.last_check = json.load(f)
                logger.info(f"Último check carregado: {self.last_check.get('timestamp', 'desconhecido')}")
            except:
                self.last_check = {"timestamp": "nunca", "issues": []}
        else:
            self.last_check = {"timestamp": "nunca", "issues": []}
    
    def save_check_results(self):
        """Salva os resultados do check atual"""
        current_check = {
            "timestamp": self.timestamp,
            "issues": self.found_issues,
            "fixes": self.applied_fixes,
            "test_results": self.test_results,
            "components_checked": self.components_checked
        }
        
        # Salvar como último check
        with open(LAST_CHECK_FILE, 'w') as f:
            json.dump(current_check, f, indent=2)
        
        # Salvar relatório detalhado
        with open(self.report_file, 'w') as f:
            json.dump(current_check, f, indent=2)
        
        logger.info(f"Resultados salvos em {self.report_file}")
    
    def check_static_files(self):
        """Verifica arquivos estáticos do sistema"""
        logger.info("Verificando arquivos estáticos...")
        
        static_dirs = ["static/css", "static/js", "static/img"]
        files_to_check = []
        
        # Coletar arquivos para verificar
        for dir_path in static_dirs:
            if os.path.exists(dir_path):
                # Adicionar todos os arquivos no diretório
                for ext in ["*.css", "*.js", "*.html", "*.svg", "*.png", "*.jpg"]:
                    files_to_check.extend(glob.glob(os.path.join(dir_path, "**", ext), recursive=True))
        
        # Verificar cada arquivo
        for file_path in files_to_check:
            self._check_file(file_path)
        
        self.components_checked["static_files"] = len(files_to_check)
        logger.info(f"Verificados {len(files_to_check)} arquivos estáticos")
    
    def check_python_files(self):
        """Verifica arquivos Python do sistema"""
        logger.info("Verificando arquivos Python...")
        
        # Encontrar todos os arquivos Python (exceto no diretório de testes)
        python_files = []
        for py_file in glob.glob("**/*.py", recursive=True):
            if not py_file.startswith(TEST_DIR) and "venv" not in py_file:
                python_files.append(py_file)
        
        # Verificar cada arquivo
        for file_path in python_files:
            self._check_file(file_path)
        
        self.components_checked["python_files"] = len(python_files)
        logger.info(f"Verificados {len(python_files)} arquivos Python")
    
    def check_templates(self):
        """Verifica arquivos de template"""
        logger.info("Verificando templates...")
        
        template_files = []
        if os.path.exists("templates"):
            template_files.extend(glob.glob("templates/**/*.html", recursive=True))
        
        # Verificar cada arquivo
        for file_path in template_files:
            self._check_file(file_path, check_jinja=True)
        
        self.components_checked["templates"] = len(template_files)
        logger.info(f"Verificados {len(template_files)} arquivos de template")
    
    def check_database_models(self):
        """Verifica modelos de banco de dados"""
        logger.info("Verificando modelos de banco de dados...")
        
        models_checked = 0
        
        # Verificar models.py
        if os.path.exists("models.py"):
            try:
                with open("models.py", 'r') as f:
                    content = f.read()
                
                # Encontrar todas as classes de modelo
                model_classes = re.findall(r'class\s+(\w+)\([^)]*db\.Model', content)
                models_checked = len(model_classes)
                
                # Verificar problemas comuns
                if "from sqlalchemy import text" in content and "text(" in content:
                    self._add_issue("models.py", "security", "Possível vulnerabilidade de injeção SQL com sqlalchemy.text()", 
                                   "Certifique-se de usar parâmetros de bind com text()")
            except Exception as e:
                logger.error(f"Erro ao verificar models.py: {e}")
        
        self.components_checked["database_models"] = models_checked
        logger.info(f"Verificados {models_checked} modelos de banco de dados")
    
    def check_api_endpoints(self):
        """Verifica endpoints de API"""
        logger.info("Verificando endpoints de API...")
        
        api_files = []
        endpoints_count = 0
        
        # Procurar por arquivos que podem conter endpoints de API
        for py_file in glob.glob("**/*.py", recursive=True):
            if not py_file.startswith(TEST_DIR) and "venv" not in py_file:
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    
                    # Procurar por definições de rota
                    if "@app.route" in content or "@blueprint.route" in content or ".route(" in content:
                        api_files.append(py_file)
                        # Contar endpoints
                        endpoints_count += len(re.findall(r'@\w+\.route\([\'"]', content))
                except Exception as e:
                    logger.error(f"Erro ao verificar {py_file}: {e}")
        
        # Verificar cada arquivo de API
        for file_path in api_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Verificar problemas comuns em endpoints de API
                if "request.form[" in content:
                    self._add_issue(file_path, "security", "Acesso direto a request.form sem verificação",
                                   "Use request.form.get() com valor padrão ou validação")
                
                if "request.args[" in content:
                    self._add_issue(file_path, "security", "Acesso direto a request.args sem verificação",
                                   "Use request.args.get() com valor padrão ou validação")
                
                # Verificar validação de formulários
                if "request.form" in content and "Form(" not in content and "validate()" not in content:
                    self._add_issue(file_path, "security", "Possível falta de validação em formulários",
                                   "Use Flask-WTF ou outra biblioteca para validação de entrada")
            except Exception as e:
                logger.error(f"Erro ao analisar {file_path}: {e}")
        
        self.components_checked["api_endpoints"] = endpoints_count
        logger.info(f"Verificados {endpoints_count} endpoints de API em {len(api_files)} arquivos")
    
    def check_authentication(self):
        """Verifica mecanismos de autenticação"""
        logger.info("Verificando mecanismos de autenticação...")
        
        auth_files = []
        auth_checked = False
        
        # Procurar arquivos relacionados à autenticação
        for py_file in glob.glob("**/*.py", recursive=True):
            if "auth" in py_file.lower() or "login" in py_file.lower() or "user" in py_file.lower():
                if not py_file.startswith(TEST_DIR) and "venv" not in py_file:
                    auth_files.append(py_file)
        
        # Verificar configurações de autenticação
        for file_path in auth_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Verificar problemas comuns
                if "password" in content.lower() and "hash" not in content.lower() and "crypt" not in content.lower():
                    self._add_issue(file_path, "security", "Possível armazenamento de senha sem hash",
                                   "Use bcrypt, werkzeug.security ou outra biblioteca para hash de senhas")
                
                # Verificar session secret
                if "SECRET_KEY" in content and ("secret" in content.lower() or "chave" in content.lower()):
                    if "os.environ" not in content and "getenv" not in content:
                        self._add_issue(file_path, "security", "Possível SECRET_KEY hardcoded",
                                       "Use variáveis de ambiente para armazenar segredos")
                
                auth_checked = True
            except Exception as e:
                logger.error(f"Erro ao verificar {file_path}: {e}")
        
        self.components_checked["authentication"] = len(auth_files)
        if not auth_checked:
            logger.warning("Não foi possível verificar autenticação")
    
    def run_component_tests(self):
        """Executa os testes de componentes"""
        logger.info("Executando testes de componentes...")
        
        # Verificar se o script de testes existe
        if not os.path.exists(TEST_COMPONENTS_SCRIPT):
            logger.warning(f"Script de testes {TEST_COMPONENTS_SCRIPT} não encontrado")
            return False
        
        try:
            # Executar o script de testes
            result = subprocess.run(
                [sys.executable, TEST_COMPONENTS_SCRIPT],
                capture_output=True,
                text=True,
                timeout=60  # 1 minuto de timeout
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            # Analisar a saída para identificar testes que falharam
            failed_tests = re.findall(r'FAIL: (test_\w+)', output)
            passed_tests = re.findall(r'OK:? (test_\w+)', output)
            
            # Salvar resultados
            self.test_results = {
                "success": success,
                "output": output,
                "failed_tests": failed_tests,
                "passed_tests": passed_tests,
                "return_code": result.returncode
            }
            
            # Adicionar problemas para testes que falharam
            for test in failed_tests:
                # Tentar extrair mensagem de erro
                error_match = re.search(f"{test}.*?Error: (.*?)(?:\n\n|$)", output, re.DOTALL)
                error_msg = error_match.group(1).strip() if error_match else "Erro desconhecido"
                
                self._add_issue(TEST_COMPONENTS_SCRIPT, "test_failure", f"Falha no teste: {test}", error_msg)
            
            logger.info(f"Testes de componentes: {len(passed_tests)} passaram, {len(failed_tests)} falharam")
            return success
        except subprocess.TimeoutExpired:
            logger.error("Timeout ao executar testes de componentes")
            self.test_results = {
                "success": False,
                "output": "Timeout ao executar testes",
                "failed_tests": ["timeout"],
                "passed_tests": [],
                "return_code": -1
            }
            return False
        except Exception as e:
            logger.error(f"Erro ao executar testes de componentes: {e}")
            self.test_results = {
                "success": False,
                "output": str(e),
                "failed_tests": ["exception"],
                "passed_tests": [],
                "return_code": -1
            }
            return False
    
    def _check_file(self, file_path, check_jinja=False):
        """Verifica um arquivo específico por problemas"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determinar o tipo de arquivo
            ext = os.path.splitext(file_path)[1].lower()
            
            # Verificar problemas baseados no tipo de arquivo
            if ext == '.py':
                self._check_python_content(file_path, content)
            elif ext == '.js':
                self._check_js_content(file_path, content)
            elif ext == '.css':
                self._check_css_content(file_path, content)
            elif ext == '.html':
                self._check_html_content(file_path, content, check_jinja)
        except Exception as e:
            logger.error(f"Erro ao verificar {file_path}: {e}")
    
    def _check_python_content(self, file_path, content):
        """Verifica problemas em código Python"""
        # Verificar imports não utilizados
        imports = re.findall(r'^\s*import\s+(\w+)|^\s*from\s+[\w.]+\s+import\s+([^(]+)', content, re.MULTILINE)
        all_imports = []
        for imp in imports:
            for i in imp:
                if i:
                    # Tratar imports múltiplos (separados por vírgula)
                    for single_imp in i.split(','):
                        clean_imp = single_imp.strip().split(' as ')[0]
                        if clean_imp:
                            all_imports.append(clean_imp)
        
        # Verificar quais imports não são usados
        unused_imports = []
        for imp in all_imports:
            # Remover o próprio import da análise
            content_without_import = re.sub(r'^\s*import\s+' + imp + r'|^\s*from\s+[\w.]+\s+import\s+([^(]*\b' + imp + r'\b[^(]*)', '', content, flags=re.MULTILINE)
            # Verificar se o nome do import aparece no resto do conteúdo
            if imp not in content_without_import:
                unused_imports.append(imp)
        
        if unused_imports:
            self._add_issue(file_path, "code_quality", f"Imports não utilizados: {', '.join(unused_imports)}",
                           "Remova imports não utilizados para melhorar a legibilidade e desempenho")
        
        # Verificar funções muito longas (mais de 50 linhas)
        long_functions = []
        in_function = False
        function_name = ""
        function_start = 0
        indent_level = 0
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            if not in_function:
                match = re.match(r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
                if match:
                    in_function = True
                    indent_level = len(match.group(1))
                    function_name = match.group(2)
                    function_start = i
            else:
                # Verificar se saímos da função
                if line.strip() and not line.startswith(' ' * (indent_level + 1)) and not line.startswith(' ' * indent_level + '@'):
                    in_function = False
                    function_length = i - function_start
                    
                    if function_length > 50:
                        long_functions.append((function_name, function_length))
        
        # Adicionar a última função, se estiver dentro de uma
        if in_function:
            function_length = len(lines) - function_start
            if function_length > 50:
                long_functions.append((function_name, function_length))
        
        if long_functions:
            self._add_issue(file_path, "code_quality", f"Funções muito longas: {', '.join([f'{name} ({length} linhas)' for name, length in long_functions])}",
                           "Funções muito longas são difíceis de entender e manter. Considere refatorá-las em funções menores")
        
        # Verificar hardcoded secrets
        secret_patterns = [
            r'api_key\s*=\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
            r'password\s*=\s*["\']([^"\']{6,})["\']',
            r'secret\s*=\s*["\']([^"\']{6,})["\']',
            r'SECRET_KEY\s*=\s*["\']([^"\']{6,})["\']'
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                self._add_issue(file_path, "security", "Possíveis secrets hardcoded no código",
                               "Mova secrets para variáveis de ambiente ou arquivos .env")
                break
        
        # Verificar print statements (deveriam ser logs em produção)
        if 'print(' in content and not file_path.endswith('test_'):
            self._add_issue(file_path, "code_quality", "Uso de print() em código de produção",
                           "Use logging ao invés de print() em código de produção")
    
    def _check_js_content(self, file_path, content):
        """Verifica problemas em código JavaScript"""
        # Verificar console.log
        if 'console.log(' in content:
            self._add_issue(file_path, "code_quality", "Uso de console.log() em código de produção",
                           "Remova console.log() em código de produção")
        
        # Verificar uso de var (deveria ser let/const)
        if re.search(r'\bvar\s+', content):
            self._add_issue(file_path, "code_quality", "Uso de 'var' em vez de let/const",
                           "Use 'const' para variáveis que não mudam e 'let' para variáveis que mudam")
        
        # Verificar alert()
        if 'alert(' in content:
            self._add_issue(file_path, "code_quality", "Uso de alert() em código de produção",
                           "Use componentes de UI mais modernos para notificações")
        
        # Verificar eval()
        if 'eval(' in content:
            self._add_issue(file_path, "security", "Uso de eval(), que é inseguro",
                           "Evite usar eval() por questões de segurança")
        
        # Verificar funções anônimas tradicionais (vs arrow functions)
        if re.search(r'function\s*\(\s*\)', content):
            self._add_issue(file_path, "code_quality", "Uso de função anônima tradicional",
                           "Considere usar arrow functions => para funções anônimas")
        
        # Verificar definição duplicada de funções
        function_defs = re.findall(r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(', content)
        duplicate_funcs = [f for f in function_defs if function_defs.count(f) > 1]
        
        if duplicate_funcs:
            unique_duplicates = set(duplicate_funcs)
            self._add_issue(file_path, "code_quality", f"Funções possivelmente duplicadas: {', '.join(unique_duplicates)}",
                           "Remova ou renomeie funções duplicadas")
    
    def _check_css_content(self, file_path, content):
        """Verifica problemas em código CSS"""
        # Verificar !important
        important_count = content.count('!important')
        if important_count > 5:
            self._add_issue(file_path, "code_quality", f"Uso excessivo de !important ({important_count} ocorrências)",
                           "Evite usar !important; melhore a especificidade dos seletores")
        
        # Verificar vendor prefixes não padronizados
        vendor_prefixes = re.findall(r'-(?:webkit|moz|ms|o)-', content)
        if vendor_prefixes:
            self._add_issue(file_path, "code_quality", f"Uso de {len(vendor_prefixes)} vendor prefixes",
                           "Considere usar autoprefixer ou uma ferramenta similar para gerenciar prefixos automaticamente")
        
        # Verificar unidades absolutas (px vs rem/em)
        px_count = len(re.findall(r'\b\d+px\b', content))
        relative_count = len(re.findall(r'\b\d+(?:rem|em|%|vh|vw)\b', content))
        
        if px_count > 2 * relative_count and px_count > 10:
            self._add_issue(file_path, "code_quality", f"Uso excessivo de unidades px ({px_count} ocorrências) vs unidades relativas ({relative_count} ocorrências)",
                           "Prefira unidades relativas (rem, em, %) para melhor responsividade")
        
        # Verificar seletores muito complexos
        complex_selectors = re.findall(r'[a-z\d\-_]+(?:\s+[a-z\d\-_]+){5,}', content)
        if complex_selectors:
            self._add_issue(file_path, "code_quality", f"Seletores CSS muito complexos ({len(complex_selectors)} ocorrências)",
                           "Seletores muito longos são difíceis de manter e podem afetar o desempenho")
        
        # Verificar propriedades duplicadas
        rules = re.findall(r'{([^}]*)}', content)
        for rule in rules:
            properties = [prop.split(':')[0].strip() for prop in rule.split(';') if ':' in prop]
            duplicate_props = [p for p in properties if properties.count(p) > 1]
            
            if duplicate_props:
                unique_duplicates = set(duplicate_props)
                self._add_issue(file_path, "code_quality", f"Propriedades CSS duplicadas: {', '.join(unique_duplicates)}",
                               "Propriedades duplicadas podem causar comportamento inesperado")
    
    def _check_html_content(self, file_path, content, check_jinja=False):
        """Verifica problemas em código HTML"""
        # Verificar atributo alt em imagens
        img_tags = re.findall(r'<img[^>]*>', content)
        img_without_alt = [img for img in img_tags if 'alt=' not in img]
        
        if img_without_alt:
            self._add_issue(file_path, "accessibility", f"Imagens sem atributo alt ({len(img_without_alt)} ocorrências)",
                           "Adicione atributos alt em todas as imagens para acessibilidade")
        
        # Verificar estilos inline
        inline_styles = re.findall(r'style\s*=\s*["\'][^"\']*["\']', content)
        if len(inline_styles) > 5:
            self._add_issue(file_path, "code_quality", f"Uso excessivo de estilos inline ({len(inline_styles)} ocorrências)",
                           "Mova estilos inline para arquivos CSS")
        
        # Verificar scripts inline
        inline_scripts = re.findall(r'<script[^>]*>.*?</script>', content, re.DOTALL)
        if len(inline_scripts) > 2:
            self._add_issue(file_path, "code_quality", f"Uso excessivo de scripts inline ({len(inline_scripts)} ocorrências)",
                           "Mova scripts inline para arquivos JS")
        
        # Verificar IDs duplicados
        id_attrs = re.findall(r'id\s*=\s*["\']([^"\']+)["\']', content)
        duplicate_ids = [id_attr for id_attr in id_attrs if id_attrs.count(id_attr) > 1]
        
        if duplicate_ids:
            unique_duplicates = set(duplicate_ids)
            self._add_issue(file_path, "code_quality", f"IDs HTML duplicados: {', '.join(unique_duplicates)}",
                           "IDs devem ser únicos em todo o documento")
        
        # Verificar problemas específicos do Jinja2
        if check_jinja:
            # Verificar blocos Jinja mal formados
            jinja_open = re.findall(r'{%\s*block\s+([a-zA-Z][a-zA-Z0-9_]*)\s*%}', content)
            jinja_close = re.findall(r'{%\s*endblock\s*(?:([a-zA-Z][a-zA-Z0-9_]*))?\s*%}', content)
            
            if len(jinja_open) != len(jinja_close):
                self._add_issue(file_path, "template", f"Blocos Jinja2 desbalanceados: {len(jinja_open)} abertos vs {len(jinja_close)} fechados",
                               "Certifique-se de que todos os blocos têm tags de fechamento correspondentes")
            
            # Verificar variáveis Jinja mal formadas
            jinja_vars = re.findall(r'{{([^}]*)}', content)
            malformed_vars = [var for var in jinja_vars if '{{' in var or '}}' in var]
            
            if malformed_vars:
                self._add_issue(file_path, "template", f"Variáveis Jinja2 mal formadas: {len(malformed_vars)} ocorrências",
                               "Corrija a sintaxe das variáveis Jinja2")
            
            # Verificar URLs hardcoded (deve usar url_for)
            hardcoded_urls = re.findall(r'href\s*=\s*["\']/([\w/\-_.]+)["\']', content)
            non_static_urls = [url for url in hardcoded_urls if not url.startswith('static')]
            
            if non_static_urls:
                self._add_issue(file_path, "template", f"URLs hardcoded sem url_for(): {len(non_static_urls)} ocorrências",
                               "Use Flask url_for() para gerar URLs")
    
    def _add_issue(self, file_path, issue_type, message, suggestion):
        """Adiciona um problema encontrado à lista"""
        issue = {
            "file": file_path,
            "type": issue_type,
            "message": message,
            "suggestion": suggestion,
            "timestamp": self.timestamp
        }
        self.found_issues.append(issue)
    
    def apply_fixes(self):
        """Aplica correções automáticas para problemas conhecidos"""
        logger.info("Aplicando correções automáticas...")
        
        fixes_applied = 0
        
        # Processar cada problema encontrado
        for issue in self.found_issues:
            file_path = issue["file"]
            issue_type = issue["type"]
            message = issue["message"]
            
            # Verificar se temos uma correção automática para este tipo de problema
            try:
                # Ler o conteúdo do arquivo
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Aplicar a correção apropriada
                new_content = None
                
                if "console.log" in message and file_path.endswith('.js'):
                    # Comentar console.log
                    new_content = re.sub(r'(console\.log\(.*?\);?)', r'// \1', content)
                
                elif "print()" in message and file_path.endswith('.py'):
                    # Substituir print por logger
                    if "import logging" not in content:
                        new_content = "import logging\nlogger = logging.getLogger(__name__)\n\n" + content
                    new_content = re.sub(r'print\((.*?)\)', r'logger.debug(\1)', new_content or content)
                
                elif "var" in message and file_path.endswith('.js'):
                    # Substituir var por let
                    new_content = re.sub(r'\bvar\b', 'let', content)
                
                elif "!important" in message and file_path.endswith('.css'):
                    # Remover !important
                    new_content = content.replace("!important", "")
                
                elif "Imagens sem atributo alt" in message:
                    # Adicionar atributo alt básico
                    new_content = re.sub(r'<img([^>]*?)(?:\s*\/)?>', lambda m: 
                                       '<img' + m.group(1) + (' alt="Imagem"' if 'alt=' not in m.group(1) else '') + '>', 
                                       content)
                
                # Se uma correção foi aplicada
                if new_content and new_content != content:
                    # Fazer backup do arquivo original
                    backup_path = os.path.join(FIXES_DIR, f"{os.path.basename(file_path)}.{self.timestamp}.bak")
                    shutil.copy2(file_path, backup_path)
                    
                    # Escrever o conteúdo corrigido
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    # Registrar a correção
                    self.applied_fixes.append({
                        "file": file_path,
                        "type": issue_type,
                        "message": message,
                        "backup": backup_path,
                        "timestamp": self.timestamp
                    })
                    
                    fixes_applied += 1
                    logger.info(f"Correção aplicada em {file_path}: {message}")
                
            except Exception as e:
                logger.error(f"Erro ao tentar corrigir {file_path}: {e}")
        
        logger.info(f"Total de {fixes_applied} correções aplicadas")
        return fixes_applied
    
    def run_checks(self, fix_issues=False):
        """Executa todas as verificações"""
        logger.info(f"Iniciando verificação automática (timestamp: {self.timestamp})")
        
        # Executar as verificações
        self.check_static_files()
        self.check_python_files()
        self.check_templates()
        self.check_database_models()
        self.check_api_endpoints()
        self.check_authentication()
        
        # Executar testes de componentes
        self.run_component_tests()
        
        # Aplicar correções, se solicitado
        if fix_issues and self.found_issues:
            self.apply_fixes()
        
        # Salvar os resultados
        self.save_check_results()
        
        # Exibir resumo
        self._display_summary()
        
        return len(self.found_issues)
    
    def _display_summary(self):
        """Exibe um resumo dos problemas encontrados"""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}RESUMO DA VERIFICAÇÃO AUTOMÁTICA{Colors.END}".center(70))
        print("=" * 70)
        
        # Estatísticas gerais
        print(f"\n{Colors.BOLD}Estatísticas:{Colors.END}")
        print(f"  • Data/hora: {self.timestamp.replace('_', ' ')}")
        print(f"  • Componentes verificados: {sum(self.components_checked.values())}")
        print(f"  • Problemas encontrados: {len(self.found_issues)}")
        print(f"  • Correções aplicadas: {len(self.applied_fixes)}")
        
        # Resultados dos testes
        print(f"\n{Colors.BOLD}Testes de componentes:{Colors.END}")
        if self.test_results:
            status = f"{Colors.GREEN}SUCESSO{Colors.END}" if self.test_results.get("success") else f"{Colors.RED}FALHA{Colors.END}"
            print(f"  • Status: {status}")
            print(f"  • Testes passaram: {len(self.test_results.get('passed_tests', []))}")
            print(f"  • Testes falharam: {len(self.test_results.get('failed_tests', []))}")
        else:
            print(f"  • {Colors.YELLOW}Testes não executados{Colors.END}")
        
        # Categorias de problemas
        if self.found_issues:
            issues_by_type = {}
            for issue in self.found_issues:
                issue_type = issue["type"]
                if issue_type not in issues_by_type:
                    issues_by_type[issue_type] = []
                issues_by_type[issue_type].append(issue)
            
            print(f"\n{Colors.BOLD}Problemas por categoria:{Colors.END}")
            for issue_type, issues in issues_by_type.items():
                if issue_type == "security":
                    print(f"  • {Colors.RED}Segurança:{Colors.END} {len(issues)} problemas")
                elif issue_type == "code_quality":
                    print(f"  • {Colors.YELLOW}Qualidade de código:{Colors.END} {len(issues)} problemas")
                else:
                    print(f"  • {issue_type.title()}: {len(issues)} problemas")
            
            # Mostrar os primeiros problemas de cada categoria
            print(f"\n{Colors.BOLD}Exemplos de problemas encontrados:{Colors.END}")
            for issue_type, issues in issues_by_type.items():
                if len(issues) > 0:
                    title = issue_type.replace("_", " ").title()
                    color = Colors.RED if issue_type == "security" else Colors.YELLOW
                    print(f"\n  {color}{title}:{Colors.END}")
                    for i, issue in enumerate(issues[:3]):
                        print(f"    - {issue['message']} ({issue['file']})")
                    if len(issues) > 3:
                        print(f"    - ... e mais {len(issues) - 3} problemas")
        
        # Detalhes do relatório
        print(f"\n{Colors.BOLD}Relatório completo:{Colors.END}")
        print(f"  • Salvo em: {self.report_file}")
        print("=" * 70)
        print()

def watch_changes(seconds=5):
    """Monitora alterações nos arquivos e executa verificações automaticamente"""
    logger.info(f"Iniciando monitoramento de alterações (intervalo: {seconds}s)")
    
    last_modified_times = {}
    
    # Coletar informações iniciais sobre os arquivos
    for ext in ["*.py", "*.js", "*.css", "*.html"]:
        for file_path in glob.glob(f"**/{ext}", recursive=True):
            if "venv" not in file_path and "test" not in file_path:
                try:
                    last_modified_times[file_path] = os.path.getmtime(file_path)
                except:
                    pass
    
    logger.info(f"Monitorando {len(last_modified_times)} arquivos")
    
    try:
        while True:
            changes = []
            
            # Verificar alterações
            for file_path, last_mtime in list(last_modified_times.items()):
                try:
                    current_mtime = os.path.getmtime(file_path)
                    if current_mtime > last_mtime:
                        changes.append(file_path)
                        last_modified_times[file_path] = current_mtime
                except:
                    # Arquivo foi removido
                    changes.append(f"{file_path} (removido)")
                    del last_modified_times[file_path]
            
            # Verificar novos arquivos
            for ext in ["*.py", "*.js", "*.css", "*.html"]:
                for file_path in glob.glob(f"**/{ext}", recursive=True):
                    if "venv" not in file_path and "test" not in file_path and file_path not in last_modified_times:
                        changes.append(f"{file_path} (novo)")
                        last_modified_times[file_path] = os.path.getmtime(file_path)
            
            # Se houver alterações, executar verificações
            if changes:
                logger.info(f"Detectadas {len(changes)} alterações")
                for change in changes[:5]:
                    logger.info(f"  - {change}")
                
                if len(changes) > 5:
                    logger.info(f"  - ... e mais {len(changes) - 5} alterações")
                
                print("\n" + "=" * 70)
                print(f"{Colors.BOLD}ALTERAÇÕES DETECTADAS{Colors.END}".center(70))
                print("=" * 70)
                print(f"\nExecutando verificação automática...\n")
                
                checker = ZelopackAutoCheck()
                checker.run_checks(fix_issues=False)
            
            # Aguardar antes da próxima verificação
            time.sleep(seconds)
    except KeyboardInterrupt:
        logger.info("Monitoramento interrompido pelo usuário")
        print("\nMonitoramento encerrado.")
    except Exception as e:
        logger.error(f"Erro no monitoramento: {e}")
        print(f"\n{Colors.RED}Erro no monitoramento: {e}{Colors.END}")

def schedule_checks(minutes=5):
    """Agenda verificações periódicas"""
    logger.info(f"Agendando verificações a cada {minutes} minutos")
    
    try:
        while True:
            # Executar verificação
            print("\n" + "=" * 70)
            print(f"{Colors.BOLD}VERIFICAÇÃO AGENDADA{Colors.END}".center(70))
            print("=" * 70)
            print(f"\nExecutando verificação automática...\n")
            
            checker = ZelopackAutoCheck()
            checker.run_checks(fix_issues=True)
            
            # Aguardar até a próxima verificação
            next_check = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            print(f"\nPróxima verificação agendada para: {next_check.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Dormir até a próxima verificação
            time.sleep(minutes * 60)
    except KeyboardInterrupt:
        logger.info("Agendamento interrompido pelo usuário")
        print("\nAgendamento encerrado.")
    except Exception as e:
        logger.error(f"Erro no agendamento: {e}")
        print(f"\n{Colors.RED}Erro no agendamento: {e}{Colors.END}")

def setup_cron_job():
    """Configura um job cron para verificações automatizadas"""
    script_path = os.path.abspath(__file__)
    
    if sys.platform == "linux" or sys.platform == "darwin":
        # Para sistemas Unix-like
        try:
            # Ver se já está no crontab
            result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
            current_crontab = result.stdout
            
            # Verificar se o script já está configurado
            if script_path in current_crontab:
                print("Job cron já está configurado")
                return
            
            # Configurar o cron para executar a cada 5 minutos
            cron_line = f"*/5 * * * * {sys.executable} {script_path} --test --fix\n"
            new_crontab = current_crontab + cron_line
            
            # Escrever em um arquivo temporário
            with open("/tmp/zelopack_crontab", "w") as f:
                f.write(new_crontab)
            
            # Instalar o novo crontab
            subprocess.run("crontab /tmp/zelopack_crontab", shell=True, check=True)
            os.remove("/tmp/zelopack_crontab")
            
            print("Job cron configurado com sucesso para executar a cada 5 minutos")
        except Exception as e:
            logger.error(f"Erro ao configurar cron job: {e}")
            print(f"{Colors.RED}Erro ao configurar cron job: {e}{Colors.END}")
    else:
        # Para Windows
        try:
            # Criar arquivo batch para executar o script
            batch_file = os.path.join(os.path.dirname(script_path), "auto_check_scheduled.bat")
            with open(batch_file, 'w') as f:
                f.write(f'@echo off\n"{sys.executable}" "{script_path}" --test --fix\n')
            
            # Agendar a tarefa (windows task scheduler)
            task_name = "ZelopackAutoCheck"
            cmd = f'schtasks /create /sc MINUTE /mo 5 /tn "{task_name}" /tr "{batch_file}" /f'
            subprocess.run(cmd, shell=True, check=True)
            
            print("Job agendado no Task Scheduler para executar a cada 5 minutos")
        except Exception as e:
            logger.error(f"Erro ao configurar Task Scheduler: {e}")
            print(f"{Colors.RED}Erro ao configurar Task Scheduler: {e}{Colors.END}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Sistema Automatizado de Testes e Melhorias do Zelopack')
    
    # Opções principais
    group = parser.add_argument_group('Opções principais')
    group.add_argument('--test', action='store_true', help='Executar testes e verificações')
    group.add_argument('--fix', action='store_true', help='Executar testes e corrigir problemas automaticamente')
    group.add_argument('--watch', action='store_true', help='Monitorar alterações e testar continuamente')
    group.add_argument('--schedule', action='store_true', help='Agendar testes periódicos')
    
    # Opções adicionais
    parser.add_argument('--interval', type=int, default=5, help='Intervalo em segundos para monitoramento (--watch)')
    parser.add_argument('--minutes', type=int, default=5, help='Intervalo em minutos para verificação agendada (--schedule)')
    parser.add_argument('--setup-cron', action='store_true', help='Configurar job cron para verificações automatizadas')
    
    args = parser.parse_args()
    
    # Verificar opções conflitantes
    options_count = sum([args.test, args.fix, args.watch, args.schedule, args.setup_cron])
    if options_count > 1:
        print(f"{Colors.RED}Erro: Escolha apenas uma das opções principales{Colors.END}")
        parser.print_help()
        return
    
    # Executar a opção selecionada
    if args.test:
        checker = ZelopackAutoCheck()
        checker.run_checks(fix_issues=False)
    elif args.fix:
        checker = ZelopackAutoCheck()
        checker.run_checks(fix_issues=True)
    elif args.watch:
        watch_changes(seconds=args.interval)
    elif args.schedule:
        schedule_checks(minutes=args.minutes)
    elif args.setup_cron:
        setup_cron_job()
    else:
        # Se nenhuma opção foi especificada, executar verificação simples
        checker = ZelopackAutoCheck()
        checker.run_checks(fix_issues=False)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        print(f"\n{Colors.RED}Erro inesperado: {e}{Colors.END}")