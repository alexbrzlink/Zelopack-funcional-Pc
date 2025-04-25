#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Agentes Especializados de IA para Zelopack

Este módulo implementa agentes especializados de IA para melhorar continuamente
diferentes componentes do sistema Zelopack de forma independente e autônoma.

Cada agente é especializado em uma área específica e aplica melhorias focadas em seu domínio.
"""

import os
import sys
import re
import json
import time
import logging
import datetime
import subprocess
import importlib
import random
import shutil
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

# Configurações de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("zelopack_ai_agents.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("zelopack_ai_agents")

# Diretório base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diretórios e arquivos importantes
AGENTS_DIR = os.path.join(BASE_DIR, "tests", "agents")
AGENTS_KNOWLEDGE_DIR = os.path.join(AGENTS_DIR, "knowledge")
AGENTS_IMPROVEMENTS_DIR = os.path.join(AGENTS_DIR, "improvements")
AGENTS_REPORTS_DIR = os.path.join(AGENTS_DIR, "reports")

# Criar diretórios necessários
os.makedirs(AGENTS_DIR, exist_ok=True)
os.makedirs(AGENTS_KNOWLEDGE_DIR, exist_ok=True)
os.makedirs(AGENTS_IMPROVEMENTS_DIR, exist_ok=True)
os.makedirs(AGENTS_REPORTS_DIR, exist_ok=True)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("Módulo OpenAI não disponível. Algumas funcionalidades dos agentes serão limitadas.")


class BaseAgent:
    """Classe base para agentes de IA especializados"""
    
    def __init__(self, name, domain, file_patterns=None, content_patterns=None, openai_api_key=None):
        """Inicializa um agente especializado de IA"""
        self.name = name
        self.domain = domain
        self.file_patterns = file_patterns or []
        self.content_patterns = content_patterns or []
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.knowledge_file = os.path.join(AGENTS_KNOWLEDGE_DIR, f"{name.lower().replace(' ', '_')}_knowledge.json")
        self.report_file = os.path.join(AGENTS_REPORTS_DIR, f"{name.lower().replace(' ', '_')}_{self.timestamp}.json")
        self.improvements_file = os.path.join(AGENTS_IMPROVEMENTS_DIR, f"{name.lower().replace(' ', '_')}_{self.timestamp}.json")
        
        # Carregar conhecimento prévio do agente
        self.knowledge_base = self._load_knowledge_base()
        
        # Configurar OpenAI
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.openai_available = OPENAI_AVAILABLE and self.openai_api_key is not None
        
        if not self.openai_available:
            logger.warning(f"Agente {self.name}: OpenAI não disponível. Usando capacidades básicas.")
        
        logger.info(f"Agente {self.name} inicializado para domínio: {self.domain}")
    
    def _load_knowledge_base(self):
        """Carrega a base de conhecimento do agente"""
        default_knowledge = {
            "domain": self.domain,
            "insights": [],
            "improvements": [],
            "learned_patterns": [],
            "statistics": {
                "scans": 0,
                "issues_found": 0,
                "improvements_applied": 0
            },
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r') as f:
                    knowledge = json.load(f)
                logger.info(f"Agente {self.name}: Base de conhecimento carregada")
                return knowledge
            else:
                # Se o arquivo não existe, criar com a base padrão
                with open(self.knowledge_file, 'w') as f:
                    json.dump(default_knowledge, f, indent=2)
                logger.info(f"Agente {self.name}: Base de conhecimento criada")
                return default_knowledge
        except Exception as e:
            logger.error(f"Agente {self.name}: Erro ao carregar base de conhecimento: {e}")
            return default_knowledge
    
    def _save_knowledge_base(self):
        """Salva a base de conhecimento do agente"""
        try:
            # Atualizar timestamp
            self.knowledge_base["last_updated"] = datetime.datetime.now().isoformat()
            
            with open(self.knowledge_file, 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
            
            logger.info(f"Agente {self.name}: Base de conhecimento atualizada")
        except Exception as e:
            logger.error(f"Agente {self.name}: Erro ao salvar base de conhecimento: {e}")
    
    def collect_relevant_files(self):
        """Coleta arquivos relevantes para o domínio do agente"""
        relevant_files = []
        
        # Verificar todos os arquivos do projeto
        for root, _, files in os.walk(BASE_DIR):
            # Ignorar diretórios específicos
            if any(ignored in root for ignored in ['.git', '__pycache__', 'venv', 'tests/agents']):
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, BASE_DIR)
                
                # Verificar se o arquivo corresponde a algum padrão deste agente
                for pattern in self.file_patterns:
                    if re.search(pattern, rel_path):
                        relevant_files.append(file_path)
                        break
                
                # Se o arquivo não corresponde pelo nome, verificar conteúdo
                if file_path not in relevant_files and self.content_patterns and file.endswith(('.py', '.js', '.html', '.css')):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for pattern in self.content_patterns:
                            if re.search(pattern, content):
                                relevant_files.append(file_path)
                                break
                    except:
                        # Ignora erros de leitura (arquivos binários, etc)
                        pass
        
        logger.info(f"Agente {self.name}: Encontrados {len(relevant_files)} arquivos relevantes")
        return relevant_files
    
    def analyze_files(self, files):
        """Analisa arquivos relevantes em busca de problemas e oportunidades de melhoria"""
        issues = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Análise específica deve ser implementada por cada agente
                file_issues = self._specific_analysis(file_path, content)
                issues.extend(file_issues)
            except Exception as e:
                logger.error(f"Agente {self.name}: Erro ao analisar {file_path}: {e}")
        
        logger.info(f"Agente {self.name}: Encontrados {len(issues)} problemas/oportunidades")
        return issues
    
    def _specific_analysis(self, file_path, content):
        """Análise específica do domínio - deve ser implementada pelos agentes concretos"""
        # Classe base retorna lista vazia
        return []
    
    def apply_improvements(self, issues, dry_run=True):
        """Aplica melhorias com base nos problemas encontrados"""
        improvements = []
        
        # Agrupar problemas por arquivo
        issues_by_file = {}
        for issue in issues:
            file_path = issue.get("file")
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        # Processar cada arquivo
        for file_path, file_issues in issues_by_file.items():
            try:
                # Ler o conteúdo original
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                # Fazer backup antes de modificar
                if not dry_run:
                    backup_path = f"{file_path}.{self.timestamp}.bak"
                    shutil.copy2(file_path, backup_path)
                
                # Aplicar melhorias específicas do domínio
                modified_content, file_improvements = self._apply_domain_improvements(
                    file_path, original_content, file_issues, dry_run)
                
                improvements.extend(file_improvements)
                
                # Se o conteúdo foi modificado e não é simulação, salvar as alterações
                if not dry_run and modified_content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    logger.info(f"Agente {self.name}: Melhorias aplicadas em {file_path}")
            except Exception as e:
                logger.error(f"Agente {self.name}: Erro ao aplicar melhorias em {file_path}: {e}")
        
        # Salvar melhorias aplicadas
        self._save_improvements(improvements, dry_run)
        
        logger.info(f"Agente {self.name}: {'Simuladas' if dry_run else 'Aplicadas'} {len(improvements)} melhorias")
        return improvements
    
    def _apply_domain_improvements(self, file_path, content, issues, dry_run):
        """Aplica melhorias específicas do domínio - deve ser implementada pelos agentes concretos"""
        # Classe base não faz modificações
        return content, []
    
    def _save_improvements(self, improvements, dry_run):
        """Salva registro das melhorias aplicadas"""
        try:
            improvements_data = {
                "timestamp": self.timestamp,
                "agent": self.name,
                "domain": self.domain,
                "dry_run": dry_run,
                "improvements": improvements
            }
            
            with open(self.improvements_file, 'w') as f:
                json.dump(improvements_data, f, indent=2)
            
            # Atualizar estatísticas na base de conhecimento
            if improvements:
                self.knowledge_base["statistics"]["issues_found"] += len(improvements)
                if not dry_run:
                    self.knowledge_base["statistics"]["improvements_applied"] += len(improvements)
                
                # Adicionar melhorias à base de conhecimento
                for improvement in improvements:
                    # Evitar duplicações
                    if improvement not in self.knowledge_base["improvements"]:
                        self.knowledge_base["improvements"].append(improvement)
                
                # Limitar o número de melhorias armazenadas (máximo 100)
                if len(self.knowledge_base["improvements"]) > 100:
                    self.knowledge_base["improvements"] = self.knowledge_base["improvements"][-100:]
                
                self._save_knowledge_base()
            
            logger.info(f"Agente {self.name}: Registro de melhorias salvo em {self.improvements_file}")
        except Exception as e:
            logger.error(f"Agente {self.name}: Erro ao salvar registro de melhorias: {e}")
    
    def generate_report(self, issues, improvements):
        """Gera relatório com insights e sugestões para o domínio específico"""
        try:
            # Básico para todos os agentes
            basic_report = {
                "timestamp": self.timestamp,
                "agent": self.name,
                "domain": self.domain,
                "issues_count": len(issues),
                "improvements_count": len(improvements),
                "issues": issues,
                "improvements": improvements
            }
            
            # Adicionar insights específicos do domínio
            if self.openai_available:
                insights = self._generate_domain_insights(issues, improvements)
                basic_report["insights"] = insights
                
                # Adicionar insights à base de conhecimento
                if insights:
                    for insight in insights:
                        if insight not in self.knowledge_base["insights"]:
                            self.knowledge_base["insights"].append(insight)
                    
                    # Limitar o número de insights armazenados (máximo 50)
                    if len(self.knowledge_base["insights"]) > 50:
                        self.knowledge_base["insights"] = self.knowledge_base["insights"][-50:]
            else:
                basic_report["insights"] = []
                logger.warning(f"Agente {self.name}: OpenAI não disponível para gerar insights")
            
            # Salvar relatório
            with open(self.report_file, 'w') as f:
                json.dump(basic_report, f, indent=2)
            
            # Salvar também em formato texto
            text_report_file = os.path.splitext(self.report_file)[0] + ".txt"
            self._generate_text_report(basic_report, text_report_file)
            
            # Atualizar estatísticas na base de conhecimento
            self.knowledge_base["statistics"]["scans"] += 1
            self._save_knowledge_base()
            
            logger.info(f"Agente {self.name}: Relatório gerado em {self.report_file}")
            return basic_report
        except Exception as e:
            logger.error(f"Agente {self.name}: Erro ao gerar relatório: {e}")
            return None
    
    def _generate_domain_insights(self, issues, improvements):
        """Gera insights específicos do domínio usando IA - implementado pelos agentes concretos"""
        if not self.openai_available:
            return []
        
        try:
            # Preparar contexto para a IA
            issues_summary = json.dumps(issues[:10] if len(issues) > 10 else issues, indent=2)
            improvements_summary = json.dumps(improvements[:10] if len(improvements) > 10 else improvements, indent=2)
            
            prompt = f"""
            Analise os problemas e melhorias a seguir para o componente {self.domain} do sistema Zelopack.
            
            ## Problemas encontrados:
            {issues_summary}
            
            ## Melhorias aplicadas ou sugeridas:
            {improvements_summary}
            
            ## Resposta solicitada:
            Gere 3-5 insights específicos sobre o componente {self.domain} com base nesta análise.
            Cada insight deve:
            1. Identificar um padrão ou problema recorrente
            2. Explicar o impacto no sistema
            3. Sugerir uma abordagem estratégica para resolver ou melhorar
            
            Responda no formato de lista simples:
            - Insight 1
            - Insight 2
            - Insight 3
            
            """
            
            # Chamar a API
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"Você é um especialista em desenvolvimento de software focado em {self.domain}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            # Processar a resposta
            insights_text = response.choices[0].message.content
            
            # Extrair insights (formato de lista)
            insights = re.findall(r'- (.+?)(?=\n- |\n\n|\Z)', insights_text, re.DOTALL)
            insights = [insight.strip() for insight in insights]
            
            logger.info(f"Agente {self.name}: Gerados {len(insights)} insights usando OpenAI")
            return insights
        except Exception as e:
            logger.error(f"Agente {self.name}: Erro ao gerar insights: {e}")
            return []
    
    def _generate_text_report(self, report_data, output_file):
        """Gera versão em texto do relatório"""
        try:
            with open(output_file, 'w') as f:
                f.write(f"=== RELATÓRIO DO AGENTE {self.name.upper()} ===\n")
                f.write(f"Data: {report_data['timestamp'].replace('_', ' ')}\n")
                f.write(f"Domínio: {report_data['domain']}\n\n")
                
                f.write("=== RESUMO ===\n")
                f.write(f"Problemas encontrados: {report_data['issues_count']}\n")
                f.write(f"Melhorias aplicadas/sugeridas: {report_data['improvements_count']}\n\n")
                
                if "insights" in report_data and report_data["insights"]:
                    f.write("=== INSIGHTS ===\n")
                    for i, insight in enumerate(report_data["insights"], 1):
                        f.write(f"{i}. {insight}\n\n")
                
                if report_data["issues"]:
                    f.write("=== PROBLEMAS ENCONTRADOS ===\n")
                    for i, issue in enumerate(report_data["issues"][:10], 1):
                        f.write(f"{i}. Arquivo: {issue.get('file')}\n")
                        f.write(f"   Tipo: {issue.get('type')}\n")
                        f.write(f"   Mensagem: {issue.get('message')}\n")
                        if "suggestion" in issue:
                            f.write(f"   Sugestão: {issue.get('suggestion')}\n")
                        f.write("\n")
                    
                    if len(report_data["issues"]) > 10:
                        f.write(f"... e mais {len(report_data['issues']) - 10} problemas\n\n")
                
                if report_data["improvements"]:
                    f.write("=== MELHORIAS ===\n")
                    for i, improvement in enumerate(report_data["improvements"][:10], 1):
                        f.write(f"{i}. Arquivo: {improvement.get('file')}\n")
                        f.write(f"   Tipo: {improvement.get('type')}\n")
                        if "original" in improvement and "modified" in improvement:
                            f.write(f"   Original: {improvement.get('original')}\n")
                            f.write(f"   Modificado: {improvement.get('modified')}\n")
                        if "description" in improvement:
                            f.write(f"   Descrição: {improvement.get('description')}\n")
                        f.write("\n")
                    
                    if len(report_data["improvements"]) > 10:
                        f.write(f"... e mais {len(report_data['improvements']) - 10} melhorias\n\n")
                
                f.write("=== FIM DO RELATÓRIO ===\n")
            
            logger.info(f"Agente {self.name}: Relatório de texto gerado em {output_file}")
        except Exception as e:
            logger.error(f"Agente {self.name}: Erro ao gerar relatório de texto: {e}")
    
    def run(self, apply_fixes=False):
        """Executa o ciclo completo do agente"""
        logger.info(f"Agente {self.name}: Iniciando ciclo para domínio '{self.domain}'")
        
        # 1. Coletar arquivos relevantes
        files = self.collect_relevant_files()
        
        # 2. Analisar arquivos
        issues = self.analyze_files(files)
        
        # 3. Aplicar ou simular melhorias
        improvements = self.apply_improvements(issues, dry_run=not apply_fixes)
        
        # 4. Gerar relatório
        report = self.generate_report(issues, improvements)
        
        logger.info(f"Agente {self.name}: Ciclo concluído. {len(issues)} problemas encontrados, {len(improvements)} melhorias {'aplicadas' if apply_fixes else 'simuladas'}")
        
        return {
            "agent": self.name,
            "domain": self.domain,
            "files_analyzed": len(files),
            "issues_found": len(issues),
            "improvements": len(improvements),
            "report_file": self.report_file
        }

# Agentes especializados para diferentes componentes do sistema

class FrontendLayoutAgent(BaseAgent):
    """Agente especializado em layout e design frontend"""
    
    def __init__(self, openai_api_key=None):
        super().__init__(
            name="Frontend Layout Agent",
            domain="Layout e Design",
            file_patterns=[
                r"static/css/.*\.css$",
                r"static/js/theme.*\.js$",
                r"templates/.*\.html$",
                r"static/img/.*\.(png|jpg|svg)$"
            ],
            content_patterns=[
                r"class=\".*\"",
                r"<div",
                r"<section",
                r"display:",
                r"margin:",
                r"padding:"
            ],
            openai_api_key=openai_api_key
        )
    
    def _specific_analysis(self, file_path, content):
        issues = []
        
        # Análise específica para arquivos CSS
        if file_path.endswith('.css'):
            # Verificar uso excessivo de !important
            important_count = content.count('!important')
            if important_count > 5:
                issues.append({
                    "file": file_path,
                    "type": "css_important",
                    "severity": "warning",
                    "message": f"Uso excessivo de !important ({important_count} ocorrências)",
                    "suggestion": "Evite usar !important; melhore a especificidade dos seletores"
                })
            
            # Verificar unidades absolutas (px vs rem/em)
            px_count = len(re.findall(r'\b\d+px\b', content))
            relative_count = len(re.findall(r'\b\d+(?:rem|em|%|vh|vw)\b', content))
            
            if px_count > 2 * relative_count and px_count > 10:
                issues.append({
                    "file": file_path,
                    "type": "css_units",
                    "severity": "info",
                    "message": f"Uso excessivo de unidades px ({px_count} ocorrências) vs unidades relativas ({relative_count} ocorrências)",
                    "suggestion": "Prefira unidades relativas (rem, em, %) para melhor responsividade"
                })
            
            # Verificar propriedades duplicadas
            rules = re.findall(r'{([^}]*)}', content)
            for rule in rules:
                properties = [prop.split(':')[0].strip() for prop in rule.split(';') if ':' in prop]
                duplicate_props = [p for p in properties if properties.count(p) > 1]
                
                if duplicate_props:
                    unique_duplicates = set(duplicate_props)
                    issues.append({
                        "file": file_path,
                        "type": "css_duplicates",
                        "severity": "warning",
                        "message": f"Propriedades CSS duplicadas: {', '.join(unique_duplicates)}",
                        "suggestion": "Remova propriedades duplicadas para evitar comportamento inesperado"
                    })
        
        # Análise específica para arquivos HTML
        elif file_path.endswith('.html'):
            # Verificar tags img sem alt
            img_tags = re.findall(r'<img[^>]*>', content)
            img_without_alt = [img for img in img_tags if 'alt=' not in img]
            
            if img_without_alt:
                issues.append({
                    "file": file_path,
                    "type": "accessibility",
                    "severity": "warning",
                    "message": f"Imagens sem atributo alt ({len(img_without_alt)} ocorrências)",
                    "suggestion": "Adicione atributos alt em todas as imagens para acessibilidade"
                })
            
            # Verificar estilos inline
            inline_styles = re.findall(r'style\s*=\s*["\'][^"\']*["\']', content)
            if len(inline_styles) > 5:
                issues.append({
                    "file": file_path,
                    "type": "css_inline",
                    "severity": "info",
                    "message": f"Uso excessivo de estilos inline ({len(inline_styles)} ocorrências)",
                    "suggestion": "Mova estilos inline para arquivos CSS"
                })
                
            # Verificar divs aninhadas em excesso
            nested_divs = re.findall(r'<div[^>]*>(?:[^<]*|<(?!div))*<div', content)
            if len(nested_divs) > 10:
                issues.append({
                    "file": file_path,
                    "type": "html_structure",
                    "severity": "info",
                    "message": f"Uso excessivo de divs aninhadas ({len(nested_divs)} ocorrências)",
                    "suggestion": "Considere usar tags semânticas como section, article, etc."
                })
        
        return issues
    
    def _apply_domain_improvements(self, file_path, content, issues, dry_run):
        improvements = []
        modified_content = content
        
        for issue in issues:
            issue_type = issue.get("type")
            
            if issue_type == "accessibility" and file_path.endswith('.html'):
                # Adicionar atributos alt às imagens
                original_content = modified_content
                modified_content = re.sub(
                    r'(<img[^>]*)(?!\s+alt=)([^>]*>)',
                    r'\1 alt="Imagem"\2',
                    modified_content
                )
                
                if modified_content != original_content:
                    improvements.append({
                        "file": file_path,
                        "type": "accessibility_fix",
                        "description": "Adicionado atributo alt às imagens",
                        "original": "Tag <img> sem alt",
                        "modified": "Tag <img> com alt=\"Imagem\""
                    })
            
            elif issue_type == "css_duplicates" and file_path.endswith('.css'):
                # Remover propriedades duplicadas é mais complexo e arriscado
                # Aqui apenas registramos a necessidade de melhoria manual
                improvements.append({
                    "file": file_path,
                    "type": "css_duplicates_detection",
                    "description": "Detectadas propriedades CSS duplicadas",
                    "requires_manual": True,
                    "suggestion": issue.get("suggestion", "")
                })
            
            # Outras melhorias específicas podem ser adicionadas aqui
        
        return modified_content, improvements


class BackendAgent(BaseAgent):
    """Agente especializado em código backend"""
    
    def __init__(self, openai_api_key=None):
        super().__init__(
            name="Backend Agent",
            domain="Backend e Lógica de Negócios",
            file_patterns=[
                r"\.py$",
                r"models\.py",
                r"routes\.py",
                r"utils/.*\.py$",
                r"blueprints/.*/routes\.py$"
            ],
            content_patterns=[
                r"def\s+\w+\s*\(",
                r"class\s+\w+\s*\(",
                r"@app\.route",
                r"@blueprint\.route",
                r"db\."
            ],
            openai_api_key=openai_api_key
        )
    
    def _specific_analysis(self, file_path, content):
        issues = []
        
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
                    issues.append({
                        "file": file_path,
                        "type": "unused_import",
                        "severity": "warning",
                        "message": f"Import não utilizado: {name}",
                        "suggestion": f"Remova o import não utilizado para melhorar a clareza e o desempenho do código"
                    })
        
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
            issues.append({
                "file": file_path,
                "type": "function_too_long",
                "severity": "warning",
                "message": f"Funções muito longas: {', '.join([f'{name} ({length} linhas)' for name, length in long_functions])}",
                "suggestion": "Funções muito longas são difíceis de entender e manter. Considere refatorá-las em funções menores"
            })
        
        # Verificar uso inadequado de exceções
        bare_excepts = re.findall(r'except\s*:', content)
        if bare_excepts:
            issues.append({
                "file": file_path,
                "type": "bare_except",
                "severity": "warning",
                "message": f"Blocos 'except:' genéricos encontrados ({len(bare_excepts)} ocorrências)",
                "suggestion": "Especifique os tipos de exceção a serem capturados (e.g., 'except ValueError:')"
            })
        
        # Verificar tratamento inadequado de exceções
        pass_excepts = re.findall(r'except\s+(?:\w+(?:\s+as\s+\w+)?)?:\s*\n\s*pass', content)
        if pass_excepts:
            issues.append({
                "file": file_path,
                "type": "pass_except",
                "severity": "warning",
                "message": f"Exceções silenciadas com 'pass' ({len(pass_excepts)} ocorrências)",
                "suggestion": "Evite silenciar exceções com 'pass'. Registre a exceção ou trate-a adequadamente"
            })
        
        return issues
    
    def _apply_domain_improvements(self, file_path, content, issues, dry_run):
        improvements = []
        modified_content = content
        
        for issue in issues:
            issue_type = issue.get("type")
            
            if issue_type == "unused_import":
                # Extrair o nome do import não utilizado
                unused_import = issue.get("message", "").replace("Import não utilizado: ", "").strip()
                if unused_import:
                    original_content = modified_content
                    
                    # Remover o import não utilizado (várias formas possíveis)
                    # Caso 1: import único
                    modified_content = re.sub(
                        fr'^import\s+{unused_import}\s*$',
                        '',
                        modified_content,
                        flags=re.MULTILINE
                    )
                    
                    # Caso 2: from ... import único
                    modified_content = re.sub(
                        fr'^from\s+[\w.]+\s+import\s+{unused_import}\s*$',
                        '',
                        modified_content,
                        flags=re.MULTILINE
                    )
                    
                    # Caso 3: import em lista
                    modified_content = re.sub(
                        fr'(import\s+[^,\n]*,\s*){unused_import}(,\s*[^,\n]*|\s*$)',
                        r'\1\2',
                        modified_content
                    )
                    modified_content = re.sub(
                        fr'(import\s+){unused_import}(,\s*)',
                        r'\1',
                        modified_content
                    )
                    
                    # Caso 4: from ... import em lista
                    modified_content = re.sub(
                        fr'(from\s+[\w.]+\s+import\s+[^,\n]*,\s*){unused_import}(,\s*[^,\n]*|\s*$)',
                        r'\1\2',
                        modified_content
                    )
                    modified_content = re.sub(
                        fr'(from\s+[\w.]+\s+import\s+){unused_import}(,\s*)',
                        r'\1',
                        modified_content
                    )
                    
                    # Remover linhas vazias extras
                    modified_content = re.sub(r'\n\n\n+', '\n\n', modified_content)
                    
                    if modified_content != original_content:
                        improvements.append({
                            "file": file_path,
                            "type": "remove_unused_import",
                            "description": f"Removido import não utilizado: {unused_import}",
                            "original": f"Import de '{unused_import}' não utilizado",
                            "modified": "Import removido"
                        })
            
            elif issue_type == "bare_except":
                # Substituir except: por except Exception:
                original_content = modified_content
                modified_content = re.sub(
                    r'except\s*:',
                    'except Exception:',
                    modified_content
                )
                
                if modified_content != original_content:
                    improvements.append({
                        "file": file_path,
                        "type": "fix_bare_except",
                        "description": "Substituído 'except:' por 'except Exception:'",
                        "original": "except:",
                        "modified": "except Exception:"
                    })
            
            elif issue_type == "pass_except":
                # Substituir pass em exceções por logging
                original_content = modified_content
                modified_content = re.sub(
                    r'(except\s+(?:\w+(?:\s+as\s+(\w+))?)?:\s*\n\s*)pass',
                    lambda m: f'{m.group(1)}logger.warning("Exceção capturada e ignorada{": " + m.group(2) if m.group(2) else ""}")',
                    modified_content
                )
                
                # Adicionar import de logging se não existir
                if "import logging" not in modified_content and modified_content != original_content:
                    modified_content = "import logging\nlogger = logging.getLogger(__name__)\n\n" + modified_content
                
                if modified_content != original_content:
                    improvements.append({
                        "file": file_path,
                        "type": "fix_pass_except",
                        "description": "Substituído 'pass' em exceção por logging",
                        "original": "except ...: pass",
                        "modified": "except ...: logger.warning(...)"
                    })
            
            # Outras melhorias específicas podem ser adicionadas aqui
        
        return modified_content, improvements


class SecurityAgent(BaseAgent):
    """Agente especializado em segurança"""
    
    def __init__(self, openai_api_key=None):
        super().__init__(
            name="Security Agent",
            domain="Segurança da Aplicação",
            file_patterns=[
                r"\.py$",
                r"auth",
                r"login",
                r"user",
                r"password",
                r"token",
                r"session",
                r"config\.py$"
            ],
            content_patterns=[
                r"password",
                r"token",
                r"SECRET_KEY",
                r"request\.(form|args|json)",
                r"render_template",
                r"session\[",
                r"\.execute\(",
                r"eval\(",
                r"exec\("
            ],
            openai_api_key=openai_api_key
        )
    
    def _specific_analysis(self, file_path, content):
        issues = []
        
        # Verificar hardcoded secrets
        secret_patterns = [
            (r'api_key\s*=\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "API key"),
            (r'password\s*=\s*["\']([^"\']{6,})["\']', "Senha"),
            (r'secret\s*=\s*["\']([^"\']{6,})["\']', "Secret"),
            (r'SECRET_KEY\s*=\s*["\']([^"\']{6,})["\']', "SECRET_KEY")
        ]
        
        for pattern, secret_type in secret_patterns:
            secrets = re.findall(pattern, content, re.IGNORECASE)
            if secrets:
                issues.append({
                    "file": file_path,
                    "type": "hardcoded_secret",
                    "severity": "critical",
                    "message": f"{secret_type} hardcoded no código",
                    "suggestion": "Mova secrets para variáveis de ambiente ou arquivo .env"
                })
        
        # Verificar SQL injection
        if "execute(" in content and "?" not in content and "%s" not in content:
            sql_injection = re.findall(r'\.execute\(\s*[f"\']{1,3}.*?\s*\+|\.execute\(\s*[f"\']{1,3}.*?{', content)
            if sql_injection:
                issues.append({
                    "file": file_path,
                    "type": "sql_injection",
                    "severity": "critical",
                    "message": "Possível vulnerabilidade de SQL Injection",
                    "suggestion": "Use consultas parametrizadas com marcadores de posição (?, %s) ou ORM"
                })
        
        # Verificar CSRF
        if "app.route" in content and "@csrf.exempt" in content:
            issues.append({
                "file": file_path,
                "type": "csrf_disabled",
                "severity": "high",
                "message": "Proteção CSRF desativada para rota",
                "suggestion": "Evite usar @csrf.exempt. Implemente tokens CSRF adequadamente"
            })
        
        # Verificar uso inseguro de variáveis de template
        if "render_template" in content and "|safe" in content:
            issues.append({
                "file": file_path,
                "type": "xss",
                "severity": "high",
                "message": "Uso de |safe em templates pode causar XSS",
                "suggestion": "Evite usar |safe com dados controlados pelo usuário"
            })
        
        # Verificar acesso inseguro a parâmetros de requisição
        form_direct_access = re.findall(r'request\.form\[[\'"](\w+)[\'"]\]', content)
        args_direct_access = re.findall(r'request\.args\[[\'"](\w+)[\'"]\]', content)
        
        if form_direct_access:
            issues.append({
                "file": file_path,
                "type": "insecure_request_access",
                "severity": "medium",
                "message": f"Acesso direto a request.form sem verificação ({len(form_direct_access)} ocorrências)",
                "suggestion": "Use request.form.get() com valor padrão ou validação"
            })
        
        if args_direct_access:
            issues.append({
                "file": file_path,
                "type": "insecure_request_access",
                "severity": "medium",
                "message": f"Acesso direto a request.args sem verificação ({len(args_direct_access)} ocorrências)",
                "suggestion": "Use request.args.get() com valor padrão ou validação"
            })
        
        # Verificar uso de eval e exec
        if "eval(" in content:
            issues.append({
                "file": file_path,
                "type": "dangerous_function",
                "severity": "critical",
                "message": "Uso de eval() é perigoso e pode levar a execução de código arbitrário",
                "suggestion": "Evite usar eval(); encontre uma alternativa mais segura"
            })
        
        if "exec(" in content:
            issues.append({
                "file": file_path,
                "type": "dangerous_function",
                "severity": "critical",
                "message": "Uso de exec() é perigoso e pode levar a execução de código arbitrário",
                "suggestion": "Evite usar exec(); encontre uma alternativa mais segura"
            })
        
        return issues
    
    def _apply_domain_improvements(self, file_path, content, issues, dry_run):
        improvements = []
        modified_content = content
        
        for issue in issues:
            issue_type = issue.get("type")
            
            if issue_type == "hardcoded_secret":
                # Implementar correção é complexo e depende de análise manual
                # Registramos apenas a necessidade de revisão
                improvements.append({
                    "file": file_path,
                    "type": "hardcoded_secret_detection",
                    "description": "Detectado secret hardcoded",
                    "requires_manual": True,
                    "suggestion": issue.get("suggestion", "")
                })
            
            elif issue_type == "insecure_request_access":
                # Substituir request.form[x] por request.form.get(x)
                original_content = modified_content
                modified_content = re.sub(
                    r'request\.form\[([\'"]\w+[\'"])\]',
                    r'request.form.get(\1)',
                    modified_content
                )
                
                # Substituir request.args[x] por request.args.get(x)
                modified_content = re.sub(
                    r'request\.args\[([\'"]\w+[\'"])\]',
                    r'request.args.get(\1)',
                    modified_content
                )
                
                if modified_content != original_content:
                    improvements.append({
                        "file": file_path,
                        "type": "fix_request_access",
                        "description": "Substituído acesso direto por método .get()",
                        "original": "request.form['x'] ou request.args['x']",
                        "modified": "request.form.get('x') ou request.args.get('x')"
                    })
            
            # Outras melhorias específicas podem ser adicionadas aqui
        
        return modified_content, improvements


class LauncherAgent(BaseAgent):
    """Agente especializado na página de início"""
    
    def __init__(self, openai_api_key=None):
        super().__init__(
            name="Launcher Agent",
            domain="Página de Início",
            file_patterns=[
                r"index\.html$",
                r"home\.html$",
                r"index\.js$",
                r"home\.js$",
                r"homepage"
            ],
            content_patterns=[
                r"home",
                r"index",
                r"dashboard",
                r"welcome"
            ],
            openai_api_key=openai_api_key
        )


class ReportsListAgent(BaseAgent):
    """Agente especializado na página de listagem de todos os laudos"""
    
    def __init__(self, openai_api_key=None):
        super().__init__(
            name="Reports List Agent",
            domain="Página de Listagem de Laudos",
            file_patterns=[
                r"reports/index\.html$",
                r"reports/list\.html$",
                r"reports\.js$",
                r"reports/list\.js$",
                r"blueprints/reports/templates"
            ],
            content_patterns=[
                r"reports",
                r"laudos",
                r"lista",
                r"table"
            ],
            openai_api_key=openai_api_key
        )


class ReportsSubmissionAgent(BaseAgent):
    """Agente especializado na página de envio de laudos"""
    
    def __init__(self, openai_api_key=None):
        super().__init__(
            name="Reports Submission Agent",
            domain="Envio de Laudos",
            file_patterns=[
                r"reports/create\.html$",
                r"reports/new\.html$",
                r"reports/form\.html$",
                r"reports/submit\.js$",
                r"reports/create\.js$"
            ],
            content_patterns=[
                r"submit",
                r"enviar",
                r"formulário",
                r"upload",
                r"criar laudo",
                r"novo laudo"
            ],
            openai_api_key=openai_api_key
        )


class AdvancedSearchAgent(BaseAgent):
    """Agente especializado na página de busca avançada"""
    
    def __init__(self, openai_api_key=None):
        super().__init__(
            name="Advanced Search Agent",
            domain="Busca Avançada",
            file_patterns=[
                r"search\.html$",
                r"search\.js$",
                r"filter\.js$",
                r"advanced_search"
            ],
            content_patterns=[
                r"search",
                r"busca",
                r"filtro",
                r"pesquisa",
                r"avançada"
            ],
            openai_api_key=openai_api_key
        )


class DashboardAgent(BaseAgent):
    """Agente especializado na página de dashboard"""
    
    def __init__(self, openai_api_key=None):
        super().__init__(
            name="Dashboard Agent",
            domain="Dashboard",
            file_patterns=[
                r"dashboard\.html$",
                r"dashboard\.js$",
                r"charts\.js$",
                r"statistics\.js$",
                r"blueprints/dashboard"
            ],
            content_patterns=[
                r"dashboard",
                r"chart",
                r"gráfico",
                r"estatística",
                r"indicador"
            ],
            openai_api_key=openai_api_key
        )


class FormsAgent(BaseAgent):
    """Agente especializado nos formulários"""
    
    def __init__(self, openai_api_key=None):
        super().__init__(
            name="Forms Agent",
            domain="Formulários",
            file_patterns=[
                r"forms/",
                r"form\.html$",
                r"form\.js$",
                r"forms\.js$",
                r"formularios"
            ],
            content_patterns=[
                r"form",
                r"formulário",
                r"input",
                r"select",
                r"textarea",
                r"label"
            ],
            openai_api_key=openai_api_key
        )


class CalculationsAgent(BaseAgent):
    """Agente especializado nos cálculos"""
    
    def __init__(self, openai_api_key=None):
        super().__init__(
            name="Calculations Agent",
            domain="Cálculos",
            file_patterns=[
                r"calculos/",
                r"calculator",
                r"calc\.js$",
                r"calculo"
            ],
            content_patterns=[
                r"calculo",
                r"cálculo",
                r"calculator",
                r"math\.",
                r"compute"
            ],
            openai_api_key=openai_api_key
        )


class AgentsManager:
    """Gerencia todos os agentes de IA especializados"""
    
    def __init__(self, openai_api_key=None):
        """Inicializa o gerenciador de agentes"""
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.summary_file = os.path.join(AGENTS_REPORTS_DIR, f"summary_{self.timestamp}.json")
        self.text_summary_file = os.path.join(AGENTS_REPORTS_DIR, f"summary_{self.timestamp}.txt")
        
        # Inicializar todos os agentes
        self.agents = [
            FrontendLayoutAgent(openai_api_key=self.openai_api_key),
            BackendAgent(openai_api_key=self.openai_api_key),
            SecurityAgent(openai_api_key=self.openai_api_key),
            LauncherAgent(openai_api_key=self.openai_api_key),
            ReportsListAgent(openai_api_key=self.openai_api_key),
            ReportsSubmissionAgent(openai_api_key=self.openai_api_key),
            AdvancedSearchAgent(openai_api_key=self.openai_api_key),
            DashboardAgent(openai_api_key=self.openai_api_key),
            FormsAgent(openai_api_key=self.openai_api_key),
            CalculationsAgent(openai_api_key=self.openai_api_key)
        ]
        
        logger.info(f"Gerenciador de Agentes inicializado com {len(self.agents)} agentes")
    
    def run_all_agents(self, apply_fixes=False):
        """Executa todos os agentes e gera relatório consolidado"""
        logger.info(f"Iniciando execução de todos os agentes (apply_fixes={apply_fixes})")
        
        results = []
        for agent in self.agents:
            logger.info(f"Executando agente: {agent.name}")
            result = agent.run(apply_fixes=apply_fixes)
            results.append(result)
            
            # Intervalo entre agentes para não sobrecarregar
            time.sleep(2)
        
        # Gerar relatório consolidado
        summary = self._generate_summary(results)
        
        logger.info(f"Execução de todos os agentes concluída. Relatório salvo em {self.text_summary_file}")
        return summary
    
    def _generate_summary(self, results):
        """Gera relatório consolidado da execução de todos os agentes"""
        try:
            # Calcular estatísticas gerais
            total_files = sum(r.get("files_analyzed", 0) for r in results)
            total_issues = sum(r.get("issues_found", 0) for r in results)
            total_improvements = sum(r.get("improvements", 0) for r in results)
            
            # Criar resumo
            summary = {
                "timestamp": self.timestamp,
                "agents_count": len(self.agents),
                "total_files_analyzed": total_files,
                "total_issues_found": total_issues,
                "total_improvements": total_improvements,
                "agents_results": results
            }
            
            # Salvar em JSON
            with open(self.summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Salvar em formato de texto
            with open(self.text_summary_file, 'w') as f:
                f.write(f"=== RESUMO DA EXECUÇÃO DOS AGENTES DE IA ===\n")
                f.write(f"Data: {self.timestamp.replace('_', ' ')}\n\n")
                
                f.write("=== ESTATÍSTICAS GERAIS ===\n")
                f.write(f"Agentes executados: {len(self.agents)}\n")
                f.write(f"Arquivos analisados: {total_files}\n")
                f.write(f"Problemas encontrados: {total_issues}\n")
                f.write(f"Melhorias aplicadas/sugeridas: {total_improvements}\n\n")
                
                f.write("=== RESULTADOS POR AGENTE ===\n")
                for result in results:
                    f.write(f"Agente: {result.get('agent')}\n")
                    f.write(f"  Domínio: {result.get('domain')}\n")
                    f.write(f"  Arquivos analisados: {result.get('files_analyzed')}\n")
                    f.write(f"  Problemas encontrados: {result.get('issues_found')}\n")
                    f.write(f"  Melhorias: {result.get('improvements')}\n")
                    f.write(f"  Relatório: {result.get('report_file')}\n\n")
                
                f.write("=== FIM DO RESUMO ===\n")
            
            return summary
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}")
            return None
    
    def schedule_agents(self, interval_minutes=5):
        """Agenda execução periódica dos agentes"""
        logger.info(f"Agendando execução dos agentes a cada {interval_minutes} minutos")
        
        # Criar arquivo de configuração de agendamento
        config_file = os.path.join(AGENTS_DIR, "scheduler_config.json")
        config = {
            "interval_minutes": interval_minutes,
            "apply_fixes": True,
            "last_run": None,
            "enabled": True
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Criar script de execução
        run_script = os.path.join(AGENTS_DIR, "run_agents.py")
        with open(run_script, 'w') as f:
            f.write("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import time
import datetime
import logging
from pathlib import Path

# Adicionar diretório pai ao path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Importar o gerenciador de agentes
from tests.ai_agents import AgentsManager

# Configurações de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("zelopack_agents_scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("zelopack_agents_scheduler")

def main():
    # Carregar configuração
    config_file = os.path.join(os.path.dirname(__file__), "scheduler_config.json")
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if not config.get("enabled", True):
            logger.info("Agendamento desativado. Saindo.")
            return
        
        # Executar agentes
        logger.info("Iniciando execução agendada dos agentes")
        manager = AgentsManager()
        summary = manager.run_all_agents(apply_fixes=config.get("apply_fixes", True))
        
        # Atualizar configuração com a última execução
        config["last_run"] = datetime.datetime.now().isoformat()
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Execução agendada concluída. Próxima execução em {config.get('interval_minutes', 5)} minutos")
    except Exception as e:
        logger.error(f"Erro na execução agendada: {e}")

if __name__ == "__main__":
    main()
""")
        
        # Tornar o script executável
        os.chmod(run_script, 0o755)
        
        # Configurar cron/agendador de tarefas
        if sys.platform == "linux" or sys.platform == "darwin":
            # Linux/MacOS: configurar cron
            try:
                # Ver se já está no crontab
                result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
                current_crontab = result.stdout
                
                # Verificar se o script já está configurado
                if run_script in current_crontab:
                    logger.info("Agendamento já está configurado no crontab")
                    return
                
                # Configurar o cron para executar a cada X minutos
                cron_line = f"*/{interval_minutes} * * * * {sys.executable} {run_script}\n"
                
                if result.returncode == 0:
                    new_crontab = current_crontab + cron_line
                else:
                    new_crontab = cron_line
                
                # Salvar em arquivo temporário
                temp_file = "/tmp/zelopack_agents_crontab"
                with open(temp_file, 'w') as f:
                    f.write(new_crontab)
                
                # Instalar o novo crontab
                subprocess.run(f"crontab {temp_file}", shell=True, check=True)
                os.remove(temp_file)
                
                logger.info(f"Agendamento configurado no crontab para executar a cada {interval_minutes} minutos")
            except Exception as e:
                logger.error(f"Erro ao configurar crontab: {e}")
        else:
            # Windows: configurar Task Scheduler
            try:
                # Criar arquivo batch para executar o script
                batch_file = os.path.join(os.path.dirname(run_script), "run_agents.bat")
                with open(batch_file, 'w') as f:
                    f.write(f'@echo off\n"{sys.executable}" "{run_script}"\n')
                
                # Agendar a tarefa
                task_name = "ZelopackAgents"
                cmd = f'schtasks /create /sc MINUTE /mo {interval_minutes} /tn "{task_name}" /tr "{batch_file}" /f'
                subprocess.run(cmd, shell=True, check=True)
                
                logger.info(f"Agendamento configurado no Task Scheduler para executar a cada {interval_minutes} minutos")
            except Exception as e:
                logger.error(f"Erro ao configurar Task Scheduler: {e}")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Agentes de IA Especializados para Zelopack')
    parser.add_argument('--key', help='Chave da API OpenAI')
    parser.add_argument('--run', action='store_true', help='Executar todos os agentes')
    parser.add_argument('--fix', action='store_true', help='Aplicar correções automáticas')
    parser.add_argument('--schedule', action='store_true', help='Configurar agendamento dos agentes')
    parser.add_argument('--interval', type=int, default=5, help='Intervalo em minutos para agendamento')
    
    args = parser.parse_args()
    
    # Usar a chave da API da linha de comando ou do ambiente
    openai_key = args.key or os.environ.get("OPENAI_API_KEY")
    
    # Inicializar o gerenciador de agentes
    manager = AgentsManager(openai_api_key=openai_key)
    
    # Executar conforme os argumentos
    if args.schedule:
        manager.schedule_agents(interval_minutes=args.interval)
    elif args.run:
        manager.run_all_agents(apply_fixes=args.fix)
    else:
        # Modo padrão: executar sem aplicar correções
        manager.run_all_agents(apply_fixes=False)


if __name__ == "__main__":
    main()