#!/usr/bin/env python3
"""
ZELOPACK - Script de Empacotamento Completo

Este script centraliza todo o processo de criação de pacotes instaláveis
para Windows, macOS e Linux em um único lugar.
"""

import os
import sys
import platform
import subprocess
import argparse
import shutil
from pathlib import Path

class ZelopackPackager:
    def __init__(self):
        """Inicializa o empacotador"""
        self.platform = platform.system().lower()
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.dist_dir = os.path.join(self.root_dir, 'dist')
        self.installers_dir = os.path.join(self.root_dir, 'installers')
        
        # Garantir que os diretórios necessários existam
        os.makedirs(self.installers_dir, exist_ok=True)
    
    def run_command(self, command, shell=False, cwd=None):
        """Executa um comando e exibe a saída"""
        print(f"Executando: {command}")
        try:
            if isinstance(command, str) and not shell:
                command = command.split()
            
            process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=cwd or self.root_dir
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            return process.poll() == 0
        except Exception as e:
            print(f"Erro ao executar comando: {e}")
            return False
    
    def generate_assets(self):
        """Gera os assets necessários para o instalador"""
        print("\n=== Gerando ícones e imagens ===")
        return self.run_command([sys.executable, 'generate_icon.py'])
    
    def build_executable(self):
        """Cria o executável usando PyInstaller"""
        print("\n=== Compilando executável ===")
        
        # Limpar pasta dist anterior, se existir
        if os.path.exists(self.dist_dir):
            print("Limpando pasta dist anterior...")
            shutil.rmtree(self.dist_dir)
        
        # Compilar com base na plataforma
        if self.platform == 'windows':
            return self.run_command('build_executable.bat', shell=True)
        else:  # macOS ou Linux
            os.chmod('build_executable.sh', 0o755)  # Tornar executável
            return self.run_command('./build_executable.sh', shell=True)
    
    def create_installer(self):
        """Cria o instalador adequado para a plataforma"""
        print("\n=== Criando instalador ===")
        
        if self.platform == 'windows':
            # Verificar se o NSIS está instalado
            nsis_found = False
            try:
                nsis_found = self.run_command('makensis -version', shell=True)
            except:
                pass
                
            if nsis_found:
                return self.run_command('create_windows_installer.bat', shell=True)
            else:
                print("AVISO: NSIS não encontrado. O instalador Windows não será criado.")
                print("Para criar o instalador, instale o NSIS de https://nsis.sourceforge.io/")
                return False
                
        elif self.platform == 'darwin':  # macOS
            os.chmod('create_macos_installer.sh', 0o755)
            return self.run_command('./create_macos_installer.sh', shell=True)
            
        elif self.platform == 'linux':
            os.chmod('create_linux_package.sh', 0o755)
            return self.run_command('./create_linux_package.sh', shell=True)
        
        return False
    
    def run_application(self):
        """Executa o aplicativo compilado para teste"""
        print("\n=== Executando aplicativo para teste ===")
        
        if self.platform == 'windows':
            exe_path = os.path.join(self.dist_dir, 'ZELOPACK', 'ZELOPACK.exe')
            if os.path.exists(exe_path):
                return self.run_command(f'"{exe_path}"', shell=True)
        
        elif self.platform == 'darwin':  # macOS
            app_path = os.path.join(self.dist_dir, 'ZELOPACK.app')
            if os.path.exists(app_path):
                return self.run_command(['open', app_path])
        
        elif self.platform == 'linux':
            exe_path = os.path.join(self.dist_dir, 'ZELOPACK', 'ZELOPACK')
            if os.path.exists(exe_path):
                os.chmod(exe_path, 0o755)
                return self.run_command(exe_path)
        
        print("Executável não encontrado para teste.")
        return False
    
    def package_all(self, run_test=False):
        """Executa todas as etapas de empacotamento"""
        print("\n=================================================")
        print(f"ZELOPACK - CRIAÇÃO DE PACOTE PARA {self.platform.upper()}")
        print("=================================================\n")
        
        # Etapa 1: Gerar assets
        if not self.generate_assets():
            print("ERRO: Falha ao gerar assets.")
            return False
        
        # Etapa 2: Compilar executável
        if not self.build_executable():
            print("ERRO: Falha ao compilar executável.")
            return False
        
        # Etapa 3: Criar instalador
        if not self.create_installer():
            print("AVISO: Falha ao criar instalador.")
            # Continuar mesmo que o instalador falhe
        
        # Etapa 4: Testar o aplicativo (opcional)
        if run_test:
            if not self.run_application():
                print("AVISO: Falha ao executar o aplicativo para teste.")
        
        print("\n=================================================")
        print(f"ZELOPACK - EMPACOTAMENTO CONCLUÍDO")
        print("=================================================\n")
        
        # Mostrar arquivos gerados
        print("Arquivos gerados:")
        
        if os.path.exists(self.dist_dir):
            print(f"\nExecutável: {self.dist_dir}")
            for item in os.listdir(self.dist_dir):
                print(f"  - {item}")
        
        if os.path.exists(self.installers_dir):
            print(f"\nInstaladores: {self.installers_dir}")
            for item in os.listdir(self.installers_dir):
                print(f"  - {item}")
        
        return True

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="ZELOPACK - Empacotador")
    parser.add_argument('--test', action='store_true', help='Testar o aplicativo após compilação')
    parser.add_argument('--assets-only', action='store_true', help='Gerar apenas os assets')
    parser.add_argument('--build-only', action='store_true', help='Apenas compilar sem criar instalador')
    parser.add_argument('--installer-only', action='store_true', help='Apenas criar instalador (assume que o executável já existe)')
    
    args = parser.parse_args()
    
    packager = ZelopackPackager()
    
    if args.assets_only:
        packager.generate_assets()
    elif args.build_only:
        packager.generate_assets()
        packager.build_executable()
    elif args.installer_only:
        packager.create_installer()
    else:
        packager.package_all(run_test=args.test)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())