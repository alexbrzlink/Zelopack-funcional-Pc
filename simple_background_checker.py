#!/usr/bin/env python3
"""
Verificador automático simplificado que executa o auto_check.py a cada 5 minutos
"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("zelopack_simple_checker.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_auto_check():
    """Executa o verificador automático e registra o resultado"""
    try:
        logging.info("Executando verificação automática...")
        result = subprocess.run(
            ["python", "auto_check.py", "--fix"],
            capture_output=True,
            text=True
        )
        
        # Escrever saída detalhada no log
        logging.info(f"Verificação concluída com código {result.returncode}")
        if result.stdout:
            logging.debug(f"Saída: {result.stdout}")
        if result.stderr:
            logging.error(f"Erros: {result.stderr}")
        
        # Atualizar arquivo de status
        with open(".last_check_time", "w") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Erro ao executar verificação: {str(e)}")
        return False

def main():
    """Função principal - loop infinito de verificação"""
    logging.info("=== Iniciando serviço de verificação simplificado ===")
    
    interval_minutes = 5
    interval_seconds = interval_minutes * 60
    
    # Criar arquivo PID para controle
    with open(".simple_checker_pid", "w") as f:
        f.write(str(os.getpid()))
    
    try:
        # Executar verificação inicial
        logging.info(f"Executando verificação inicial...")
        run_auto_check()
        
        # Loop principal
        while True:
            now = datetime.now()
            logging.info(f"Próxima verificação em {interval_minutes} minutos ({now.strftime('%H:%M:%S')})")
            
            # Aguardar até o próximo ciclo
            time.sleep(interval_seconds)
            
            # Executar verificação
            run_auto_check()
            
    except KeyboardInterrupt:
        logging.info("Serviço interrompido pelo usuário")
    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}")
        return 1
    finally:
        # Limpar arquivo PID ao encerrar
        if os.path.exists(".simple_checker_pid"):
            os.remove(".simple_checker_pid")
            
    return 0

if __name__ == "__main__":
    sys.exit(main())