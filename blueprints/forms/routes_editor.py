"""
Módulo de Rotas para o Editor Universal do ZeloPack
"""

import os
import json
import uuid
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from flask import (
    Blueprint, render_template, redirect, url_for, request, 
    flash, jsonify, session, send_file, abort, current_app
)
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf

from models import db, FormPreset, StandardFields
from blueprints.forms.online_editor import OnlineEditorConverter, extract_fields_from_file

# Criar blueprint
editor_bp = Blueprint('editor', __name__, url_prefix='/editor')

# Configurações
FORMS_DIR = os.environ.get('FORMS_DIR', 'attached_assets')
EXTRACTED_FORMS_DIR = os.path.join(os.getcwd(), 'extracted_forms')

# Garantir que a pasta de formulários extraídos exista
os.makedirs(EXTRACTED_FORMS_DIR, exist_ok=True)


@editor_bp.route('/')
@login_required
def index():
    """Página inicial do editor universal."""
    # Obter todas as categorias (pastas)
    categories = []
    
    try:
        # Listar pastas no diretório de formulários
        for item in os.listdir(FORMS_DIR):
            full_path = os.path.join(FORMS_DIR, item)
            if os.path.isdir(full_path) and not item.startswith('.'):
                categories.append(item)
        
        # Ordenar categorias em ordem alfabética
        categories.sort()
    except Exception as e:
        flash(f'Erro ao listar categorias: {str(e)}', 'danger')
    
    return render_template(
        'forms/editor_index.html',
        title='Editor Universal de Formulários',
        categories=categories
    )


@editor_bp.route('/lista/<category>')
@login_required
def category(category):
    """Lista todos os formulários de uma categoria para edição online."""
    # Validar caminho da categoria
    category_path = os.path.join(FORMS_DIR, category)
    if not os.path.exists(category_path) or not os.path.isdir(category_path):
        flash('Categoria não encontrada.', 'danger')
        return redirect(url_for('editor.index'))
    
    # Obter lista de formulários
    forms = []
    
    try:
        for item in os.listdir(category_path):
            if item.startswith('.') or item.startswith('~$'):
                continue
                
            full_path = os.path.join(category_path, item)
            if os.path.isfile(full_path):
                file_path = os.path.join(category, item)
                file_ext = os.path.splitext(item)[1].lower()
                
                # Verificar se é um tipo de arquivo suportado
                if file_ext in ['.pdf', '.docx', '.xlsx', '.xls']:
                    # Obter ícone baseado na extensão
                    icon = ''
                    if file_ext == '.pdf':
                        icon = 'fa-file-pdf'
                    elif file_ext == '.docx':
                        icon = 'fa-file-word'
                    elif file_ext in ['.xlsx', '.xls']:
                        icon = 'fa-file-excel'
                    else:
                        icon = 'fa-file-alt'
                    
                    forms.append({
                        'name': item,
                        'path': file_path,
                        'icon': icon,
                        'ext': file_ext
                    })
        
        # Ordenar formulários em ordem alfabética
        forms.sort(key=lambda x: x['name'])
    except Exception as e:
        flash(f'Erro ao listar formulários: {str(e)}', 'danger')
    
    return render_template(
        'forms/editor_category.html',
        title=f'Formulários de {category}',
        category=category,
        forms=forms
    )


@editor_bp.route('/editar/<path:file_path>')
@login_required
def edit_form(file_path):
    """Interface do editor universal para formulários."""
    try:
        # Inicializar conversor
        converter = OnlineEditorConverter(file_path, FORMS_DIR)
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Obter campos padronizados disponíveis
        standard_fields = StandardFields.query.filter_by(
            is_active=True
        ).order_by(StandardFields.is_default.desc(), StandardFields.name).all()
        
        # Obter predefinições disponíveis para esse formulário
        presets = FormPreset.query.filter_by(
            form_type=file_name,
            is_active=True
        ).order_by(FormPreset.is_default.desc(), FormPreset.name).all()
        
        # Gerar CSRF token para o template
        csrf_token = generate_csrf()
        
        return render_template(
            'forms/editor_form.html',
            title=f'Editor Universal - {file_name}',
            file_path=file_path,
            file_name=file_name,
            file_ext=file_ext,
            standard_fields=standard_fields,
            presets=presets,
            csrf_token=csrf_token
        )
    except Exception as e:
        flash(f'Erro ao abrir editor: {str(e)}', 'danger')
        return redirect(url_for('editor.index'))


@editor_bp.route('/api/load/<path:file_path>')
@login_required
def api_load_content(file_path):
    """API para carregar o conteúdo do documento para edição."""
    try:
        converter = OnlineEditorConverter(file_path, FORMS_DIR)
        content = converter.get_editable_content()
        return jsonify(content)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar conteúdo: {str(e)}'
        })


@editor_bp.route('/api/save/<path:file_path>', methods=['POST'])
@login_required
def api_save_content(file_path):
    """API para salvar o conteúdo editado."""
    try:
        # Obter dados enviados
        edited_data = request.json
        if not edited_data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos.'
            })
        
        # Salvar o conteúdo
        converter = OnlineEditorConverter(file_path, FORMS_DIR)
        result = converter.save_edited_content(edited_data)
        
        if result.get('success'):
            # Guardar o caminho temporário na sessão para download posterior
            session['saved_temp_file'] = result['file_path']
            session['saved_file_name'] = result['file_name']
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar conteúdo: {str(e)}'
        })


@editor_bp.route('/api/download-edited')
@login_required
def api_download_edited():
    """API para baixar o arquivo editado."""
    try:
        # Obter caminho do arquivo temporário da sessão
        temp_file_path = session.get('saved_temp_file')
        file_name = session.get('saved_file_name')
        
        if not temp_file_path or not os.path.exists(temp_file_path):
            abort(404)
        
        # Enviar o arquivo para download
        return send_file(
            temp_file_path,
            as_attachment=True,
            download_name=file_name
        )
    except Exception as e:
        flash(f'Erro ao baixar arquivo: {str(e)}', 'danger')
        return redirect(url_for('editor.index'))


@editor_bp.route('/api/preset/<int:preset_id>')
@login_required
def api_get_preset(preset_id):
    """API para obter dados de uma predefinição."""
    preset = FormPreset.query.get_or_404(preset_id)
    
    return jsonify({
        'success': True,
        'preset': {
            'id': preset.id,
            'name': preset.name,
            'description': preset.description,
            'form_type': preset.form_type,
            'data': preset.data,
            'is_default': preset.is_default
        }
    })


@editor_bp.route('/api/standard-fields/<int:fields_id>')
@login_required
def api_get_standard_fields(fields_id):
    """API para obter dados de campos padronizados."""
    std_fields = StandardFields.query.get_or_404(fields_id)
    
    return jsonify({
        'success': True,
        'standard_fields': {
            'id': std_fields.id,
            'name': std_fields.name,
            'description': std_fields.description,
            'data': std_fields.data,
            'is_default': std_fields.is_default
        }
    })


@editor_bp.route('/api/create-preset/<path:file_path>', methods=['POST'])
@login_required
def api_create_preset(file_path):
    """API para criar uma predefinição para o formulário."""
    try:
        full_path = os.path.join(FORMS_DIR, file_path)
        
        # Verificar se o arquivo existe
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            return jsonify({
                'success': False,
                'message': 'Arquivo não encontrado.'
            }), 404
        
        file_name = os.path.basename(full_path)
        
        # Obter dados da requisição
        data = request.json
        
        if not data or not data.get('name') or not data.get('data'):
            return jsonify({
                'success': False,
                'message': 'Dados incompletos. Nome e campos são obrigatórios.'
            }), 400
        
        preset_name = data.get('name')
        preset_description = data.get('description', '')
        is_default = data.get('is_default', False)
        preset_data = data.get('data', {})
        
        # Verificar se já existe uma predefinição com esse nome
        existing = FormPreset.query.filter_by(
            form_type=file_name,
            name=preset_name,
            is_active=True
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'message': f'Já existe uma predefinição com o nome "{preset_name}" para este formulário.'
            }), 400
        
        # Verificar se estamos definindo como padrão
        if is_default:
            # Remover a definição de padrão de outras predefinições para este formulário
            FormPreset.query.filter_by(
                form_type=file_name,
                is_default=True,
                is_active=True
            ).update({
                'is_default': False
            })
        
        # Criar nova predefinição
        preset = FormPreset(
            name=preset_name,
            description=preset_description,
            form_type=file_name,
            data=preset_data,
            is_default=is_default,
            created_by=current_user.id
        )
        
        db.session.add(preset)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Predefinição criada com sucesso!',
            'preset': {
                'id': preset.id,
                'name': preset.name,
                'description': preset.description,
                'is_default': preset.is_default
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar predefinição: {str(e)}'
        }), 500