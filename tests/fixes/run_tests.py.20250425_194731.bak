#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Zelopack - Sistema Integrado de Testes e Melhoria Contínua

Este script é um ponto de entrada para todas as funcionalidades
de teste, monitoramento e melhoria do código do sistema Zelopack.

MODO DE USO:
1. Teste básico: python run_tests.py --test
2. Teste com análise detalhada: python run_tests.py --analyze
3. Teste com sugestões de IA: python run_tests.py --ai
4. Monitoramento contínuo: python run_tests.py --watch
5. Aplicar melhorias automáticas: python run_tests.py --fix
"""

import os
import sys
import time
import argparse
import subprocess
import datetime
import webbrowser
import json
from pathlib import Path

# Verificar Python 3.6+
if sys.version_info < (3, 6):
    print("Este script requer Python 3.6 ou superior")
    sys.exit(1)

# Constantes
TEST_DIR = 'tests'
COMPONENT_TEST_SCRIPT = os.path.join(TEST_DIR, 'test_components.py')
MONITOR_SCRIPT = os.path.join(TEST_DIR, 'zelopack_monitor.py')
AI_SCRIPT = os.path.join(TEST_DIR, 'zelopack_ai_assistant.py')
AUTO_TEST_SCRIPT = os.path.join(TEST_DIR, 'auto_test_runner.py')
REPORT_DIR = os.path.join(TEST_DIR, 'reports')

# Cores ANSI para terminal
class TermColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    """Imprime um cabeçalho formatado"""
    print(f"\n{TermColors.HEADER}{TermColors.BOLD}{'=' * 60}{TermColors.END}")
    print(f"{TermColors.HEADER}{TermColors.BOLD}{text.center(60)}{TermColors.END}")
    print(f"{TermColors.HEADER}{TermColors.BOLD}{'=' * 60}{TermColors.END}\n")

def print_success(text):
    """Imprime uma mensagem de sucesso"""
    print(f"{TermColors.GREEN}{TermColors.BOLD}✓ {text}{TermColors.END}")

def print_error(text):
    """Imprime uma mensagem de erro"""
    print(f"{TermColors.RED}{TermColors.BOLD}✗ {text}{TermColors.END}")

def print_warning(text):
    """Imprime uma mensagem de aviso"""
    print(f"{TermColors.YELLOW}{TermColors.BOLD}⚠ {text}{TermColors.END}")

def print_info(text):
    """Imprime uma mensagem informativa"""
    print(f"{TermColors.BLUE}ℹ {text}{TermColors.END}")

def setup_environment():
    """Configura o ambiente de testes"""
    print_info("Configurando ambiente de testes...")
    
    # Criar diretórios necessários
    os.makedirs(TEST_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    # Verificar se os scripts necessários existem
    missing_scripts = []
    for script in [COMPONENT_TEST_SCRIPT, MONITOR_SCRIPT, AI_SCRIPT, AUTO_TEST_SCRIPT]:
        if not os.path.exists(script):
            missing_scripts.append(script)
    
    if missing_scripts:
        print_error(f"Arquivos de teste necessários não encontrados:")
        for script in missing_scripts:
            print(f"  - {script}")
        sys.exit(1)
    
    print_success("Ambiente de testes configurado com sucesso")

def run_component_tests():
    """Executa os testes de componentes"""
    print_header("TESTES DE COMPONENTES")
    print_info("Executando testes de componentes...")
    
    try:
        result = subprocess.run(
            [sys.executable, COMPONENT_TEST_SCRIPT],
            capture_output=True,
            text=True
        )
        
        success = result.returncode == 0
        
        if success:
            print_success("Todos os testes de componentes passaram!")
        else:
            print_error("Falha nos testes de componentes")
            print("\nSaída do teste:")
            print("-" * 60)
            print(result.stdout + result.stderr)
            print("-" * 60)
        
        return success
    except Exception as e:
        print_error(f"Erro ao executar testes de componentes: {e}")
        return False

def run_code_analysis():
    """Executa análise detalhada de código"""
    print_header("ANÁLISE DE CÓDIGO")
    print_info("Executando análise detalhada de código...")
    
    try:
        result = subprocess.run(
            [sys.executable, MONITOR_SCRIPT, '--run'],
            capture_output=True,
            text=True
        )
        
        success = result.returncode == 0
        
        print("\nResultados da análise:")
        print("-" * 60)
        print(result.stdout)
        print("-" * 60)
        
        # Tentar extrair o relatório gerado
        report_match = None
        for line in result.stdout.splitlines():
            if "Relatório completo gerado:" in line:
                report_match = line.split("Relatório completo gerado:")[1].strip()
                break
        
        if report_match and os.path.exists(report_match):
            print_info(f"Relatório detalhado disponível em: {report_match}")
            
            # Perguntar se deseja abrir
            response = input("Deseja abrir o relatório no navegador (se disponível)? (s/n): ")
            if response.lower() == 's':
                try:
                    # Verificar se há um .txt correspondente
                    txt_report = os.path.splitext(report_match)[0] + '.txt'
                    if os.path.exists(txt_report):
                        # Em sistemas Unix, tentar abrir com less/more, ou no navegador em Windows
                        if os.name == 'posix':
                            os.system(f"less {txt_report}")
                        else:
                            webbrowser.open(f"file://{os.path.abspath(txt_report)}")
                    else:
                        webbrowser.open(f"file://{os.path.abspath(report_match)}")
                except Exception as e:
                    print_warning(f"Não foi possível abrir o relatório: {e}")
        
        return success
    except Exception as e:
        print_error(f"Erro ao executar análise de código: {e}")
        return False

def run_ai_analysis():
    """Executa análise com IA para sugestões de melhoria"""
    print_header("ANÁLISE COM IA")
    print_info("Executando análise com IA para sugestões de melhoria...")
    
    # Verificar se a chave de API está configurada
    openai_key = os.environ.get('OPENAI_API_KEY')
    if not openai_key:
        print_warning("Chave de API OpenAI não encontrada. Algumas funcionalidades avançadas de IA não estarão disponíveis.")
        print_info("Configure a variável de ambiente OPENAI_API_KEY para ativar todas as funcionalidades.")
    
    try:
        cmd = [sys.executable, AI_SCRIPT, '--suggestions']
        
        # Adicionar a chave de API se disponível
        if openai_key:
            cmd.extend(['--api-key', openai_key])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        success = result.returncode == 0
        
        # Tentar extrair o relatório de sugestões
        suggestions_file = None
        txt_file = None
        
        for line in result.stdout.splitlines():
            if line.startswith('Sugestões salvas em'):
                # Verificar JSON e TXT
                parts = line.split('e')
                if len(parts) >= 2:
                    suggestions_file = parts[0].replace('Sugestões salvas em', '').strip()
                    txt_file = parts[1].strip()
        
        if txt_file and os.path.exists(txt_file):
            print_info(f"Relatório de sugestões disponível em: {txt_file}")
            
            # Mostrar as primeiras sugestões
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                print("\nPrincipais sugestões:")
                print("-" * 60)
                
                # Extrair e mostrar as 3 primeiras sugestões
                suggestions_section = content.split('=== SUGESTÕES DE MELHORIA ===')[1].split('===')[0]
                suggestions = suggestions_section.split('SUGESTÃO #')
                
                for i, suggestion in enumerate(suggestions[1:4], 1):
                    # Limitar a 5 linhas por sugestão
                    suggestion_lines = suggestion.strip().split('\n')[:5]
                    print(f"SUGESTÃO #{i}")
                    for line in suggestion_lines:
                        print(line)
                    print()
                
                print("-" * 60)
                
                # Perguntar se deseja ver todas as sugestões
                response = input("Deseja ver todas as sugestões? (s/n): ")
                if response.lower() == 's':
                    if os.name == 'posix':
                        os.system(f"less {txt_file}")
                    else:
                        webbrowser.open(f"file://{os.path.abspath(txt_file)}")
            except Exception as e:
                print_warning(f"Não foi possível ler sugestões: {e}")
        
        return success
    except Exception as e:
        print_error(f"Erro ao executar análise com IA: {e}")
        return False

def apply_auto_fixes():
    """Aplica correções automáticas de problemas no código"""
    print_header("CORREÇÕES AUTOMÁTICAS")
    print_warning("Esta operação modificará arquivos do projeto.")
    response = input("Deseja continuar? (s/n): ")
    
    if response.lower() != 's':
        print_info("Operação cancelada pelo usuário")
        return False
    
    print_info("Aplicando correções automáticas...")
    
    try:
        # Primeiro executar o monitor para identificar problemas
        subprocess.run(
            [sys.executable, MONITOR_SCRIPT, '--run'],
            capture_output=True,
            text=True
        )
        
        # Agora aplicar as correções
        result = subprocess.run(
            [sys.executable, AI_SCRIPT, '--apply'],
            capture_output=True,
            text=True
        )
        
        success = result.returncode == 0
        
        print("\nResultados das correções:")
        print("-" * 60)
        print(result.stdout)
        print("-" * 60)
        
        # Verificar quantas correções foram aplicadas
        fix_count = 0
        for line in result.stdout.splitlines():
            if "Aplicadas" in line and "melhorias com IA" in line:
                try:
                    fix_count = int(line.split("Aplicadas")[1].split("melhorias")[0].strip())
                except:
                    pass
        
        if fix_count > 0:
            print_success(f"Foram aplicadas {fix_count} correções automáticas")
        else:
            print_info("Nenhuma correção automática foi aplicada")
        
        return success
    except Exception as e:
        print_error(f"Erro ao aplicar correções automáticas: {e}")
        return False

def start_continuous_monitoring():
    """Inicia o monitoramento contínuo"""
    print_header("MONITORAMENTO CONTÍNUO")
    print_info("Iniciando monitoramento contínuo de alterações no código...")
    print_info("Pressione Ctrl+C para encerrar")
    
    try:
        # Iniciar o monitoramento em modo watch
        subprocess.run(
            [sys.executable, AUTO_TEST_SCRIPT, '--watch'],
            check=True
        )
        
        return True
    except KeyboardInterrupt:
        print_info("\nMonitoramento encerrado pelo usuário")
        return True
    except Exception as e:
        print_error(f"Erro no monitoramento contínuo: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Zelopack - Sistema Integrado de Testes e Melhoria Contínua',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--test', action='store_true', help='Executar testes básicos de componentes')
    group.add_argument('--analyze', action='store_true', help='Executar análise detalhada de código')
    group.add_argument('--ai', action='store_true', help='Executar análise com IA para sugestões de melhoria')
    group.add_argument('--watch', action='store_true', help='Iniciar monitoramento contínuo de alterações')
    group.add_argument('--fix', action='store_true', help='Aplicar correções automáticas de problemas no código')
    group.add_argument('--full', action='store_true', help='Executar todo o processo (testes, análise, IA)')
    
    args = parser.parse_args()
    
    print_header("ZELOPACK - SISTEMA DE TESTES E MELHORIA")
    
    # Configurar ambiente
    setup_environment()
    
    # Executar a ação selecionada
    if args.test:
        run_component_tests()
    elif args.analyze:
        run_code_analysis()
    elif args.ai:
        run_ai_analysis()
    elif args.watch:
        start_continuous_monitoring()
    elif args.fix:
        apply_auto_fixes()
    elif args.full:
        # Executar todo o processo
        component_success = run_component_tests()
        analysis_success = run_code_analysis()
        ai_success = run_ai_analysis()
        
        print_header("RESUMO DE EXECUÇÃO")
        
        if component_success:
            print_success("Testes de componentes: SUCESSO")
        else:
            print_error("Testes de componentes: FALHA")
        
        if analysis_success:
            print_success("Análise de código: SUCESSO")
        else:
            print_warning("Análise de código: CONCLUÍDA COM AVISOS")
        
        if ai_success:
            print_success("Análise com IA: SUCESSO")
        else:
            print_warning("Análise com IA: CONCLUÍDA COM AVISOS")
        
        # Perguntar se deseja aplicar correções
        print()
        response = input("Deseja aplicar correções automáticas? (s/n): ")
        if response.lower() == 's':
            apply_auto_fixes()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)