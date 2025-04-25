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
import json
import time
import logging
import datetime
import subprocess
import re
import glob
import argparse
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('zelopack_monitor')

# Constantes
REPORT_DIR = 'tests/reports'
COMPONENT_TEST_SCRIPT = 'tests/test_components.py'
IMPROVEMENT_RULES_FILE = 'tests/improvement_rules.json'

# Criar diretórios necessários
os.makedirs(REPORT_DIR, exist_ok=True)

class ZelopackMonitor:
    """Sistema de monitoramento inteligente do Zelopack"""
    
    def __init__(self):
        """Inicializar o monitor"""
        self.last_run = None
        self.improvements = []
        self.load_improvement_rules()
        
    def load_improvement_rules(self):
        """Carrega regras de melhoria do arquivo JSON ou usa padrões"""
        try:
            if os.path.exists(IMPROVEMENT_RULES_FILE):
                with open(IMPROVEMENT_RULES_FILE, 'r', encoding='utf-8') as f:
                    self.rules = json.load(f)
                logger.info(f"Regras de melhoria carregadas de {IMPROVEMENT_RULES_FILE}")
            else:
                # Regras padrão se o arquivo não existir
                self.rules = {
                    "js": {
                        "patterns": [
                            {"pattern": r"console\.log\(", "message": "Remover console.log em produção", "severity": "warning"},
                            {"pattern": r"function\s*\(\)\s*{", "message": "Usar arrow functions para expressões simples", "severity": "suggestion"},
                            {"pattern": r"var\s+", "message": "Substituir 'var' por 'const' ou 'let'", "severity": "warning"},
                            {"pattern": r"\.forEach\(\s*function", "message": "Usar arrow function com forEach", "severity": "suggestion"},
                            {"pattern": r"setTimeout\s*\(\s*function", "message": "Usar arrow function com setTimeout", "severity": "suggestion"}
                        ]
                    },
                    "css": {
                        "patterns": [
                            {"pattern": r"!important", "message": "Evitar uso de !important", "severity": "warning"},
                            {"pattern": r"rgba?\(", "message": "Considerar usar variáveis CSS para cores", "severity": "suggestion"},
                            {"pattern": r"@media\s+screen", "message": "Usar pontos de quebra consistentes para responsividade", "severity": "info"}
                        ]
                    },
                    "html": {
                        "patterns": [
                            {"pattern": r"<img[^>]+(?!alt=)[^>]*>", "message": "Adicionar atributo alt em imagens", "severity": "warning"},
                            {"pattern": r"<table", "message": "Garantir que tabelas são responsivas com .table-responsive", "severity": "suggestion"},
                            {"pattern": r"style=\"", "message": "Evitar estilos inline", "severity": "warning"}
                        ]
                    },
                    "py": {
                        "patterns": [
                            {"pattern": r"print\(", "message": "Substituir print por logger em código de produção", "severity": "warning"},
                            {"pattern": r"except\s*:", "message": "Evitar captura genérica de exceções", "severity": "warning"},
                            {"pattern": r"\.execute\([\"']", "message": "Risco de injeção SQL, usar parâmetros", "severity": "critical"},
                            {"pattern": r"os\.system\(", "message": "Evitar os.system, usar subprocess", "severity": "warning"}
                        ]
                    }
                }
                # Salvar regras padrão para uso futuro
                with open(IMPROVEMENT_RULES_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.rules, f, indent=4)
                logger.info(f"Regras padrão criadas e salvas em {IMPROVEMENT_RULES_FILE}")
        except Exception as e:
            logger.error(f"Erro ao carregar regras de melhoria: {e}")
            # Fallback para regras mínimas
            self.rules = {"js": {"patterns": []}, "css": {"patterns": []}, "html": {"patterns": []}, "py": {"patterns": []}}

    def run_component_tests(self):
        """Executa os testes de componentes"""
        logger.info("Iniciando testes de componentes")
        
        try:
            result = subprocess.run(
                [sys.executable, COMPONENT_TEST_SCRIPT],
                capture_output=True,
                text=True
            )
            
            success = result.returncode == 0
            logger.info(f"Testes de componentes concluídos com status: {success}")
            
            # Analisar a saída dos testes
            test_output = result.stdout + result.stderr
            
            return {
                "success": success,
                "output": test_output,
                "return_code": result.returncode,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao executar testes de componentes: {e}")
            return {
                "success": False,
                "output": str(e),
                "return_code": -1,
                "timestamp": datetime.datetime.now().isoformat()
            }

    def analyze_file(self, file_path):
        """Analisa um arquivo em busca de melhorias"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lstrip('.')
        
        # Mapear extensão para tipo de regra
        rule_type = {
            'js': 'js',
            'css': 'css',
            'html': 'html',
            'py': 'py',
            'jinja2': 'html',
            'htm': 'html',
            'scss': 'css',
            'less': 'css',
            'jsx': 'js',
            'ts': 'js',
            'tsx': 'js'
        }.get(ext.lower())
        
        if not rule_type or rule_type not in self.rules:
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            improvements = []
            
            # Verificar cada padrão definido nas regras
            for pattern_info in self.rules[rule_type]['patterns']:
                pattern = pattern_info['pattern']
                message = pattern_info['message']
                severity = pattern_info['severity']
                
                matches = re.finditer(pattern, content)
                for match in matches:
                    # Calcular o número da linha
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Obter o contexto da linha
                    lines = content.splitlines()
                    line_content = lines[line_number - 1] if line_number <= len(lines) else ""
                    
                    improvements.append({
                        "file": file_path,
                        "line": line_number,
                        "message": message,
                        "severity": severity,
                        "pattern": pattern,
                        "context": line_content.strip()
                    })
            
            return improvements
            
        except Exception as e:
            logger.error(f"Erro ao analisar {file_path}: {e}")
            return []

    def scan_for_improvements(self):
        """Escaneia o código em busca de possíveis melhorias"""
        logger.info("Iniciando análise de código para melhorias")
        
        improvements = []
        file_patterns = [
            'static/js/**/*.js',
            'static/css/**/*.css',
            'templates/**/*.html',
            '*.py',
            'blueprints/**/*.py',
            'utils/**/*.py',
            'models/**/*.py'
        ]
        
        files_to_analyze = []
        for pattern in file_patterns:
            files_to_analyze.extend(glob.glob(pattern, recursive=True))
        
        # Limitar a arquivos que realmente existem e são arquivos regulares
        files_to_analyze = [f for f in files_to_analyze if os.path.isfile(f)]
        
        # Usar processamento paralelo para arquivos maiores
        if len(files_to_analyze) > 10:
            with ThreadPoolExecutor(max_workers=min(os.cpu_count(), 4)) as executor:
                results = list(executor.map(self.analyze_file, files_to_analyze))
                
            for result in results:
                improvements.extend(result)
        else:
            for file_path in files_to_analyze:
                file_improvements = self.analyze_file(file_path)
                improvements.extend(file_improvements)
        
        # Agrupar melhorias por tipo e severidade para o relatório
        self.improvements = sorted(improvements, key=lambda x: (x['severity'], x['file'], x['line']))
        logger.info(f"Análise concluída, encontradas {len(improvements)} possíveis melhorias")
        
        return improvements

    def check_performance(self):
        """Verifica métricas de performance do sistema"""
        logger.info("Verificando métricas de performance")
        
        performance_issues = []
        
        # Verificar tamanho de arquivos estáticos
        for path, folders, files in os.walk('static'):
            for file in files:
                file_path = os.path.join(path, file)
                file_size = os.path.getsize(file_path)
                
                # Definir limites de tamanho por tipo de arquivo
                if file.endswith('.js') and file_size > 500 * 1024:
                    performance_issues.append({
                        "type": "large_file",
                        "file": file_path,
                        "size": file_size,
                        "message": f"Arquivo JavaScript grande ({file_size/1024:.1f} KB). Considere dividir ou minificar."
                    })
                elif file.endswith('.css') and file_size > 250 * 1024:
                    performance_issues.append({
                        "type": "large_file",
                        "file": file_path,
                        "size": file_size,
                        "message": f"Arquivo CSS grande ({file_size/1024:.1f} KB). Considere dividir ou minificar."
                    })
                elif file.endswith(('.jpg', '.jpeg', '.png')) and file_size > 500 * 1024:
                    performance_issues.append({
                        "type": "large_image",
                        "file": file_path,
                        "size": file_size,
                        "message": f"Imagem grande ({file_size/1024:.1f} KB). Considere otimizar ou usar WebP."
                    })
        
        # Verificar duplicação em JavaScript
        js_content = {}
        for js_file in glob.glob('static/js/**/*.js', recursive=True):
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    js_content[js_file] = f.read()
            except Exception:
                continue
        
        # Verificação simples de funções duplicadas (poderia ser mais sofisticada com AST)
        function_defs = {}
        for js_file, content in js_content.items():
            function_matches = re.finditer(r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*{', content)
            for match in function_matches:
                func_name = match.group(1)
                if func_name in function_defs:
                    performance_issues.append({
                        "type": "duplicate_function",
                        "function": func_name,
                        "file1": function_defs[func_name],
                        "file2": js_file,
                        "message": f"Função '{func_name}' possivelmente duplicada em múltiplos arquivos"
                    })
                else:
                    function_defs[func_name] = js_file
        
        return performance_issues

    def auto_fix_issues(self, improvements, dry_run=True):
        """Tenta corrigir automaticamente problemas simples"""
        logger.info(f"Tentando corrigir automaticamente problemas {'(modo simulação)' if dry_run else ''}")
        
        fixes_applied = []
        for issue in improvements:
            if issue['severity'] not in ['critical', 'warning']:
                continue  # Apenas corrigir problemas de alta severidade
                
            file_path = issue['file']
            pattern = issue['pattern']
            
            # Lista de padrões que sabemos como corrigir automaticamente
            auto_fixable = {
                r"console\.log\(": (r"console\.log\(([^)]*)\)", r"// console.log(\1)"),
                r"var\s+": (r"var\s+([a-zA-Z_$][a-zA-Z0-9_$]*)", r"let \1"),
                r"\.forEach\(\s*function": (r"\.forEach\(\s*function\s*\(([^)]*)\)\s*{([^}]*)}", r".forEach((\1) => {\2}"),
                r"setTimeout\s*\(\s*function": (r"setTimeout\s*\(\s*function\s*\(([^)]*)\)\s*{([^}]*)}", r"setTimeout((\1) => {\2}"),
                r"print\(": (r"print\(([^)]*)\)", r"logger.debug(\1)"),
                r"except\s*:": (r"except\s*:", r"except Exception as e:"),
            }
            
            if pattern in auto_fixable:
                search_pattern, replace_pattern = auto_fixable[pattern]
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = re.sub(search_pattern, replace_pattern, content)
                    
                    if new_content != content:
                        if not dry_run:
                            # Fazer backup do arquivo original
                            backup_path = f"{file_path}.bak"
                            shutil.copy2(file_path, backup_path)
                            
                            # Escrever o conteúdo corrigido
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                        
                        fixes_applied.append({
                            "file": file_path,
                            "pattern": pattern,
                            "message": issue['message'],
                            "applied": not dry_run
                        })
                except Exception as e:
                    logger.error(f"Erro ao tentar corrigir {file_path}: {e}")
        
        logger.info(f"Correções automáticas: {len(fixes_applied)} {'simuladas' if dry_run else 'aplicadas'}")
        return fixes_applied

    def generate_report(self, test_results, improvements, performance_issues, fixes):
        """Gera um relatório detalhado com os resultados"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_filename = f"{REPORT_DIR}/zelopack_report_{timestamp}.json"
        
        # Contagens de severidade para o resumo
        severity_counts = {
            "critical": 0,
            "warning": 0,
            "suggestion": 0,
            "info": 0
        }
        
        for issue in improvements:
            severity = issue.get('severity', 'info')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        report = {
            "timestamp": timestamp,
            "test_results": test_results,
            "improvements": {
                "total": len(improvements),
                "by_severity": severity_counts,
                "items": improvements
            },
            "performance": {
                "total_issues": len(performance_issues),
                "items": performance_issues
            },
            "auto_fixes": {
                "total_applied": len([f for f in fixes if f.get('applied', False)]),
                "total_available": len(fixes),
                "items": fixes
            },
            "summary": {
                "tests_passed": test_results.get('success', False),
                "critical_issues": severity_counts.get('critical', 0),
                "warnings": severity_counts.get('warning', 0),
                "suggestions": severity_counts.get('suggestion', 0) + severity_counts.get('info', 0),
                "performance_issues": len(performance_issues)
            }
        }
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Relatório completo gerado: {report_filename}")
        
        # Gerar também uma versão em texto para fácil leitura
        txt_report_filename = f"{REPORT_DIR}/zelopack_report_{timestamp}.txt"
        self.generate_text_report(report, txt_report_filename)
        
        return report_filename, txt_report_filename

    def generate_text_report(self, report, filename):
        """Gera uma versão em texto do relatório para fácil leitura"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== RELATÓRIO DE MONITORAMENTO ZELOPACK ===\n")
            f.write(f"Data: {report['timestamp']}\n\n")
            
            # Resumo
            f.write("=== RESUMO ===\n")
            f.write(f"Testes: {'PASSOU' if report['summary']['tests_passed'] else 'FALHOU'}\n")
            f.write(f"Problemas críticos: {report['summary']['critical_issues']}\n")
            f.write(f"Avisos: {report['summary']['warnings']}\n")
            f.write(f"Sugestões: {report['summary']['suggestions']}\n")
            f.write(f"Problemas de performance: {report['summary']['performance_issues']}\n\n")
            
            # Detalhes dos testes
            f.write("=== RESULTADOS DOS TESTES ===\n")
            test_results = report['test_results']
            f.write(f"Status: {'SUCESSO' if test_results.get('success', False) else 'FALHA'}\n")
            f.write(f"Código de retorno: {test_results.get('return_code', 'N/A')}\n")
            f.write("\n")
            
            # Problemas críticos
            critical_issues = [i for i in report['improvements']['items'] if i.get('severity') == 'critical']
            if critical_issues:
                f.write("=== PROBLEMAS CRÍTICOS ===\n")
                for issue in critical_issues:
                    f.write(f"Arquivo: {issue['file']}, Linha: {issue['line']}\n")
                    f.write(f"Mensagem: {issue['message']}\n")
                    f.write(f"Contexto: {issue['context']}\n")
                    f.write("\n")
            
            # Avisos
            warning_issues = [i for i in report['improvements']['items'] if i.get('severity') == 'warning']
            if warning_issues:
                f.write("=== AVISOS ===\n")
                for issue in warning_issues:
                    f.write(f"Arquivo: {issue['file']}, Linha: {issue['line']}\n")
                    f.write(f"Mensagem: {issue['message']}\n")
                    f.write(f"Contexto: {issue['context']}\n")
                    f.write("\n")
            
            # Problemas de performance
            if report['performance']['items']:
                f.write("=== PROBLEMAS DE PERFORMANCE ===\n")
                for issue in report['performance']['items']:
                    f.write(f"Tipo: {issue['type']}\n")
                    f.write(f"Arquivo: {issue['file']}\n")
                    f.write(f"Mensagem: {issue['message']}\n")
                    f.write("\n")
            
            # Correções automáticas
            if report['auto_fixes']['items']:
                f.write("=== CORREÇÕES AUTOMÁTICAS ===\n")
                for fix in report['auto_fixes']['items']:
                    status = "Aplicada" if fix.get('applied', False) else "Disponível"
                    f.write(f"Arquivo: {fix['file']}\n")
                    f.write(f"Status: {status}\n")
                    f.write(f"Problema: {fix['message']}\n")
                    f.write("\n")
            
            # Sugestões de melhoria
            suggestion_issues = [i for i in report['improvements']['items'] 
                                if i.get('severity') in ['suggestion', 'info']]
            if suggestion_issues:
                f.write("=== SUGESTÕES DE MELHORIA ===\n")
                for issue in suggestion_issues[:10]:  # Limitar a 10 sugestões
                    f.write(f"Arquivo: {issue['file']}, Linha: {issue['line']}\n")
                    f.write(f"Sugestão: {issue['message']}\n")
                    f.write("\n")
                
                if len(suggestion_issues) > 10:
                    f.write(f"...e mais {len(suggestion_issues) - 10} sugestões. Veja o relatório completo para detalhes.\n\n")
        
        logger.info(f"Relatório em texto gerado: {filename}")

    def run_monitoring_cycle(self, fix_issues=False):
        """Executa um ciclo completo de monitoramento"""
        logger.info("Iniciando ciclo de monitoramento")
        
        # Executar testes de componentes
        test_results = self.run_component_tests()
        
        # Analisar código e buscar melhorias
        improvements = self.scan_for_improvements()
        
        # Verificar performance
        performance_issues = self.check_performance()
        
        # Tentar corrigir problemas automaticamente
        fixes = self.auto_fix_issues(improvements, dry_run=not fix_issues)
        
        # Gerar relatório
        report_file, txt_report = self.generate_report(
            test_results, improvements, performance_issues, fixes)
        
        # Mostrar resumo no console
        self.print_summary(test_results, improvements, performance_issues, fixes)
        
        self.last_run = datetime.datetime.now()
        
        return {
            "success": test_results.get('success', False),
            "report_file": report_file,
            "txt_report": txt_report,
            "improvements": len(improvements),
            "critical_issues": len([i for i in improvements if i.get('severity') == 'critical']),
            "performance_issues": len(performance_issues),
            "fixes_applied": len([f for f in fixes if f.get('applied', False)])
        }

    def print_summary(self, test_results, improvements, performance_issues, fixes):
        """Imprime um resumo dos resultados no console"""
        print("\n" + "=" * 60)
        print("=== RESUMO DO MONITORAMENTO ZELOPACK ===")
        print("=" * 60)
        
        # Status dos testes
        test_status = "PASSOU" if test_results.get('success', False) else "FALHOU"
        print(f"Testes de componentes: {test_status}")
        
        # Contagem de melhorias por severidade
        severity_counts = {"critical": 0, "warning": 0, "suggestion": 0, "info": 0}
        for issue in improvements:
            severity = issue.get('severity', 'info')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        print(f"Problemas encontrados:")
        print(f"  - Críticos: {severity_counts.get('critical', 0)}")
        print(f"  - Avisos: {severity_counts.get('warning', 0)}")
        print(f"  - Sugestões: {severity_counts.get('suggestion', 0) + severity_counts.get('info', 0)}")
        
        # Performance
        print(f"Problemas de performance: {len(performance_issues)}")
        
        # Correções
        fixes_applied = len([f for f in fixes if f.get('applied', False)])
        print(f"Correções automáticas: {fixes_applied} aplicadas / {len(fixes)} disponíveis")
        print("=" * 60)
        
        # Mostrar detalhes dos problemas críticos
        critical_issues = [i for i in improvements if i.get('severity') == 'critical']
        if critical_issues:
            print("\nProblemas críticos encontrados:")
            for issue in critical_issues:
                print(f"  - {issue['file']}:{issue['line']} - {issue['message']}")
        
        # Sugerir próximos passos
        print("\nPróximos passos recomendados:")
        if severity_counts.get('critical', 0) > 0:
            print("  - Corrija os problemas críticos imediatamente")
        if severity_counts.get('warning', 0) > 0:
            print("  - Revise os avisos na próxima iteração")
        if len(performance_issues) > 0:
            print("  - Otimize os problemas de performance")
        
        print("\nRelatório completo disponível em:")
        print(f"  - {REPORT_DIR}/")
        print("=" * 60 + "\n")

def setup_cron_job():
    """Configura um job cron para executar o monitor periodicamente"""
    import platform
    
    script_path = os.path.abspath(__file__)
    
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        # Para sistemas Unix-like
        cron_cmd = f"0 */4 * * * {sys.executable} {script_path} --run"
        
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
            
            with open('/tmp/zelopack_crontab', 'w') as f:
                f.write(new_crontab)
            
            install_cmd = "crontab /tmp/zelopack_crontab"
            subprocess.run(install_cmd, shell=True, check=True)
            os.remove('/tmp/zelopack_crontab')
            
            print("Job cron configurado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar job cron: {e}")
            return False
    else:
        # Para Windows, sugerir usar o Agendador de Tarefas
        print("Para Windows, configure o script para execução periódica usando o Agendador de Tarefas")
        print(f"Comando: {sys.executable} {script_path} --run")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Sistema de Monitoramento e Melhoria Contínua para Zelopack')
    parser.add_argument('--run', action='store_true', help='Executar um ciclo de monitoramento')
    parser.add_argument('--setup-cron', action='store_true', help='Configurar job cron para execução periódica')
    parser.add_argument('--fix', action='store_true', help='Tentar corrigir problemas automaticamente')
    args = parser.parse_args()
    
    if args.setup_cron:
        setup_cron_job()
        return
    
    monitor = ZelopackMonitor()
    
    if args.run:
        monitor.run_monitoring_cycle(fix_issues=args.fix)
    else:
        print("Sistema de Monitoramento e Melhoria Contínua para Zelopack")
        print("Opções disponíveis:")
        print("  --run         Executar um ciclo de monitoramento")
        print("  --setup-cron  Configurar job cron para execução periódica")
        print("  --fix         Tentar corrigir problemas automaticamente")
        print("\nExemplo: python zelopack_monitor.py --run")

if __name__ == "__main__":
    main()