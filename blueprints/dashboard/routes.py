from flask import render_template
from sqlalchemy import func
from datetime import datetime, timedelta

from app import db
from models import Report, Category, Supplier
from blueprints.dashboard import dashboard_bp

@dashboard_bp.route('/')
def index():
    """Dashboard principal com visão geral."""
    # Contagem total de laudos
    total_reports = Report.query.count()
    
    # Total por categoria
    categories = db.session.query(
        Report.category, 
        func.count(Report.id).label('count')
    ).group_by(Report.category).all()
    
    # Total por fornecedor
    suppliers = db.session.query(
        Report.supplier,
        func.count(Report.id).label('count')
    ).group_by(Report.supplier).all()
    
    # Laudos por mês (últimos 6 meses)
    today = datetime.utcnow()
    six_months_ago = today - timedelta(days=180)
    
    reports_by_month = db.session.query(
        func.strftime('%Y-%m', Report.upload_date).label('month'),
        func.count(Report.id).label('count')
    ).filter(Report.upload_date >= six_months_ago).group_by('month').all()
    
    # Laudos recentes
    recent_reports = Report.query.order_by(Report.upload_date.desc()).limit(5).all()
    
    return render_template(
        'dashboard/overview.html',
        title="Dashboard",
        total_reports=total_reports,
        categories=categories,
        suppliers=suppliers,
        reports_by_month=reports_by_month,
        recent_reports=recent_reports
    )
