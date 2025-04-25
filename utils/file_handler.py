import os
from flask import current_app
import uuid
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """
    Verifica se o arquivo possui uma extensão permitida.
    
    Args:
        filename: Nome do arquivo a ser verificado
        
    Returns:
        Boolean indicando se o arquivo é permitido
    """
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file):
    """
    Salva o arquivo enviado com nome seguro.
    
    Args:
        file: Objeto de arquivo do Flask
        
    Returns:
        Tupla com (nome_arquivo_seguro, caminho_completo, nome_original)
    """
    original_filename = file.filename
    # Gerar nome seguro para evitar conflitos e vulnerabilidades
    unique_id = uuid.uuid4().hex
    extension = os.path.splitext(original_filename)[1]
    secure_name = f"{unique_id}{extension}"
    
    # Definir caminho completo
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_name)
    
    # Salvar arquivo
    file.save(file_path)
    
    return (secure_name, file_path, original_filename)

def get_file_size(file_path):
    """
    Obtém o tamanho do arquivo em bytes.
    
    Args:
        file_path: Caminho completo para o arquivo
        
    Returns:
        Tamanho do arquivo em bytes
    """
    return os.path.getsize(file_path)
