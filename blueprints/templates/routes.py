import os
import json
import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from sqlalchemy import desc
from werkzeug.utils import secure_filename
import io
import pandas as pd
import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer

from . import templates_bp
from app import db
from blueprints.templates.forms import ImportTemplateForm, CreateTemplateForm, FillReportForm
from models import ReportTemplate, Report, User, Client, Sample, ReportAttachment


@templates_bp.route('/')
@login_required
def index():
    """Página principal do módulo de templates de laudos."""
    templates = ReportTemplate.query.order_by(ReportTemplate.name).all()
    
    return render_template(
        'templates/index.html',
        title='Templates de Laudos',
        templates=templates
    )


@templates_bp.route('/importar-template', methods=['GET', 'POST'])
@login_required
def import_template():
    """Importar um template de formulário da Zelopack."""
    form = ImportTemplateForm()
    
    if form.validate_on_submit():
        try:
            # Obter o arquivo enviado e gerar nome seguro
            template_file = form.template_file.data
            original_filename = secure_filename(template_file.filename)
            file_ext = os.path.splitext(original_filename)[1]
            
            # Gerar nome único para o arquivo
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            
            # Caminho para salvar o arquivo
            templates_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'templates')
            os.makedirs(templates_folder, exist_ok=True)
            file_path = os.path.join(templates_folder, unique_filename)
            
            # Salvar o arquivo
            template_file.save(file_path)
            
            # Detectar o tipo de formulário automaticamente se não foi especificado
            form_type = form.template_type.data
            
            # Criar o template no banco de dados
            new_template = ReportTemplate(
                name=form.name.data,
                description=form.description.data,
                file_path=file_path,
                original_filename=original_filename,
                template_type=form_type,
                version=form.version.data,
                is_active=form.is_active.data,
                creator_id=current_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(new_template)
            db.session.commit()
            
            flash(f'Template "{form.name.data}" importado com sucesso!', 'success')
            return redirect(url_for('templates.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao importar o template: {str(e)}', 'danger')
    
    return render_template(
        'templates/import_zelopack_form.html',
        title='Importar Template',
        form=form
    )


@templates_bp.route('/criar-template', methods=['GET', 'POST'])
@login_required
def create_template():
    """Criar um novo template manualmente."""
    form = CreateTemplateForm()
    
    if form.validate_on_submit():
        try:
            # Criar estrutura do template
            structure = json.loads(form.structure.data)
            
            # Criar o template no banco de dados
            new_template = ReportTemplate(
                name=form.name.data,
                description=form.description.data,
                structure=form.structure.data,  # JSON como string
                template_type='custom',
                version=form.version.data,
                is_active=form.is_active.data,
                creator_id=current_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(new_template)
            db.session.commit()
            
            flash(f'Template "{form.name.data}" criado com sucesso!', 'success')
            return redirect(url_for('templates.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar o template: {str(e)}', 'danger')
    
    return render_template(
        'templates/create_template.html',
        title='Criar Template',
        form=form
    )


@templates_bp.route('/editar-template/<int:template_id>', methods=['GET', 'POST'])
@login_required
def edit_template(template_id):
    """Editar um template existente."""
    template = ReportTemplate.query.get_or_404(template_id)
    form = CreateTemplateForm(obj=template)
    
    if request.method == 'GET':
        # Se o template foi importado e não tem estrutura definida, criar estrutura vazia
        if not template.structure:
            form.structure.data = json.dumps({'fields': {}})
    
    if form.validate_on_submit():
        try:
            template.name = form.name.data
            template.description = form.description.data
            template.structure = form.structure.data
            template.is_active = form.is_active.data
            template.version = form.version.data
            template.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Template "{template.name}" atualizado com sucesso!', 'success')
            return redirect(url_for('templates.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o template: {str(e)}', 'danger')
    
    return render_template(
        'templates/edit_template.html',
        title=f'Editar Template - {template.name}',
        form=form,
        template=template
    )


@templates_bp.route('/preencher-laudo/<int:template_id>', methods=['GET', 'POST'])
@login_required
def fill_report(template_id):
    """Preencher um laudo com base em um template."""
    template = ReportTemplate.query.get_or_404(template_id)
    form = FillReportForm()
    
    # Carregar opções para os selects
    clients = Client.query.order_by(Client.name).all()
    form.client_id.choices = [(0, 'Selecione um cliente')] + [(c.id, c.name) for c in clients]
    
    samples = Sample.query.order_by(desc(Sample.created_at)).all()
    form.sample_id.choices = [(0, 'Selecione uma amostra')] + [(s.id, f"{s.code} - {s.description[:30] + '...' if s.description and len(s.description) > 30 else s.description or ''} ({s.created_at.strftime('%d/%m/%Y')})") for s in samples]
    
    users = User.query.filter_by(is_active=True).order_by(User.name).all()
    form.assigned_to.choices = [(0, 'Selecione um responsável')] + [(u.id, u.name) for u in users]
    
    # Valores padrão
    if request.method == 'GET':
        form.report_date.data = datetime.today()
        form.title.data = f"Laudo - {template.name}"
    
    # Carregar a estrutura do template
    template_structure = {}
    if template.structure:
        try:
            template_structure = json.loads(template.structure)
        except:
            template_structure = {'fields': {}}
    
    if form.validate_on_submit():
        try:
            # Extrair dados adicionais específicos do template
            additional_metrics = {}
            if form.additional_metrics.data:
                additional_metrics = json.loads(form.additional_metrics.data)
            
            # Criar o relatório
            new_report = Report(
                title=form.title.data,
                description=form.description.data,
                report_date=form.report_date.data,
                template_id=template.id,
                client_id=form.client_id.data if form.client_id.data != 0 else None,
                sample_id=form.sample_id.data if form.sample_id.data != 0 else None,
                creator_id=current_user.id,
                assigned_to=form.assigned_to.data if form.assigned_to.data != 0 else None,
                status='pendente',
                priority=form.priority.data,
                due_date=form.due_date.data,
                creation_date=datetime.utcnow(),
                ph_value=form.ph_value.data,
                brix_value=form.brix_value.data,
                acidity_value=form.acidity_value.data,
                color_value=form.color_value.data,
                density_value=request.form.get('density_value', type=float),
                additional_metrics=json.dumps(additional_metrics)
            )
            
            db.session.add(new_report)
            db.session.flush()  # Para obter o ID do relatório
            
            # Processar anexos
            if form.attachments.data:
                for attachment in form.attachments.data:
                    if attachment and attachment.filename:
                        filename = secure_filename(attachment.filename)
                        
                        # Criar pasta de anexos se não existir
                        attachments_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'report_attachments')
                        os.makedirs(attachments_folder, exist_ok=True)
                        
                        # Gerar nome único para o arquivo
                        file_ext = os.path.splitext(filename)[1]
                        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
                        file_path = os.path.join(attachments_folder, unique_filename)
                        
                        # Salvar arquivo
                        attachment.save(file_path)
                        
                        # Criar registro de anexo
                        new_attachment = ReportAttachment(
                            report_id=new_report.id,
                            file_path=file_path,
                            original_filename=filename,
                            file_type=file_ext.replace('.', ''),
                            file_size=os.path.getsize(file_path),
                            upload_date=datetime.utcnow(),
                            uploader_id=current_user.id
                        )
                        
                        db.session.add(new_attachment)
            
            db.session.commit()
            
            flash(f'Laudo "{form.title.data}" criado com sucesso!', 'success')
            return redirect(url_for('templates.view_report', report_id=new_report.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar o laudo: {str(e)}', 'danger')
    
    return render_template(
        'templates/fill_report.html',
        title=f'Preencher Laudo - {template.name}',
        form=form,
        template=template,
        template_structure=template_structure
    )


@templates_bp.route('/visualizar-laudo/<int:report_id>')
@login_required
def view_report(report_id):
    """Visualizar um laudo específico."""
    report = Report.query.get_or_404(report_id)
    template = ReportTemplate.query.get(report.template_id) if report.template_id else None
    
    # Obter anexos
    attachments = ReportAttachment.query.filter_by(report_id=report.id).all()
    
    # Obter métricas adicionais
    additional_metrics = {}
    if report.additional_metrics:
        try:
            additional_metrics = json.loads(report.additional_metrics)
        except:
            pass
    
    return render_template(
        'templates/view_report.html',
        title=f'Laudo - {report.title}',
        report=report,
        template=template,
        attachments=attachments,
        additional_metrics=additional_metrics
    )


@templates_bp.route('/download-pdf/<int:report_id>')
@login_required
def download_pdf(report_id):
    """Gerar e baixar o PDF de um laudo."""
    report = Report.query.get_or_404(report_id)
    template = ReportTemplate.query.get(report.template_id) if report.template_id else None
    
    # Criar um buffer para o PDF
    buffer = io.BytesIO()
    
    # Criar o documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter, title=report.title)
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=20
    )
    elements.append(Paragraph(f"<b>{report.title}</b>", title_style))
    elements.append(Spacer(1, 10))
    
    # Informações básicas
    data = [
        ["ID:", str(report.id)],
        ["Data:", report.report_date.strftime('%d/%m/%Y') if report.report_date else 'N/A'],
        ["Status:", report.get_status_label()],
        ["Template:", template.name if template else 'N/A'],
        ["Cliente:", report.client.name if report.client else 'N/A'],
        ["Amostra:", report.sample.code if report.sample else 'N/A'],
        ["Criado por:", report.creator_user.name if report.creator_user else 'N/A'],
        ["Criado em:", report.creation_date.strftime('%d/%m/%Y %H:%M') if report.creation_date else 'N/A']
    ]
    
    t = Table(data, colWidths=[100, 300])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Descrição
    if report.description:
        elements.append(Paragraph("<b>Descrição:</b>", styles['Heading3']))
        elements.append(Paragraph(report.description, styles['Normal']))
        elements.append(Spacer(1, 20))
    
    # Resultados da análise
    elements.append(Paragraph("<b>Resultados da Análise:</b>", styles['Heading3']))
    
    analysis_data = [["Parâmetro", "Valor", "Unidade", "Referência"]]
    
    if report.ph_value is not None:
        analysis_data.append(["pH", f"{report.ph_value:.2f}", "", "3.5 - 4.5"])
    
    if report.brix_value is not None:
        analysis_data.append(["Brix", f"{report.brix_value:.1f}", "°Bx", "10.0 - 15.0"])
    
    if report.acidity_value is not None:
        analysis_data.append(["Acidez", f"{report.acidity_value:.2f}", "g/100mL", "0.5 - 1.5"])
    
    if report.color_value:
        analysis_data.append(["Cor", report.color_value, "", ""])
    
    if report.density_value is not None:
        analysis_data.append(["Densidade", f"{report.density_value:.4f}", "g/cm³", ""])
    
    # Adicionar métricas adicionais
    additional_metrics = {}
    if report.additional_metrics:
        try:
            additional_metrics = json.loads(report.additional_metrics)
            for key, value in additional_metrics.items():
                analysis_data.append([key, str(value), "", ""])
        except:
            pass
    
    if len(analysis_data) == 1:
        analysis_data.append(["Não há dados de análise disponíveis.", "", "", ""])
    
    at = Table(analysis_data, colWidths=[100, 150, 100, 100])
    at.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(at)
    
    # Rodapé
    elements.append(Spacer(1, 30))
    footer_text = f"Laudo gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} pelo sistema Zelopack"
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Construir o PDF
    doc.build(elements)
    
    # Preparar o arquivo para download
    buffer.seek(0)
    
    # Nome do arquivo para download
    filename = f"Laudo-{report.id}-{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )


@templates_bp.route('/obter-dados-amostra/<int:sample_id>', methods=['GET'])
@login_required
def get_sample_data(sample_id):
    """API para obter dados de uma amostra específica."""
    sample = Sample.query.get_or_404(sample_id)
    
    sample_data = {
        'id': sample.id,
        'code': sample.code,
        'description': sample.description,
        'material_type': sample.material_type,
        'batch_number': sample.batch_number,
        'client_id': sample.client_id,
        'collection_date': sample.collection_date.strftime('%Y-%m-%d') if sample.collection_date else None,
        'created_at': sample.created_at.strftime('%Y-%m-%d')
    }
    
    return jsonify(sample_data)