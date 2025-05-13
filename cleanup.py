import os
import shutil

# Lista de arquivos que podem ser removidos com segurança
files_to_remove = [
    # Arquivos de teste e verificação
    'auto_check.py',
    'background_checker.py',
    'check_admin.py',
    'check_alex.py',
    'check_zip.py',
    'run_background_checker.py',
    'run_tests.py',
    'simple_background_checker.py',
    'test_connection.py',
    'test_db.py',
    'test_full_system.py',
    'test_system.py',
    'test_zelopack.py',
    
    # Arquivos de aplicação redundantes ou obsoletos
    'app_minimal.py',
    'app_simple.py',
    'models_temp.py',
    'login_as_alex.py',
    'login_page.html',
    
    # Scripts de empacotamento e instalação
    'build_executable.bat',
    'build_executable.sh',
    'create_archive.py',
    'create_installer_images.py',
    'create_linux_package.sh',
    'create_macos_installer.sh',
    'create_windows_installer.bat',
    'installer_config.nsi',
    'package_all.py',
    'setup.py',
    'zelopack.spec',
    
    # Arquivos de log e temporários
    'zelopack_ai_agents.log',
    'zelopack_auto_check.log',
    'zelopack_background_checker.log',
    'zelopack_checker.log',
    'zelopack_system_20250427_062501.zip',
    'cookies.txt',
    'relatorio_testes.txt',
    '.checker_pid',
    
    # Arquivos de configuração para ambientes específicos
    '.replit',
    '.replit.workflow',
]

# Diretórios a serem removidos
directories_to_remove = [
    'tests',
    'extracted_forms',  # Parece ser um diretório de dados extraídos para testes
]

# Verificar e remover arquivos
removed_files = []
for file_name in files_to_remove:
    if os.path.exists(file_name):
        try:
            os.remove(file_name)
            removed_files.append(file_name)
            print(f"Removido: {file_name}")
        except Exception as e:
            print(f"Erro ao remover {file_name}: {e}")

# Verificar e remover diretórios
removed_dirs = []
for dir_name in directories_to_remove:
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        try:
            shutil.rmtree(dir_name)
            removed_dirs.append(dir_name)
            print(f"Removido diretório: {dir_name}")
        except Exception as e:
            print(f"Erro ao remover diretório {dir_name}: {e}")

print(f"\nTotal de {len(removed_files)} arquivos removidos.")
print(f"Total de {len(removed_dirs)} diretórios removidos.")
