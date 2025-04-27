import zipfile
import sys

zip_file = "zelopack_system_20250427_062501.zip"

try:
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        print(f"O arquivo {zip_file} contém {len(file_list)} arquivos.")
        print("Primeiros 20 arquivos:")
        for file in file_list[:20]:
            print(f"- {file}")
        
        # Verificar se os arquivos principais estão incluídos
        main_files = ['app.py', 'main.py', 'models.py', 'config.py']
        print("\nVerificando arquivos principais:")
        for file in main_files:
            if file in file_list:
                print(f"✓ {file} está incluído no ZIP")
            else:
                print(f"✗ {file} NÃO está incluído no ZIP")
        
        # Verificar diretórios principais
        main_dirs = ['templates/', 'static/', 'blueprints/']
        print("\nVerificando diretórios principais:")
        for dir_name in main_dirs:
            dir_files = [f for f in file_list if f.startswith(dir_name)]
            if dir_files:
                print(f"✓ Diretório '{dir_name}' está incluído com {len(dir_files)} arquivos")
            else:
                print(f"✗ Diretório '{dir_name}' NÃO está incluído ou está vazio")
except Exception as e:
    print(f"Erro ao verificar o arquivo ZIP: {str(e)}")