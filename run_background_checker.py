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
        # Verificar se já está em execução
        if os.path.exists(".background_checker_pid"):
            try:
                with open(".background_checker_pid", "r") as f:
                    pid = int(f.read().strip())
                
                try:
                    # Verifica se o processo ainda existe
                    os.kill(pid, 0)
                    print(f"Verificador automático já está em execução (PID: {pid})")
                    return 0
                except ProcessLookupError:
                    # O processo não existe mais, podemos continuar
                    os.remove(".background_checker_pid")
                    print("Processo anterior não encontrado, iniciando novo processo...")
            except Exception as e:
                print(f"Erro ao verificar processo anterior: {str(e)}")
                # Continua mesmo com erro
        
        # Cria diretório para nohup.out se não existir
        if not os.path.exists("logs"):
            os.makedirs("logs")
            
        # Inicia o processo em segundo plano usando nohup para garantir que continue rodando
        # mesmo após o terminal ser fechado
        cmd = "nohup python background_checker.py > zelopack_background_checker.log 2>&1 &"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        
        # Obtém o PID do processo em execução
        try:
            # Use pgrep para encontrar o PID
            find_pid = subprocess.Popen(
                ["pgrep", "-f", "python background_checker.py"],
                stdout=subprocess.PIPE
            )
            pid_output = find_pid.communicate()[0].decode().strip()
            
            if pid_output:
                pid = int(pid_output.split("\n")[0])  # Em caso de múltiplos PIDs, pegue o primeiro
                print(f"Verificador automático iniciado em segundo plano (PID: {pid})")
                print("Log disponível em: zelopack_background_checker.log")
                
                # Salva o PID para referência futura
                with open(".background_checker_pid", "w") as f:
                    f.write(str(pid))
                
                return 0
            else:
                print("Não foi possível determinar o PID do verificador automático")
                return 1
        except Exception as e:
            print(f"Erro ao obter PID: {str(e)}")
            return 1
            
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