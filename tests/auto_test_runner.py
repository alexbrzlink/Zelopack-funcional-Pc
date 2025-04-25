#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema Automático de Teste Contínuo do Zelopack

Este script executa automaticamente:
1. Testes periódicos de todos os componentes
2. Análises e verificações de código
3. Reporte de erros e problemas encontrados
4. Sugestões de melhorias usando IA

MODO DE USO:
1. Em segundo plano: python auto_test_runner.py --daemon
2. Teste único: python auto_test_runner.py --run
3. Ver último relatório: python auto_test_runner.py --report
"""

import os
import sys
import json
import time
import logging
import argparse
import datetime
import subprocess
import signal
import re
import glob
import threading
import multiprocessing
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/auto_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('zelopack_test_runner')

# Diretórios e arquivos importantes
REPORT_DIR = 'tests/reports'
COMPONENT_TEST_SCRIPT = 'tests/test_components.py'
MONITOR_SCRIPT = 'tests/zelopack_monitor.py'
AI_ASSISTANT_SCRIPT = 'tests/zelopack_ai_assistant.py'
STATUS_FILE = 'tests/test_status.json'
LAST_REPORT_FILE = 'tests/last_report.json'

# Criar diretórios necessários
os.makedirs(REPORT_DIR, exist_ok=True)

# Configurações globais
TEST_INTERVAL = 3600  # 1 hora entre testes em modo daemon
WATCH_INTERVAL = 10  # 10 segundos para verificar mudanças no modo watch

class AutoTestRunner:
    """Runner de testes automáticos do Zelopack"""
    
    def __init__(self):
        """Inicializa o runner"""
        self.running = False
        self.last_run = None
        self.current_status = self._load_status()
        
    def _load_status(self):
        """Carrega o status atual dos testes"""
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Status padrão
        return {
            "last_run": None,
            "total_runs": 0,
            "pass_count": 0,
            "fail_count": 0,
            "last_status": "unknown",
            "watched_files": []
        }
    
    def _save_status(self):
        """Salva o status atual dos testes"""
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump(self.current_status, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar status: {e}")
    
    def run_tests(self):
        """Executa a suíte completa de testes"""
        logger.info("Iniciando execução dos testes automáticos")
        
        start_time = time.time()
        results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "components": self._run_component_tests(),
            "code_quality": self._run_code_quality_checks(),
            "ai_suggestions": self._get_ai_suggestions()
        }
        end_time = time.time()
        
        results["run_time"] = end_time - start_time
        results["success"] = results["components"]["success"] and results["code_quality"]["success"]
        
        # Atualizar status
        self.current_status["last_run"] = datetime.datetime.now().isoformat()
        self.current_status["total_runs"] += 1
        
        if results["success"]:
            self.current_status["pass_count"] += 1
            self.current_status["last_status"] = "pass"
        else:
            self.current_status["fail_count"] += 1
            self.current_status["last_status"] = "fail"
        
        self._save_status()
        
        # Salvar o relatório
        self._save_report(results)
        
        # Exibir resumo
        self._display_summary(results)
        
        self.last_run = datetime.datetime.now()
        
        return results
    
    def _run_component_tests(self):
        """Executa os testes de componentes"""
        logger.info("Executando testes de componentes")
        
        try:
            result = subprocess.run(
                [sys.executable, COMPONENT_TEST_SCRIPT],
                capture_output=True,
                text=True,
                timeout=300  # Timeout de 5 minutos
            )
            
            success = result.returncode == 0
            logger.info(f"Testes de componentes concluídos com status: {success}")
            
            # Extrair informações importantes do output
            test_output = result.stdout + result.stderr
            
            # Detectar falhas específicas
            test_failures = []
            failure_match = re.findall(r'FAIL: (test_\w+)', test_output)
            
            for failure in failure_match:
                # Tentar extrair a mensagem de erro
                error_match = re.search(f"{failure}.*?AssertionError: (.*?)(?:\n\n|$)", test_output, re.DOTALL)
                error_message = error_match.group(1).strip() if error_match else "Erro desconhecido"
                
                test_failures.append({
                    "test": failure,
                    "error": error_message
                })
            
            return {
                "success": success,
                "return_code": result.returncode,
                "output": test_output,
                "failures": test_failures,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            logger.error("Timeout ao executar testes de componentes")
            return {
                "success": False,
                "return_code": -1,
                "output": "Timeout ao executar testes de componentes",
                "failures": [{"test": "timeout", "error": "Os testes demoraram muito para concluir"}],
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao executar testes de componentes: {e}")
            return {
                "success": False,
                "return_code": -1,
                "output": str(e),
                "failures": [{"test": "exception", "error": str(e)}],
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _run_code_quality_checks(self):
        """Executa verificações de qualidade de código"""
        logger.info("Executando verificações de qualidade de código")
        
        try:
            result = subprocess.run(
                [sys.executable, MONITOR_SCRIPT, '--run'],
                capture_output=True,
                text=True,
                timeout=300  # Timeout de 5 minutos
            )
            
            success = result.returncode == 0
            logger.info(f"Verificações de qualidade concluídas com status: {success}")
            
            # Tentar extrair o caminho do relatório gerado
            report_match = re.search(r'Relatório completo gerado: (.*?)\n', result.stdout)
            report_file = report_match.group(1) if report_match else None
            
            # Carregar detalhes do relatório se disponível
            report_data = {}
            if report_file and os.path.exists(report_file):
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                except:
                    pass
            
            return {
                "success": success,
                "return_code": result.returncode,
                "output": result.stdout + result.stderr,
                "report_file": report_file,
                "report_data": report_data,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            logger.error("Timeout ao executar verificações de qualidade")
            return {
                "success": False,
                "return_code": -1,
                "output": "Timeout ao executar verificações de qualidade",
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao executar verificações de qualidade: {e}")
            return {
                "success": False,
                "return_code": -1,
                "output": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _get_ai_suggestions(self):
        """Obtém sugestões de melhoria usando IA"""
        logger.info("Obtendo sugestões de melhoria com IA")
        
        try:
            result = subprocess.run(
                [sys.executable, AI_ASSISTANT_SCRIPT, '--suggestions'],
                capture_output=True,
                text=True,
                timeout=300  # Timeout de 5 minutos
            )
            
            success = result.returncode == 0
            logger.info(f"Obtenção de sugestões concluída com status: {success}")
            
            # Tentar extrair o caminho do arquivo de sugestões
            suggestions_match = re.search(r'Sugestões salvas em (.*?\.json)', result.stdout)
            suggestions_file = suggestions_match.group(1) if suggestions_match else None
            
            # Carregar sugestões se disponível
            suggestions_data = []
            if suggestions_file and os.path.exists(suggestions_file):
                try:
                    with open(suggestions_file, 'r', encoding='utf-8') as f:
                        suggestions_data = json.load(f)
                except:
                    pass
            
            return {
                "success": success,
                "output": result.stdout + result.stderr,
                "suggestions_file": suggestions_file,
                "suggestions": suggestions_data,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            logger.error("Timeout ao obter sugestões de IA")
            return {
                "success": False,
                "output": "Timeout ao obter sugestões de IA",
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter sugestões de IA: {e}")
            return {
                "success": False,
                "output": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _save_report(self, results):
        """Salva o relatório da execução"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(REPORT_DIR, f"auto_test_report_{timestamp}.json")
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
                
            # Atualizar também o arquivo de último relatório
            with open(LAST_REPORT_FILE, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
                
            logger.info(f"Relatório salvo em {report_file}")
            
            # Gerar também um relatório em texto
            txt_report_file = os.path.join(REPORT_DIR, f"auto_test_report_{timestamp}.txt")
            self._generate_text_report(results, txt_report_file)
            
            return report_file
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")
            return None
    
    def _generate_text_report(self, results, filename):
        """Gera um relatório em texto para fácil leitura"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== RELATÓRIO DE TESTES AUTOMÁTICOS ZELOPACK ===\n")
                f.write(f"Data: {results['timestamp']}\n")
                f.write(f"Status geral: {'SUCESSO' if results['success'] else 'FALHA'}\n")
                f.write(f"Tempo de execução: {results['run_time']:.2f} segundos\n\n")
                
                # Testes de componentes
                f.write("=== TESTES DE COMPONENTES ===\n")
                comp_results = results['components']
                f.write(f"Status: {'PASSOU' if comp_results['success'] else 'FALHOU'}\n")
                
                if not comp_results['success'] and comp_results['failures']:
                    f.write("Falhas encontradas:\n")
                    for failure in comp_results['failures']:
                        f.write(f"- {failure['test']}: {failure['error']}\n")
                f.write("\n")
                
                # Verificações de qualidade
                f.write("=== VERIFICAÇÕES DE QUALIDADE DE CÓDIGO ===\n")
                quality_results = results['code_quality']
                f.write(f"Status: {'PASSOU' if quality_results['success'] else 'FALHOU'}\n")
                
                if 'report_data' in quality_results and quality_results['report_data']:
                    report_data = quality_results['report_data']
                    summary = report_data.get('summary', {})
                    
                    f.write("Resumo de problemas:\n")
                    f.write(f"- Problemas críticos: {summary.get('critical_issues', 0)}\n")
                    f.write(f"- Avisos: {summary.get('warnings', 0)}\n")
                    f.write(f"- Sugestões: {summary.get('suggestions', 0)}\n")
                    f.write(f"- Problemas de performance: {summary.get('performance_issues', 0)}\n")
                f.write("\n")
                
                # Sugestões de IA
                f.write("=== SUGESTÕES DE MELHORIA ===\n")
                ai_results = results['ai_suggestions']
                if 'suggestions' in ai_results and ai_results['suggestions']:
                    suggestions = ai_results['suggestions']
                    
                    f.write(f"Total de sugestões: {len(suggestions)}\n\n")
                    for i, suggestion in enumerate(suggestions[:5], 1):
                        f.write(f"{i}. {suggestion.get('title', 'Sem título')}\n")
                        f.write(f"   Tipo: {suggestion.get('type', 'N/A')}\n")
                        f.write(f"   {suggestion.get('description', 'Sem descrição')}\n\n")
                    
                    if len(suggestions) > 5:
                        f.write(f"... e mais {len(suggestions) - 5} sugestões no relatório completo.\n")
                else:
                    f.write("Nenhuma sugestão disponível.\n")
                
                # Conclusão
                f.write("\n=== CONCLUSÃO ===\n")
                if results['success']:
                    f.write("Todos os testes passaram com sucesso!\n")
                else:
                    f.write("Foram encontrados problemas que precisam ser corrigidos.\n")
                    
                f.write("\nRelatório completo disponível em: " + os.path.abspath(REPORT_DIR) + "\n")
                
            logger.info(f"Relatório de texto gerado em {filename}")
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de texto: {e}")
    
    def _display_summary(self, results):
        """Exibe um resumo dos resultados no console"""
        print("\n" + "=" * 60)
        print("=== RESUMO DE TESTES AUTOMÁTICOS ZELOPACK ===")
        print("=" * 60)
        
        status = "PASSOU" if results['success'] else "FALHOU"
        print(f"Status geral: {status}")
        print(f"Tempo de execução: {results['run_time']:.2f} segundos")
        print()
        
        # Testes de componentes
        comp_status = "PASSOU" if results['components']['success'] else "FALHOU"
        print(f"Testes de componentes: {comp_status}")
        
        if not results['components']['success'] and results['components']['failures']:
            print("  Falhas encontradas:")
            for failure in results['components']['failures']:
                print(f"  - {failure['test']}: {failure['error']}")
        print()
        
        # Verificações de qualidade
        quality_status = "PASSOU" if results['code_quality']['success'] else "FALHOU"
        print(f"Verificações de qualidade: {quality_status}")
        
        if 'report_data' in results['code_quality'] and results['code_quality']['report_data']:
            report_data = results['code_quality']['report_data']
            summary = report_data.get('summary', {})
            
            print("  Resumo de problemas:")
            print(f"  - Problemas críticos: {summary.get('critical_issues', 0)}")
            print(f"  - Avisos: {summary.get('warnings', 0)}")
            print(f"  - Sugestões: {summary.get('suggestions', 0)}")
            print(f"  - Problemas de performance: {summary.get('performance_issues', 0)}")
        print()
        
        # Sugestões de IA
        if 'suggestions' in results['ai_suggestions'] and results['ai_suggestions']['suggestions']:
            suggestions = results['ai_suggestions']['suggestions']
            print(f"Sugestões de melhoria: {len(suggestions)} encontradas")
            
            # Mostrar as primeiras 3 sugestões
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"  {i}. {suggestion.get('title', 'Sem título')}")
            
            if len(suggestions) > 3:
                print(f"  ... e mais {len(suggestions) - 3} sugestões no relatório completo.")
        else:
            print("Sugestões de melhoria: Nenhuma disponível")
        
        print()
        print("Relatório completo salvo em:")
        print(f"  {os.path.abspath(LAST_REPORT_FILE)}")
        print("=" * 60 + "\n")
    
    def show_last_report(self):
        """Mostra o último relatório de testes"""
        if not os.path.exists(LAST_REPORT_FILE):
            print("Nenhum relatório disponível ainda. Execute os testes primeiro.")
            return
        
        try:
            with open(LAST_REPORT_FILE, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            self._display_summary(results)
            
            # Perguntar se deseja ver detalhes
            response = input("Deseja ver mais detalhes? (s/n): ")
            if response.lower() == 's':
                # Determinar o relatório de texto correspondente
                timestamp = datetime.datetime.fromisoformat(results['timestamp']).strftime("%Y%m%d_%H%M%S")
                txt_report = os.path.join(REPORT_DIR, f"auto_test_report_{timestamp}.txt")
                
                if os.path.exists(txt_report):
                    with open(txt_report, 'r', encoding='utf-8') as f:
                        print("\n" + "=" * 60)
                        print(f.read())
                        print("=" * 60 + "\n")
                else:
                    print("\nRelatório detalhado não encontrado.")
        except Exception as e:
            print(f"Erro ao mostrar o relatório: {e}")
    
    def start_daemon(self):
        """Inicia o modo daemon para executar testes periodicamente"""
        logger.info(f"Iniciando modo daemon (intervalo: {TEST_INTERVAL}s)")
        self.running = True
        
        def signal_handler(sig, frame):
            logger.info("Sinal de interrupção recebido. Encerrando...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            while self.running:
                self.run_tests()
                
                logger.info(f"Aguardando {TEST_INTERVAL} segundos até a próxima execução...")
                
                # Aguardar, mas verificar periodicamente se ainda está rodando
                for _ in range(int(TEST_INTERVAL / 5)):
                    if not self.running:
                        break
                    time.sleep(5)
        except Exception as e:
            logger.error(f"Erro no modo daemon: {e}")
        finally:
            logger.info("Daemon encerrado")
    
    def start_watch_mode(self):
        """Inicia o modo observador que executa testes quando arquivos mudam"""
        logger.info("Iniciando modo watch")
        self.running = True
        
        # Encontrar todos os arquivos a serem observados
        watched_files = {}
        
        # Adicionar arquivos .py, .js, .html e .css
        for ext in ['.py', '.js', '.html', '.css']:
            for file_path in glob.glob(f'**/*{ext}', recursive=True):
                if 'tests/' not in file_path and 'venv/' not in file_path and '.git/' not in file_path:
                    watched_files[file_path] = os.path.getmtime(file_path)
        
        # Adicionar arquivos específicos
        for file_path in ['app.py', 'main.py', 'models.py', 'config.py']:
            if os.path.exists(file_path):
                watched_files[file_path] = os.path.getmtime(file_path)
        
        # Atualizar status
        self.current_status['watched_files'] = list(watched_files.keys())
        self._save_status()
        
        logger.info(f"Observando {len(watched_files)} arquivos")
        
        def signal_handler(sig, frame):
            logger.info("Sinal de interrupção recebido. Encerrando...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        last_run_time = 0
        
        try:
            while self.running:
                changes = []
                
                # Verificar alterações nos arquivos
                for file_path, last_mtime in list(watched_files.items()):
                    if os.path.exists(file_path):
                        current_mtime = os.path.getmtime(file_path)
                        if current_mtime > last_mtime:
                            changes.append(file_path)
                            watched_files[file_path] = current_mtime
                    else:
                        # Arquivo removido
                        changes.append(file_path + " (removido)")
                        del watched_files[file_path]
                
                # Verificar novos arquivos
                for ext in ['.py', '.js', '.html', '.css']:
                    for file_path in glob.glob(f'**/*{ext}', recursive=True):
                        if 'tests/' not in file_path and 'venv/' not in file_path and '.git/' not in file_path:
                            if file_path not in watched_files:
                                changes.append(file_path + " (novo)")
                                watched_files[file_path] = os.path.getmtime(file_path)
                
                # Executar testes se houver alterações e pelo menos 10s desde a última execução
                current_time = time.time()
                if changes and (current_time - last_run_time) > 10:
                    logger.info(f"Alterações detectadas em {len(changes)} arquivos")
                    for change in changes[:5]:
                        logger.info(f"  - {change}")
                    
                    if len(changes) > 5:
                        logger.info(f"  - ... e mais {len(changes) - 5} arquivos")
                    
                    # Executar testes
                    self.run_tests()
                    last_run_time = time.time()
                
                # Esperar antes da próxima verificação
                time.sleep(WATCH_INTERVAL)
        except Exception as e:
            logger.error(f"Erro no modo watch: {e}")
        finally:
            logger.info("Modo watch encerrado")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Sistema Automático de Teste Contínuo do Zelopack')
    parser.add_argument('--run', action='store_true', help='Executar os testes uma vez')
    parser.add_argument('--daemon', action='store_true', help='Iniciar em modo daemon (periódico)')
    parser.add_argument('--watch', action='store_true', help='Iniciar em modo watch (detectar mudanças)')
    parser.add_argument('--report', action='store_true', help='Mostrar o último relatório')
    args = parser.parse_args()
    
    runner = AutoTestRunner()
    
    if args.run:
        runner.run_tests()
    elif args.daemon:
        runner.start_daemon()
    elif args.watch:
        runner.start_watch_mode()
    elif args.report:
        runner.show_last_report()
    else:
        print("Sistema Automático de Teste Contínuo do Zelopack")
        print("Opções disponíveis:")
        print("  --run     Executar os testes uma vez")
        print("  --daemon  Iniciar em modo daemon (periódico)")
        print("  --watch   Iniciar em modo watch (detectar mudanças)")
        print("  --report  Mostrar o último relatório")
        print("\nExemplo: python auto_test_runner.py --run")

if __name__ == "__main__":
    main()