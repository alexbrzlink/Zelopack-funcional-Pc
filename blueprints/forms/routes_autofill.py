import logging
from datetime import datetime, timedelta
from flask import render_template, jsonify, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from models import FormPreset, StandardFields
import json

from . import forms_bp

@forms_bp.route('/autofill')
@login_required
def autofill():
    """Página de preenchimento automático de formulários."""
    # Dados para a página
    hoje = datetime.now().strftime('%Y-%m-%d')
    validade_padrao = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    
    # Buscar templates salvos
    presets = FormPreset.query.filter_by(user_id=current_user.id).order_by(FormPreset.is_default.desc(), FormPreset.name).all()
    
    return render_template(
        'forms/autofill.html',
        hoje=hoje,
        validade_padrao=validade_padrao,
        usuario_atual=current_user,
        presets=presets
    )

@forms_bp.route('/api/autofill/templates', methods=['GET'])
@login_required
def get_templates():
    """API para listar templates de preenchimento salvos."""
    templates = FormPreset.query.filter_by(user_id=current_user.id).order_by(FormPreset.is_default.desc(), FormPreset.name).all()
    
    result = []
    for template in templates:
        result.append({
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'is_default': template.is_default,
            'created_at': template.created_at.strftime('%d/%m/%Y'),
            'fields': json.loads(template.fields_json) if template.fields_json else {}
        })
    
    return jsonify({'success': True, 'templates': result})

@forms_bp.route('/api/autofill/templates', methods=['POST'])
@login_required
def create_template():
    """API para criar um novo template de preenchimento."""
    data = request.get_json()
    
    if not data or 'name' not in data or 'fields' not in data:
        return jsonify({'success': False, 'message': 'Dados incompletos para criar template'}), 400
    
    # Se for o primeiro template, definir como padrão
    is_default = False
    if FormPreset.query.filter_by(user_id=current_user.id).count() == 0:
        is_default = True
    
    # Se este for marcado como padrão, desmarcar outros
    if data.get('is_default', False):
        is_default = True
        FormPreset.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
        db.session.commit()
    
    # Criar novo template
    new_template = FormPreset(
        name=data['name'],
        description=data.get('description', ''),
        fields_json=json.dumps(data['fields']),
        is_default=is_default,
        user_id=current_user.id
    )
    
    db.session.add(new_template)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Template criado com sucesso',
        'template': {
            'id': new_template.id,
            'name': new_template.name,
            'description': new_template.description,
            'is_default': new_template.is_default,
            'created_at': new_template.created_at.strftime('%d/%m/%Y')
        }
    })

@forms_bp.route('/api/autofill/templates/<int:template_id>', methods=['PUT'])
@login_required
def update_template(template_id):
    """API para atualizar um template existente."""
    template = FormPreset.query.filter_by(id=template_id, user_id=current_user.id).first()
    
    if not template:
        return jsonify({'success': False, 'message': 'Template não encontrado'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'Dados incompletos para atualizar template'}), 400
    
    # Atualizar campos
    if 'name' in data:
        template.name = data['name']
    
    if 'description' in data:
        template.description = data['description']
    
    if 'fields' in data:
        template.fields_json = json.dumps(data['fields'])
    
    # Se for definido como padrão, desmarcar outros
    if 'is_default' in data and data['is_default']:
        FormPreset.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
        template.is_default = True
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Template atualizado com sucesso'
    })

@forms_bp.route('/api/autofill/templates/<int:template_id>', methods=['DELETE'])
@login_required
def delete_template(template_id):
    """API para excluir um template."""
    template = FormPreset.query.filter_by(id=template_id, user_id=current_user.id).first()
    
    if not template:
        return jsonify({'success': False, 'message': 'Template não encontrado'}), 404
    
    # Se for o template padrão, definir outro como padrão (se existir)
    if template.is_default:
        next_template = FormPreset.query.filter(
            FormPreset.user_id == current_user.id,
            FormPreset.id != template_id
        ).first()
        
        if next_template:
            next_template.is_default = True
    
    db.session.delete(template)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Template excluído com sucesso'
    })

@forms_bp.route('/api/autofill/apply', methods=['POST'])
@login_required
def apply_autofill():
    """API para aplicar preenchimento automático a um formulário."""
    data = request.get_json()
    
    if not data or 'form_id' not in data or 'fields' not in data:
        return jsonify({'success': False, 'message': 'Dados incompletos para aplicar preenchimento'}), 400
    
    # Aqui seria implementada a lógica para aplicar os campos ao formulário específico
    # Simulação de sucesso para este exemplo
    
    return jsonify({
        'success': True, 
        'message': 'Campos aplicados com sucesso',
        'redirect_url': url_for('forms.edit_form', form_id=data['form_id'])
    })

@forms_bp.route('/api/autofill/suggest', methods=['GET'])
@login_required
def get_suggestions():
    """API para obter sugestões de preenchimento para campos."""
    # Sugestões padrão
    suggestions = {
        'empresa': 'Zelopack',
        'produto': 'Suco Natural',
        'marca': 'ZeloPack Premium',
        'lote': f'L-{datetime.now().strftime("%Y-%m-%d")}',
        'responsavel': current_user.name,
        'data_fabricacao': datetime.now().strftime('%Y-%m-%d'),
        'data_validade': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
        'brix': '11.2',
        'ph': '3.85',
        'acidez': '0.32',
        'densidade': '1.045',
        'temperatura': '20.0'
    }
    
    return jsonify({
        'success': True,
        'suggestions': suggestions
    })