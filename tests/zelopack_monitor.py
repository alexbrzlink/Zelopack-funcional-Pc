#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Monitoramento e Melhoria Contínua para Zelopack

Este script executa:
1. Testes periódicos de todos os componentes
2. Análise de código e busca por possíveis melhorias
3. Geração de relatórios com sugestões inteligentes
4. Correção automática de problemas simples (quando possível)
"""

import os
import sys
import re
import json
import time
import logging
import datetime
import subprocess
from pathlib import Path
import importlib

# Configurações de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("zelopack_monitor.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("zelopack_monitor")

# Diretório base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Arquivos e diretórios importantes
REPORTS_DIR = os.path.join(BASE_DIR, "tests", "reports")
RULES_FILE = os.path.join(BASE_DIR, "tests", "improvement_rules.json")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
BLUEPRINT_DIR = os.path.join(BASE_DIR, "blueprints")

# Criar diretórios necessários
os.makedirs(REPORTS_DIR, exist_ok=True)

class ZelopackMonitor:
    """Sistema de monitoramento inteligente do Zelopack"""
    
    def __init__(self):
        """Inicializar o monitor"""
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.report_file = os.path.join(REPORTS_DIR, f"zelopack_report_{self.timestamp}.json")
        self.text_report_file = os.path.join(REPORTS_DIR, f"zelopack_report_{self.timestamp}.txt")
        self.improvements = []
        self.test_results = {}
        self.performance_issues = []
        self.auto_fixes = []
        self.improvement_rules = self.load_improvement_rules()
    
    def load_improvement_rules(self):
        """Carrega regras de melhoria do arquivo JSON ou usa padrões"""
        default_rules = {
            "python": {
                "imports": {
                    "unused_imports": {"level": "warning", "auto_fix": True},
                    "wildcard_imports": {"level": "warning", "auto_fix": False}
                },
                "code_style": {
                    "line_too_long": {"level": "warning", "auto_fix": False, "max_length": 100},
                    "too_many_args": {"level": "warning", "auto_fix": False, "max_args": 5},
                    "too_many_locals": {"level": "warning", "auto_fix": False, "max_locals": 10},
                    "too_complex": {"level": "warning", "auto_fix": False, "max_complexity": 10}
                },
                "security": {
                    "hardcoded_passwords": {"level": "critical", "auto_fix": False},
                    "sql_injection": {"level": "critical", "auto_fix": False},
                    "debug_enabled": {"level": "warning", "auto_fix": True}
                }
            },
            "javascript": {
                "code_style": {
                    "missing_semicolons": {"level": "warning", "auto_fix": True},
                    "console_log": {"level": "warning", "auto_fix": True},
                    "unused_vars": {"level": "warning", "auto_fix": False}
                },
                "security": {
                    "eval_usage": {"level": "critical", "auto_fix": False},
                    "innerhtml": {"level": "warning", "auto_fix": False}
                }
            },
            "html": {
                "accessibility": {
                    "missing_alt": {"level": "warning", "auto_fix": True},
                    "missing_labels": {"level": "warning", "auto_fix": False}
                },
                "best_practices": {
                    "inline_styles": {"level": "info", "auto_fix": False},
                    "inline_scripts": {"level": "info", "auto_fix": False}
                }
            },
            "css": {
                "best_practices": {
                    "important_usage": {"level": "warning", "auto_fix": False},
                    "vendor_prefixes": {"level": "info", "auto_fix": False}
                }
            },
            "flask": {
                "security": {
                    "csrf_protection": {"level": "critical", "auto_fix": False},
                    "secure_session": {"level": "critical", "auto_fix": False},
                    "debug_mode": {"level": "critical", "auto_fix": True}
                },
                "best_practices": {
                    "hardcoded_urls": {"level": "warning", "auto_fix": False},
                    "form_validation": {"level": "warning", "auto_fix": False}
                }
            }
        }
        
        try:
            if os.path.exists(RULES_FILE):
                with open(RULES_FILE, 'r') as f:
                    loaded_rules = json.load(f)
                return loaded_rules
            else:
                # Se o arquivo não existe, criar com as regras padrão
                with open(RULES_FILE, 'w') as f:
                    json.dump(default_rules, f, indent=2)
                return default_rules
        except Exception as e:
            logger.error(f"Erro ao carregar regras: {e}")
            return default_rules
    
    def run_component_tests(self):
        """Executa os testes de componentes"""
        logger.info("Executando testes de componentes...")
        
        test_dirs = ["tests"]
        test_files = []
        
        # Encontrar arquivos de teste
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                for root, _, files in os.walk(test_dir):
                    for file in files:
                        if file.startswith("test_") and file.endswith(".py") and file != "test_components.py":
                            test_files.append(os.path.join(root, file))
        
        test_results = {
            "passed": [],
            "failed": [],
            "errors": [],
            "details": {}
        }
        
        # Executar cada arquivo de teste
        for test_file in test_files:
            test_name = os.path.splitext(os.path.basename(test_file))[0]
            
            try:
                # Executar o teste usando subprocess
                logger.info(f"Executando {test_name}...")
                result = subprocess.run(
                    [sys.executable, test_file],
                    capture_output=True,
                    text=True,
                    timeout=60  # Timeout de 1 minuto
                )
                
                # Analisar a saída e determinar o resultado
                output = result.stdout + result.stderr
                
                # Considerar o teste como bem-sucedido se o código de retorno for 0
                if result.returncode == 0:
                    test_results["passed"].append(test_name)
                    test_results["details"][test_name] = {
                        "status": "passed",
                        "output": output,
                        "returncode": result.returncode
                    }
                    logger.info(f"{test_name} PASSOU")
                else:
                    # Verificar se é erro ou falha
                    test_results["failed"].append(test_name)
                    test_results["details"][test_name] = {
                        "status": "failed",
                        "output": output,
                        "returncode": result.returncode
                    }
                    logger.warning(f"{test_name} FALHOU")
                
            except subprocess.TimeoutExpired:
                test_results["errors"].append(test_name)
                test_results["details"][test_name] = {
                    "status": "error",
                    "output": "Timeout ao executar o teste",
                    "returncode": -1
                }
                logger.error(f"{test_name} TIMEOUT")
            except Exception as e:
                test_results["errors"].append(test_name)
                test_results["details"][test_name] = {
                    "status": "error",
                    "output": str(e),
                    "returncode": -1
                }
                logger.error(f"{test_name} ERRO: {e}")
        
        logger.info(f"Testes concluídos: {len(test_results['passed'])} passaram, "
                  f"{len(test_results['failed'])} falharam, "
                  f"{len(test_results['errors'])} erros")
        
        self.test_results = test_results
        return test_results
    
    def analyze_file(self, file_path):
        """Analisa um arquivo em busca de melhorias"""
        if not os.path.exists(file_path):
            return []
        
        file_improvements = []
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Análise baseada no tipo de arquivo
            if ext == '.py':
                file_improvements.extend(self._analyze_python(file_path, content, lines))
            elif ext == '.js':
                file_improvements.extend(self._analyze_javascript(file_path, content, lines))
            elif ext == '.html':
                file_improvements.extend(self._analyze_html(file_path, content, lines))
            elif ext == '.css':
                file_improvements.extend(self._analyze_css(file_path, content, lines))
            
            # Verificar problemas gerais para todos os tipos de arquivo
            file_improvements.extend(self._analyze_general(file_path, content, lines))
            
        except Exception as e:
            logger.error(f"Erro ao analisar {file_path}: {e}")
        
        return file_improvements
    
    def _analyze_python(self, file_path, content, lines):
        """Analisa código Python"""
        improvements = []
        
        # Verificar imports não utilizados
        imports = re.findall(r'^(?:from\s+[\w.]+\s+import\s+(?:[^(]*)|\s*import\s+(?:[^(]*))', content, re.MULTILINE)
        if imports:
            imported_names = []
            
            # Extrair os nomes importados
            for imp in imports:
                if 'from' in imp:
                    match = re.search(r'from\s+[\w.]+\s+import\s+(.*)', imp)
                    if match:
                        names = match.group(1).split(',')
                        for name in names:
                            clean_name = name.strip().split(' as ')[0].strip()
                            if clean_name:
                                imported_names.append(clean_name)
                else:
                    match = re.search(r'import\s+(.*)', imp)
                    if match:
                        names = match.group(1).split(',')
                        for name in names:
                            clean_name = name.strip().split(' as ')[0].strip()
                            if clean_name:
                                imported_names.append(clean_name)
            
            # Verificar uso de cada nome importado
            for name in imported_names:
                # Remover o próprio import da análise
                pattern = fr'from\s+[\w.]+\s+import.*\b{name}\b|\bimport\s+.*\b{name}\b'
                content_without_import = re.sub(pattern, '', content, flags=re.MULTILINE)
                
                # Verificar se o nome aparece no código
                if not re.search(fr'\b{name}\b', content_without_import):
                    improvements.append({
                        "file": file_path,
                        "line": None,  # Linha não especificada
                        "type": "unused_import",
                        "severity": "warning",
                        "message": f"Import não utilizado: {name}",
                        "suggestion": f"Remova o import não utilizado para melhorar a clareza e o desempenho do código"
                    })
        
        # Verificar linhas muito longas
        for i, line in enumerate(lines):
            if len(line) > 100:
                improvements.append({
                    "file": file_path,
                    "line": i + 1,
                    "type": "line_too_long",
                    "severity": "info",
                    "message": f"Linha muito longa ({len(line)} caracteres)",
                    "suggestion": "Considere quebrar a linha para melhorar a legibilidade"
                })
        
        # Verificar funções muito complexas
        functions = re.finditer(r'def\s+(\w+)\s*\(([^)]*)\):', content)
        for func in functions:
            func_name = func.group(1)
            params = func.group(2).split(',')
            
            # Verificar número de parâmetros
            if len(params) > 5:
                improvements.append({
                    "file": file_path,
                    "line": content[:func.start()].count('\n') + 1,
                    "type": "too_many_args",
                    "severity": "warning",
                    "message": f"Função '{func_name}' tem muitos parâmetros ({len(params)})",
                    "suggestion": "Considere refatorar usando um dicionário, classe ou reduzindo a complexidade"
                })
        
        # Verificar problemas de segurança
        if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
            improvements.append({
                "file": file_path,
                "line": None,
                "type": "hardcoded_password",
                "severity": "critical",
                "message": "Possível senha hardcoded no código",
                "suggestion": "Use variáveis de ambiente ou um sistema seguro de gerenciamento de segredos"
            })
        
        if "eval(" in content:
            for i, line in enumerate(lines):
                if "eval(" in line:
                    improvements.append({
                        "file": file_path,
                        "line": i + 1,
                        "type": "eval_usage",
                        "severity": "critical",
                        "message": "Uso de eval() é perigoso e pode levar a vulnerabilidades",
                        "suggestion": "Evite usar eval(); encontre uma alternativa mais segura"
                    })
        
        # Verificar uso de print em código de produção
        if "print(" in content:
            for i, line in enumerate(lines):
                if "print(" in line and not line.strip().startswith("#"):
                    improvements.append({
                        "file": file_path,
                        "line": i + 1,
                        "type": "print_statement",
                        "severity": "warning",
                        "message": "Uso de print() em código de produção",
                        "suggestion": "Use logging para código de produção ao invés de print()"
                    })
        
        # Verificar modo de debug em produção
        if "DEBUG = True" in content:
            improvements.append({
                "file": file_path,
                "line": None,
                "type": "debug_mode",
                "severity": "critical",
                "message": "DEBUG = True pode ser inseguro em produção",
                "suggestion": "Use variáveis de ambiente para controlar o modo debug; desative em produção"
            })
        
        return improvements
    
    def _analyze_javascript(self, file_path, content, lines):
        """Analisa código JavaScript"""
        improvements = []
        
        # Verificar pontos e vírgulas faltando
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith('//') and not line.endswith(';') and \
               not line.endswith('{') and not line.endswith('}') and \
               not line.endswith(':') and not line.startswith('import') and \
               not line.endswith(',') and not line.endswith('(') and \
               not line.endswith('[') and line != "":
                improvements.append({
                    "file": file_path,
                    "line": i + 1,
                    "type": "missing_semicolon",
                    "severity": "warning",
                    "message": "Ponto e vírgula faltando",
                    "suggestion": "Adicione ponto e vírgula ao final da linha para evitar problemas de ASI (Automatic Semicolon Insertion)"
                })
        
        # Verificar uso de console.log
        for i, line in enumerate(lines):
            if "console.log" in line and not line.strip().startswith("//"):
                improvements.append({
                    "file": file_path,
                    "line": i + 1,
                    "type": "console_log",
                    "severity": "warning",
                    "message": "console.log() em código de produção",
                    "suggestion": "Remova ou comente os console.log() em código de produção"
                })
        
        # Verificar uso de var (em vez de let/const)
        for i, line in enumerate(lines):
            if re.search(r'\bvar\s+', line) and not line.strip().startswith("//"):
                improvements.append({
                    "file": file_path,
                    "line": i + 1,
                    "type": "var_usage",
                    "severity": "info",
                    "message": "Uso de 'var' em vez de let/const",
                    "suggestion": "Use 'const' para valores que não mudam e 'let' para variáveis que precisam ser reatribuídas"
                })
        
        # Verificar uso de eval()
        for i, line in enumerate(lines):
            if "eval(" in line and not line.strip().startswith("//"):
                improvements.append({
                    "file": file_path,
                    "line": i + 1,
                    "type": "eval_usage",
                    "severity": "critical",
                    "message": "Uso de eval() é perigoso e pode levar a vulnerabilidades",
                    "suggestion": "Evite usar eval(); encontre uma alternativa mais segura"
                })
        
        # Verificar uso inseguro de innerHTML
        for i, line in enumerate(lines):
            if "innerHTML" in line and not line.strip().startswith("//"):
                improvements.append({
                    "file": file_path,
                    "line": i + 1,
                    "type": "innerhtml_usage",
                    "severity": "warning",
                    "message": "Uso de innerHTML pode ser arriscado",
                    "suggestion": "Use textContent para conteúdo de texto ou técnicas mais seguras para HTML"
                })
        
        # Verificar uso de alert em código de produção
        for i, line in enumerate(lines):
            if "alert(" in line and not line.strip().startswith("//"):
                improvements.append({
                    "file": file_path,
                    "line": i + 1,
                    "type": "alert_usage",
                    "severity": "info",
                    "message": "Uso de alert() em código de produção",
                    "suggestion": "Use notificações modernas ou componentes de UI ao invés de alert()"
                })
        
        return improvements
    
    def _analyze_html(self, file_path, content, lines):
        """Analisa código HTML"""
        improvements = []
        
        # Verificar tags img sem alt
        img_tags = re.findall(r'<img\s+[^>]*>', content)
        for img in img_tags:
            if 'alt=' not in img.lower():
                improvements.append({
                    "file": file_path,
                    "line": None,
                    "type": "missing_alt",
                    "severity": "warning",
                    "message": "Tag <img> sem atributo alt",
                    "suggestion": "Adicione o atributo alt para acessibilidade e SEO"
                })
        
        # Verificar inputs sem label
        input_tags = re.findall(r'<input\s+[^>]*>', content)
        for input_tag in input_tags:
            # Ignorar inputs hidden, submit, button e image
            if re.search(r'type\s*=\s*["\'](?:hidden|submit|button|image)["\']', input_tag, re.IGNORECASE):
                continue
            
            # Extrair id do input, se existir
            id_match = re.search(r'id\s*=\s*["\']([^"\']+)["\']', input_tag)
            if id_match:
                input_id = id_match.group(1)
                
                # Verificar se existe um label associado
                label_pattern = fr'<label\s+[^>]*for\s*=\s*["\']({input_id})["\'][^>]*>'
                if not re.search(label_pattern, content, re.IGNORECASE):
                    improvements.append({
                        "file": file_path,
                        "line": None,
                        "type": "missing_label",
                        "severity": "warning",
                        "message": f"Input com id='{input_id}' não tem label associado",
                        "suggestion": "Adicione um <label> com atributo 'for' para melhorar a acessibilidade"
                    })
        
        # Verificar estilos inline
        inline_styles = re.findall(r'style\s*=\s*["\'][^"\']*["\']', content)
        if len(inline_styles) > 5:  # Mais de 5 estilos inline pode indicar um problema
            improvements.append({
                "file": file_path,
                "line": None,
                "type": "inline_styles",
                "severity": "info",
                "message": f"Uso excessivo de estilos inline ({len(inline_styles)} ocorrências)",
                "suggestion": "Mova os estilos para uma folha de estilo externa para melhor manutenibilidade"
            })
        
        # Verificar scripts inline
        inline_scripts = re.findall(r'<script\s*(?!src)[^>]*>[\s\S]*?</script>', content)
        if len(inline_scripts) > 2:  # Mais de 2 scripts inline pode indicar um problema
            improvements.append({
                "file": file_path,
                "line": None,
                "type": "inline_scripts",
                "severity": "info",
                "message": f"Uso excessivo de scripts inline ({len(inline_scripts)} ocorrências)",
                "suggestion": "Mova os scripts para arquivos externos para melhor manutenibilidade e cachê"
            })
        
        # Verificar URLs hardcoded (sem url_for() ou similar)
        hardcoded_urls = re.findall(r'(?:href|src)\s*=\s*["\'](?!{{\s*url_for|{{\s*static|https?://|#|javascript:)(/\S+)["\']', content)
        if hardcoded_urls:
            improvements.append({
                "file": file_path,
                "line": None, 
                "type": "hardcoded_urls",
                "severity": "warning",
                "message": f"URLs hardcoded ({len(hardcoded_urls)} ocorrências)",
                "suggestion": "Use funções como url_for() para gerar URLs dinâmicas"
            })
        
        return improvements
    
    def _analyze_css(self, file_path, content, lines):
        """Analisa código CSS"""
        improvements = []
        
        # Verificar uso excessivo de !important
        important_count = content.count('!important')
        if important_count > 5:
            improvements.append({
                "file": file_path,
                "line": None,
                "type": "important_usage",
                "severity": "warning",
                "message": f"Uso excessivo de !important ({important_count} ocorrências)",
                "suggestion": "Evite usar !important; melhore a especificidade dos seletores"
            })
        
        # Verificar vendor prefixes não padronizados
        vendor_prefixes = re.findall(r'-(?:webkit|moz|ms|o)-', content)
        if vendor_prefixes:
            improvements.append({
                "file": file_path,
                "line": None,
                "type": "vendor_prefixes",
                "severity": "info",
                "message": f"Uso de {len(vendor_prefixes)} vendor prefixes",
                "suggestion": "Considere usar autoprefixer ou uma ferramenta similar para gerenciar prefixos automaticamente"
            })
        
        # Verificar unidades absolutas (px vs rem/em)
        px_count = len(re.findall(r'\b\d+px\b', content))
        relative_count = len(re.findall(r'\b\d+(?:rem|em|%|vh|vw)\b', content))
        
        if px_count > 2 * relative_count and px_count > 10:
            improvements.append({
                "file": file_path,
                "line": None,
                "type": "absolute_units",
                "severity": "info",
                "message": f"Uso excessivo de unidades px ({px_count} ocorrências) vs unidades relativas ({relative_count} ocorrências)",
                "suggestion": "Prefira unidades relativas (rem, em, %) para melhor responsividade"
            })
        
        # Verificar classes/IDs com nomes muito longos
        selectors = re.findall(r'[.#]([a-zA-Z0-9_-]+)', content)
        for selector in selectors:
            if len(selector) > 30:
                improvements.append({
                    "file": file_path,
                    "line": None,
                    "type": "long_selector",
                    "severity": "info",
                    "message": f"Seletor muito longo: {selector}",
                    "suggestion": "Use nomes mais curtos e descritivos para classes e IDs"
                })
        
        return improvements
    
    def _analyze_general(self, file_path, content, lines):
        """Analisa problemas gerais em qualquer tipo de arquivo"""
        improvements = []
        
        # Verificar linhas em branco excessivas
        blank_lines = [i for i, line in enumerate(lines) if line.strip() == ""]
        consecutive_blank_lines = 0
        for i in range(1, len(blank_lines)):
            if blank_lines[i] == blank_lines[i-1] + 1:
                consecutive_blank_lines += 1
                
                # Reportar 3 ou mais linhas em branco consecutivas
                if consecutive_blank_lines >= 2:  # 3 linhas consecutivas
                    improvements.append({
                        "file": file_path,
                        "line": blank_lines[i-2] + 1,
                        "type": "excess_blank_lines",
                        "severity": "info",
                        "message": "Linhas em branco excessivas",
                        "suggestion": "Remova linhas em branco desnecessárias para melhorar a legibilidade"
                    })
                    consecutive_blank_lines = 0
            else:
                consecutive_blank_lines = 0
        
        # Verificar arquivo muito grande (>500 linhas)
        if len(lines) > 500:
            improvements.append({
                "file": file_path,
                "line": None,
                "type": "file_too_large",
                "severity": "warning",
                "message": f"Arquivo muito grande ({len(lines)} linhas)",
                "suggestion": "Considere dividir o arquivo em módulos menores para melhorar a manutenibilidade"
            })
        
        # Verificar linhas com mix de tabs e espaços
        for i, line in enumerate(lines):
            if '\t' in line and '    ' in line:
                improvements.append({
                    "file": file_path,
                    "line": i + 1,
                    "type": "mixed_indentation",
                    "severity": "warning",
                    "message": "Linha com mix de tabs e espaços",
                    "suggestion": "Use consistentemente tabs OU espaços para indentação, não ambos"
                })
        
        # Verificar caracteres especiais indesejados (ex: BOM, zero-width spaces)
        special_chars = [
            ('\ufeff', 'Byte Order Mark (BOM)'),
            ('\u200b', 'Zero-width space'),
            ('\u00a0', 'Non-breaking space')
        ]
        
        for char, name in special_chars:
            if char in content:
                improvements.append({
                    "file": file_path,
                    "line": None,
                    "type": "special_characters",
                    "severity": "warning",
                    "message": f"Caractere especial encontrado: {name}",
                    "suggestion": "Remova caracteres especiais invisíveis que podem causar problemas"
                })
        
        return improvements
    
    def scan_for_improvements(self):
        """Escaneia o código em busca de possíveis melhorias"""
        logger.info("Escaneando código em busca de melhorias...")
        
        # Diretórios para escanear
        dirs_to_scan = [".", "static", "templates", "blueprints"]
        file_count = 0
        
        # Extensões de arquivo para escanear
        extensions = ['.py', '.js', '.html', '.css']
        
        # Coletar arquivos para analisar
        files_to_analyze = []
        for dir_path in dirs_to_scan:
            if os.path.exists(dir_path):
                for root, _, files in os.walk(dir_path):
                    # Pular diretórios de teste e virtualenv
                    if "tests/" in root + "/" or "venv/" in root + "/" or "__pycache__/" in root + "/":
                        continue
                    
                    for file in files:
                        if any(file.endswith(ext) for ext in extensions):
                            file_path = os.path.join(root, file)
                            files_to_analyze.append(file_path)
        
        # Analisar cada arquivo
        all_improvements = []
        for file_path in files_to_analyze:
            file_improvements = self.analyze_file(file_path)
            if file_improvements:
                all_improvements.extend(file_improvements)
                logger.info(f"Encontradas {len(file_improvements)} possíveis melhorias em {file_path}")
            file_count += 1
        
        self.improvements = all_improvements
        logger.info(f"Escaneamento concluído: {file_count} arquivos analisados, {len(all_improvements)} possíveis melhorias encontradas")
        
        # Agrupar por severidade
        severity_counts = {"critical": 0, "warning": 0, "info": 0}
        for improvement in all_improvements:
            severity = improvement.get("severity", "info")
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        logger.info(f"Distribuição de severidade: {severity_counts['critical']} críticas, "
                   f"{severity_counts['warning']} avisos, {severity_counts['info']} informações")
        
        return all_improvements
    
    def check_performance(self):
        """Verifica métricas de performance do sistema"""
        logger.info("Verificando métricas de performance...")
        
        performance_issues = []
        
        # Verificar arquivos CSS e JS não minificados
        for ext, folder in [('.css', 'static/css'), ('.js', 'static/js')]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if file.endswith(ext) and not file.endswith('.min' + ext):
                        file_path = os.path.join(folder, file)
                        try:
                            size = os.path.getsize(file_path) / 1024  # KB
                            if size > 50:  # Mais de 50KB pode ser candidato a minificação
                                performance_issues.append({
                                    "type": "large_unminified_file",
                                    "file": file_path,
                                    "size_kb": round(size, 2),
                                    "message": f"Arquivo grande não minificado: {file_path} ({round(size, 2)} KB)",
                                    "suggestion": f"Considere minificar este arquivo para melhorar o tempo de carregamento"
                                })
                        except Exception as e:
                            logger.error(f"Erro ao verificar tamanho de {file_path}: {e}")
        
        # Verificar imagens não otimizadas
        image_folders = ['static/img', 'static/images']
        large_images = []
        
        for folder in image_folders:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            file_path = os.path.join(root, file)
                            try:
                                size = os.path.getsize(file_path) / 1024  # KB
                                if size > 200:  # Mais de 200KB pode ser candidato a otimização
                                    large_images.append({
                                        "path": file_path,
                                        "size_kb": round(size, 2)
                                    })
                            except Exception as e:
                                logger.error(f"Erro ao verificar tamanho de {file_path}: {e}")
        
        if large_images:
            performance_issues.append({
                "type": "large_images",
                "images": large_images,
                "message": f"Encontradas {len(large_images)} imagens grandes que podem afetar o desempenho",
                "suggestion": "Otimize as imagens usando ferramentas como TinyPNG, ou considere formatos como WebP"
            })
        
        # Verificar funções Python potencialmente lentas
        python_files = []
        for root, _, files in os.walk("."):
            # Pular diretórios de teste e virtualenv
            if "tests/" in root + "/" or "venv/" in root + "/" or "__pycache__/" in root + "/":
                continue
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar operações potencialmente lentas em loops
                nested_loops = re.findall(r'for\s+\w+\s+in\s+.*:\s*\n\s+for\s+\w+\s+in', content)
                if nested_loops:
                    performance_issues.append({
                        "type": "nested_loops",
                        "file": file_path,
                        "count": len(nested_loops),
                        "message": f"Encontrados {len(nested_loops)} loops aninhados potencialmente lentos em {file_path}",
                        "suggestion": "Considere otimizar loops aninhados para melhorar o desempenho"
                    })
                
                # Verificar operações lentas em loops
                slow_ops_in_loops = []
                if re.search(r'for\s+.*:\s*\n\s+.*\bdb\.\b', content, re.MULTILINE):
                    slow_ops_in_loops.append("operações de banco de dados")
                
                if re.search(r'for\s+.*:\s*\n\s+.*\b(?:requests\.|urllib\.|http\.|json\.loads\(|json\.dumps\()', content, re.MULTILINE):
                    slow_ops_in_loops.append("operações de rede/IO")
                
                if slow_ops_in_loops:
                    performance_issues.append({
                        "type": "slow_operations_in_loops",
                        "file": file_path,
                        "operations": slow_ops_in_loops,
                        "message": f"Possíveis operações lentas em loops em {file_path}: {', '.join(slow_ops_in_loops)}",
                        "suggestion": "Mova operações lentas para fora dos loops quando possível"
                    })
            
            except Exception as e:
                logger.error(f"Erro ao analisar desempenho de {file_path}: {e}")
        
        # Verificar consultas SQL não indexadas
        sql_operations = []
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Procurar por possíveis consultas SQL
                if re.search(r'\.query\.\b(?:filter\(|order_by\(|join\()', content):
                    sql_operations.append(file_path)
            except Exception as e:
                logger.error(f"Erro ao analisar consultas SQL em {file_path}: {e}")
        
        if sql_operations:
            performance_issues.append({
                "type": "potentially_unindexed_queries",
                "files": sql_operations,
                "message": f"Possíveis consultas SQL não otimizadas em {len(sql_operations)} arquivos",
                "suggestion": "Verifique se as consultas usam campos indexados e se há otimizações necessárias (eager loading, paginação, etc.)"
            })
        
        self.performance_issues = performance_issues
        logger.info(f"Verificação de performance concluída: {len(performance_issues)} problemas encontrados")
        
        return performance_issues
    
    def auto_fix_issues(self, improvements, dry_run=True):
        """Tenta corrigir automaticamente problemas simples"""
        logger.info(f"{'Simulando' if dry_run else 'Aplicando'} correções automáticas...")
        
        fixes = []
        
        for improvement in improvements:
            file_path = improvement.get("file")
            fix_type = improvement.get("type")
            line_num = improvement.get("line")
            
            # Pular se não temos o arquivo ou tipo
            if not file_path or not os.path.exists(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                fixed = False
                new_lines = lines.copy()
                
                # Aplicar correção com base no tipo
                if fix_type == "missing_semicolon" and line_num is not None:
                    # Adicionar ponto e vírgula
                    line_idx = line_num - 1
                    if line_idx < len(lines):
                        line = lines[line_idx].rstrip()
                        if not line.endswith(';') and not line.endswith('{') and not line.endswith('}'):
                            new_lines[line_idx] = line + ';\n'
                            fixed = True
                
                elif fix_type == "console_log" and line_num is not None:
                    # Comentar console.log
                    line_idx = line_num - 1
                    if line_idx < len(lines) and "console.log" in lines[line_idx]:
                        new_lines[line_idx] = "// " + lines[line_idx]
                        fixed = True
                
                elif fix_type == "print_statement" and line_num is not None:
                    # Transformar print em logging
                    line_idx = line_num - 1
                    if line_idx < len(lines) and "print(" in lines[line_idx]:
                        # Verificar se temos import logging
                        has_logging_import = any("import logging" in line for line in lines)
                        has_logger_setup = any("logger =" in line for line in lines)
                        
                        # Transformar print em logger.info
                        line = lines[line_idx]
                        new_line = line.replace("print(", "logger.info(")
                        new_lines[line_idx] = new_line
                        
                        # Adicionar import de logging se necessário
                        if not has_logging_import:
                            new_lines.insert(0, "import logging\n")
                        
                        # Adicionar configuração do logger se necessário
                        if not has_logger_setup:
                            new_lines.insert(1 if has_logging_import else 1, "logger = logging.getLogger(__name__)\n")
                        
                        fixed = True
                
                elif fix_type == "missing_alt":
                    # Adicionar atributos alt às tags img
                    content = ''.join(lines)
                    new_content = re.sub(
                        r'(<img\s+[^>]*)(?!\s+alt=)([^>]*>)',
                        r'\1 alt="Imagem"\2',
                        content
                    )
                    
                    if new_content != content:
                        new_lines = new_content.splitlines(True)
                        fixed = True
                
                elif fix_type == "debug_mode":
                    # Corrigir DEBUG = True
                    content = ''.join(lines)
                    if "DEBUG = True" in content:
                        new_content = content.replace(
                            "DEBUG = True",
                            "DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'"
                        )
                        
                        # Adicionar import de os se necessário
                        if "import os" not in content:
                            if "import " in content:
                                # Encontrar o último import
                                import_lines = [i for i, line in enumerate(lines) if line.strip().startswith("import ")]
                                if import_lines:
                                    last_import = max(import_lines)
                                    new_lines.insert(last_import + 1, "import os\n")
                            else:
                                # Adicionar no topo
                                new_lines.insert(0, "import os\n")
                        
                        new_lines = new_content.splitlines(True)
                        fixed = True
                
                elif fix_type == "var_usage" and line_num is not None:
                    # Substituir var por let
                    line_idx = line_num - 1
                    if line_idx < len(lines) and "var " in lines[line_idx]:
                        new_lines[line_idx] = lines[line_idx].replace("var ", "let ")
                        fixed = True
                
                # Se correções foram aplicadas e não é dry run, salvar o arquivo
                if fixed and not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                
                if fixed:
                    fixes.append({
                        "file": file_path, 
                        "type": fix_type,
                        "line": line_num,
                        "applied": not dry_run,
                        "message": improvement.get("message"),
                        "diff": "Simulação - não mostrado" if dry_run else "Correção aplicada"
                    })
                    logger.info(f"{'[SIMULAÇÃO] ' if dry_run else ''}Corrigido: {file_path} - {improvement.get('message')}")
            
            except Exception as e:
                logger.error(f"Erro ao tentar corrigir {file_path}: {e}")
        
        self.auto_fixes = fixes
        logger.info(f"{'Simulação de correções' if dry_run else 'Correções'} concluída: {len(fixes)} problemas {'seriam' if dry_run else 'foram'} corrigidos")
        
        return fixes
    
    def generate_report(self, test_results, improvements, performance_issues, fixes):
        """Gera um relatório detalhado com os resultados"""
        logger.info("Gerando relatório detalhado...")
        
        # Contar severidades
        severity_counts = {"critical": 0, "warning": 0, "info": 0}
        for improvement in improvements:
            severity = improvement.get("severity", "info")
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Preparar relatório
        report = {
            "timestamp": self.timestamp,
            "test_results": test_results,
            "improvements": {
                "total": len(improvements),
                "by_severity": severity_counts,
                "critical_issues": severity_counts["critical"],
                "details": improvements
            },
            "performance_issues": {
                "total": len(performance_issues),
                "details": performance_issues
            },
            "auto_fixes": {
                "total": len(fixes),
                "applied": sum(1 for fix in fixes if fix.get("applied", False)),
                "details": fixes
            }
        }
        
        # Salvar relatório como JSON
        with open(self.report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Gerar versão textual do relatório
        self.generate_text_report(report, self.text_report_file)
        
        logger.info(f"Relatório gerado: {self.report_file}")
        return report
    
    def generate_text_report(self, report, filename):
        """Gera uma versão em texto do relatório para fácil leitura"""
        with open(filename, 'w') as f:
            f.write("=== RELATÓRIO DE MONITORAMENTO ZELOPACK ===\n")
            f.write(f"Data: {report['timestamp']}\n\n")
            
            # Resumo
            f.write("=== RESUMO ===\n")
            tests_passed = len(report['test_results'].get('passed', []))
            tests_failed = len(report['test_results'].get('failed', [])) + len(report['test_results'].get('errors', []))
            test_status = "PASSOU" if tests_failed == 0 else "FALHOU"
            
            f.write(f"Testes: {test_status}\n")
            f.write(f"Problemas críticos: {report['improvements']['critical_issues']}\n")
            f.write(f"Avisos: {report['improvements']['by_severity']['warning']}\n")
            f.write(f"Sugestões: {report['improvements']['by_severity']['info']}\n")
            f.write(f"Problemas de performance: {report['performance_issues']['total']}\n\n")
            
            # Resultados dos testes
            f.write("=== RESULTADOS DOS TESTES ===\n")
            if tests_failed > 0:
                f.write("Status: FALHA\n")
                f.write(f"Código de retorno: 1\n\n")
            else:
                f.write("Status: SUCESSO\n")
                f.write(f"Código de retorno: 0\n\n")
            
            # Avisos (severity warning)
            f.write("=== AVISOS ===\n")
            warnings = [imp for imp in report['improvements']['details'] if imp.get('severity') == 'warning']
            for warning in warnings[:10]:  # Mostrar os primeiros 10
                file_info = f"{warning['file']}, Linha: {warning['line']}" if warning.get('line') else warning['file']
                f.write(f"Arquivo: {file_info}\n")
                f.write(f"Mensagem: {warning['message']}\n")
                if 'suggestion' in warning:
                    f.write(f"Sugestão: {warning['suggestion']}\n")
                f.write("\n")
            
            if len(warnings) > 10:
                f.write(f"... e mais {len(warnings) - 10} avisos\n\n")
            
            # Problemas críticos
            f.write("=== PROBLEMAS CRÍTICOS ===\n")
            criticals = [imp for imp in report['improvements']['details'] if imp.get('severity') == 'critical']
            if criticals:
                for critical in criticals:
                    file_info = f"{critical['file']}, Linha: {critical['line']}" if critical.get('line') else critical['file']
                    f.write(f"Arquivo: {file_info}\n")
                    f.write(f"Mensagem: {critical['message']}\n")
                    if 'suggestion' in critical:
                        f.write(f"Sugestão: {critical['suggestion']}\n")
                    f.write("\n")
            else:
                f.write("Nenhum problema crítico encontrado.\n\n")
            
            # Problemas de performance
            f.write("=== PROBLEMAS DE PERFORMANCE ===\n")
            if report['performance_issues']['details']:
                for issue in report['performance_issues']['details']:
                    f.write(f"Tipo: {issue['type']}\n")
                    f.write(f"Mensagem: {issue['message']}\n")
                    if 'suggestion' in issue:
                        f.write(f"Sugestão: {issue['suggestion']}\n")
                    f.write("\n")
            else:
                f.write("Nenhum problema de performance encontrado.\n\n")
            
            # Correções automáticas
            f.write("=== CORREÇÕES AUTOMÁTICAS ===\n")
            if report['auto_fixes']['details']:
                f.write(f"Total de correções: {report['auto_fixes']['total']}\n")
                f.write(f"Correções aplicadas: {report['auto_fixes']['applied']}\n\n")
                
                for fix in report['auto_fixes']['details']:
                    status = "Aplicada" if fix.get('applied', False) else "Simulada"
                    file_info = f"{fix['file']}, Linha: {fix['line']}" if fix.get('line') else fix['file']
                    f.write(f"Arquivo: {file_info}\n")
                    f.write(f"Status: {status}\n")
                    f.write(f"Tipo: {fix['type']}\n")
                    f.write(f"Mensagem: {fix['message']}\n\n")
            else:
                f.write("Nenhuma correção automática aplicada ou simulada.\n\n")
            
            # Rodapé
            f.write("=== FIM DO RELATÓRIO ===\n")
            f.write(f"Relatório completo disponível em: {self.report_file}\n")
    
    def run_monitoring_cycle(self, fix_issues=False):
        """Executa um ciclo completo de monitoramento"""
        logger.info(f"Iniciando ciclo de monitoramento ({self.timestamp})")
        
        # Executar testes de componentes
        test_results = self.run_component_tests()
        
        # Escanear por melhorias
        improvements = self.scan_for_improvements()
        
        # Verificar problemas de performance
        performance_issues = self.check_performance()
        
        # Tentar corrigir problemas automaticamente
        fixes = self.auto_fix_issues(improvements, dry_run=not fix_issues)
        
        # Gerar relatório
        report = self.generate_report(test_results, improvements, performance_issues, fixes)
        
        # Exibir resumo no console
        self.print_summary(test_results, improvements, performance_issues, fixes)
        
        logger.info(f"Ciclo de monitoramento concluído. Relatório salvo em {self.report_file}")
        
        return report
    
    def print_summary(self, test_results, improvements, performance_issues, fixes):
        """Imprime um resumo dos resultados no console"""
        print("\n" + "=" * 80)
        print(" RESUMO DE MONITORAMENTO ZELOPACK ".center(80, "="))
        print("=" * 80)
        
        # Testes
        tests_passed = len(test_results.get('passed', []))
        tests_failed = len(test_results.get('failed', [])) + len(test_results.get('errors', []))
        print(f"\n[TESTES DE COMPONENTES]")
        print(f"  Passaram: {tests_passed}")
        print(f"  Falharam/Erros: {tests_failed}")
        
        # Melhorias
        severity_counts = {"critical": 0, "warning": 0, "info": 0}
        for improvement in improvements:
            severity = improvement.get("severity", "info")
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        print(f"\n[MELHORIAS POTENCIAIS]")
        print(f"  Problemas críticos: {severity_counts['critical']}")
        print(f"  Avisos: {severity_counts['warning']}")
        print(f"  Sugestões: {severity_counts['info']}")
        
        # Performance
        print(f"\n[PROBLEMAS DE PERFORMANCE]")
        print(f"  Total: {len(performance_issues)}")
        
        # Correções
        applied_fixes = sum(1 for fix in fixes if fix.get("applied", False))
        print(f"\n[CORREÇÕES AUTOMÁTICAS]")
        print(f"  Total simuladas/aplicadas: {len(fixes)}")
        print(f"  Efetivamente aplicadas: {applied_fixes}")
        
        # Relatório
        print(f"\n[RELATÓRIO]")
        print(f"  Relatório detalhado: {self.report_file}")
        print(f"  Relatório em texto: {self.text_report_file}")
        
        print("\n" + "=" * 80)

def setup_cron_job():
    """Configura um job cron para executar o monitor periodicamente"""
    script_path = os.path.abspath(__file__)
    
    if os.name != 'nt':  # Linux/MacOS
        try:
            # Verificar se já está no crontab
            result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
            current_crontab = result.stdout
            
            # Verificar se o script já está no crontab
            if script_path in current_crontab:
                logger.info("Monitor já está configurado no crontab")
                return
            
            # Adicionar ao crontab (executar a cada 4 horas)
            cron_line = f"0 */4 * * * {sys.executable} {script_path} --fix\n"
            
            if result.returncode == 0:
                new_crontab = current_crontab + cron_line
            else:
                new_crontab = cron_line
            
            # Salvar em arquivo temporário
            temp_file = "/tmp/zelopack_crontab"
            with open(temp_file, 'w') as f:
                f.write(new_crontab)
            
            # Instalar o crontab
            subprocess.run(f"crontab {temp_file}", shell=True, check=True)
            os.remove(temp_file)
            
            logger.info("Monitor agendado no crontab para executar a cada 4 horas")
        
        except Exception as e:
            logger.error(f"Erro ao configurar crontab: {e}")
    
    else:  # Windows
        try:
            # Criar arquivo batch para executar o script
            batch_file = os.path.join(os.path.dirname(script_path), "run_zelopack_monitor.bat")
            with open(batch_file, 'w') as f:
                f.write(f'@echo off\n"{sys.executable}" "{script_path}" --fix\n')
            
            # Agendar a tarefa (windows task scheduler)
            task_name = "ZelopackMonitor"
            cmd = f'schtasks /create /sc MINUTE /mo 5 /tn "{task_name}" /tr "{batch_file}" /f'
            subprocess.run(cmd, shell=True, check=True)
            
            logger.info("Monitor agendado no Task Scheduler para executar a cada 5 minutos")
        
        except Exception as e:
            logger.error(f"Erro ao configurar Task Scheduler: {e}")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Monitoramento Zelopack')
    parser.add_argument('--fix', action='store_true', help='Aplicar correções automáticas')
    parser.add_argument('--watch', action='store_true', help='Monitorar alterações continuamente')
    parser.add_argument('--schedule', action='store_true', help='Agendar execução periódica')
    parser.add_argument('--interval', type=int, default=60, help='Intervalo em segundos para modo watch')
    
    args = parser.parse_args()
    
    if args.schedule:
        setup_cron_job()
        return
    
    if args.watch:
        logger.info(f"Iniciando modo watch (intervalo: {args.interval}s)")
        
        try:
            last_run = 0
            while True:
                # Verificar se é hora de executar
                current_time = time.time()
                if current_time - last_run >= args.interval:
                    print("\n" + "=" * 80)
                    print(f" EXECUÇÃO PERIÓDICA - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".center(80, "="))
                    print("=" * 80 + "\n")
                    
                    monitor = ZelopackMonitor()
                    monitor.run_monitoring_cycle(fix_issues=args.fix)
                    
                    last_run = time.time()
                
                # Dormir por um curto período
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Monitoramento interrompido pelo usuário")
            print("\nMonitoramento interrompido pelo usuário.")
        
        return
    
    # Execução padrão (uma vez)
    monitor = ZelopackMonitor()
    monitor.run_monitoring_cycle(fix_issues=args.fix)

if __name__ == "__main__":
    main()