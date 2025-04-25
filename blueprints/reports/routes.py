import os
import io
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory, current_app, abort, make_response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm

from app import db
from models import Report, Category, Supplier
from utils.search import search_reports
from utils.file_handler import save_file, allowed_file, get_file_size
from blueprints.reports import reports_bp
from blueprints.reports.forms import ReportUploadForm, SearchForm, SupplierForm


# Definir função para gerar PDF do laudo
def generate_print_version(report):
    """Gera uma versão em PDF do laudo para impressão e download."""
    # Diretório para salvar os PDFs gerados
    pdf_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdf_reports')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Caminho onde o PDF será salvo
    pdf_filename = f"laudo_{report.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    # Criar o PDF usando ReportLab
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Preparar estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Criar estilo personalizado para o cabeçalho
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        textColor=colors.darkblue,
        borderPadding=5,
        borderWidth=1,
        borderColor=colors.lightblue,
        backColor=colors.lightblue,
        alignment=1  # Central
    )
    
    # Elementos do PDF
    elements = []
    
    # Verificar se existe um logo da empresa (caso não exista, apenas usar texto)
    logo_path = os.path.join(current_app.static_folder, 'img', 'logo.png')
    
    # Cabeçalho com logo (se disponível)
    if os.path.exists(logo_path):
        # Adicionar logo e texto lado a lado
        logo_data = [
            [Image(logo_path, width=4*cm, height=2*cm), 
             Paragraph("ZELOPACK INDÚSTRIA<br/>LAUDO TÉCNICO DE ANÁLISE", header_style)]
        ]
        logo_table = Table(logo_data, colWidths=[4*cm, 11*cm])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(logo_table)
    else:
        # Usar apenas texto se logo não estiver disponível
        elements.append(Paragraph("ZELOPACK INDÚSTRIA", title_style))
        elements.append(Paragraph("LAUDO TÉCNICO DE ANÁLISE", header_style))
    
    elements.append(Spacer(1, 0.5*cm))
    
    # Informações principais
    elements.append(Paragraph(f"<b>Laudo Nº:</b> {report.id}", normal_style))
    elements.append(Paragraph(f"<b>Título:</b> {report.title}", normal_style))
    elements.append(Paragraph(f"<b>Data:</b> {report.report_date.strftime('%d/%m/%Y') if report.report_date else 'N/A'}", normal_style))
    elements.append(Paragraph(f"<b>Fornecedor:</b> {report.supplier}", normal_style))
    elements.append(Paragraph(f"<b>Categoria:</b> {report.category}", normal_style))
    elements.append(Paragraph(f"<b>Lote:</b> {report.batch_number or 'N/A'}", normal_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Datas importantes
    data_fabricacao = report.manufacturing_date.strftime('%d/%m/%Y') if report.manufacturing_date else 'N/A'
    data_validade = report.expiration_date.strftime('%d/%m/%Y') if report.expiration_date else 'N/A'
    
    elements.append(Paragraph("<b>Datas:</b>", subtitle_style))
    dates_data = [
        ["Data de Fabricação", "Data de Validade", "Hora do Laudo"],
        [data_fabricacao, data_validade, report.report_time.strftime('%H:%M') if report.report_time else 'N/A']
    ]
    dates_table = Table(dates_data, colWidths=[5*cm, 5*cm, 5*cm])
    dates_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(dates_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Tabela de análises do laudo
    elements.append(Paragraph("<b>Análises do Laudo:</b>", subtitle_style))
    analysis_data = [
        ["Parâmetro", "Laudo", "Laboratório", "Unidade"],
        ["pH", str(report.ph or 'N/A'), str(report.lab_ph or 'N/A'), ""],
        ["Brix", str(report.brix or 'N/A'), str(report.lab_brix or 'N/A'), "°Bx"],
        ["Acidez", str(report.acidity or 'N/A'), str(report.lab_acidity or 'N/A'), "g/100ml"]
    ]
    
    analysis_table = Table(analysis_data, colWidths=[4*cm, 4*cm, 4*cm, 3*cm])
    analysis_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(analysis_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Validação físico-química
    elements.append(Paragraph("<b>Status de Validação:</b>", subtitle_style))
    validation_text = "OK" if report.physicochemical_validation == "OK" else "NÃO PADRÃO"
    validation_color = colors.green if report.physicochemical_validation == "OK" else colors.red
    
    validation_data = [
        ["Validação Físico-Química", "Status"],
        [report.physicochemical_validation or 'N/A', validation_text]
    ]
    
    validation_table = Table(validation_data, colWidths=[8*cm, 7*cm])
    validation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (1, 1), (1, 1), validation_color if validation_text != 'N/A' else colors.white),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.white if validation_text != 'N/A' else colors.black),
    ]))
    elements.append(validation_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Rastreabilidade
    elements.append(Paragraph("<b>Informações de Rastreabilidade:</b>", subtitle_style))
    
    rastreab_data = [
        ["Item", "Status"],
        ["Laudo Arquivado", "Sim" if report.report_archived else "Não"],
        ["Microbiologia Coletada", "Sim" if report.microbiology_collected else "Não"],
        ["Possui Documento Físico", "Sim" if report.has_report_document else "Não"]
    ]
    
    rastreab_table = Table(rastreab_data, colWidths=[8*cm, 7*cm])
    rastreab_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(rastreab_table)
    elements.append(Spacer(1, 1*cm))
    
    # Assinaturas
    elements.append(Paragraph("<b>Responsáveis:</b>", subtitle_style))
    
    sign_data = [
        ["Aprovado por", "Verificado por", "Elaborado por"],
        ["_______________", "_______________", "_______________"],
        ["Data: ___/___/___", "Data: ___/___/___", "Data: ___/___/___"]
    ]
    
    sign_table = Table(sign_data, colWidths=[5*cm, 5*cm, 5*cm])
    sign_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 1), (-1, 1), 30),
    ]))
    elements.append(sign_table)
    
    # Rodapé
    elements.append(Spacer(1, 2*cm))
    
    # Criar uma tabela para o rodapé com uma linha separadora acima
    footer_data = [
        [Paragraph(f"Documento gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style)],
        [Paragraph("© ZELOPACK INDÚSTRIA - Sistema de Gerenciamento de Laudos", normal_style)]
    ]
    
    footer_table = Table(footer_data, colWidths=[15*cm])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('LINEABOVE', (0, 0), (0, 0), 1, colors.gray),
        ('TOPPADDING', (0, 0), (0, 0), 10),
    ]))
    elements.append(footer_table)
    
    # Criar função para adicionar numeração de páginas e outros elementos ao cabeçalho/rodapé de cada página
    def add_page_number(canvas, doc):
        canvas.saveState()
        # Adicionar número de página ao rodapé
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(A4[0] - 2*cm, 1*cm, text)
        
        # Adicionar uma linha separadora no topo da página (exceto na primeira página)
        if page_num > 1:
            canvas.setStrokeColor(colors.gray)
            canvas.line(2*cm, A4[1] - 1*cm, A4[0] - 2*cm, A4[1] - 1*cm)
            # Adicionar texto de continuação no topo das páginas adicionais
            canvas.setFont("Helvetica", 9)
            canvas.drawString(2*cm, A4[1] - 1.5*cm, f"Laudo Nº {report.id} - Continuação")
        
        canvas.restoreState()
    
    # Gerar o PDF com a função para cabeçalho/rodapé
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    # Atualizar o relatório com o caminho do PDF gerado
    report.has_print_version = True
    report.print_version_path = pdf_path
    db.session.commit()
    
    return pdf_path

@reports_bp.route('/')
@login_required
def index():
    """Página inicial do módulo de laudos."""
    recent_reports = Report.query.order_by(Report.upload_date.desc()).limit(10).all()
    return render_template('reports/view.html', reports=recent_reports, title="Laudos Recentes")

@reports_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload de novos laudos."""
    form = ReportUploadForm()
    
    # Carregar opções para os selects
    categories = Category.query.order_by(Category.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    
    # Verificar se há categorias para evitar o erro "Choices cannot be None"
    if categories:
        form.category.choices = [(c.name, c.name) for c in categories]
        form.category.choices.insert(0, ('', 'Selecione uma categoria'))
    else:
        form.category.choices = [('', 'Nenhuma categoria disponível')]
    
    # Verificar se há fornecedores para evitar o erro "Choices cannot be None"
    if suppliers:
        form.supplier.choices = [(s.name, s.name) for s in suppliers]
        form.supplier.choices.insert(0, ('', 'Selecione um fornecedor'))
    else:
        form.supplier.choices = [('', 'Nenhum fornecedor disponível')]
        
    # Garantir que outros campos select também tenham opções válidas
    # O campo assigned_to precisa de initialização
    if not hasattr(form.assigned_to, 'choices') or form.assigned_to.choices is None:
        form.assigned_to.choices = [('', 'Nenhum usuário disponível')]
    
    # Garantir que todos os SelectFields tenham choices inicializados
    for field in form:
        if hasattr(field, 'choices') and field.choices is None:
            field.choices = [('', f'Nenhuma opção disponível para {field.label.text}')]
    
    # Adiciona debug mais detalhado para encontrar o problema
    print(f"Formulário submetido - form.errors: {form.errors}")
    current_app.logger.info(f"Formulário submetido - form.errors: {form.errors}")
    
    # Verifica se o formulário é válido sem considerar o CSRF
    form_valid = form.validate()
    current_app.logger.info(f"form.validate() = {form_valid}")
    
    # Verifica se foi enviado via POST
    is_submitted = form.is_submitted()
    current_app.logger.info(f"form.is_submitted() = {is_submitted}")
    
    # Mostra dados dos campos mais importantes
    current_app.logger.info(f"Título: {form.title.data}")
    current_app.logger.info(f"Arquivo: {form.file.data}")
    current_app.logger.info(f"Categoria: {form.category.data}")
    current_app.logger.info(f"Fornecedor: {form.supplier.data}")
    
    if form.validate_on_submit():
        # Se chegou aqui, o formulário foi validado com sucesso
        print("Formulário validado com sucesso!")
        current_app.logger.info("Formulário validado com sucesso!")
        
        # Validação adicional para garantir que o título seja preenchido
        if not form.title.data or form.title.data.strip() == "":
            flash('Erro: O título do laudo é obrigatório!', 'danger')
            return render_template('reports/upload.html', form=form, title="Upload de Laudo")
            
        file = form.file.data
        
        # Se não tiver arquivo, criar um laudo sem arquivo
        if not file:
            current_app.logger.info("Criando laudo sem arquivo anexado...")
            
            # Valores padrão para campos obrigatórios
            title = form.title.data if form.title.data else "Laudo sem título"
            category_value = form.category.data if form.category.data else ""
            supplier_value = form.supplier_manual.data if form.supplier_manual.data else form.supplier.data
            supplier_final = supplier_value if supplier_value else ""
            
            # Preparar datas do laudo
            report_date = form.report_date.data if form.report_date.data else None
            manufacturing_date = form.manufacturing_date.data if form.manufacturing_date.data else None
            expiration_date = form.expiration_date.data if form.expiration_date.data else None
            report_time = form.report_time.data if form.report_time.data else None
                
            try:
                # Criar novo registro de laudo sem arquivo
                new_report = Report(
                    title=title,
                    description=form.description.data,
                    filename="sem_arquivo.txt",
                    original_filename="sem_arquivo.txt",
                    file_path="",
                    file_type="txt",
                    file_size=0,
                    
                    # Categorização
                    category=category_value,
                    supplier=supplier_final,
                    batch_number=form.batch_number.data,
                    raw_material_type=form.raw_material_type.data,
                    sample_code=form.sample_code.data,
                    
                    # Análises físico-químicas do laudo
                    brix=form.brix.data,
                    ph=form.ph.data,
                    acidity=form.acidity.data,
                    
                    # Análises realizadas em laboratório
                    lab_brix=form.lab_brix.data,
                    lab_ph=form.lab_ph.data,
                    lab_acidity=form.lab_acidity.data,
                    
                    # Validação físico-química
                    physicochemical_validation=form.physicochemical_validation.data if form.physicochemical_validation.data else "não verificado",
                    
                    # Campos adicionais de rastreabilidade
                    report_archived=form.report_archived.data if form.report_archived.data is not None else False,
                    microbiology_collected=form.microbiology_collected.data if form.microbiology_collected.data is not None else False,
                    has_report_document=form.has_report_document.data if form.has_report_document.data is not None else False,
                    
                    # Datas
                    report_date=report_date,
                    report_time=report_time,
                    manufacturing_date=manufacturing_date,
                    expiration_date=expiration_date,
                    
                    # Indicadores (mantidos para compatibilidade)
                    ph_value=form.ph_value.data,
                    brix_value=form.brix_value.data,
                    acidity_value=form.acidity_value.data,
                    color_value=form.color_value.data if form.color_value.data else "",
                    density_value=form.density_value.data
                )
                
                db.session.add(new_report)
                db.session.commit()
                
                flash('Laudo salvo com sucesso (sem arquivo)!', 'success')
                return redirect(url_for('reports.view', id=new_report.id))
                
            except Exception as e:
                current_app.logger.error(f"Erro ao criar laudo sem arquivo: {str(e)}")
                flash(f"Erro ao criar laudo: {str(e)}", "danger")
                return render_template('reports/upload.html', form=form, title="Upload de Laudo")
        
        elif file and allowed_file(file.filename):
            # Gerar nome seguro para o arquivo
            original_filename = file.filename
            file_extension = os.path.splitext(original_filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            
            # Criar caminho do arquivo
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Salvar arquivo
            file.save(file_path)
            
            # Obter o tamanho do arquivo
            file_size = get_file_size(file_path)
            
            # Preparar datas do laudo
            report_date = form.report_date.data if form.report_date.data else None
            manufacturing_date = form.manufacturing_date.data if form.manufacturing_date.data else None
            expiration_date = form.expiration_date.data if form.expiration_date.data else None
            report_time = form.report_time.data if form.report_time.data else None
            
            # Guardar valores em variáveis e fazer verificações antes de criar o objeto
            title = form.title.data if form.title.data else "Laudo sem título"
            category_value = form.category.data if form.category.data else ""
            supplier_value = form.supplier_manual.data if form.supplier_manual.data else form.supplier.data
            supplier_final = supplier_value if supplier_value else ""
            
            # Valores padrão para os campos de validação físico-química
            phys_validation = form.physicochemical_validation.data
            if not phys_validation:
                phys_validation = "não verificado"
                
            # Log detalhado
            current_app.logger.info(f"Criando novo laudo com título: {title}")
            current_app.logger.info(f"Categoria: {category_value}, Fornecedor: {supplier_final}")
            
            try:
                # Criar novo registro de laudo com verificações para campos obrigatórios
                new_report = Report(
                    title=title,
                    description=form.description.data,
                    filename=unique_filename,
                    original_filename=original_filename,
                    file_path=file_path,
                    file_type=file_extension[1:] if file_extension else "unknown",  # Remover o ponto do início
                    file_size=file_size,
                    
                    # Categorização
                    category=category_value,
                    supplier=supplier_final,
                    batch_number=form.batch_number.data,
                    raw_material_type=form.raw_material_type.data,
                    sample_code=form.sample_code.data,
                    
                    # Análises físico-químicas do laudo
                    brix=form.brix.data,
                    ph=form.ph.data,
                    acidity=form.acidity.data,
                    
                    # Análises realizadas em laboratório
                    lab_brix=form.lab_brix.data,
                    lab_ph=form.lab_ph.data,
                    lab_acidity=form.lab_acidity.data,
                    
                    # Validação físico-química
                    physicochemical_validation=phys_validation,
                    
                    # Campos adicionais de rastreabilidade
                    report_archived=form.report_archived.data if form.report_archived.data is not None else False,
                    microbiology_collected=form.microbiology_collected.data if form.microbiology_collected.data is not None else False,
                    has_report_document=form.has_report_document.data if form.has_report_document.data is not None else False,
                    
                    # Datas
                    report_date=report_date,
                    report_time=report_time,
                    manufacturing_date=manufacturing_date,
                    expiration_date=expiration_date,
                    
                    # Indicadores (mantidos para compatibilidade)
                    ph_value=form.ph_value.data,
                    brix_value=form.brix_value.data,
                    acidity_value=form.acidity_value.data,
                    color_value=form.color_value.data if form.color_value.data else "",
                    density_value=form.density_value.data
                )
                current_app.logger.info("Objeto Report criado com sucesso!")
            except Exception as e:
                current_app.logger.error(f"Erro ao criar objeto Report: {str(e)}")
                flash(f"Erro ao criar laudo: {str(e)}", "danger")
                return render_template('reports/upload.html', form=form, title="Upload de Laudo")
            
            db.session.add(new_report)
            db.session.commit()
            
            # Gerar versão para impressão do relatório - com tratamento de erros
            try:
                current_app.logger.info("Gerando versão para impressão do relatório...")
                generate_print_version(new_report)
                current_app.logger.info("Versão para impressão gerada com sucesso!")
            except Exception as e:
                current_app.logger.error(f"Erro ao gerar PDF: {str(e)}")
                flash(f"Laudo salvo, mas houve um erro ao gerar o PDF: {str(e)}", "warning")
            
            flash('Laudo enviado com sucesso!', 'success')
            # Redirecionar para a página de impressão do relatório
            return redirect(url_for('reports.print_report', id=new_report.id))
        else:
            flash('Tipo de arquivo não permitido!', 'danger')
    
    return render_template('reports/upload.html', form=form, title="Upload de Laudo")

@reports_bp.route('/view')
@login_required
def view_all():
    """Visualizar todos os laudos."""
    page = request.args.get('page', 1, type=int)
    reports = Report.query.order_by(Report.upload_date.desc()).paginate(page=page, per_page=20)
    return render_template('reports/view.html', reports=reports, title="Todos os Laudos")

@reports_bp.route('/view/<int:id>')
@login_required
def view(id):
    """Visualizar um laudo específico."""
    report = Report.query.get_or_404(id)
    return render_template('reports/view.html', report=report, single_view=True, title=report.title)

@reports_bp.route('/download/<int:id>')
@login_required
def download(id):
    """Download do arquivo de laudo."""
    report = Report.query.get_or_404(id)
    return send_from_directory(
        directory=os.path.dirname(report.file_path),
        path=report.filename,
        as_attachment=True,
        download_name=report.original_filename
    )

@reports_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Busca de laudos."""
    form = SearchForm()
    
    # Carregar opções para os selects
    categories = Category.query.order_by(Category.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    
    # Verificar se há categorias para evitar o erro "Choices cannot be None"
    if categories:
        form.category.choices = [(c.name, c.name) for c in categories]
        form.category.choices.insert(0, ('', 'Todas as categorias'))
    else:
        form.category.choices = [('', 'Todas as categorias')]
    
    # Verificar se há fornecedores para evitar o erro "Choices cannot be None"
    if suppliers:
        form.supplier.choices = [(s.name, s.name) for s in suppliers]
        form.supplier.choices.insert(0, ('', 'Todos os fornecedores'))
    else:
        form.supplier.choices = [('', 'Todos os fornecedores')]
    
    results = []
    
    if request.method == 'POST' and form.validate():
        query = form.query.data
        category = form.category.data
        supplier = form.supplier.data
        date_from = form.date_from.data
        date_to = form.date_to.data
        sort_by = request.form.get('sort_by', 'date')
        
        # Determinar se deve ordenar por título ou data
        order_by_title = sort_by == 'title'
        
        # Realizar busca com os filtros
        results = search_reports(query, category, supplier, date_from, date_to, order_by_title)
    
    return render_template('reports/search.html', form=form, results=results, title="Buscar Laudos")

@reports_bp.route('/api/search')
@login_required
def api_search():
    """API para busca de laudos (AJAX)."""
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    supplier = request.args.get('supplier', '')
    sort_by = request.args.get('sort_by', 'date')
    
    date_from_str = request.args.get('date_from', '')
    date_to_str = request.args.get('date_to', '')
    
    date_from = None
    date_to = None
    
    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Determinar se deve ordenar por título ou data
    order_by_title = sort_by == 'title'
    
    results = search_reports(query, category, supplier, date_from, date_to, order_by_title)
    return jsonify([r.to_dict() for r in results])

@reports_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Excluir um laudo."""
    report = Report.query.get_or_404(id)
    
    # Excluir arquivo físico
    try:
        os.remove(report.file_path)
    except OSError:
        flash('Erro ao excluir arquivo físico!', 'warning')
    
    # Excluir registro do banco
    db.session.delete(report)
    db.session.commit()
    
    flash('Laudo excluído com sucesso!', 'success')
    return redirect(url_for('reports.view_all'))

@reports_bp.route('/suppliers', methods=['GET'])
@login_required
def suppliers():
    """Lista todos os fornecedores."""
    page = request.args.get('page', 1, type=int)
    suppliers = Supplier.query.order_by(Supplier.name).paginate(page=page, per_page=20)
    return render_template('reports/suppliers.html', suppliers=suppliers, title="Fornecedores")

@reports_bp.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    """Adicionar novo fornecedor."""
    form = SupplierForm()
    
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            contact_name=form.contact_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            notes=form.notes.data,
            type=form.type.data
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        flash('Fornecedor adicionado com sucesso!', 'success')
        return redirect(url_for('reports.suppliers'))
    
    return render_template('reports/supplier_form.html', form=form, title="Adicionar Fornecedor")

@reports_bp.route('/suppliers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    """Editar um fornecedor existente."""
    supplier = Supplier.query.get_or_404(id)
    form = SupplierForm(obj=supplier)
    
    if form.validate_on_submit():
        supplier.name = form.name.data
        supplier.contact_name = form.contact_name.data
        supplier.email = form.email.data
        supplier.phone = form.phone.data
        supplier.address = form.address.data
        supplier.notes = form.notes.data
        supplier.type = form.type.data
        
        db.session.commit()
        
        flash('Fornecedor atualizado com sucesso!', 'success')
        return redirect(url_for('reports.suppliers'))
    
    return render_template('reports/supplier_form.html', form=form, supplier=supplier, title="Editar Fornecedor")

@reports_bp.route('/excluir-fornecedor/<int:supplier_id>', methods=['POST', 'GET'])
@login_required
def excluir_fornecedor(supplier_id):
    """Excluir um fornecedor de forma simplificada."""
    try:
        # Buscar o fornecedor pelo ID
        supplier = Supplier.query.get_or_404(supplier_id)
        
        # Verificar se há laudos associados a este fornecedor
        reports_count = Report.query.filter_by(supplier=supplier.name).count()
        
        if reports_count > 0:
            flash(f'Não é possível excluir este fornecedor. Existem {reports_count} laudos associados a ele.', 'danger')
            return redirect(url_for('reports.suppliers'))
        
        # Salvar o nome para a mensagem de confirmação
        nome_fornecedor = supplier.name
        
        # Excluir o fornecedor
        db.session.delete(supplier)
        db.session.commit()
        
        # Mensagem de sucesso
        flash(f'Fornecedor "{nome_fornecedor}" excluído com sucesso!', 'success')
    except Exception as e:
        # Em caso de erro, exibir mensagem e fazer rollback
        db.session.rollback()
        flash(f'Erro ao excluir fornecedor: {str(e)}', 'danger')
    
    # Redirecionar para a lista de fornecedores
    return redirect(url_for('reports.suppliers'))

@reports_bp.route('/print/<int:id>')
@login_required
def print_report(id):
    """Exibe a página de impressão do laudo."""
    report = Report.query.get_or_404(id)
    
    # Oferece duas opções: visualização no HTML ou download do PDF
    # Se o usuário quiser o PDF, ele poderá usar o botão na página
    now = datetime.now()
    return render_template('reports/print.html', report=report, now=now, title=f"Impressão - {report.title}")
    
@reports_bp.route('/print-pdf/<int:id>')
@login_required
def print_report_pdf(id):
    """Gera ou exibe a versão PDF para impressão do laudo."""
    report = Report.query.get_or_404(id)
    
    # Verificar se já existe uma versão para impressão
    if not report.has_print_version or not report.print_version_path or not os.path.exists(report.print_version_path):
        # Gerar uma nova versão para impressão
        pdf_path = generate_print_version(report)
    else:
        pdf_path = report.print_version_path
    
    # Verificar se o arquivo existe
    if not os.path.exists(pdf_path):
        flash('Erro ao gerar relatório para impressão.', 'danger')
        return redirect(url_for('reports.view', id=report.id))
    
    # Exibir o PDF no navegador
    return send_from_directory(
        directory=os.path.dirname(pdf_path),
        path=os.path.basename(pdf_path),
        as_attachment=False
    )

@reports_bp.route('/download-print/<int:id>')
@login_required
def download_print_report(id):
    """Download da versão para impressão do laudo."""
    report = Report.query.get_or_404(id)
    
    # Verificar se já existe uma versão para impressão
    if not report.has_print_version or not report.print_version_path or not os.path.exists(report.print_version_path):
        # Gerar uma nova versão para impressão
        pdf_path = generate_print_version(report)
    else:
        pdf_path = report.print_version_path
    
    # Verificar se o arquivo existe
    if not os.path.exists(pdf_path):
        flash('Erro ao gerar relatório para impressão.', 'danger')
        return redirect(url_for('reports.view', id=report.id))
    
    # Nome para download
    download_name = f"Laudo_{report.id}_{report.supplier}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Fazer download do PDF
    return send_from_directory(
        directory=os.path.dirname(pdf_path),
        path=os.path.basename(pdf_path),
        as_attachment=True,
        download_name=download_name
    )
