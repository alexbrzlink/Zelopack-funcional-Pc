import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import uuid

from app import db
from models import Report, Category, Supplier
from utils.search import search_reports
from utils.file_handler import save_file, allowed_file, get_file_size
from blueprints.reports import reports_bp
from blueprints.reports.forms import ReportUploadForm, SearchForm, SupplierForm

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
    
    form.category.choices = [(c.name, c.name) for c in categories]
    form.category.choices.insert(0, ('', 'Selecione uma categoria'))
    
    form.supplier.choices = [(s.name, s.name) for s in suppliers]
    form.supplier.choices.insert(0, ('', 'Selecione um fornecedor'))
    
    if form.validate_on_submit():
        file = form.file.data
        
        if file and allowed_file(file.filename):
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
            
            # Criar novo registro de laudo
            new_report = Report(
                title=form.title.data,
                description=form.description.data,
                filename=unique_filename,
                original_filename=original_filename,
                file_path=file_path,
                file_type=file_extension[1:],  # Remover o ponto do início
                file_size=file_size,
                
                # Categorização
                category=form.category.data,
                supplier=form.supplier_manual.data if form.supplier_manual.data else form.supplier.data,
                batch_number=form.batch_number.data,
                raw_material_type=form.raw_material_type.data,
                sample_code=form.sample_code.data,
                
                # Análises físico-químicas
                brix=form.brix.data,
                ph=form.ph.data,
                acidity=form.acidity.data,
                
                # Datas
                report_date=report_date,
                report_time=report_time,
                manufacturing_date=manufacturing_date,
                expiration_date=expiration_date,
                
                # Indicadores (mantidos para compatibilidade)
                ph_value=form.ph_value.data,
                brix_value=form.brix_value.data,
                acidity_value=form.acidity_value.data,
                color_value=form.color_value.data
            )
            
            db.session.add(new_report)
            db.session.commit()
            
            flash('Laudo enviado com sucesso!', 'success')
            return redirect(url_for('reports.view', id=new_report.id))
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
    
    form.category.choices = [(c.name, c.name) for c in categories]
    form.category.choices.insert(0, ('', 'Todas as categorias'))
    
    form.supplier.choices = [(s.name, s.name) for s in suppliers]
    form.supplier.choices.insert(0, ('', 'Todos os fornecedores'))
    
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
