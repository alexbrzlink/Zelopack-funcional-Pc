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
import re
import json
import time
import logging
import datetime
import subprocess
from pathlib import Path
import importlib
import shutil
import traceback
import random
from typing import List, Dict, Any, Optional, Tuple, Union

# Configurações de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("zelopack_ai.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("zelopack_ai")

# Diretório base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Arquivos e diretórios importantes
REPORTS_DIR = os.path.join(BASE_DIR, "tests", "reports")
KNOWLEDGE_BASE_FILE = os.path.join(BASE_DIR, "tests", "ai_knowledge_base.json")
PATTERNS_FILE = os.path.join(BASE_DIR, "tests", "code_patterns.json")
SUGGESTIONS_DIR = os.path.join(BASE_DIR, "tests", "suggestions")
PROJECT_INFO_FILE = os.path.join(BASE_DIR, "tests", "project_info.json")

# Criar diretórios necessários
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(SUGGESTIONS_DIR, exist_ok=True)

class ZelopackAI:
    """Assistente de IA para o Zelopack"""
    
    def __init__(self, openai_api_key=None):
        """Inicializar o assistente de IA"""
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.report_file = os.path.join(REPORTS_DIR, f"ai_report_{self.timestamp}.json")
        self.text_report_file = os.path.join(REPORTS_DIR, f"ai_report_{self.timestamp}.txt")
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.openai_available = self._check_openai_available()
        
        # Carregar dados
        self.code_patterns = self._load_code_patterns()
        self.knowledge_base = self._load_knowledge_base()
        self.project_info = self._collect_project_info()
        
        logger.info(f"ZelopackAI inicializado (OpenAI disponível: {self.openai_available})")
    
    def _check_openai_available(self):
        """Verifica se a API OpenAI está disponível"""
        if not self.openai_api_key:
            logger.warning("Chave da API OpenAI não encontrada. Usando apenas funcionalidades básicas.")
            return False
        
        try:
            import openai
            return True
        except ImportError:
            logger.warning("Módulo OpenAI não encontrado. Usando apenas funcionalidades básicas.")
            return False
    
    def _load_code_patterns(self):
        """Carrega padrões de código para análise"""
        default_patterns = {
            "python": {
                "anti_patterns": [
                    {
                        "name": "except_pass",
                        "pattern": r"except\s+(?:\w+(?:\s+as\s+\w+)?)?:\s*\n\s*pass",
                        "message": "Exceção capturada sem tratamento (usando pass)",
                        "suggestion": "Trate a exceção apropriadamente ou registre-a em log",
                        "severity": "warning"
                    },
                    {
                        "name": "bare_except",
                        "pattern": r"except\s*:",
                        "message": "Exceção genérica sem especificação de tipo",
                        "suggestion": "Especifique os tipos de exceção a serem capturados",
                        "severity": "warning"
                    },
                    {
                        "name": "mutable_default_args",
                        "pattern": r"def\s+\w+\(.*?=\s*\[\].*?\):",
                        "message": "Uso de lista vazia como valor padrão de parâmetro",
                        "suggestion": "Use None como valor padrão e inicialize a lista dentro da função",
                        "severity": "warning"
                    },
                    {
                        "name": "debug_print",
                        "pattern": r"print\(['\"]DEBUG:",
                        "message": "Uso de print para debug",
                        "suggestion": "Use logging para mensagens de depuração",
                        "severity": "info"
                    }
                ],
                "best_practices": [
                    {
                        "name": "use_pathlib",
                        "pattern": r"os\.path\.(join|exists|basename|dirname)",
                        "message": "Uso de os.path que poderia usar pathlib",
                        "suggestion": "Considere usar a biblioteca pathlib para manipulação de caminhos",
                        "severity": "info"
                    },
                    {
                        "name": "use_fstring",
                        "pattern": r"(\"|')\s*%\s*\(",
                        "message": "Uso de formatação de string antiga (%)",
                        "suggestion": "Use f-strings para formatação mais moderna e legível",
                        "severity": "info"
                    },
                    {
                        "name": "use_context_manager",
                        "pattern": r"open\([^)]+\)(?!\s*as\b)",
                        "message": "Arquivo aberto sem gerenciador de contexto (with)",
                        "suggestion": "Use 'with open(...) as f:' para garantir que o arquivo seja fechado",
                        "severity": "warning"
                    }
                ]
            },
            "javascript": {
                "anti_patterns": [
                    {
                        "name": "document_write",
                        "pattern": r"document\.write\(",
                        "message": "Uso de document.write()",
                        "suggestion": "Use métodos DOM modernos como createElement() e appendChild()",
                        "severity": "warning"
                    },
                    {
                        "name": "eval_usage",
                        "pattern": r"\beval\(",
                        "message": "Uso de eval()",
                        "suggestion": "Evite eval() por razões de segurança e desempenho",
                        "severity": "critical"
                    },
                    {
                        "name": "innerHTML_assignment",
                        "pattern": r"\.innerHTML\s*=",
                        "message": "Atribuição direta a innerHTML",
                        "suggestion": "Use métodos mais seguros como textContent ou insertAdjacentHTML()",
                        "severity": "warning"
                    }
                ],
                "best_practices": [
                    {
                        "name": "use_strict",
                        "pattern_not": r"'use strict'|\"use strict\"",
                        "message": "Faltando 'use strict'",
                        "suggestion": "Adicione 'use strict' no início do arquivo para ativar modo estrito",
                        "severity": "info"
                    },
                    {
                        "name": "use_const_let",
                        "pattern": r"\bvar\b",
                        "message": "Uso de 'var' em vez de 'const' ou 'let'",
                        "suggestion": "Use 'const' para valores que não mudam e 'let' para variáveis",
                        "severity": "info"
                    },
                    {
                        "name": "use_fetch",
                        "pattern": r"new XMLHttpRequest\(\)",
                        "message": "Uso de XMLHttpRequest",
                        "suggestion": "Use a API Fetch para requisições HTTP modernas",
                        "severity": "info"
                    }
                ]
            },
            "html": {
                "accessibility": [
                    {
                        "name": "img_alt",
                        "pattern": r"<img[^>]*(?!alt=)[^>]*>",
                        "message": "Imagem sem atributo alt",
                        "suggestion": "Adicione o atributo alt para acessibilidade",
                        "severity": "warning"
                    },
                    {
                        "name": "semantic_headings",
                        "pattern": r"<div[^>]*class=['\"].*?(?:title|heading|header).*?['\"][^>]*>",
                        "message": "Possível uso de div para título em vez de tags h1-h6",
                        "suggestion": "Use tags semânticas como h1-h6 para títulos",
                        "severity": "info"
                    }
                ]
            },
            "css": {
                "best_practices": [
                    {
                        "name": "avoid_important",
                        "pattern": r"!important",
                        "message": "Uso de !important",
                        "suggestion": "Evite !important. Melhore a especificidade dos seletores",
                        "severity": "info"
                    },
                    {
                        "name": "use_relative_units",
                        "pattern": r"\b\d+px\b",
                        "message": "Uso de unidades absolutas (px)",
                        "suggestion": "Considere usar unidades relativas (rem, em, %) para melhor responsividade",
                        "severity": "info"
                    }
                ]
            }
        }
        
        try:
            if os.path.exists(PATTERNS_FILE):
                with open(PATTERNS_FILE, 'r') as f:
                    loaded_patterns = json.load(f)
                logger.info(f"Padrões de código carregados de {PATTERNS_FILE}")
                return loaded_patterns
            else:
                # Se o arquivo não existe, criar com os padrões padrão
                with open(PATTERNS_FILE, 'w') as f:
                    json.dump(default_patterns, f, indent=2)
                logger.info(f"Arquivo de padrões criado em {PATTERNS_FILE}")
                return default_patterns
        except Exception as e:
            logger.error(f"Erro ao carregar padrões de código: {e}")
            return default_patterns
    
    def _load_knowledge_base(self):
        """Carrega a base de conhecimento para sugestões inteligentes"""
        default_knowledge = {
            "common_issues": [],
            "solutions": {},
            "code_improvements": [],
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        try:
            if os.path.exists(KNOWLEDGE_BASE_FILE):
                with open(KNOWLEDGE_BASE_FILE, 'r') as f:
                    knowledge = json.load(f)
                logger.info(f"Base de conhecimento carregada de {KNOWLEDGE_BASE_FILE}")
                return knowledge
            else:
                # Se o arquivo não existe, criar com a base padrão
                with open(KNOWLEDGE_BASE_FILE, 'w') as f:
                    json.dump(default_knowledge, f, indent=2)
                logger.info(f"Arquivo de base de conhecimento criado em {KNOWLEDGE_BASE_FILE}")
                return default_knowledge
        except Exception as e:
            logger.error(f"Erro ao carregar base de conhecimento: {e}")
            return default_knowledge
    
    def update_knowledge_base(self, report_data):
        """Atualiza a base de conhecimento com informações do relatório"""
        if not report_data:
            return
        
        try:
            # Extrair problemas do relatório
            issues = []
            if "improvements" in report_data and "details" in report_data["improvements"]:
                issues.extend(report_data["improvements"]["details"])
            
            # Atualizar problemas comuns
            for issue in issues:
                issue_type = issue.get("type", "unknown")
                file_path = issue.get("file", "")
                severity = issue.get("severity", "info")
                message = issue.get("message", "")
                
                # Verificar se já temos este problema
                issue_key = f"{issue_type}:{file_path}:{message}"
                found = False
                
                for common_issue in self.knowledge_base["common_issues"]:
                    if common_issue.get("key") == issue_key:
                        # Incrementar contagem
                        common_issue["count"] = common_issue.get("count", 1) + 1
                        common_issue["last_seen"] = datetime.datetime.now().isoformat()
                        found = True
                        break
                
                if not found:
                    # Adicionar novo problema
                    self.knowledge_base["common_issues"].append({
                        "key": issue_key,
                        "type": issue_type,
                        "file": file_path,
                        "severity": severity,
                        "message": message,
                        "count": 1,
                        "first_seen": datetime.datetime.now().isoformat(),
                        "last_seen": datetime.datetime.now().isoformat()
                    })
            
            # Organizar por contagem
            self.knowledge_base["common_issues"].sort(key=lambda x: x.get("count", 0), reverse=True)
            
            # Limitar a 100 problemas para manter o arquivo gerenciável
            if len(self.knowledge_base["common_issues"]) > 100:
                self.knowledge_base["common_issues"] = self.knowledge_base["common_issues"][:100]
            
            # Atualizar timestamp
            self.knowledge_base["last_updated"] = datetime.datetime.now().isoformat()
            
            # Salvar base de conhecimento atualizada
            with open(KNOWLEDGE_BASE_FILE, 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
            
            logger.info(f"Base de conhecimento atualizada com {len(issues)} problemas")
        except Exception as e:
            logger.error(f"Erro ao atualizar base de conhecimento: {e}")
    
    def apply_ai_improvements(self, dry_run=True):
        """Aplica melhorias usando IA"""
        logger.info(f"{'Simulando' if dry_run else 'Aplicando'} melhorias usando IA...")
        
        applied_improvements = []
        
        # 1. Verificar arquivos Python para padrões conhecidos
        for root, _, files in os.walk("."):
            # Pular diretórios de teste e virtualenv
            if "tests/" in root + "/" or "venv/" in root + "/" or "__pycache__/" in root + "/":
                continue
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Fazer backup antes de modificar
                        if not dry_run:
                            backup_path = f"{file_path}.bak"
                            shutil.copy2(file_path, backup_path)
                        
                        # Aplicar padrões
                        modified_content = content
                        
                        # Verificar padrões Python
                        if "python" in self.code_patterns:
                            for pattern_type in ["anti_patterns", "best_practices"]:
                                if pattern_type in self.code_patterns["python"]:
                                    for pattern in self.code_patterns["python"][pattern_type]:
                                        pattern_regex = pattern.get("pattern")
                                        if pattern_regex:
                                            # Verificar correspondências
                                            matches = re.finditer(pattern_regex, content, re.MULTILINE)
                                            for match in matches:
                                                # Obter a linha
                                                line_start = content[:match.start()].count('\n') + 1
                                                line = content.split('\n')[line_start - 1]
                                                
                                                # Aplicar correção
                                                fixed_line = self._apply_fix(line, pattern, "python")
                                                if fixed_line and fixed_line != line:
                                                    # Substituir no conteúdo modificado
                                                    modified_content = modified_content.replace(line, fixed_line)
                                                    
                                                    # Registrar melhoria
                                                    applied_improvements.append({
                                                        "file": file_path,
                                                        "line": line_start,
                                                        "pattern": pattern.get("name"),
                                                        "original": line,
                                                        "fixed": fixed_line,
                                                        "applied": not dry_run
                                                    })
                        
                        # Se houve mudanças e não é simulação, salvar o arquivo
                        if not dry_run and modified_content != content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(modified_content)
                            logger.info(f"Aplicadas melhorias em {file_path}")
                    
                    except Exception as e:
                        logger.error(f"Erro ao processar {file_path}: {e}")
        
        # 2. Verificar arquivos JavaScript, HTML e CSS
        for ext, pattern_key in [(".js", "javascript"), (".html", "html"), (".css", "css")]:
            for root, _, files in os.walk("."):
                # Pular diretórios de teste e virtualenv
                if "tests/" in root + "/" or "venv/" in root + "/" or "node_modules/" in root + "/":
                    continue
                
                for file in files:
                    if file.endswith(ext):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Fazer backup antes de modificar
                            if not dry_run:
                                backup_path = f"{file_path}.bak"
                                shutil.copy2(file_path, backup_path)
                            
                            # Aplicar padrões
                            modified_content = content
                            
                            # Verificar padrões do tipo de arquivo
                            if pattern_key in self.code_patterns:
                                for pattern_group in self.code_patterns[pattern_key]:
                                    if isinstance(self.code_patterns[pattern_key][pattern_group], list):
                                        for pattern in self.code_patterns[pattern_key][pattern_group]:
                                            pattern_regex = pattern.get("pattern")
                                            if pattern_regex:
                                                # Verificar correspondências
                                                matches = re.finditer(pattern_regex, content, re.MULTILINE)
                                                for match in matches:
                                                    # Obter a linha
                                                    line_start = content[:match.start()].count('\n') + 1
                                                    line = content.split('\n')[line_start - 1]
                                                    
                                                    # Aplicar correção
                                                    fixed_line = self._apply_fix(line, pattern, pattern_key)
                                                    if fixed_line and fixed_line != line:
                                                        # Substituir no conteúdo modificado
                                                        modified_content = modified_content.replace(line, fixed_line)
                                                        
                                                        # Registrar melhoria
                                                        applied_improvements.append({
                                                            "file": file_path,
                                                            "line": line_start,
                                                            "pattern": pattern.get("name"),
                                                            "original": line,
                                                            "fixed": fixed_line,
                                                            "applied": not dry_run
                                                        })
                            
                            # Se houve mudanças e não é simulação, salvar o arquivo
                            if not dry_run and modified_content != content:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(modified_content)
                                logger.info(f"Aplicadas melhorias em {file_path}")
                        
                        except Exception as e:
                            logger.error(f"Erro ao processar {file_path}: {e}")
        
        logger.info(f"{'Simulação de melhorias' if dry_run else 'Melhorias'} concluída: {len(applied_improvements)} melhorias {'seriam' if dry_run else 'foram'} aplicadas")
        
        return applied_improvements
    
    def _apply_fix(self, line, pattern, language):
        """Aplica uma correção conhecida a uma linha de código"""
        if not line:
            return line
        
        name = pattern.get("name", "")
        
        # Melhorias específicas por linguagem e padrão
        if language == "python":
            if name == "except_pass":
                # Transformar except: pass em log
                return line.replace("pass", "logger.warning('Exceção capturada e ignorada')")
            
            elif name == "bare_except":
                # Transformar except: em except Exception:
                return line.replace("except:", "except Exception:")
            
            elif name == "mutable_default_args":
                # Substituir lista vazia por None
                return re.sub(r'(def\s+\w+\(.*?)=\s*\[\](.*?\))', r'\1=None\2', line)
            
            elif name == "debug_print":
                # Transformar print de debug em logging
                return line.replace("print(", "logger.debug(")
            
            elif name == "use_pathlib":
                # Sugerir uso de pathlib mas não alterar (muito complexo)
                return line
            
            elif name == "use_fstring":
                # Difícil converter automaticamente, apenas sugerir
                return line
            
            elif name == "use_context_manager":
                # Difícil converter automaticamente, apenas sugerir
                return line
                
        elif language == "javascript":
            if name == "document_write":
                # Comentar o document.write
                return f"// TODO: Substituir por métodos DOM modernos: {line}"
            
            elif name == "eval_usage":
                # Comentar o eval
                return f"// SECURITY: Evitar uso de eval(): {line}"
            
            elif name == "innerHTML_assignment":
                # Comentar a atribuição de innerHTML
                return f"// SECURITY: Usar textContent ou insertAdjacentHTML: {line}"
            
            elif name == "use_strict":
                # Não alterar linha específica, adicionar 'use strict' é feito no arquivo todo
                return line
            
            elif name == "use_const_let":
                # Substituir var por let (const seria mais complicado)
                return line.replace("var ", "let ")
            
            elif name == "use_fetch":
                # Difícil converter automaticamente, apenas sugerir
                return line
                
        elif language == "html":
            if name == "img_alt":
                # Adicionar alt vazio para imagens sem alt
                return re.sub(r'(<img[^>]*)(?!alt=)([^>]*>)', r'\1 alt=""\2', line)
            
            elif name == "semantic_headings":
                # Difícil converter automaticamente, apenas sugerir
                return line
                
        elif language == "css":
            if name == "avoid_important":
                # Comentar o !important
                return line.replace("!important", "/* !important removido */")
            
            elif name == "use_relative_units":
                # Difícil converter automaticamente, apenas sugerir
                return line
        
        # Se não houver conversão específica, retornar a linha original
        return line
    
    def generate_ai_suggestions(self):
        """Gera sugestões avançadas usando IA, se disponível"""
        if self.openai_available:
            suggestions = self._generate_openai_suggestions()
        else:
            suggestions = self._generate_rule_based_suggestions()
        
        return suggestions
    
    def _generate_rule_based_suggestions(self):
        """Gera sugestões baseadas em regras predefinidas"""
        logger.info("Gerando sugestões baseadas em regras (OpenAI não disponível)")
        
        suggestions = []
        
        # 1. Verificar problemas comuns com base na knowledge_base
        common_issues = sorted(self.knowledge_base.get("common_issues", []), 
                              key=lambda x: x.get("count", 0), 
                              reverse=True)
        
        top_issues = common_issues[:5]
        if top_issues:
            suggestion = {
                "title": "Resolver problemas recorrentes",
                "description": "Existem alguns problemas que aparecem frequentemente nas análises:",
                "items": [],
                "priority": "high"
            }
            
            for issue in top_issues:
                issue_type = issue.get("type", "unknown")
                file = issue.get("file", "")
                message = issue.get("message", "")
                count = issue.get("count", 0)
                
                suggestion["items"].append(
                    f"Problema '{message}' (tipo: {issue_type}) em {file} - encontrado {count} vezes"
                )
            
            suggestions.append(suggestion)
        
        # 2. Verificar arquivos muito grandes
        large_files = []
        for root, _, files in os.walk("."):
            # Pular diretórios de teste e virtualenv
            if "tests/" in root + "/" or "venv/" in root + "/" or "__pycache__/" in root + "/" or "node_modules/" in root + "/":
                continue
            
            for file in files:
                if file.endswith((".py", ".js", ".html", ".css")):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            line_count = sum(1 for _ in f)
                        
                        if line_count > 300:
                            large_files.append((file_path, line_count))
                    except:
                        pass
        
        if large_files:
            large_files.sort(key=lambda x: x[1], reverse=True)
            top_large_files = large_files[:5]
            
            suggestion = {
                "title": "Refatorar arquivos grandes",
                "description": "Os seguintes arquivos são muito grandes e poderiam ser divididos em módulos menores:",
                "items": [f"{file} ({line_count} linhas)" for file, line_count in top_large_files],
                "priority": "medium"
            }
            
            suggestions.append(suggestion)
        
        # 3. Verificar imports comuns que poderiam ser centralizados
        imports_by_file = {}
        for root, _, files in os.walk("."):
            # Pular diretórios de teste e virtualenv
            if "tests/" in root + "/" or "venv/" in root + "/" or "__pycache__/" in root + "/":
                continue
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        imports = re.findall(r'^(?:from\s+([\w.]+)\s+import\s+(?:[^(]*)|\s*import\s+([\w.]+))', content, re.MULTILINE)
                        file_imports = []
                        
                        for imp in imports:
                            if imp[0]:  # from ... import
                                file_imports.append(imp[0])
                            elif imp[1]:  # import ...
                                file_imports.append(imp[1])
                        
                        imports_by_file[file_path] = file_imports
                    except:
                        pass
        
        # Contar imports comuns
        import_counts = {}
        for file_imports in imports_by_file.values():
            for imp in file_imports:
                if imp in import_counts:
                    import_counts[imp] += 1
                else:
                    import_counts[imp] = 1
        
        common_imports = [(imp, count) for imp, count in import_counts.items() if count >= 5]
        if common_imports:
            common_imports.sort(key=lambda x: x[1], reverse=True)
            top_common_imports = common_imports[:10]
            
            suggestion = {
                "title": "Centralizar imports comuns",
                "description": "Os seguintes módulos são importados frequentemente e poderiam ser centralizados:",
                "items": [f"{imp} (usado em {count} arquivos)" for imp, count in top_common_imports],
                "priority": "low"
            }
            
            suggestions.append(suggestion)
        
        # 4. Verificar consistência na estrutura de arquivos
        file_extensions = {}
        for root, _, files in os.walk("."):
            # Pular diretórios de teste e virtualenv
            if "tests/" in root + "/" or "venv/" in root + "/" or "__pycache__/" in root + "/" or "node_modules/" in root + "/":
                continue
            
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext:
                    if ext in file_extensions:
                        file_extensions[ext] += 1
                    else:
                        file_extensions[ext] = 1
        
        # Gerar sugestão sobre estrutura de arquivos
        suggestion = {
            "title": "Análise da estrutura de arquivos",
            "description": "Distribuição de tipos de arquivo no projeto:",
            "items": [f"{ext}: {count} arquivos" for ext, count in sorted(file_extensions.items(), key=lambda x: x[1], reverse=True)[:10]],
            "priority": "info"
        }
        
        suggestions.append(suggestion)
        
        # 5. Gerar sugestões aleatórias para demonstrar capacidades
        random_suggestions = [
            {
                "title": "Implementar testes unitários",
                "description": "O projeto poderia se beneficiar de mais testes unitários para garantir a qualidade do código.",
                "items": [
                    "Implementar testes para as principais funcionalidades",
                    "Configurar CI/CD para executar testes automaticamente",
                    "Adicionar testes de integração para funcionalidades críticas"
                ],
                "priority": "medium"
            },
            {
                "title": "Melhorar documentação",
                "description": "A documentação do projeto poderia ser aprimorada para facilitar a manutenção e colaboração.",
                "items": [
                    "Adicionar docstrings em funções importantes",
                    "Criar um README.md detalhado",
                    "Documentar a arquitetura do sistema"
                ],
                "priority": "medium"
            },
            {
                "title": "Otimizar desempenho",
                "description": "Existem oportunidades para melhorar o desempenho do sistema.",
                "items": [
                    "Otimizar consultas ao banco de dados",
                    "Implementar cache para dados frequentemente acessados",
                    "Minimizar e compactar arquivos estáticos"
                ],
                "priority": "medium"
            }
        ]
        
        # Adicionar uma sugestão aleatória
        suggestions.append(random.choice(random_suggestions))
        
        # Salvar sugestões em um arquivo
        suggestion_file = os.path.join(SUGGESTIONS_DIR, f"suggestions_{self.timestamp}.json")
        with open(suggestion_file, 'w') as f:
            json.dump(suggestions, f, indent=2)
        
        # Salvar também em formato texto para fácil leitura
        text_file = os.path.join(SUGGESTIONS_DIR, f"suggestions_{self.timestamp}.txt")
        with open(text_file, 'w') as f:
            f.write("=== SUGESTÕES DE MELHORIA ZELOPACK ===\n")
            f.write(f"Data: {self.timestamp.replace('_', ' ')}\n\n")
            
            for i, suggestion in enumerate(suggestions, 1):
                priority_text = {
                    "high": "ALTA",
                    "medium": "MÉDIA",
                    "low": "BAIXA",
                    "info": "INFORMATIVA"
                }.get(suggestion.get("priority", ""), "MÉDIA")
                
                f.write(f"{i}. {suggestion.get('title', 'Sugestão')}\n")
                f.write(f"   Prioridade: {priority_text}\n")
                f.write(f"   {suggestion.get('description', '')}\n")
                
                for item in suggestion.get("items", []):
                    f.write(f"   * {item}\n")
                
                f.write("\n")
        
        logger.info(f"Geradas {len(suggestions)} sugestões baseadas em regras")
        
        return suggestions
    
    def _generate_openai_suggestions(self):
        """Gera sugestões usando a API OpenAI"""
        logger.info("Gerando sugestões usando OpenAI...")
        
        try:
            import openai
            
            # Preparar informações do projeto
            project_info = json.dumps(self.project_info, indent=2)
            
            # Preparar os problemas mais comuns
            common_issues = sorted(self.knowledge_base.get("common_issues", []), 
                                  key=lambda x: x.get("count", 0), 
                                  reverse=True)
            
            top_issues = common_issues[:10]
            issues_text = json.dumps(top_issues, indent=2)
            
            # Contexto para a IA
            prompt = f"""
            Análise o seguinte projeto Python/Flask e gere sugestões de melhoria.
            
            # Informações do projeto:
            {project_info}
            
            # Problemas mais comuns encontrados:
            {issues_text}
            
            # Resposta solicitada:
            Gere entre 3 e 5 sugestões de melhoria para o projeto, classificadas por prioridade (alta, média, baixa).
            Cada sugestão deve incluir:
            1. Um título conciso
            2. Uma descrição explicando a sugestão
            3. Uma lista de itens específicos a serem implementados
            4. Uma prioridade (alta, média, baixa)
            
            Formate sua resposta como um objeto JSON no seguinte formato:
            [
                {{
                    "title": "Título da sugestão",
                    "description": "Descrição detalhada da sugestão",
                    "items": ["Item 1", "Item 2", "Item 3"],
                    "priority": "high|medium|low"
                }},
                ...
            ]
            """
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            # Chamar a API
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em análise de código e melhoria de projetos Python/Flask."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Processar a resposta
            result = response.choices[0].message.content
            suggestions = json.loads(result)
            
            # Salvar sugestões em um arquivo
            suggestion_file = os.path.join(SUGGESTIONS_DIR, f"suggestions_{self.timestamp}.json")
            with open(suggestion_file, 'w') as f:
                json.dump(suggestions, f, indent=2)
            
            # Salvar também em formato texto para fácil leitura
            text_file = os.path.join(SUGGESTIONS_DIR, f"suggestions_{self.timestamp}.txt")
            with open(text_file, 'w') as f:
                f.write("=== SUGESTÕES DE MELHORIA ZELOPACK (GERADAS POR IA) ===\n")
                f.write(f"Data: {self.timestamp.replace('_', ' ')}\n\n")
                
                for i, suggestion in enumerate(suggestions, 1):
                    priority_text = {
                        "high": "ALTA",
                        "medium": "MÉDIA",
                        "low": "BAIXA"
                    }.get(suggestion.get("priority", ""), "MÉDIA")
                    
                    f.write(f"{i}. {suggestion.get('title', 'Sugestão')}\n")
                    f.write(f"   Prioridade: {priority_text}\n")
                    f.write(f"   {suggestion.get('description', '')}\n")
                    
                    for item in suggestion.get("items", []):
                        f.write(f"   * {item}\n")
                    
                    f.write("\n")
            
            logger.info(f"Geradas {len(suggestions)} sugestões usando OpenAI")
            
            return suggestions
        except Exception as e:
            logger.error(f"Erro ao gerar sugestões com OpenAI: {e}")
            logger.info("Fallback para sugestões baseadas em regras")
            return self._generate_rule_based_suggestions()
    
    def _collect_project_info(self):
        """Coleta informações sobre o projeto para contextualizar a IA"""
        logger.info("Coletando informações sobre o projeto...")
        
        project_info = {
            "name": "Zelopack",
            "framework": "Flask",
            "file_stats": {},
            "dependencies": [],
            "directories": [],
            "database": "unknown"
        }
        
        try:
            # Contar arquivos por tipo
            file_counts = {}
            for root, dirs, files in os.walk("."):
                # Pular diretórios de teste e virtualenv
                if "tests/" in root + "/" or "venv/" in root + "/" or "__pycache__/" in root + "/" or "node_modules/" in root + "/":
                    continue
                
                # Adicionar diretórios
                for dir_name in dirs:
                    if not dir_name.startswith("__") and not dir_name.startswith("."):
                        dir_path = os.path.join(root, dir_name)
                        rel_path = os.path.relpath(dir_path, ".")
                        if rel_path not in ["venv", "__pycache__", "node_modules"]:
                            project_info["directories"].append(rel_path)
                
                # Contar arquivos
                for file in files:
                    ext = os.path.splitext(file)[1]
                    if ext:
                        if ext in file_counts:
                            file_counts[ext] += 1
                        else:
                            file_counts[ext] = 1
            
            project_info["file_stats"] = file_counts
            
            # Verificar dependências
            if os.path.exists("requirements.txt"):
                with open("requirements.txt", 'r') as f:
                    requirements = f.readlines()
                project_info["dependencies"] = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]
            
            # Verificar package.json
            if os.path.exists("package.json"):
                try:
                    with open("package.json", 'r') as f:
                        package_data = json.load(f)
                    
                    if "dependencies" in package_data:
                        for dep, version in package_data["dependencies"].items():
                            project_info["dependencies"].append(f"{dep}@{version}")
                except:
                    pass
            
            # Verificar tipo de banco de dados
            for root, _, files in os.walk("."):
                for file in files:
                    if file.endswith((".py", ".js")):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read().lower()
                            
                            if "sqlalchemy" in content:
                                project_info["database"] = "SQLAlchemy"
                                if "postgresql" in content or "postgres" in content:
                                    project_info["database"] = "PostgreSQL (SQLAlchemy)"
                                elif "sqlite" in content:
                                    project_info["database"] = "SQLite (SQLAlchemy)"
                                elif "mysql" in content:
                                    project_info["database"] = "MySQL (SQLAlchemy)"
                            elif "sqlite3" in content:
                                project_info["database"] = "SQLite (sqlite3)"
                            elif "psycopg2" in content:
                                project_info["database"] = "PostgreSQL (psycopg2)"
                            elif "pymysql" in content or "mysql-connector" in content:
                                project_info["database"] = "MySQL"
                            elif "mongodb" in content or "pymongo" in content:
                                project_info["database"] = "MongoDB"
                        except:
                            pass
            
            # Salvar informações do projeto
            with open(PROJECT_INFO_FILE, 'w') as f:
                json.dump(project_info, f, indent=2)
            
            logger.info(f"Informações do projeto coletadas e salvas em {PROJECT_INFO_FILE}")
            return project_info
        
        except Exception as e:
            logger.error(f"Erro ao coletar informações do projeto: {e}")
            return project_info
    
    def run_scheduled_check(self):
        """Executa o monitoramento e a análise de IA em sequência"""
        logger.info("Iniciando verificação agendada com IA...")
        
        try:
            # Importar e executar o monitor Zelopack
            from zelopack_monitor import ZelopackMonitor
            
            # Executar o monitor
            monitor = ZelopackMonitor()
            report = monitor.run_monitoring_cycle(fix_issues=False)
            
            # Atualizar a base de conhecimento
            self.update_knowledge_base(report)
            
            # Gerar sugestões
            suggestions = self.generate_ai_suggestions()
            
            # Aplicar melhorias automáticas
            improvements = self.apply_ai_improvements(dry_run=True)
            
            return {
                "report": report,
                "suggestions": suggestions,
                "improvements": improvements
            }
        
        except Exception as e:
            logger.error(f"Erro na verificação agendada: {e}")
            logger.error(traceback.format_exc())
            return None

def setup_cron_job():
    """Configura um job cron para verificações agendadas"""
    script_path = os.path.abspath(__file__)
    
    if os.name != 'nt':  # Linux/MacOS
        try:
            # Verificar se já está no crontab
            result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
            current_crontab = result.stdout
            
            # Verificar se o script já está no crontab
            if script_path in current_crontab:
                logger.info("Assistente IA já está configurado no crontab")
                return
            
            # Adicionar ao crontab (executar às 2h da manhã todos os dias)
            cron_line = f"0 2 * * * {sys.executable} {script_path}\n"
            
            if result.returncode == 0:
                new_crontab = current_crontab + cron_line
            else:
                new_crontab = cron_line
            
            # Salvar em arquivo temporário
            temp_file = "/tmp/zelopack_ai_crontab"
            with open(temp_file, 'w') as f:
                f.write(new_crontab)
            
            # Instalar o crontab
            subprocess.run(f"crontab {temp_file}", shell=True, check=True)
            os.remove(temp_file)
            
            logger.info("Assistente IA agendado no crontab para executar diariamente às 2h")
        
        except Exception as e:
            logger.error(f"Erro ao configurar crontab: {e}")
    
    else:  # Windows
        try:
            # Criar arquivo batch para executar o script
            batch_file = os.path.join(os.path.dirname(script_path), "run_zelopack_ai.bat")
            with open(batch_file, 'w') as f:
                f.write(f'@echo off\n"{sys.executable}" "{script_path}"\n')
            
            # Agendar a tarefa (windows task scheduler)
            task_name = "ZelopackAI"
            cmd = f'schtasks /create /sc MINUTE /mo 5 /tn "{task_name}" /tr "{batch_file}" /f'
            subprocess.run(cmd, shell=True, check=True)
            
            logger.info("Assistente IA agendado no Task Scheduler para executar a cada 5 minutos")
        
        except Exception as e:
            logger.error(f"Erro ao configurar Task Scheduler: {e}")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Assistente de IA do Zelopack')
    parser.add_argument('--key', help='Chave da API OpenAI')
    parser.add_argument('--suggest', action='store_true', help='Gerar sugestões de melhoria')
    parser.add_argument('--fix', action='store_true', help='Aplicar melhorias automaticamente')
    parser.add_argument('--dry-run', action='store_true', help='Simular melhorias sem aplicá-las')
    parser.add_argument('--schedule', action='store_true', help='Agendar execução periódica')
    
    args = parser.parse_args()
    
    # Usar a chave da API da linha de comando ou do ambiente
    openai_key = args.key or os.environ.get("OPENAI_API_KEY")
    
    # Inicializar o assistente
    assistant = ZelopackAI(openai_api_key=openai_key)
    
    if args.schedule:
        setup_cron_job()
        return
    
    # Executar de acordo com os argumentos
    if args.suggest:
        suggestions = assistant.generate_ai_suggestions()
        print(f"\nGeradas {len(suggestions)} sugestões")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion.get('title', 'Sugestão')} (Prioridade: {suggestion.get('priority', 'média')})")
            print(f"   {suggestion.get('description', '')}")
            for item in suggestion.get('items', []):
                print(f"   - {item}")
    
    elif args.fix or args.dry_run:
        improvements = assistant.apply_ai_improvements(dry_run=args.dry_run or not args.fix)
        action = "Simuladas" if args.dry_run or not args.fix else "Aplicadas"
        
        print(f"\n{action} {len(improvements)} melhorias automáticas")
        for i, improvement in enumerate(improvements[:10], 1):
            print(f"\n{i}. Arquivo: {improvement.get('file')}, Linha: {improvement.get('line')}")
            print(f"   Padrão: {improvement.get('pattern')}")
            print(f"   Original: {improvement.get('original')}")
            print(f"   Alteração: {improvement.get('fixed')}")
        
        if len(improvements) > 10:
            print(f"\n... e mais {len(improvements) - 10} melhorias")
    
    else:
        # Executar modo padrão (verificação completa)
        print("\n=== VERIFICAÇÃO COMPLETA COM IA ===")
        
        # Atualizar a base de conhecimento
        print("\n1. Atualizando base de conhecimento...")
        assistant.update_knowledge_base(None)
        
        # Gerar sugestões
        print("\n2. Gerando sugestões de melhoria...")
        suggestions = assistant.generate_ai_suggestions()
        
        # Aplicar melhorias automáticas (simulação)
        print("\n3. Simulando melhorias automáticas...")
        improvements = assistant.apply_ai_improvements(dry_run=True)
        
        # Exibir resumo
        print("\n=== RESUMO ===")
        print(f"\nGeradas {len(suggestions)} sugestões")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion.get('title', 'Sugestão')} (Prioridade: {suggestion.get('priority', 'média')})")
            print(f"   {suggestion.get('description', '')}")
            
            # Limitar itens para não sobrecarregar o console
            items = suggestion.get('items', [])
            for item in items[:3]:
                print(f"   - {item}")
            
            if len(items) > 3:
                print(f"   - ... e mais {len(items) - 3} itens")
        
        print(f"\nSimuladas {len(improvements)} melhorias automáticas")
        for i, improvement in enumerate(improvements[:5], 1):
            print(f"\n{i}. Arquivo: {improvement.get('file')}, Linha: {improvement.get('line')}")
            print(f"   Padrão: {improvement.get('pattern')}")
            print(f"   Original: {improvement.get('original')}")
            print(f"   Alteração: {improvement.get('fixed')}")
        
        if len(improvements) > 5:
            print(f"\n... e mais {len(improvements) - 5} melhorias")
        
        # Mostrar os arquivos de relatório
        print(f"\nRelatórios salvos em:")
        print(f"  - Sugestões: {os.path.join(SUGGESTIONS_DIR, f'suggestions_{assistant.timestamp}.txt')}")
        print(f"  - Informações do projeto: {PROJECT_INFO_FILE}")

if __name__ == "__main__":
    main()