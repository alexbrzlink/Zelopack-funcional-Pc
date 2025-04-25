#!/usr/bin/env python3
"""
Script de verificação automática em segundo plano para o Zelopack.
Este script executa o auto_check.py a cada 5 minutos continuamente.
"""

import logging
import subprocess
import time
import sys
import os
from datetime import datetime

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='zelopack_background_checker.log'
)

def run_check(fix=True):
    """Executa o script de verificação automática"""
    try:
        command = ["python", "auto_check.py"]
        if fix:
            command.append("--fix")
        
        logging.info(f"Executando verificação automática: {' '.join(command)}")
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            logging.info("Verificação concluída com sucesso")
        else:
            logging.error(f"Verificação falhou com código {process.returncode}")
            logging.error(f"Erro: {process.stderr}")
            
        return process.returncode == 0
    except Exception as e:
        logging.error(f"Erro ao executar verificação: {str(e)}")
        return False

def run_ai_agents(fix=True):
    """Executa os agentes de IA para melhorias automáticas"""
    try:
        command = ["python", "tests/ai_agents.py", "--run"]
        if fix:
            command.append("--fix")
        
        logging.info(f"Executando agentes de IA: {' '.join(command)}")
        # Timeout de 60 segundos para evitar que o processo fique preso
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=60
        )
        
        if process.returncode == 0:
            logging.info("Agentes de IA executados com sucesso")
        else:
            logging.error(f"Execução dos agentes falhou com código {process.returncode}")
            logging.error(f"Erro: {process.stderr}")
            
        return process.returncode == 0
    except subprocess.TimeoutExpired:
        logging.warning("Timeout na execução dos agentes de IA")
        return False
    except Exception as e:
        logging.error(f"Erro ao executar agentes de IA: {str(e)}")
        return False

def main():
    """Função principal"""
    # Vamos usar tanto logging quanto print para garantir visibilidade
    print("=== Iniciando verificação automática em segundo plano ===")
    logging.info("=== Iniciando verificação automática em segundo plano ===")
    
    interval_minutes = 5
    interval_seconds = interval_minutes * 60
    
    try:
        # Executar uma verificação imediata ao iniciar
        print(f"Executando verificação inicial em {datetime.now().strftime('%H:%M:%S')}")
        run_check(fix=True)
        
        # Loop principal
        while True:
            now = datetime.now()
            msg = f"Iniciando verificação às {now.strftime('%H:%M:%S')}"
            print(msg)
            logging.info(msg)
            
            # Executa a verificação automática com correções
            success = run_check(fix=True)
            
            if success:
                print("Verificação executada com sucesso")
            else:
                print("Verificação falhou, mas continuando...")
            
            # A cada 15 minutos (3 ciclos), executa também os agentes de IA
            if now.minute % 15 < interval_minutes:
                msg = "Executando agentes de IA (verificação a cada 15 minutos)"
                print(msg)
                logging.info(msg)
                run_ai_agents(fix=True)
            
            msg = f"Próxima verificação em {interval_minutes} minutos"
            print(msg)
            logging.info(msg)
            
            # Escrever em arquivo para verificação de execução
            with open(".background_checker_last_run", "w") as f:
                f.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        msg = "Verificação automática interrompida pelo usuário"
        print(msg)
        logging.info(msg)
    except Exception as e:
        msg = f"Erro fatal: {str(e)}"
        print(msg)
        logging.error(msg)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())