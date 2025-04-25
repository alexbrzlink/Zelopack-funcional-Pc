#!/usr/bin/env python3
"""
Script para iniciar o verificador em segundo plano como um processo separado
"""

import subprocess
import os
import sys

def start_background_checker():
    """Inicia o verificador em segundo plano"""
    try:
        # Inicia o processo em segundo plano
        process = subprocess.Popen(
            ["python", "background_checker.py"],
            stdout=open("zelopack_background_checker.log", "a"),
            stderr=open("zelopack_background_checker.log", "a"),
            # Desvincula o processo do terminal
            start_new_session=True
        )
        
        print(f"Verificador automático iniciado em segundo plano (PID: {process.pid})")
        print("Log disponível em: zelopack_background_checker.log")
        
        # Salva o PID para referência futura
        with open(".background_checker_pid", "w") as f:
            f.write(str(process.pid))
        
        return 0
    except Exception as e:
        print(f"Erro ao iniciar verificador automático: {str(e)}")
        return 1

def stop_background_checker():
    """Para o verificador em segundo plano"""
    try:
        if os.path.exists(".background_checker_pid"):
            with open(".background_checker_pid", "r") as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, 15)  # SIGTERM
                print(f"Verificador automático (PID: {pid}) interrompido com sucesso")
                os.remove(".background_checker_pid")
            except ProcessLookupError:
                print(f"Processo {pid} não encontrado. Talvez já tenha sido encerrado.")
                os.remove(".background_checker_pid")
            except Exception as e:
                print(f"Erro ao interromper processo {pid}: {str(e)}")
        else:
            print("Nenhum verificador automático em execução")
        
        return 0
    except Exception as e:
        print(f"Erro ao parar verificador automático: {str(e)}")
        return 1

def status_background_checker():
    """Verifica o status do verificador em segundo plano"""
    if os.path.exists(".background_checker_pid"):
        try:
            with open(".background_checker_pid", "r") as f:
                pid = int(f.read().strip())
            
            try:
                # Envia sinal 0 para verificar se o processo existe
                os.kill(pid, 0)
                print(f"Verificador automático está em execução (PID: {pid})")
                return 0
            except ProcessLookupError:
                print("Verificador automático não está em execução (processo não encontrado)")
                os.remove(".background_checker_pid")
                return 1
        except Exception as e:
            print(f"Erro ao verificar status: {str(e)}")
            return 1
    else:
        print("Verificador automático não está em execução")
        return 1

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python run_background_checker.py [start|stop|status]")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "start":
        return start_background_checker()
    elif command == "stop":
        return stop_background_checker()
    elif command == "status":
        return status_background_checker()
    else:
        print(f"Comando desconhecido: {command}")
        print("Comandos disponíveis: start, stop, status")
        return 1

if __name__ == "__main__":
    sys.exit(main())