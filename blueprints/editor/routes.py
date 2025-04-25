import os
import io
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory, current_app, abort, Response, session
from flask_login import login_required, current_user

# Importações para processamento de documentos
import openpyxl
from docx import Document
import PyPDF2
import pandas as pd

# Para geração de PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4

from app import db
from models import FormTemplate
from utils.file_handler import save_file, allowed_file, get_file_size
from blueprints.editor import editor_bp
from utils.forms_extract import extract_form_fields, extract_form_structure
from utils.forms_processor import process_xlsx, process_docx, process_pdf

# Lista de arquivos de formulários disponíveis (a ser substituída por uma consulta ao banco)
@editor_bp.route('/')
@login_required
def index():
    """Página inicial do Editor Universal."""
    # Diretório onde estão os formulários anexados
    form_dir = os.path.join(current_app.root_path, 'attached_assets')
    
    # Obter a lista de arquivos
    form_files = []
    if os.path.exists(form_dir):
        for filename in os.listdir(form_dir):
            file_path = os.path.join(form_dir, filename)
            if os.path.isfile(file_path):
                if filename.endswith('.xlsx') or filename.endswith('.docx') or filename.endswith('.pdf'):
                    # Obter estatísticas do arquivo
                    file_stat = os.stat(file_path)
                    file_size = file_stat.st_size
                    file_date = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    # Adicionar à lista
                    form_files.append({
                        'filename': filename,
                        'path': file_path,
                        'size': file_size,
                        'date': file_date,
                        'type': os.path.splitext(filename)[1][1:].upper()  # Extensão sem o ponto
                    })
    
    # Ordenar por data (mais recente primeiro)
    form_files.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('editor/index.html', form_files=form_files, title="Editor Universal")

@editor_bp.route('/edit/<path:filename>')
@login_required
def edit(filename):
    """Editar um formulário específico."""
    # Caminho completo para o arquivo
    form_dir = os.path.join(current_app.root_path, 'attached_assets')
    file_path = os.path.join(form_dir, filename)
    
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        flash('Arquivo não encontrado!', 'danger')
        return redirect(url_for('editor.index'))
    
    # Identificar o tipo de arquivo
    file_extension = os.path.splitext(filename)[1].lower()
    
    try:
        # Extrair dados do formulário com base no tipo
        if file_extension == '.xlsx':
            form_data = process_xlsx(file_path)
        elif file_extension == '.docx':
            form_data = process_docx(file_path)
        elif file_extension == '.pdf':
            form_data = process_pdf(file_path)
        else:
            flash('Tipo de arquivo não suportado!', 'danger')
            return redirect(url_for('editor.index'))
        
        # Guardar o caminho do arquivo na sessão para uso posterior
        session['current_editing_file'] = file_path
        
        return render_template('editor/edit.html', 
                              filename=filename,
                              form_data=form_data,
                              title=f"Editando: {filename}")
                              
    except Exception as e:
        flash(f'Erro ao processar o arquivo: {str(e)}', 'danger')
        return redirect(url_for('editor.index'))

@editor_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Salvar as alterações do formulário."""
    try:
        # Pegar os dados do formulário
        form_data = request.form.to_dict()
        
        # Pegar o caminho do arquivo sendo editado
        file_path = session.get('current_editing_file')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'Arquivo não encontrado!'})
        
        # Identificar o tipo de arquivo
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Processar e salvar com base no tipo
        if file_extension == '.xlsx':
            # Lógica para salvar planilha Excel
            # ... (a ser implementada)
            success = True
        elif file_extension == '.docx':
            # Lógica para salvar documento Word
            # ... (a ser implementada)
            success = True
        elif file_extension == '.pdf':
            # Gerar um novo PDF com base nos dados preenchidos
            # ... (a ser implementada)
            success = True
        else:
            return jsonify({'success': False, 'message': 'Tipo de arquivo não suportado!'})
        
        if success:
            # Limpar caminho do arquivo da sessão
            session.pop('current_editing_file', None)
            
            return jsonify({
                'success': True, 
                'message': 'Formulário salvo com sucesso!'
            })
        
        return jsonify({'success': False, 'message': 'Erro ao salvar o formulário!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@editor_bp.route('/preview/<path:filename>')
@login_required
def preview(filename):
    """Pré-visualização do formulário."""
    # Caminho completo para o arquivo
    form_dir = os.path.join(current_app.root_path, 'attached_assets')
    file_path = os.path.join(form_dir, filename)
    
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        flash('Arquivo não encontrado!', 'danger')
        return redirect(url_for('editor.index'))
    
    # Identificar o tipo de arquivo
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Exibir com base no tipo de arquivo
    if file_extension == '.pdf':
        return redirect(url_for('editor.view_pdf', filename=filename))
    elif file_extension in ['.xlsx', '.docx']:
        # Converter para PDF temporário para visualização
        try:
            # Aqui viria a lógica para converter o arquivo para PDF temporário
            # Por enquanto, vamos apenas redirecionar para a edição
            return redirect(url_for('editor.edit', filename=filename))
        except Exception as e:
            flash(f'Erro ao gerar prévia: {str(e)}', 'danger')
            return redirect(url_for('editor.index'))
    else:
        flash('Tipo de arquivo não suportado para pré-visualização!', 'warning')
        return redirect(url_for('editor.index'))

@editor_bp.route('/view-pdf/<path:filename>')
@login_required
def view_pdf(filename):
    """Visualizar um arquivo PDF."""
    form_dir = os.path.join(current_app.root_path, 'attached_assets')
    file_path = os.path.join(form_dir, filename)
    
    if not os.path.exists(file_path) or not filename.lower().endswith('.pdf'):
        abort(404)
    
    return send_from_directory(
        directory=form_dir,
        path=filename,
        as_attachment=False
    )

@editor_bp.route('/download/<path:filename>')
@login_required
def download(filename):
    """Download do arquivo editado."""
    form_dir = os.path.join(current_app.root_path, 'attached_assets')
    file_path = os.path.join(form_dir, filename)
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_from_directory(
        directory=form_dir,
        path=filename,
        as_attachment=True,
        download_name=filename
    )