import os
import mimetypes
from flask import render_template, send_file, abort, Response, jsonify, request
from flask_login import login_required, current_user
from . import forms_bp
import os

# Diretório base dos formulários
FORMS_DIR = os.path.join(os.getcwd(), 'extracted_forms')

@forms_bp.route('/')
@login_required
def index():
    """Página principal para visualização de formulários."""
    # Obtém as categorias de formulários (pastas)
    categories = []
    for item in os.listdir(FORMS_DIR):
        if os.path.isdir(os.path.join(FORMS_DIR, item)):
            categories.append(item)
    
    return render_template(
        'forms/index.html',
        title="Formulários Zelopack",
        categories=categories
    )

@forms_bp.route('/category/<category>')
@login_required
def category(category):
    """Visualizar formulários de uma categoria específica."""
    category_path = os.path.join(FORMS_DIR, category)
    
    # Verificar se a categoria existe
    if not os.path.exists(category_path) or not os.path.isdir(category_path):
        abort(404)
    
    # Listar formulários na categoria
    forms = []
    for root, dirs, files in os.walk(category_path):
        relative_path = os.path.relpath(root, FORMS_DIR)
        
        for file in files:
            if file.startswith('~$') or file.startswith('.'):  # Ignorar arquivos temporários
                continue
                
            file_path = os.path.join(relative_path, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # Ícone baseado na extensão
            icon = 'fa-file'
            if file_ext in ['.pdf']:
                icon = 'fa-file-pdf'
            elif file_ext in ['.doc', '.docx']:
                icon = 'fa-file-word'
            elif file_ext in ['.xls', '.xlsx']:
                icon = 'fa-file-excel'
            elif file_ext in ['.ppt', '.pptx']:
                icon = 'fa-file-powerpoint'
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                icon = 'fa-file-image'
            
            forms.append({
                'name': file,
                'path': file_path,
                'icon': icon,
                'date': os.path.getmtime(os.path.join(FORMS_DIR, file_path))
            })
    
    # Ordenar formulários por nome
    forms.sort(key=lambda x: x['name'])
    
    return render_template(
        'forms/category.html',
        title=f"Formulários - {category}",
        category=category,
        forms=forms
    )

@forms_bp.route('/view/<path:file_path>')
@login_required
def view_form(file_path):
    """Visualizar um formulário específico."""
    full_path = os.path.join(FORMS_DIR, file_path)
    
    # Verificar se o arquivo existe
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        abort(404)
    
    # Obter o tipo MIME do arquivo
    mime_type, _ = mimetypes.guess_type(full_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    
    # Enviar o arquivo para visualização
    return send_file(
        full_path,
        mimetype=mime_type,
        as_attachment=False,
        download_name=os.path.basename(full_path)
    )

@forms_bp.route('/download/<path:file_path>')
@login_required
def download_form(file_path):
    """Baixar um formulário específico."""
    full_path = os.path.join(FORMS_DIR, file_path)
    
    # Verificar se o arquivo existe
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        abort(404)
    
    # Enviar o arquivo para download
    return send_file(
        full_path,
        as_attachment=True,
        download_name=os.path.basename(full_path)
    )

@forms_bp.route('/search')
@login_required
def search_forms():
    """Pesquisar formulários."""
    query = request.args.get('q', '').lower()
    if not query or len(query) < 3:
        return jsonify([])
    
    results = []
    
    # Buscar em todas as pastas
    for root, dirs, files in os.walk(FORMS_DIR):
        for file in files:
            if file.startswith('~$') or file.startswith('.'):  # Ignorar arquivos temporários
                continue
                
            if query in file.lower():
                relative_path = os.path.relpath(root, FORMS_DIR)
                file_path = os.path.join(relative_path, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Ícone baseado na extensão
                icon = 'fa-file'
                if file_ext in ['.pdf']:
                    icon = 'fa-file-pdf'
                elif file_ext in ['.doc', '.docx']:
                    icon = 'fa-file-word'
                elif file_ext in ['.xls', '.xlsx']:
                    icon = 'fa-file-excel'
                elif file_ext in ['.ppt', '.pptx']:
                    icon = 'fa-file-powerpoint'
                elif file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    icon = 'fa-file-image'
                
                results.append({
                    'name': file,
                    'path': file_path,
                    'category': os.path.basename(root),
                    'icon': icon
                })
    
    # Ordenar resultados por nome
    results.sort(key=lambda x: x['name'])
    
    return jsonify(results)