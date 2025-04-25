import logging
logger = logging.getLogger(__name__)

"""
Módulo de Rotas para o Editor Universal do ZeloPack

Este módulo implementa as rotas para o editor universal de formulários,
permitindo a edição online sem necessidade de download dos arquivos.
"""

import os
import json
import base64
from datetime import datetime
from io import BytesIO

# Importações do Flask
from flask import (
    Blueprint, render_template, request, jsonify, url_for, 
    current_app, session, send_file, redirect, flash
)
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf

# Importar funções de processamento de documentos
from .online_editor import (
    extract_data_from_excel,
    extract_data_from_docx,
    extract_data_from_pdf, 
    apply_excel_fields,
    apply_docx_fields,
    apply_pdf_fields
)

# Importações de modelos
from app import db
from models import FormPreset, StandardFields

# Criar blueprint para o editor universal
editor_bp = Blueprint('editor', __name__, url_prefix='/forms/editor')

@editor_bp.route('/')
@login_required
def index():
    """Página inicial do editor universal."""
    # Obter todas as categorias de formulários disponíveis
    categories = os.listdir(current_app.config['ATTACHED_ASSETS_FOLDER'])
    # Filtrar apenas diretórios e excluir arquivos
    categories = [c for c in categories if os.path.isdir(os.path.join(current_app.config['ATTACHED_ASSETS_FOLDER'], c))]
    
    # Ordenar alfabeticamente
    categories.sort()
    
    return render_template(
        'forms/editor_index.html',
        title='Editor Universal de Formulários',
        categories=categories
    )

@editor_bp.route('/categoria/<category>')
@login_required
def category(category):
    """Lista todos os formulários de uma categoria para edição online."""
    # Verificar se a categoria existe
    category_path = os.path.join(current_app.config['ATTACHED_ASSETS_FOLDER'], category)
    if not os.path.exists(category_path) or not os.path.isdir(category_path):
        flash(f'Categoria {category} não encontrada!', 'danger')
        return redirect(url_for('editor.index'))
    
    # Listar todos os arquivos na categoria
    files = []
    for filename in os.listdir(category_path):
        file_path = os.path.join(category_path, filename)
        if os.path.isfile(file_path):
            # Obter extensão do arquivo
            extension = os.path.splitext(filename)[1].lower()
            # Verificar se é um formato suportado
            if extension in ['.xlsx', '.xls', '.docx', '.pdf']:
                # Obter data de modificação
                modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                # Formatar para exibição
                modified_str = modified.strftime('%d/%m/%Y %H:%M')
                
                # Verificar se existem presets para este formulário
                file_rel_path = os.path.join(category, filename)
                preset_count = FormPreset.query.filter_by(form_path=file_rel_path).count()
                
                files.append({
                    'name': filename,
                    'extension': extension,
                    'path': os.path.join(category, filename),
                    'modified': modified_str,
                    'size': os.path.getsize(file_path),
                    'preset_count': preset_count
                })
    
    # Ordenar por nome de arquivo (ordem alfabética)
    files.sort(key=lambda x: x['name'])
    
    return render_template(
        'forms/editor_category.html',
        title=f'Formulários para Edição - {category}',
        category=category,
        files=files
    )

@editor_bp.route('/editar/<path:file_path>')
@login_required
def edit_form(file_path):
    """Interface do editor universal para formulários."""
    # Verificar se o arquivo existe
    full_path = os.path.join(current_app.config['ATTACHED_ASSETS_FOLDER'], file_path)
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        flash(f'Arquivo {file_path} não encontrado!', 'danger')
        return redirect(url_for('editor.index'))
    
    # Obter nome do arquivo e extensão
    file_name = os.path.basename(full_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # Buscar presets para este formulário
    presets = FormPreset.query.filter_by(form_path=file_path).all()
    
    # Buscar campos padronizados
    standard_fields = StandardFields.query.all()
    
    return render_template(
        'forms/editor_form.html',
        title=f'Editor Universal - {file_name}',
        file_path=file_path,
        file_name=file_name,
        file_ext=file_ext,
        presets=presets,
        standard_fields=standard_fields,
        csrf_token=generate_csrf()
    )

@editor_bp.route('/api/load-content/<path:file_path>')
@login_required
def api_load_content(file_path):
    """API para carregar o conteúdo do documento para edição."""
    # Verificar se o arquivo existe
    full_path = os.path.join(current_app.config['ATTACHED_ASSETS_FOLDER'], file_path)
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'success': False, 'message': 'Arquivo não encontrado'})
    
    # Obter extensão do arquivo
    file_ext = os.path.splitext(full_path)[1].lower()
    
    try:
        # Processar o arquivo de acordo com a extensão
        if file_ext in ['.xlsx', '.xls']:
            # Excel
            data = extract_data_from_excel(full_path)
            return jsonify({
                'success': True,
                'content_type': 'excel',
                'active_sheet': data['active_sheet'],
                'sheets': data['sheets'],
                'fields': data['fields']
            })
        elif file_ext == '.docx':
            # Word
            data = extract_data_from_docx(full_path)
            return jsonify({
                'success': True,
                'content_type': 'docx',
                'paragraphs': data['paragraphs'],
                'tables': data['tables'],
                'fields': data['fields']
            })
        elif file_ext == '.pdf':
            # PDF
            data = extract_data_from_pdf(full_path)
            
            # Converter o PDF para base64 para visualização
            with open(full_path, 'rb') as pdf_file:
                pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
            
            return jsonify({
                'success': True,
                'content_type': 'pdf',
                'pdf_base64': pdf_base64,
                'fields': data['fields']
            })
        else:
            # Formato não suportado
            return jsonify({'success': False, 'message': 'Formato de arquivo não suportado'})
    
    except Exception as e:
        # Em caso de erro, enviar mensagem de falha
        return jsonify({'success': False, 'message': f'Erro ao processar arquivo: {str(e)}'})

@editor_bp.route('/api/save-content/<path:file_path>', methods=['POST'])
@login_required
def api_save_content(file_path):
    """API para salvar o conteúdo editado."""
    # Verificar se o arquivo existe
    full_path = os.path.join(current_app.config['ATTACHED_ASSETS_FOLDER'], file_path)
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'success': False, 'message': 'Arquivo não encontrado'})
    
    # Obter dados do formulário
    data = request.get_json()
    
    if not data or 'fields' not in data:
        return jsonify({'success': False, 'message': 'Dados inválidos'})
    
    # Obter extensão do arquivo
    file_ext = os.path.splitext(full_path)[1].lower()
    
    try:
        # Criar uma cópia temporária do arquivo com os campos preenchidos
        file_name = os.path.basename(full_path)
        output_filename = f"edited_{file_name}"
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
        
        # Aplicar os campos preenchidos ao arquivo de acordo com o tipo
        if file_ext in ['.xlsx', '.xls']:
            # Excel
            apply_excel_fields(full_path, output_path, data['fields'])
        elif file_ext == '.docx':
            # Word
            apply_docx_fields(full_path, output_path, data['fields'])
        elif file_ext == '.pdf':
            # PDF
            apply_pdf_fields(full_path, output_path, data['fields'])
        else:
            return jsonify({'success': False, 'message': 'Formato de arquivo não suportado'})
        
        # Salvar o caminho do arquivo na sessão para download posterior
        session['edited_file'] = output_path
        
        return jsonify({'success': True, 'message': 'Documento salvo com sucesso'})
    
    except Exception as e:
        # Em caso de erro, enviar mensagem de falha
        return jsonify({'success': False, 'message': f'Erro ao salvar arquivo: {str(e)}'})

@editor_bp.route('/api/download-edited')
@login_required
def api_download_edited():
    """API para baixar o arquivo editado."""
    # Verificar se existe um arquivo editado na sessão
    if 'edited_file' not in session:
        flash('Nenhum arquivo editado encontrado!', 'danger')
        return redirect(url_for('editor.index'))
    
    # Obter caminho do arquivo
    file_path = session['edited_file']
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        flash('Arquivo não encontrado!', 'danger')
        return redirect(url_for('editor.index'))
    
    # Obter nome do arquivo
    file_name = os.path.basename(file_path)
    
    # Enviar arquivo para download
    return send_file(
        file_path,
        as_attachment=True,
        download_name=file_name
    )

@editor_bp.route('/api/get-preset/<int:preset_id>')
@login_required
def api_get_preset(preset_id):
    """API para obter dados de uma predefinição."""
    preset = FormPreset.query.get(preset_id)
    if not preset:
        return jsonify({'success': False, 'message': 'Predefinição não encontrada'})
    
    # Converter dados JSON para dicionário
    try:
        data = json.loads(preset.data)
    except Exception:
        data = {}
    
    return jsonify({
        'success': True,
        'preset': {
            'id': preset.id,
            'name': preset.name,
            'description': preset.description,
            'is_default': preset.is_default,
            'data': data
        }
    })

@editor_bp.route('/api/get-standard-fields/<int:fields_id>')
@login_required
def api_get_standard_fields(fields_id):
    """API para obter dados de campos padronizados."""
    standard_fields = StandardFields.query.get(fields_id)
    if not standard_fields:
        return jsonify({'success': False, 'message': 'Campos padronizados não encontrados'})
    
    # Converter dados JSON para dicionário
    try:
        data = json.loads(standard_fields.data)
    except Exception:
        data = {}
    
    return jsonify({
        'success': True,
        'standard_fields': {
            'id': standard_fields.id,
            'name': standard_fields.name,
            'is_default': standard_fields.is_default,
            'data': data
        }
    })

@editor_bp.route('/api/create-preset/<path:file_path>', methods=['POST'])
@login_required
def api_create_preset(file_path):
    """API para criar uma predefinição para o formulário."""
    # Obter dados do formulário
    data = request.get_json()
    
    if not data or 'name' not in data or 'data' not in data:
        return jsonify({'success': False, 'message': 'Dados inválidos'})
    
    # Verificar se o arquivo existe
    full_path = os.path.join(current_app.config['ATTACHED_ASSETS_FOLDER'], file_path)
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'success': False, 'message': 'Arquivo não encontrado'})
    
    try:
        # Se esta predefinição for marcada como padrão, desmarcar outras como padrão
        if data.get('is_default', False):
            # Buscar todas as predefinições deste formulário marcadas como padrão
            default_presets = FormPreset.query.filter_by(
                form_path=file_path,
                is_default=True
            ).all()
            
            # Desmarcar como padrão
            for preset in default_presets:
                preset.is_default = False
            
            # Commit das alterações
            db.session.commit()
        
        # Criar nova predefinição
        preset = FormPreset(
            name=data['name'],
            description=data.get('description', ''),
            form_path=file_path,
            is_default=data.get('is_default', False),
            data=json.dumps(data['data']),
            created_by=current_user.id
        )
        
        # Salvar no banco de dados
        db.session.add(preset)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Predefinição criada com sucesso',
            'preset_id': preset.id
        })
    
    except Exception as e:
        # Em caso de erro, reverter as alterações no banco de dados
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar predefinição: {str(e)}'})