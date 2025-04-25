from flask import render_template, redirect, url_for, request, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from werkzeug.utils import secure_filename
import os
import datetime
import json
import io
import glob
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app import db
from models import Report, ReportTemplate, ReportAttachment, Client, Sample, User, Category
from blueprints.templates import templates_bp
from blueprints.templates.forms import TemplateForm, AutoFillReportForm, ZelopackFormImportForm


@templates_bp.route('/')
@login_required
def index():
    """Página principal do módulo de templates e preenchimento automático."""
    templates = ReportTemplate.query.filter_by(is_active=True).all()
    recent_reports = Report.query.filter(
        Report.template_id.isnot(None)
    ).order_by(Report.updated_date.desc()).limit(5).all()
    
    return render_template(
        'templates/index.html',
        title='Preenchimento Automático de Laudos',
        templates=templates,
        recent_reports=recent_reports
    )


@templates_bp.route('/criar-template', methods=['GET', 'POST'])
@login_required
def create_template():
    """Criar um novo template para laudos."""
    form = TemplateForm()
    
    if form.validate_on_submit():
        template = ReportTemplate(
            name=form.name.data,
            description=form.description.data,
            structure=json.dumps(form.structure.data),
            created_by=current_user.id,
            is_active=True
        )
        
        db.session.add(template)
        db.session.commit()
        
        flash('Template criado com sucesso!', 'success')
        return redirect(url_for('templates.index'))
    
    return render_template(
        'templates/create_template.html',
        title='Criar Template de Laudo',
        form=form
    )


@templates_bp.route('/editar-template/<int:template_id>', methods=['GET', 'POST'])
@login_required
def edit_template(template_id):
    """Editar um template existente."""
    template = ReportTemplate.query.get_or_404(template_id)
    form = TemplateForm(obj=template)
    
    if form.validate_on_submit():
        template.name = form.name.data
        template.description = form.description.data
        template.structure = json.dumps(form.structure.data)
        template.updated_at = datetime.datetime.utcnow()
        
        db.session.commit()
        
        flash('Template atualizado com sucesso!', 'success')
        return redirect(url_for('templates.index'))
    
    # Preencher o campo structure com JSON do banco
    if not form.is_submitted():
        form.structure.data = json.loads(template.structure)
    
    return render_template(
        'templates/edit_template.html',
        title='Editar Template de Laudo',
        form=form,
        template=template
    )


@templates_bp.route('/preencher-laudo/<int:template_id>', methods=['GET', 'POST'])
@login_required
def fill_report(template_id):
    """Preenchimento automático de um laudo a partir de um template."""
    template = ReportTemplate.query.get_or_404(template_id)
    form = AutoFillReportForm()
    
    # Carregar opções para clientes e amostras
    form.client_id.choices = [(c.id, c.name) for c in Client.query.filter_by(is_active=True).all()]
    form.sample_id.choices = [(s.id, f"{s.code} - {s.description}") for s in Sample.query.all()]
    
    if form.validate_on_submit():
        # Criar novo relatório a partir do template
        report = Report(
            title=form.title.data,
            description=form.description.data,
            client_id=form.client_id.data,
            sample_id=form.sample_id.data,
            template_id=template.id,
            report_date=form.report_date.data,
            due_date=form.due_date.data,
            status='pendente',
            stage='rascunho',
            priority=form.priority.data,
            assigned_to=form.assigned_to.data,
            created_by=current_user.id,
            ph_value=form.ph_value.data,
            brix_value=form.brix_value.data,
            acidity_value=form.acidity_value.data,
            color_value=form.color_value.data
        )
        
        # Adicionar métricas adicionais como JSON
        additional_metrics = {}
        if form.additional_metrics.data:
            additional_metrics = json.loads(form.additional_metrics.data)
            report.additional_metrics = json.dumps(additional_metrics)
        
        db.session.add(report)
        db.session.commit()
        
        # Processar os anexos
        if form.attachments.data:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            report_folder = os.path.join(upload_folder, f"report_{report.id}")
            
            os.makedirs(report_folder, exist_ok=True)
            
            for attachment in form.attachments.data:
                if attachment.filename:
                    filename = secure_filename(attachment.filename)
                    file_path = os.path.join(report_folder, filename)
                    attachment.save(file_path)
                    
                    # Registrar o anexo no banco de dados
                    file_size = os.path.getsize(file_path)
                    file_type = os.path.splitext(filename)[1][1:].lower()
                    
                    report_attachment = ReportAttachment(
                        report_id=report.id,
                        filename=filename,
                        original_filename=attachment.filename,
                        file_path=file_path,
                        file_type=file_type,
                        file_size=file_size,
                        description=f"Anexo de {filename}",
                        uploaded_by=current_user.id,
                    )
                    
                    db.session.add(report_attachment)
        
        # Gerar PDF do laudo
        generate_pdf_report(report.id)
        
        db.session.commit()
        
        flash('Laudo preenchido e gerado com sucesso!', 'success')
        return redirect(url_for('templates.view_report', report_id=report.id))
    
    # Pré-carregar estrutura do template 
    template_structure = json.loads(template.structure)
    
    return render_template(
        'templates/fill_report.html',
        title='Preenchimento Automático de Laudo',
        form=form,
        template=template,
        template_structure=template_structure
    )


@templates_bp.route('/visualizar-laudo/<int:report_id>')
@login_required
def view_report(report_id):
    """Visualizar um laudo gerado."""
    report = Report.query.get_or_404(report_id)
    attachments = ReportAttachment.query.filter_by(report_id=report.id).all()
    
    template = None
    template_structure = {}
    if report.template_id:
        template = ReportTemplate.query.get(report.template_id)
        if template:
            template_structure = json.loads(template.structure)
    
    # Converter métricas adicionais de JSON para dicionário
    additional_metrics = {}
    if report.additional_metrics:
        try:
            additional_metrics = json.loads(report.additional_metrics)
        except:
            additional_metrics = {}
    
    return render_template(
        'templates/view_report.html',
        title=f'Laudo: {report.title}',
        report=report,
        template=template,
        template_structure=template_structure,
        additional_metrics=additional_metrics,
        attachments=attachments
    )


@templates_bp.route('/baixar-pdf/<int:report_id>')
@login_required
def download_pdf(report_id):
    """Baixar o PDF gerado para um laudo."""
    report = Report.query.get_or_404(report_id)
    
    if report.has_print_version and report.print_version_path:
        return send_file(
            report.print_version_path,
            as_attachment=True,
            download_name=f"laudo_{report.id}_{report.title}.pdf"
        )
    else:
        # Se não tiver uma versão PDF, gerar na hora
        pdf_path = generate_pdf_report(report.id)
        if pdf_path:
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"laudo_{report.id}_{report.title}.pdf"
            )
        else:
            flash('Erro ao gerar o PDF do laudo.', 'danger')
            return redirect(url_for('templates.view_report', report_id=report.id))


@templates_bp.route('/obter-dados-amostra/<int:sample_id>')
@login_required
def get_sample_data(sample_id):
    """API para obter dados de uma amostra para preenchimento automático."""
    sample = Sample.query.get_or_404(sample_id)
    
    result = {
        'code': sample.code,
        'description': sample.description,
        'material_type': sample.material_type,
        'batch_number': sample.batch_number,
        'client_id': sample.client_id
    }
    
    return jsonify(result)


@templates_bp.route('/obter-dados-cliente/<int:client_id>')
@login_required
def get_client_data(client_id):
    """API para obter dados de um cliente para preenchimento automático."""
    client = Client.query.get_or_404(client_id)
    
    result = {
        'name': client.name,
        'contact_name': client.contact_name,
        'email': client.email,
        'phone': client.phone,
        'address': client.address
    }
    
    return jsonify(result)


@templates_bp.route('/obter-formularios-zelopack/<form_type>')
@login_required
def get_zelopack_forms(form_type):
    """API para obter lista de formulários Zelopack disponíveis para um determinado tipo."""
    # Diretório onde estão os formulários
    forms_dir = current_app.config.get('ATTACHED_ASSETS_FOLDER', 'attached_assets')

    # Lista padrão para tipos de formulários conhecidos
    form_files = []
    
    if form_type == 'controle_qualidade':
        # Procurar por formulários de controle de qualidade (F_QLD_*.*)
        pattern = os.path.join(forms_dir, 'F_QLD_*.*')
        form_files = glob.glob(pattern)
    elif form_type == 'producao':
        # Procurar por formulários de produção (F_PRD_*.*)
        pattern = os.path.join(forms_dir, 'F_PRD_*.*')
        form_files = glob.glob(pattern)
    elif form_type == 'laboratorio':
        # Procurar por formulários de laboratório
        patterns = [
            os.path.join(forms_dir, '*Laboratório*.*'),
            os.path.join(forms_dir, '*Laboratorio*.*'),
            os.path.join(forms_dir, '*Análise*.*'),
            os.path.join(forms_dir, '*Analise*.*')
        ]
        for pattern in patterns:
            form_files.extend(glob.glob(pattern))
    else:
        # Procurar por todos os formulários
        pattern = os.path.join(forms_dir, '*.*')
        form_files = glob.glob(pattern)
        # Filtrar apenas arquivos Excel, Word e PDF
        form_files = [f for f in form_files if f.lower().endswith(('.xlsx', '.xls', '.docx', '.doc', '.pdf'))]
    
    # Formatar os resultados para o frontend
    result = []
    for file_path in form_files:
        file_name = os.path.basename(file_path)
        result.append({
            'value': file_name,
            'label': file_name,
            'path': file_path
        })
    
    return jsonify(result)


@templates_bp.route('/importar-formulario-zelopack', methods=['GET', 'POST'])
@login_required
def import_zelopack_form():
    """Importar um formulário da Zelopack como template."""
    form = ZelopackFormImportForm()
    
    # Carregar categorias para o select field
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.category_id.choices.insert(0, (0, 'Sem categoria'))
    
    # Deixar a lista de formulários em branco inicialmente
    # Será carregada via JavaScript quando o usuário selecionar um tipo
    form.zelopack_form.choices = [('', 'Primeiro selecione um tipo de formulário')]
    
    if form.validate_on_submit():
        # Obter o arquivo de formulário selecionado
        form_file = form.zelopack_form.data
        forms_dir = current_app.config.get('ATTACHED_ASSETS_FOLDER', 'attached_assets')
        file_path = os.path.join(forms_dir, form_file)
        
        if not os.path.exists(file_path):
            flash('Arquivo de formulário não encontrado.', 'danger')
            return redirect(url_for('templates.import_zelopack_form'))
        
        # Determinar a extensão e tipo de arquivo
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Fazer upload e copiar para a área de templates
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        template_folder = os.path.join(upload_folder, 'templates')
        os.makedirs(template_folder, exist_ok=True)
        
        # Nome do arquivo de destino
        dest_filename = secure_filename(f"template_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}")
        dest_path = os.path.join(template_folder, dest_filename)
        
        # Copiar o arquivo para a pasta de uploads
        import shutil
        shutil.copy2(file_path, dest_path)
        
        # Gerar estrutura JSON simples para o template
        structure = {
            "form_type": form.form_type.data,
            "source_file": form_file,
            "fields": {}
        }
        
        # Se opção de gerar campos automaticamente estiver marcada
        if form.auto_generate_fields.data:
            # Aqui faríamos a análise do arquivo para extrair campos
            # Por enquanto, vamos adicionar alguns campos padrão
            if ext in ['.xlsx', '.xls']:
                structure["fields"] = {
                    "data": {"type": "date", "label": "Data", "required": True},
                    "responsavel": {"type": "text", "label": "Responsável", "required": True},
                    "observacoes": {"type": "textarea", "label": "Observações", "required": False}
                }
            elif ext in ['.docx', '.doc']:
                structure["fields"] = {
                    "data": {"type": "date", "label": "Data", "required": True},
                    "processo": {"type": "text", "label": "Processo", "required": True},
                    "responsavel": {"type": "text", "label": "Responsável", "required": True}
                }
        
        # Criar o template no banco de dados
        template = ReportTemplate(
            name=form.name.data,
            description=form.description.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            template_file=dest_filename,
            file_path=dest_path,
            structure=json.dumps(structure),
            created_by=current_user.id,
            version=form.version.data,
            is_active=form.is_active.data
        )
        
        db.session.add(template)
        db.session.commit()
        
        flash(f'Formulário "{form_file}" importado com sucesso como template!', 'success')
        return redirect(url_for('templates.index'))
    
    return render_template(
        'templates/import_zelopack_form.html',
        title='Importar Formulário Zelopack',
        form=form
    )


def generate_pdf_report(report_id):
    """Função para gerar um PDF para um laudo a partir do template."""
    try:
        report = Report.query.get(report_id)
        if not report:
            return None
        
        # Verificar se o relatório tem um template associado
        template = None
        if report.template_id:
            template = ReportTemplate.query.get(report.template_id)
        
        # Definir caminho para salvar o PDF
        upload_folder = current_app.config['UPLOAD_FOLDER']
        report_folder = os.path.join(upload_folder, f"report_{report.id}")
        os.makedirs(report_folder, exist_ok=True)
        
        pdf_filename = f"laudo_{report.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(report_folder, pdf_filename)
        
        # Criar o buffer para o PDF
        buffer = io.BytesIO()
        
        # Criar o documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Título e cabeçalho
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,  # Centralizado
        )
        
        # Adicionar título
        elements.append(Paragraph(f"LAUDO TÉCNICO #{report.id}", header_style))
        elements.append(Spacer(1, 12))
        
        # Adicionar data e informações básicas
        elements.append(Paragraph(f"<b>Título:</b> {report.title}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Data:</b> {report.report_date.strftime('%d/%m/%Y') if report.report_date else 'N/A'}", styles["Normal"]))
        if report.client:
            elements.append(Paragraph(f"<b>Cliente:</b> {report.client.name}", styles["Normal"]))
        elements.append(Spacer(1, 12))
        
        # Adicionar descrição
        if report.description:
            elements.append(Paragraph("<b>Descrição:</b>", styles["Normal"]))
            elements.append(Paragraph(report.description, styles["Normal"]))
            elements.append(Spacer(1, 12))
        
        # Adicionar informações da amostra
        if report.sample:
            elements.append(Paragraph("<b>Dados da Amostra:</b>", styles["Heading3"]))
            elements.append(Paragraph(f"<b>Código:</b> {report.sample.code}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Tipo de Material:</b> {report.sample.material_type or 'N/A'}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Lote:</b> {report.sample.batch_number or 'N/A'}", styles["Normal"]))
            elements.append(Spacer(1, 12))
        
        # Adicionar resultados das análises
        elements.append(Paragraph("<b>Resultados da Análise:</b>", styles["Heading3"]))
        
        # Criar tabela com os valores de análise
        data = [
            ["Parâmetro", "Valor", "Unidade", "Referência"],
        ]
        
        # Adicionar valores principais se disponíveis
        if report.ph_value is not None:
            data.append(["pH", f"{report.ph_value:.2f}", "", "3.5 - 4.5"])
        
        if report.brix_value is not None:
            data.append(["Brix", f"{report.brix_value:.1f}", "°Bx", "10.0 - 15.0"])
        
        if report.acidity_value is not None:
            data.append(["Acidez", f"{report.acidity_value:.2f}", "g/100mL", "0.5 - 1.5"])
        
        if report.color_value:
            data.append(["Cor", report.color_value, "", ""])
        
        if report.density_value is not None:
            data.append(["Densidade", f"{report.density_value:.4f}", "g/cm³", ""])
        
        # Adicionar métricas adicionais se houver
        if report.additional_metrics:
            try:
                additional = json.loads(report.additional_metrics)
                for key, value in additional.items():
                    data.append([key, value, "", ""])
            except:
                pass
                
        # Criar a tabela
        if len(data) > 1:  # Verificar se há dados além do cabeçalho
            table = Table(data, colWidths=[120, 100, 80, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Não há dados de análise disponíveis.", styles["Normal"]))
            
        elements.append(Spacer(1, 12))
        
        # Adicionar notas e observações
        elements.append(Paragraph("<b>Observações:</b>", styles["Heading3"]))
        elements.append(Paragraph("Este laudo foi gerado automaticamente pelo Sistema Zelopack.", styles["Normal"]))
        
        if report.approver_user:
            elements.append(Spacer(1, 36))
            elements.append(Paragraph(f"_______________________________", styles["Normal"]))
            elements.append(Paragraph(f"{report.approver_user.name}", styles["Normal"]))
            elements.append(Paragraph(f"Aprovado em: {report.signature_date.strftime('%d/%m/%Y') if report.signature_date else 'N/A'}", styles["Normal"]))
        
        # Construir o PDF
        doc.build(elements)
        
        # Obter o PDF do buffer
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        
        # Salvar o arquivo físico
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        # Atualizar o relatório com o caminho do PDF
        report.has_print_version = True
        report.print_version_path = pdf_path
        db.session.commit()
        
        return pdf_path
    
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return None