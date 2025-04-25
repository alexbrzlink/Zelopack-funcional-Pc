#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Assistente de IA para Zelopack

Este script usa inteligência artificial para:
1. Analisar o código e sugerir melhorias avançadas
2. Aprender com problemas e bugs encontrados
3. Gerar sugestões de otimização específicas para o projeto
4. Ajudar a resolver problemas complexos automaticamente
"""

import os
import sys
import json
import time
import logging
import re
import glob
import argparse
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/zelopack_ai.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('zelopack_ai')

# Diretórios
AI_DIR = 'tests/ai'
SUGGESTIONS_DIR = os.path.join(AI_DIR, 'suggestions')
REPORT_DIR = 'tests/reports'
MONITOR_SCRIPT = 'tests/zelopack_monitor.py'

# Criar diretórios necessários
os.makedirs(AI_DIR, exist_ok=True)
os.makedirs(SUGGESTIONS_DIR, exist_ok=True)

class ZelopackAI:
    """Assistente de IA para o Zelopack"""
    
    def __init__(self, openai_api_key=None):
        """Inicializar o assistente de IA"""
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        self.openai_available = self._check_openai_available()
        self.code_patterns = self._load_code_patterns()
        self.knowledge_base = self._load_knowledge_base()
        
    def _check_openai_available(self):
        """Verifica se a API OpenAI está disponível"""
        if not self.openai_api_key:
            logger.warning("Chave de API OpenAI não encontrada. Algumas funcionalidades avançadas não estarão disponíveis.")
            return False
            
        try:
            import openai
            openai.api_key = self.openai_api_key
            # Fazer uma chamada simples para testar
            openai.Completion.create(
                engine="davinci",
                prompt="Hello",
                max_tokens=5
            )
            logger.info("API OpenAI conectada com sucesso")
            return True
        except Exception as e:
            logger.warning(f"API OpenAI não disponível: {e}")
            return False
    
    def _load_code_patterns(self):
        """Carrega padrões de código para análise"""
        patterns_file = os.path.join(AI_DIR, 'code_patterns.json')
        
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar padrões de código: {e}")
        
        # Padrões padrão se o arquivo não existir
        default_patterns = {
            "bad_practices": [
                {
                    "language": "python",
                    "pattern": r"except Exception as e:(\s*pass|\s*print)",
                    "description": "Exceção capturada sem tratamento adequado",
                    "suggestion": "Implemente um tratamento adequado ou log da exceção"
                },
                {
                    "language": "python",
                    "pattern": r"os\.system\(",
                    "description": "Uso inseguro de os.system()",
                    "suggestion": "Use subprocess.run() para execução mais segura de comandos"
                },
                {
                    "language": "javascript",
                    "pattern": r"innerHTML\s*=",
                    "description": "Uso de innerHTML pode levar a ataques XSS",
                    "suggestion": "Use textContent ou innerText para conteúdo de texto, ou métodos DOM seguros"
                },
                {
                    "language": "javascript",
                    "pattern": r"eval\(",
                    "description": "Uso de eval() é perigoso e inseguro",
                    "suggestion": "Evite usar eval() e encontre alternativas mais seguras"
                },
                {
                    "language": "html",
                    "pattern": r"<script[^>]*src=['\"]http://",
                    "description": "Uso de script via HTTP (não HTTPS)",
                    "suggestion": "Use sempre HTTPS para recursos externos"
                },
                {
                    "language": "css",
                    "pattern": r"position:\s*fixed",
                    "description": "Elementos com position:fixed podem causar problemas em mobile",
                    "suggestion": "Considere usar position:sticky ou outras abordagens responsivas"
                }
            ],
            "optimization_patterns": [
                {
                    "language": "python",
                    "pattern": r"for\s+\w+\s+in\s+range\(len\((\w+)\)\):",
                    "description": "Iteração ineficiente sobre lista",
                    "suggestion": "Use 'for item in lista:' ou 'for i, item in enumerate(lista):'"
                },
                {
                    "language": "javascript",
                    "pattern": r"document\.getElementsBy(?:TagName|ClassName|Id)",
                    "description": "Métodos getElement mais antigos",
                    "suggestion": "Use métodos modernos como querySelector/querySelectorAll"
                },
                {
                    "language": "javascript", 
                    "pattern": r"for\s*\(\s*var\s+i\s*=\s*0",
                    "description": "Loop for tradicional para array",
                    "suggestion": "Use forEach, map, filter ou outros métodos de array"
                },
                {
                    "language": "python",
                    "pattern": r"\.execute\([\"']SELECT.*?FROM",
                    "description": "Consulta SQL direta",
                    "suggestion": "Use SQLAlchemy ou outros ORMs para consultas mais seguras"
                }
            ],
            "modern_practices": [
                {
                    "language": "javascript",
                    "pattern": r"var\s+",
                    "description": "Uso de 'var' em vez de let/const",
                    "suggestion": "Use 'const' para variáveis que não mudam e 'let' para variáveis que mudam"
                },
                {
                    "language": "javascript",
                    "pattern": r"function\s*\(\s*\)\s*{",
                    "description": "Função anônima tradicional",
                    "suggestion": "Use arrow functions: () => {}"
                },
                {
                    "language": "python",
                    "pattern": r"def\s+\w+\([^)]*self",
                    "description": "Método de classe tradicional",
                    "suggestion": "Considere usar @classmethod, @staticmethod ou funções independentes quando apropriado"
                },
                {
                    "language": "html",
                    "pattern": r"<table",
                    "description": "Uso de tabela HTML",
                    "suggestion": "Para layouts, use CSS Grid ou Flexbox em vez de tabelas"
                }
            ]
        }
        
        # Salvar para uso futuro
        try:
            with open(patterns_file, 'w', encoding='utf-8') as f:
                json.dump(default_patterns, f, indent=2)
            logger.info("Arquivo de padrões de código criado com padrões iniciais")
        except Exception as e:
            logger.error(f"Erro ao salvar padrões de código: {e}")
            
        return default_patterns
    
    def _load_knowledge_base(self):
        """Carrega a base de conhecimento para sugestões inteligentes"""
        kb_file = os.path.join(AI_DIR, 'knowledge_base.json')
        
        if os.path.exists(kb_file):
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar base de conhecimento: {e}")
        
        # Base de conhecimento inicial
        default_kb = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "project_specific": {
                "naming_conventions": {},
                "common_bugs": [],
                "best_practices": []
            },
            "frameworks": {
                "flask": {
                    "best_practices": [
                        "Use Blueprints para organizar rotas",
                        "Configure CSRF protection",
                        "Use SQLAlchemy para acesso ao banco de dados",
                        "Utilize Flask-WTF para validação de formulários",
                        "Mantenha rotas e lógica de negócios separadas"
                    ],
                    "common_pitfalls": [
                        "Não usar app.run() em produção",
                        "Hardcoding de configurações sensíveis",
                        "Falta de tratamento de erros",
                        "Queries SQL vulneráveis a injeção"
                    ]
                },
                "javascript": {
                    "best_practices": [
                        "Use let/const em vez de var",
                        "Evite modificar o DOM diretamente, use frameworks",
                        "Use async/await para operações assíncronas",
                        "Modularize seu código"
                    ],
                    "common_pitfalls": [
                        "Vazamento de memória em closures",
                        "Falta de tratamento de erros em Promises",
                        "Modificação direta do prototype de objetos nativos"
                    ]
                }
            }
        }
        
        # Salvar para uso futuro
        try:
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(default_kb, f, indent=2)
            logger.info("Base de conhecimento criada com dados iniciais")
        except Exception as e:
            logger.error(f"Erro ao salvar base de conhecimento: {e}")
            
        return default_kb
    
    def update_knowledge_base(self, report_data):
        """Atualiza a base de conhecimento com informações do relatório"""
        try:
            # Extrair informações úteis do relatório
            new_issues = []
            for issue in report_data.get('improvements', {}).get('items', []):
                file_path = issue.get('file', '')
                extension = os.path.splitext(file_path)[1].lower()
                
                language = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.html': 'html',
                    '.css': 'css'
                }.get(extension, 'unknown')
                
                if language != 'unknown':
                    new_issues.append({
                        "language": language,
                        "pattern": issue.get('pattern', ''),
                        "description": issue.get('message', ''),
                        "file": file_path,
                        "line": issue.get('line', 0),
                        "context": issue.get('context', ''),
                        "severity": issue.get('severity', 'info'),
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Identificar padrões de nomenclatura
            naming_conventions = {}
            function_names = set()
            class_names = set()
            
            # Analisar arquivos Python para padrões de nomenclatura
            for py_file in glob.glob('**/*.py', recursive=True):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Extrair nomes de funções
                    func_matches = re.finditer(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                    for match in func_matches:
                        function_names.add(match.group(1))
                    
                    # Extrair nomes de classes
                    class_matches = re.finditer(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                    for match in class_matches:
                        class_names.add(match.group(1))
                except Exception:
                    continue
            
            # Detectar convenções de nomenclatura
            if function_names:
                snake_case_count = sum(1 for name in function_names if re.match(r'^[a-z][a-z0-9_]*$', name))
                camel_case_count = sum(1 for name in function_names if re.match(r'^[a-z][a-zA-Z0-9]*$', name) and '_' not in name)
                
                if snake_case_count > 0.8 * len(function_names):
                    naming_conventions["functions"] = "snake_case"
                elif camel_case_count > 0.8 * len(function_names):
                    naming_conventions["functions"] = "camelCase"
            
            if class_names:
                pascal_case_count = sum(1 for name in class_names if re.match(r'^[A-Z][a-zA-Z0-9]*$', name))
                
                if pascal_case_count > 0.8 * len(class_names):
                    naming_conventions["classes"] = "PascalCase"
            
            # Atualizar a base de conhecimento
            self.knowledge_base["last_updated"] = datetime.now().isoformat()
            
            # Atualizar padrões de nomenclatura
            if naming_conventions:
                self.knowledge_base["project_specific"]["naming_conventions"].update(naming_conventions)
            
            # Adicionar novos problemas comuns
            if new_issues:
                # Limitar a quantidade de problemas armazenados
                existing_bugs = self.knowledge_base["project_specific"]["common_bugs"]
                max_bugs = 50
                
                # Adicionar novos problemas críticos e de aviso
                critical_bugs = [issue for issue in new_issues if issue['severity'] in ['critical', 'warning']]
                
                # Combinar, remover duplicados e limitar
                combined_bugs = existing_bugs + critical_bugs
                unique_bugs = []
                seen = set()
                
                for bug in combined_bugs:
                    key = f"{bug.get('language')}:{bug.get('pattern')}"
                    if key not in seen:
                        seen.add(key)
                        unique_bugs.append(bug)
                
                self.knowledge_base["project_specific"]["common_bugs"] = unique_bugs[:max_bugs]
            
            # Salvar a base de conhecimento atualizada
            kb_file = os.path.join(AI_DIR, 'knowledge_base.json')
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2)
            
            logger.info("Base de conhecimento atualizada com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar base de conhecimento: {e}")
            return False
    
    def apply_ai_improvements(self, dry_run=True):
        """Aplica melhorias usando IA"""
        logger.info(f"Aplicando melhorias com IA {'(simulação)' if dry_run else ''}")
        
        improvements_applied = []
        
        # Buscar os relatórios mais recentes
        report_files = sorted(glob.glob(f"{REPORT_DIR}/zelopack_report_*.json"))
        if not report_files:
            logger.warning("Nenhum relatório encontrado para analisar")
            return []
        
        # Usar o relatório mais recente
        latest_report_file = report_files[-1]
        try:
            with open(latest_report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # Atualizar a base de conhecimento
            self.update_knowledge_base(report_data)
            
            # Obter a lista de problemas
            improvements = report_data.get('improvements', {}).get('items', [])
            
            # Organizar por tipo de arquivo
            files_to_improve = {}
            for issue in improvements:
                file_path = issue.get('file', '')
                if not file_path or not os.path.exists(file_path):
                    continue
                
                if file_path not in files_to_improve:
                    files_to_improve[file_path] = []
                
                files_to_improve[file_path].append(issue)
            
            # Processar cada arquivo
            for file_path, issues in files_to_improve.items():
                try:
                    # Verificar se podemos processar este tipo de arquivo
                    ext = os.path.splitext(file_path)[1].lower()
                    supported_exts = ['.py', '.js', '.html', '.css']
                    
                    if ext not in supported_exts:
                        continue
                    
                    logger.info(f"Analisando {file_path} com {len(issues)} problemas")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Ordenar os problemas por linha (decrescente) para não afetar os números de linha
                    issues = sorted(issues, key=lambda x: x.get('line', 0), reverse=True)
                    
                    new_content = content
                    changes_made = []
                    
                    for issue in issues:
                        severity = issue.get('severity', 'info')
                        line_num = issue.get('line', 0)
                        message = issue.get('message', '')
                        pattern = issue.get('pattern', '')
                        
                        if not pattern or severity not in ['critical', 'warning']:
                            continue
                        
                        # Obter o contexto da linha
                        lines = new_content.splitlines()
                        if line_num <= 0 or line_num > len(lines):
                            continue
                        
                        line = lines[line_num - 1]
                        
                        # Tentar aplicar correções conhecidas
                        fixed_line = self._apply_fix(line, pattern, ext[1:])
                        
                        if fixed_line and fixed_line != line:
                            # Aplicar a correção
                            lines[line_num - 1] = fixed_line
                            new_content = '\n'.join(lines)
                            
                            changes_made.append({
                                "line": line_num,
                                "original": line,
                                "fixed": fixed_line,
                                "message": message
                            })
                    
                    # Se foram feitas alterações, salvar o arquivo
                    if changes_made and not dry_run:
                        # Fazer backup do arquivo original
                        backup_path = f"{file_path}.bak"
                        shutil.copy2(file_path, backup_path)
                        
                        # Salvar o arquivo modificado
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        improvements_applied.append({
                            "file": file_path,
                            "changes": changes_made,
                            "timestamp": datetime.now().isoformat()
                        })
                    elif changes_made:
                        # Simulação apenas
                        improvements_applied.append({
                            "file": file_path,
                            "changes": changes_made,
                            "timestamp": datetime.now().isoformat(),
                            "simulated": True
                        })
                except Exception as e:
                    logger.error(f"Erro ao processar {file_path}: {e}")
        except Exception as e:
            logger.error(f"Erro ao analisar relatório: {e}")
        
        # Salvar registro das melhorias aplicadas
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        improvements_file = os.path.join(AI_DIR, f"improvements_{timestamp}.json")
        
        try:
            with open(improvements_file, 'w', encoding='utf-8') as f:
                json.dump(improvements_applied, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar registro de melhorias: {e}")
        
        logger.info(f"Aplicadas {len(improvements_applied)} melhorias com IA")
        return improvements_applied
    
    def _apply_fix(self, line, pattern, language):
        """Aplica uma correção conhecida a uma linha de código"""
        # Para cada linguagem, temos regras específicas de correção
        fixes = {
            'py': {
                r"print\(": lambda match: line.replace(match.group(0), "logger.debug("),
                r"except\s*:": lambda match: line.replace(match.group(0), "except Exception as e:"),
                r"os\.system\(": lambda match: line.replace(match.group(0), "subprocess.run("),
                r"for\s+\w+\s+in\s+range\(len\((\w+)\)\):": lambda match: re.sub(r"for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):", r"for \1, item in enumerate(\2):", line)
            },
            'js': {
                r"console\.log\(": lambda match: line.replace(match.group(0), "// console.log("),
                r"var\s+": lambda match: re.sub(r"var\s+([a-zA-Z_$][a-zA-Z0-9_$]*)", r"let \1", line),
                r"\.forEach\(\s*function": lambda match: re.sub(r"\.forEach\(\s*function\s*\(([^)]*)\)", r".forEach((\1) =>", line),
                r"setTimeout\s*\(\s*function": lambda match: re.sub(r"setTimeout\s*\(\s*function\s*\(([^)]*)\)", r"setTimeout((\1) =>", line)
            },
            'html': {
                r"<img[^>]+(?!alt=)[^>]*>": lambda match: re.sub(r"<img([^>]+)>", r"<img\1 alt='Image'>", line),
            },
            'css': {
                r"!important": lambda match: line.replace("!important", ""),
                r"position:\s*fixed": lambda match: "/* Considere usar position:sticky para melhor responsividade */\n" + line
            }
        }
        
        # Aplicar a correção se houver uma regra correspondente
        if language in fixes:
            for fix_pattern, fix_func in fixes[language].items():
                match = re.search(fix_pattern, line)
                if match:
                    try:
                        return fix_func(match)
                    except Exception:
                        pass
        
        return line
    
    def generate_ai_suggestions(self):
        """Gera sugestões avançadas usando IA, se disponível"""
        logger.info("Gerando sugestões avançadas com IA")
        
        if not self.openai_available:
            logger.warning("API OpenAI não disponível. Gerando sugestões baseadas em regras apenas.")
            suggestions = self._generate_rule_based_suggestions()
        else:
            suggestions = self._generate_openai_suggestions()
            
        # Salvar as sugestões
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suggestions_file = os.path.join(SUGGESTIONS_DIR, f"suggestions_{timestamp}.json")
        
        try:
            with open(suggestions_file, 'w', encoding='utf-8') as f:
                json.dump(suggestions, f, indent=2)
                
            # Gerar também uma versão legível
            txt_file = os.path.join(SUGGESTIONS_DIR, f"suggestions_{timestamp}.txt")
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write("=== SUGESTÕES DE MELHORIA ZELOPACK ===\n")
                f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for i, suggestion in enumerate(suggestions, 1):
                    f.write(f"SUGESTÃO #{i}: {suggestion['title']}\n")
                    f.write(f"Tipo: {suggestion['type']}\n")
                    f.write(f"Contexto: {suggestion['context']}\n")
                    f.write(f"Descrição:\n{suggestion['description']}\n")
                    
                    if 'code_example' in suggestion and suggestion['code_example']:
                        f.write("\nExemplo de código:\n")
                        f.write("```\n")
                        f.write(suggestion['code_example'])
                        f.write("\n```\n")
                    
                    f.write("\n---\n\n")
            
            logger.info(f"Sugestões salvas em {suggestions_file} e {txt_file}")
            return suggestions_file, txt_file
        except Exception as e:
            logger.error(f"Erro ao salvar sugestões: {e}")
            return None, None
    
    def _generate_rule_based_suggestions(self):
        """Gera sugestões baseadas em regras predefinidas"""
        suggestions = []
        
        # Verificar convenções de nomenclatura
        naming_conventions = self.knowledge_base.get('project_specific', {}).get('naming_conventions', {})
        if 'functions' in naming_conventions:
            convention = naming_conventions['functions']
            
            # Verificar consistência nos arquivos
            inconsistent_files = []
            
            for py_file in glob.glob('**/*.py', recursive=True):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extrair nomes de funções
                    func_matches = re.finditer(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                    functions = [match.group(1) for match in func_matches]
                    
                    # Verificar se seguem a convenção
                    if convention == 'snake_case':
                        non_snake_case = [f for f in functions if not re.match(r'^[a-z][a-z0-9_]*$', f)]
                        if non_snake_case:
                            inconsistent_files.append((py_file, non_snake_case))
                    elif convention == 'camelCase':
                        non_camel_case = [f for f in functions if not (re.match(r'^[a-z][a-zA-Z0-9]*$', f) and '_' not in f)]
                        if non_camel_case:
                            inconsistent_files.append((py_file, non_camel_case))
                except Exception:
                    continue
            
            if inconsistent_files:
                examples = []
                for file_path, funcs in inconsistent_files[:3]:
                    examples.append(f"{file_path}: {', '.join(funcs[:3])}")
                
                suggestions.append({
                    "title": "Manter Consistência em Convenções de Nomenclatura",
                    "type": "code_style",
                    "context": "Nomenclatura de funções",
                    "description": f"O projeto usa predominantemente a convenção {convention} para funções, " +
                                 f"mas foram encontradas inconsistências em {len(inconsistent_files)} arquivos. " +
                                 "A consistência nas convenções melhora a legibilidade e manutenção do código.",
                    "examples": examples
                })
        
        # Verificar imports duplicados ou não utilizados em Python
        unused_imports = []
        duplicate_imports = []
        
        for py_file in glob.glob('**/*.py', recursive=True):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrair imports
                import_matches = re.finditer(r'^(?:from\s+[a-zA-Z0-9_\.]+\s+)?import\s+([a-zA-Z0-9_,\s\.]+)', content, re.MULTILINE)
                imports = {}
                
                for match in import_matches:
                    import_stmt = match.group(0)
                    
                    # Verificar imports duplicados
                    for module in re.split(r',\s*', match.group(1)):
                        module = module.strip()
                        if ' as ' in module:
                            module = module.split(' as ')[0].strip()
                            
                        if module in imports:
                            duplicate_imports.append((py_file, module))
                        else:
                            imports[module] = import_stmt
                    
                    # Verificar se o import é usado
                    for module, stmt in imports.items():
                        # Remover o próprio import da análise
                        content_without_import = content.replace(stmt, '')
                        
                        # Para imports como 'from x import y'
                        if ' import ' in stmt and 'from ' in stmt:
                            imported_item = stmt.split(' import ')[1].strip()
                            if imported_item not in content_without_import:
                                unused_imports.append((py_file, stmt.strip()))
                        # Para imports diretos como 'import x'
                        elif module not in content_without_import:
                            unused_imports.append((py_file, stmt.strip()))
            except Exception:
                continue
        
        if unused_imports:
            suggestions.append({
                "title": "Remover Imports Não Utilizados",
                "type": "code_optimization",
                "context": "Python imports",
                "description": f"Foram encontrados {len(unused_imports)} imports possivelmente não utilizados. " +
                             "Remover imports não utilizados melhora a clareza do código e reduz o tempo de importação.",
                "examples": [f"{file}: {imp}" for file, imp in unused_imports[:5]]
            })
        
        if duplicate_imports:
            suggestions.append({
                "title": "Corrigir Imports Duplicados",
                "type": "code_cleanup",
                "context": "Python imports",
                "description": f"Foram encontrados {len(duplicate_imports)} imports possivelmente duplicados. " +
                             "Imports duplicados podem causar confusão e poluir o namespace.",
                "examples": [f"{file}: {imp}" for file, imp in duplicate_imports[:5]]
            })
        
        # Verificar funções muito longas
        long_functions = []
        
        for py_file in glob.glob('**/*.py', recursive=True):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrair funções e contar linhas
                lines = content.splitlines()
                in_function = False
                function_name = ""
                function_start = 0
                indent_level = 0
                
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
                            
                            # Considerar funções com mais de 30 linhas como muito longas
                            if function_length > 30:
                                long_functions.append((py_file, function_name, function_length))
                
                # Verificar a última função do arquivo
                if in_function:
                    function_length = len(lines) - function_start
                    if function_length > 30:
                        long_functions.append((py_file, function_name, function_length))
            except Exception:
                continue
        
        if long_functions:
            suggestions.append({
                "title": "Refatorar Funções Longas",
                "type": "code_quality",
                "context": "Complexidade de funções",
                "description": f"Foram encontradas {len(long_functions)} funções com mais de 30 linhas. " +
                             "Funções longas podem ser difíceis de entender e manter. Considere dividir em funções menores.",
                "examples": [f"{file}: {func} ({lines} linhas)" for file, func, lines in sorted(long_functions, key=lambda x: x[2], reverse=True)[:5]]
            })
        
        # Verificar comentários TODO/FIXME esquecidos
        todos = []
        
        for ext in ['.py', '.js', '.html', '.css']:
            for file_path in glob.glob(f'**/*{ext}', recursive=True):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    todo_matches = re.finditer(r'(?:^|\s)(?://|#|<!--)\s*(TODO|FIXME)(?::|\s)([^\n]*)', content, re.MULTILINE | re.IGNORECASE)
                    for match in todo_matches:
                        todos.append((file_path, match.group(1), match.group(2).strip(), content[:match.start()].count('\n') + 1))
                except Exception:
                    continue
        
        if todos:
            suggestions.append({
                "title": "Resolver TODOs e FIXMEs",
                "type": "code_maintenance",
                "context": "Comentários pendentes",
                "description": f"Foram encontrados {len(todos)} comentários TODO/FIXME no código. " +
                             "Revisar e resolver esses itens pendentes pode melhorar a qualidade do código.",
                "examples": [f"{file}:{line}: {todo_type} - {desc}" for file, todo_type, desc, line in todos[:5]]
            })
        
        # Outras sugestões de qualidade
        if os.path.exists('requirements.txt'):
            try:
                with open('requirements.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar se as versões são fixas
                unpinned = []
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#') and '==' not in line and not re.match(r'^-e', line):
                        unpinned.append(line)
                
                if unpinned:
                    suggestions.append({
                        "title": "Fixar Versões de Dependências",
                        "type": "project_management",
                        "context": "Gerenciamento de dependências",
                        "description": f"Foram encontradas {len(unpinned)} dependências sem versão fixa em requirements.txt. " +
                                     "Fixar versões com '==' garante reprodutibilidade do ambiente.",
                        "examples": unpinned[:5],
                        "code_example": "\n".join([f"{dep}==x.y.z" for dep in unpinned[:3]])
                    })
            except Exception:
                pass
        
        # Verificar duplicações em JavaScript
        js_duplications = []
        js_functions = {}
        
        for js_file in glob.glob('**/*.js', recursive=True):
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrair funções
                func_matches = re.finditer(r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*{', content)
                for match in func_matches:
                    func_name = match.group(1)
                    if func_name in js_functions:
                        js_duplications.append((js_file, func_name, js_functions[func_name]))
                    else:
                        js_functions[func_name] = js_file
            except Exception:
                continue
        
        if js_duplications:
            suggestions.append({
                "title": "Resolver Duplicações em JavaScript",
                "type": "code_duplication",
                "context": "JavaScript functions",
                "description": f"Foram encontradas {len(js_duplications)} funções JavaScript possivelmente duplicadas. " +
                             "Considere consolidar em módulos reutilizáveis.",
                "examples": [f"{file1}: {func} (também em {file2})" for file1, func, file2 in js_duplications[:5]]
            })
        
        return suggestions
    
    def _generate_openai_suggestions(self):
        """Gera sugestões usando a API OpenAI"""
        import openai
        openai.api_key = self.openai_api_key
        
        # Primeiro, gerar sugestões baseadas em regras como base
        base_suggestions = self._generate_rule_based_suggestions()
        
        # Coletar informações do projeto para contextualizar a IA
        project_info = self._collect_project_info()
        
        try:
            # Resumir aspectos do código para análise
            code_examples = []
            
            # Coletar exemplos de código de diferentes partes do projeto
            for file_pattern in ['app.py', 'main.py', 'models.py', 'static/js/main.js', 'templates/base.html']:
                if glob.glob(file_pattern):
                    file_path = glob.glob(file_pattern)[0]
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Limitar o tamanho para não exceder tokens
                            if len(content) > 1000:
                                content = content[:1000] + "...\n[truncado]"
                            code_examples.append(f"Arquivo: {file_path}\n```\n{content}\n```")
                    except Exception:
                        continue
            
            # Limite de exemplos
            code_examples = code_examples[:3]
            
            # Criar o prompt para a IA
            prompt = f"""
            Você é um especialista em análise e melhoria de código para o projeto Zelopack, um sistema de gerenciamento industrial.
            
            INFORMAÇÕES DO PROJETO:
            {project_info}
            
            EXEMPLOS DE CÓDIGO DO PROJETO:
            {chr(10).join(code_examples)}
            
            SUGESTÕES INICIAIS BASEADAS EM REGRAS:
            {json.dumps(base_suggestions, indent=2)}
            
            TAREFA:
            Com base no contexto acima, gere 3-5 sugestões avançadas para melhorar o código e a arquitetura do projeto. Suas sugestões devem:
            1. Ser específicas e aplicáveis ao contexto deste projeto
            2. Incluir exemplos concretos de implementação quando possível
            3. Explicar os benefícios das melhorias sugeridas
            4. Focar em questões arquiteturais, padrões de design, segurança, performance ou manutenção
            
            Responda no seguinte formato JSON:
            [
                {{
                    "title": "Título da sugestão",
                    "type": "Tipo (arquitetura/segurança/performance/manutenção/etc)",
                    "context": "Em qual contexto esta sugestão se aplica",
                    "description": "Descrição detalhada da sugestão e seus benefícios",
                    "code_example": "Exemplo de código que implementa a sugestão (quando aplicável)"
                }},
                ...
            ]
            """
            
            # Fazer a chamada à API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "Você é um assistente especialista em desenvolvimento de software com foco em Python, Flask e JavaScript."},
                          {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2500,
                n=1,
                stop=None
            )
            
            # Extrair a resposta
            ai_response = response.choices[0].message.content.strip()
            
            # Tentar extrair o JSON da resposta
            try:
                # Localizar o JSON na resposta
                json_match = re.search(r'\[\s*\{.*\}\s*\]', ai_response, re.DOTALL)
                if json_match:
                    ai_suggestions = json.loads(json_match.group(0))
                else:
                    # Tentar encontrar qualquer coisa entre colchetes
                    json_match = re.search(r'\[(.*)\]', ai_response, re.DOTALL)
                    if json_match:
                        ai_suggestions = json.loads(f"[{json_match.group(1)}]")
                    else:
                        logger.warning("Não foi possível extrair sugestões do formato JSON na resposta")
                        ai_suggestions = []
                
                # Combinar com sugestões baseadas em regras
                combined_suggestions = base_suggestions + ai_suggestions
                
                return combined_suggestions
            except json.JSONDecodeError:
                logger.error("Erro ao decodificar JSON da resposta da IA")
                return base_suggestions
            except Exception as e:
                logger.error(f"Erro ao processar resposta da IA: {e}")
                return base_suggestions
                
        except Exception as e:
            logger.error(f"Erro ao gerar sugestões com OpenAI: {e}")
            return base_suggestions
    
    def _collect_project_info(self):
        """Coleta informações sobre o projeto para contextualizar a IA"""
        info = {
            "frameworks": [],
            "language_stats": {},
            "file_counts": {},
            "dependencies": [],
            "database": "unknown"
        }
        
        # Detectar frameworks
        if os.path.exists('app.py') or os.path.exists('main.py'):
            with open('app.py' if os.path.exists('app.py') else 'main.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'flask' in content.lower():
                    info["frameworks"].append("Flask")
                if 'sqlalchemy' in content.lower():
                    info["frameworks"].append("SQLAlchemy")
                if 'wtforms' in content.lower() or 'flask_wtf' in content.lower():
                    info["frameworks"].append("WTForms")
        
        # Contar arquivos por tipo
        extensions = ['.py', '.js', '.html', '.css', '.json', '.md']
        for ext in extensions:
            count = len(glob.glob(f'**/*{ext}', recursive=True))
            info["file_counts"][ext] = count
            
            # Calcular estatísticas de linguagem
            total_files = sum(info["file_counts"].values())
            if total_files > 0:
                info["language_stats"] = {ext: count / total_files for ext, count in info["file_counts"].items()}
        
        # Detectar dependências
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        info["dependencies"].append(line)
        elif os.path.exists('Pipfile'):
            with open('Pipfile', 'r', encoding='utf-8') as f:
                content = f.read()
                if '[packages]' in content:
                    packages_section = content.split('[packages]')[1].split('[')[0]
                    for line in packages_section.splitlines():
                        line = line.strip()
                        if line and '=' in line:
                            pkg_name = line.split('=')[0].strip()
                            if pkg_name:
                                info["dependencies"].append(pkg_name)
        
        # Detectar banco de dados
        if os.path.exists('app.py') or os.path.exists('config.py'):
            file_to_check = 'app.py' if os.path.exists('app.py') else 'config.py'
            with open(file_to_check, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'sqlite' in content.lower():
                    info["database"] = "SQLite"
                elif 'postgresql' in content.lower() or 'postgres' in content.lower():
                    info["database"] = "PostgreSQL"
                elif 'mysql' in content.lower():
                    info["database"] = "MySQL"
        
        return json.dumps(info, indent=2)
    
    def run_scheduled_check(self):
        """Executa o monitoramento e a análise de IA em sequência"""
        logger.info("Iniciando verificação agendada com IA")
        
        try:
            # Executar o monitoramento básico primeiro
            monitor_result = subprocess.run(
                [sys.executable, MONITOR_SCRIPT, '--run'],
                capture_output=True,
                text=True
            )
            
            monitor_success = monitor_result.returncode == 0
            logger.info(f"Monitoramento básico concluído com status: {monitor_success}")
            
            # Gerar sugestões de IA
            suggestions_file, txt_file = self.generate_ai_suggestions()
            
            # Tentar aplicar melhorias automaticamente
            improvements = self.apply_ai_improvements(dry_run=True)
            
            # Gerar relatório da verificação agendada
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(AI_DIR, f"scheduled_check_{timestamp}.json")
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "monitor_success": monitor_success,
                "monitor_output": monitor_result.stdout + monitor_result.stderr,
                "ai_suggestions": suggestions_file,
                "improvements": {
                    "total": len(improvements),
                    "items": improvements
                }
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Verificação agendada concluída. Relatório: {report_file}")
            return report_file
        except Exception as e:
            logger.error(f"Erro na verificação agendada: {e}")
            return None

def setup_cron_job():
    """Configura um job cron para verificações agendadas"""
    import platform
    
    script_path = os.path.abspath(__file__)
    
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        # Para sistemas Unix-like
        cron_cmd = f"0 2 * * * {sys.executable} {script_path} --check"
        
        try:
            # Ver se já está no crontab
            check_cmd = "crontab -l"
            check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            
            if script_path in check_result.stdout:
                print("Job cron já está configurado")
                return True
            
            # Adicionar ao crontab
            crontab = check_result.stdout.strip()
            new_crontab = f"{crontab}\n{cron_cmd}\n" if crontab else f"{cron_cmd}\n"
            
            with open('/tmp/zelopack_ai_crontab', 'w') as f:
                f.write(new_crontab)
            
            install_cmd = "crontab /tmp/zelopack_ai_crontab"
            subprocess.run(install_cmd, shell=True, check=True)
            os.remove('/tmp/zelopack_ai_crontab')
            
            print("Job cron configurado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar job cron: {e}")
            return False
    else:
        # Para Windows, sugerir usar o Agendador de Tarefas
        print("Para Windows, configure o script para execução periódica usando o Agendador de Tarefas")
        print(f"Comando: {sys.executable} {script_path} --check")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Assistente de IA para Zelopack')
    parser.add_argument('--check', action='store_true', help='Executar verificação agendada')
    parser.add_argument('--suggestions', action='store_true', help='Gerar sugestões de melhoria')
    parser.add_argument('--apply', action='store_true', help='Aplicar melhorias automaticamente')
    parser.add_argument('--setup-cron', action='store_true', help='Configurar job cron para verificações agendadas')
    parser.add_argument('--api-key', help='Chave de API OpenAI para funcionalidades avançadas')
    args = parser.parse_args()
    
    # Usar a chave de API da linha de comando ou da variável de ambiente
    api_key = args.api_key or os.environ.get('OPENAI_API_KEY')
    
    assistant = ZelopackAI(openai_api_key=api_key)
    
    if args.setup_cron:
        setup_cron_job()
        return
    
    if args.check:
        assistant.run_scheduled_check()
    elif args.suggestions:
        assistant.generate_ai_suggestions()
    elif args.apply:
        assistant.apply_ai_improvements(dry_run=False)
    else:
        print("Assistente de IA para Zelopack")
        print("Opções disponíveis:")
        print("  --check        Executar verificação agendada")
        print("  --suggestions  Gerar sugestões de melhoria")
        print("  --apply        Aplicar melhorias automaticamente")
        print("  --setup-cron   Configurar job cron para verificações agendadas")
        print("  --api-key      Chave de API OpenAI para funcionalidades avançadas")
        print("\nExemplo: python zelopack_ai_assistant.py --check")

if __name__ == "__main__":
    main()