#!/usr/bin/env python3
"""
Script para criar um arquivo ZIP do sistema Zelopack.
"""

import os
import sys
import zipfile
import datetime

def create_zip_archive(output_filename=None):
    """
    Cria um arquivo ZIP contendo todos os arquivos do projeto Zelopack.
    """
    # Se o nome do arquivo não foi fornecido, gerar um nome com timestamp
    if not output_filename:
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"zelopack_system_{current_time}.zip"
    
    # Diretórios e arquivos a serem excluídos
    exclude_dirs = [
        '__pycache__',
        '.git',
        'instance',
        'node_modules',
        'venv',
        'env',
        '.pytest_cache'
    ]
    
    # Extensões de arquivo a serem excluídas
    exclude_extensions = [
        '.pyc',
        '.pyo',
        '.pyd',
        '.git',
        '.gitignore',
        '.DS_Store',
        '.coverage'
    ]
    
    # Arquivos específicos a serem excluídos
    exclude_files = [
        'zelopack.db',
        'zelopack_backup.db',
        '.env',
        'create_archive.py'  # Excluir este próprio script
    ]
    
    # Criar o arquivo ZIP
    try:
        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Percorrer todos os diretórios e arquivos
            for root, dirs, files in os.walk('.'):
                # Excluir diretórios da lista dirs para que não sejam percorridos
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                # Adicionar arquivos ao ZIP
                for file in files:
                    # Verificar se o arquivo deve ser excluído
                    _, file_extension = os.path.splitext(file)
                    if (file_extension in exclude_extensions or
                            file in exclude_files):
                        continue
                    
                    file_path = os.path.join(root, file)
                    # Remover './' do início do path para armazenar
                    archive_path = file_path[2:] if file_path.startswith('./') else file_path
                    
                    try:
                        # Adicionar o arquivo ao ZIP
                        zipf.write(file_path, archive_path)
                        print(f"Adicionado: {archive_path}")
                    except Exception as e:
                        print(f"Erro ao adicionar {file_path}: {str(e)}", file=sys.stderr)
        
        print(f"\nArquivo ZIP criado com sucesso: {output_filename}")
        return output_filename
    
    except Exception as e:
        print(f"Erro ao criar arquivo ZIP: {str(e)}", file=sys.stderr)
        return None

if __name__ == "__main__":
    # Se for fornecido um nome de arquivo como argumento, usá-lo
    output_filename = sys.argv[1] if len(sys.argv) > 1 else None
    create_zip_archive(output_filename)